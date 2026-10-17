"""Client BizHawk de Final Fantasy IV DS (version US).

Boucle principale (game_watcher), environ deux fois par seconde :
1. lire la mémoire (bloc de sauvegarde, flags, indicateur de cinématique, carte) ;
2. à chaque nouvelle carte, repérer les coffres et y écrire leur contenu Archipelago :
   - si le jeu sait le donner lui-même (objet pour ce joueur, gils dans un coffre de gils) ;
   - sinon, un objet "porteur" renommé avec le nom de l'objet Archipelago (names.py),
     retiré de l'inventaire après ouverture ;
3. envoyer au serveur les locations dont le flag vaut 1 ;
4. pour une location qui vient d'être validée sans contenu natif : retirer l'objet d'origine ;
5. livrer les objets reçus (hors cinématique), sauf ceux déjà donnés par un coffre ;
6. annoncer la victoire quand le flag de l'objectif vaut 1.

Toutes les écritures sont "gardées" : si le jeu a modifié la mémoire entre la
lecture et l'écriture, rien n'est écrit et on recommence au tour suivant.
"""
from __future__ import annotations

import logging
import struct
from typing import TYPE_CHECKING, Any, NamedTuple

from NetUtils import ClientStatus

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

from .data import (CHEST_FLAG_BASE, GIL_BOX_TYPE, GOAL_FLAG, ITEM_BOX_TYPE, ITEMS, LOCATIONS, RAM,
                   ItemData)
from .inventory import SlotList
from .names import PLACEHOLDERS, Placeholder, find_msda, parse_entries, read_string, to_game_text
from .spells import ITEM_SPELLS, SPELL_BLOCK_BASE, SPELL_BLOCK_SIZE, add_spells, spells_from_items

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

logger = logging.getLogger("Client")

MAIN_RAM = "Main RAM"
DS_RAM_BASE = 0x02000000       # les pointeurs du jeu sont des adresses DS

# En-tête de la cartouche, recopié par la console en fin de RAM principale.
HEADER_ADDR = 0x3FFE00
GAME_CODE = b"YF4E"            # Final Fantasy IV, version US

# Bloc de sauvegarde lu en une fois : étiquette "PRTY", inventaire, objets clés, or.
BLOCK_START = 0x0D7A78         # étiquette "PRTY" (présente seulement en jeu)
BLOCK_END = RAM["gil"] + 4
INV_SLOTS = RAM["inventory"]
INV_COUNT = RAM["inventory_count"]
KEY_SLOTS = RAM["key_items"]
KEY_COUNT = RAM["key_items_count"]
GIL = RAM["gil"]
MAX_GIL = 9_999_999

# Compteur d'objets reçus, stocké dans le dernier slot de l'inventaire pour
# être sauvegardé avec la partie (l'inventaire est donc limité à 383 slots).
RECEIVED_COUNTER = INV_SLOTS + 383 * 4
INV_CAPACITY = 383
KEY_CAPACITY = 128

# Objets de la carte courante
OBJECT_LIST = RAM["object_list"]   # pointeur (4 octets) suivi du nom de la carte (8 octets)
MAX_OBJECTS = 64
RESCAN_TICKS = 10              # environ 5 secondes de repérage après chaque changement de carte
OBJ_TYPE, OBJ_NEXT, OBJ_FLAG, OBJ_CONTENT, OBJ_QTY = 0x00, 0x04, 0x48, 0x7C, 0x80
OBJ_READ_SIZE = 0x84

# Recherche de la table des textes d'objets ("MSDA")
# Fenêtres les plus probables d'abord (0x250EA8 avec la ROM d'origine), puis toute la RAM :
# avec la ROM patchée, les fichiers chargés en mémoire changent de taille et la table se déplace.
MSDA_SEARCH_WINDOWS = [(0x240000, 0x40000), (0x200000, 0x40000), (0x280000, 0x80000),
                       (0x100000, 0x100000), (0x300000, 0xFF000)]
MSDA_READ_SIZE = 0x10000
READ_CHUNK = 0x8000            # le canal BizHawk refuse les messages de plus de 64 Ko (base64 compris)

# Flags : une seule lecture couvrant toutes les locations et l'objectif.
FLAG_IDS = sorted([data.flag for data in LOCATIONS.values()] + [GOAL_FLAG])
FLAGS_START = FLAG_IDS[0]
FLAGS_SIZE = FLAG_IDS[-1] - FLAGS_START + 1

VANILLA_BY_FLAG = {data.flag: data.vanilla for data in LOCATIONS.values()}
# Contenu réellement donné par le jeu quand le client n'a rien écrit dans le coffre.
# La ROM patchée transforme les coffres de gils en coffres d'objets contenant une Potion.
GIL_CHEST_DEFAULT = ItemData(0x1389)
IN_GAME_BY_FLAG = {
    data.flag: (GIL_CHEST_DEFAULT if data.category == "coffre" and ITEMS[data.vanilla].game_id == 0
                else ITEMS[data.vanilla])
    for data in LOCATIONS.values() if data.vanilla
}
ITEM_BY_AP_ID = {data.ap_id: (name, data) for name, data in ITEMS.items()}
KEY_ITEM_MIN_ID = 0x2329       # à partir de 9001 : objets clés et augments

# Listes de sorts des personnages 1 (Cecil paladin) à 13 (FuSoYa), lues d'un coup.
SPELLS_START = SPELL_BLOCK_BASE + SPELL_BLOCK_SIZE
SPELLS_SIZE = 13 * SPELL_BLOCK_SIZE


def off(address: int) -> int:
    """Position d'une adresse dans le bloc lu."""
    return address - BLOCK_START


def is_key_item(data: ItemData) -> bool:
    return data.key_item or data.game_id >= KEY_ITEM_MIN_ID


class Chest(NamedTuple):
    address: int      # adresse de l'objet coffre dans "Main RAM"
    obj_type: int     # ITEM_BOX_TYPE ou GIL_BOX_TYPE
    flag: int         # adresse du flag = identifiant de la location


class FF4DSClient(BizHawkClient):
    game = "Final Fantasy IV DS"
    system = "NDS"
    patch_suffix = ".apff4ds"

    def __init__(self) -> None:
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self.previous_flags: dict[int, int] | None = None
        self.pending_removals: list[ItemData] = []  # objets à retirer (contenu d'origine ou porteur)
        self.scout_requested = False
        self.map_key: bytes | None = None          # pointeur + nom de la carte au dernier repérage
        self.chests: list[Chest] = []
        self.rescans_left = 0                      # repérages restants après un changement de carte
        self.patched: set[int] = set()             # coffres de la carte courante au contenu natif
        self.native_found: set[int] = set()        # locations dont le jeu a lui-même donné l'objet AP
        self.msda_base: int | None = None
        self.placeholders: list[Placeholder] | None = None  # None : pas encore cherché, [] : indisponible
        self.labelled: dict[int, Placeholder] = {}  # coffre (flag) -> porteur utilisé sur cette carte
        self.msda_retry = False                    # table introuvable : réessayer à la prochaine carte
        self.msda_warned = False

    # ------------------------------------------------------------------ #
    async def validate_rom(self, ctx: BizHawkClientContext) -> bool:
        try:
            header = (await bizhawk.read(ctx.bizhawk_ctx, [(HEADER_ADDR, 0x10, MAIN_RAM)]))[0]
        except bizhawk.RequestFailedError:
            return False
        if header[0x0C:0x10] != GAME_CODE:
            return False

        ctx.game = self.game
        ctx.items_handling = 0b111   # le serveur nous renvoie aussi nos propres objets
        ctx.want_slot_data = True
        ctx.watcher_timeout = 0.5
        self.reset()
        return True

    def on_package(self, ctx: BizHawkClientContext, cmd: str, args: dict[str, Any]) -> None:
        if cmd == "Connected":
            self.reset()

    @staticmethod
    def planned(ctx: BizHawkClientContext, flag: int) -> tuple[int, int] | None:
        """(joueur destinataire, objet) prévu à cette location, d'après LocationScouts."""
        info = ctx.locations_info.get(flag)
        return None if info is None else (info.player, info.item)

    # ------------------------------------------------------------------ #
    def native_content(self, ctx: BizHawkClientContext, chest: Chest) -> ItemData | None:
        """Contenu que le jeu peut donner lui-même dans ce coffre, sinon None."""
        planned = self.planned(ctx, chest.flag)
        if planned is None or planned[0] != ctx.slot:
            return None  # objet d'un autre joueur (ou plan inconnu) : on garde l'objet d'origine
        entry = ITEM_BY_AP_ID.get(planned[1])
        if entry is None:
            return None
        data = entry[1]
        if chest.obj_type == GIL_BOX_TYPE and data.game_id == 0:
            return data
        if chest.obj_type == ITEM_BOX_TYPE and data.game_id != 0 and not is_key_item(data):
            return data
        return None

    async def scan_chests(self, ctx: BizHawkClientContext, head: int) -> list[Chest]:
        """Parcourt la liste chaînée des objets de la carte et garde les coffres de nos locations."""
        chests: list[Chest] = []
        pointer = head
        for _ in range(MAX_OBJECTS):
            if not DS_RAM_BASE <= pointer < DS_RAM_BASE + 0x400000:
                break
            address = pointer - DS_RAM_BASE
            raw = (await bizhawk.read(ctx.bizhawk_ctx, [(address, OBJ_READ_SIZE, MAIN_RAM)]))[0]
            obj_type, pointer = struct.unpack_from("<II", raw, 0)
            if obj_type in (ITEM_BOX_TYPE, GIL_BOX_TYPE):
                flag = CHEST_FLAG_BASE + struct.unpack_from("<I", raw, OBJ_FLAG)[0]
                if flag in VANILLA_BY_FLAG:
                    chests.append(Chest(address, obj_type, flag))
        return chests

    async def patch_chests(self, ctx: BizHawkClientContext, flags: dict[int, int]) -> None:
        """Écrit le contenu Archipelago dans les coffres non ouverts de la carte courante."""
        for chest in self.chests:
            if chest.flag in self.patched or chest.flag in self.labelled or flags.get(chest.flag):
                continue
            data = self.native_content(ctx, chest)
            if data is None:
                await self.label_chest(ctx, chest)
                continue
            if chest.obj_type == GIL_BOX_TYPE:
                writes = [(chest.address + OBJ_CONTENT, struct.pack("<I", data.quantity), MAIN_RAM)]
            else:
                writes = [(chest.address + OBJ_CONTENT, struct.pack("<II", data.game_id, data.quantity), MAIN_RAM)]
            guards = [
                (chest.address + OBJ_TYPE, struct.pack("<I", chest.obj_type), MAIN_RAM),
                (chest.address + OBJ_FLAG, struct.pack("<I", chest.flag - CHEST_FLAG_BASE), MAIN_RAM),
            ]
            if await bizhawk.guarded_write(ctx.bizhawk_ctx, writes, guards):
                self.patched.add(chest.flag)

    @staticmethod
    async def read_large(ctx: BizHawkClientContext, start: int, size: int) -> bytes:
        """Lit une grande zone mémoire en plusieurs morceaux."""
        chunks = []
        for address in range(start, start + size, READ_CHUNK):
            length = min(READ_CHUNK, start + size - address)
            chunks.append((await bizhawk.read(ctx.bizhawk_ctx, [(address, length, MAIN_RAM)]))[0])
        return b"".join(chunks)

    async def setup_placeholders(self, ctx: BizHawkClientContext) -> None:
        """Trouve la table des textes d'objets et prépare les porteurs.
        Si elle est introuvable (pas encore chargée), on réessaiera à la prochaine carte."""
        self.placeholders = []
        for start, size in MSDA_SEARCH_WINDOWS:
            window = await self.read_large(ctx, start, size)
            base = find_msda(window, start)
            if base is not None:
                break
        else:
            if not self.msda_warned:
                logger.warning("Table des noms d'objets introuvable pour l'instant : "
                               "nouvel essai à chaque changement de carte.")
                self.msda_warned = True
            self.msda_retry = True
            return
        self.msda_retry = False
        logger.info(f"Table des noms d'objets trouvée à 0x{base:06X}.")
        raw = await self.read_large(ctx, base, MSDA_READ_SIZE)
        entries = parse_entries(base, raw)
        for item_id in PLACEHOLDERS:
            if item_id not in entries or item_id + 10000 not in entries:
                continue
            name_field, name_offset = entries[item_id]
            _, desc_offset = entries[item_id + 10000]
            if name_offset == desc_offset or desc_offset >= len(raw):
                continue  # déjà détourné par une session précédente : on ne s'en sert pas
            self.placeholders.append(Placeholder(item_id, name_field, name_offset, desc_offset,
                                                 base + desc_offset, read_string(raw, desc_offset)))
        self.msda_base = base

    async def restore_labels(self, ctx: BizHawkClientContext) -> None:
        """Rend leur nom et leur description d'origine aux porteurs utilisés."""
        if not self.labelled or self.msda_base is None:
            self.labelled = {}
            return
        writes = []
        for p in set(self.labelled.values()):
            writes.append((p.name_offset_addr, struct.pack("<I", p.name_offset), MAIN_RAM))
            writes.append((p.desc_addr, p.desc_original + b"\x00\x00", MAIN_RAM))
        await bizhawk.guarded_write(ctx.bizhawk_ctx, writes, [(self.msda_base, b"MSDA", MAIN_RAM)])
        self.labelled = {}

    def label_for(self, ctx: BizHawkClientContext, flag: int) -> str | None:
        planned = self.planned(ctx, flag)
        if planned is None:
            return None
        receiver, item = planned
        item_name = ctx.item_names.lookup_in_slot(item, receiver)
        if receiver == ctx.slot:
            return item_name
        return f"{item_name} ({ctx.player_names.get(receiver, '?')})"

    async def label_chest(self, ctx: BizHawkClientContext, chest: Chest) -> bool:
        """Met un porteur renommé dans un coffre d'objet. Renvoie True si c'est fait."""
        if chest.obj_type != ITEM_BOX_TYPE or not self.placeholders or self.msda_base is None:
            return False
        native_ids = {data.game_id for c in self.chests if (data := self.native_content(ctx, c)) is not None}
        free = [p for p in self.placeholders
                if p not in self.labelled.values() and p.item_id not in native_ids]
        label = self.label_for(ctx, chest.flag)
        if not free or label is None:
            return False
        p = free[0]
        text = to_game_text(label, len(p.desc_original) // 2 + 1)
        writes = [
            (p.desc_addr, text, MAIN_RAM),
            (p.name_offset_addr, struct.pack("<I", p.desc_offset), MAIN_RAM),
            (chest.address + OBJ_CONTENT, struct.pack("<II", p.item_id, 1), MAIN_RAM),
        ]
        guards = [
            (self.msda_base, b"MSDA", MAIN_RAM),
            (chest.address + OBJ_TYPE, struct.pack("<I", chest.obj_type), MAIN_RAM),
            (chest.address + OBJ_FLAG, struct.pack("<I", chest.flag - CHEST_FLAG_BASE), MAIN_RAM),
        ]
        if await bizhawk.guarded_write(ctx.bizhawk_ctx, writes, guards):
            self.labelled[chest.flag] = p
            return True
        return False

    # ------------------------------------------------------------------ #
    async def sync_spells(self, ctx: BizHawkClientContext, delivered_count: int) -> None:
        """Sorts en objets : chaque sort reçu (et déjà compté comme livré) doit être dans la
        liste de tous les personnages qui l'apprennent normalement. On complète ce qui manque.
        Écriture idempotente : si le jeu a reconstruit une liste (un personnage rejoint),
        le sort est simplement réécrit au tour suivant."""
        itemized = (ctx.slot_data or {}).get("spell_items") or []
        if not itemized:
            return
        wanted = spells_from_items([item.item for item in ctx.items_received[:delivered_count]], itemized)
        if not wanted:
            return
        raw = (await bizhawk.read(ctx.bizhawk_ctx, [(SPELLS_START, SPELLS_SIZE, MAIN_RAM)]))[0]
        data = add_spells(raw, wanted)
        if data != raw:
            await bizhawk.guarded_write(ctx.bizhawk_ctx, [(SPELLS_START, bytes(data), MAIN_RAM)],
                                        [(SPELLS_START, raw, MAIN_RAM), (RAM["event_running"], [0], MAIN_RAM)])

    async def game_watcher(self, ctx: BizHawkClientContext) -> None:
        if ctx.server is None or ctx.slot is None:
            return

        # Demander une fois au serveur le contenu de toutes nos locations.
        if not self.scout_requested and ctx.server_locations:
            self.scout_requested = True
            await ctx.send_msgs([{"cmd": "LocationScouts", "locations": sorted(ctx.server_locations),
                                  "create_as_hint": 0}])

        try:
            block, flags_raw, event_raw, map_raw = await bizhawk.read(ctx.bizhawk_ctx, [
                (BLOCK_START, BLOCK_END - BLOCK_START, MAIN_RAM),
                (FLAGS_START, FLAGS_SIZE, MAIN_RAM),
                (RAM["event_running"], 1, MAIN_RAM),
                (OBJECT_LIST, 12, MAIN_RAM),
            ])
        except bizhawk.RequestFailedError:
            return

        # Écran titre ou chargement : pas de partie en cours.
        if block[0:4] != b"PRTY":
            self.previous_flags = None
            self.map_key = None
            return

        flags = {flag: flags_raw[flag - FLAGS_START] for flag in FLAG_IDS}

        # --- 1. Coffres de la carte courante ---------------------------------
        try:
            if self.placeholders is None or (self.msda_retry and map_raw != self.map_key):
                await self.setup_placeholders(ctx)
            if map_raw != self.map_key:
                self.map_key = map_raw
                self.patched = set()
                await self.restore_labels(ctx)
                self.chests = []
                self.rescans_left = RESCAN_TICKS
            if self.rescans_left > 0:
                # Les coffres sont créés par le script de la carte, parfois après le changement
                # de nom : on reparcourt la liste pendant quelques tours après l'arrivée.
                self.rescans_left -= 1
                found = {chest.flag: chest for chest in self.chests}
                for chest in await self.scan_chests(ctx, struct.unpack_from("<I", map_raw, 0)[0]):
                    found[chest.flag] = chest          # adresse la plus récente
                if len(found) != len(self.chests):
                    map_name = map_raw[4:12].split(b"\0")[0].decode("ascii", "replace")
                    logger.info(f"Carte {map_name} : {len(found)} coffre(s) Archipelago repéré(s).")
                self.chests = list(found.values())
            if ctx.locations_info:
                await self.patch_chests(ctx, flags)
        except bizhawk.RequestFailedError:
            return

        # --- 2. Locations validées -------------------------------------------
        checked = {flag for flag in VANILLA_BY_FLAG if flags[flag]}
        new_checks = checked - ctx.checked_locations
        if new_checks:
            await ctx.send_msgs([{"cmd": "LocationChecks", "locations": sorted(new_checks)}])

        # Une location qui passe de 0 à 1 pendant que le client tourne.
        if self.previous_flags is not None:
            for flag in VANILLA_BY_FLAG:
                if not flags[flag] or self.previous_flags[flag]:
                    continue
                if flag in self.patched:
                    self.native_found.add(flag)       # le jeu a donné l'objet AP lui-même
                elif flag in self.labelled:
                    self.pending_removals.append(ItemData(self.labelled[flag].item_id))  # le porteur
                elif flag in IN_GAME_BY_FLAG:
                    self.pending_removals.append(IN_GAME_BY_FLAG[flag])
                planned = self.planned(ctx, flag)
                if planned is not None and planned[0] != ctx.slot:
                    item_name = ctx.item_names.lookup_in_slot(planned[1], planned[0])
                    receiver = ctx.player_names.get(planned[0], "?")
                    await bizhawk.display_message(ctx.bizhawk_ctx, f"Envoyé : {item_name} à {receiver}")
        self.previous_flags = flags

        # --- 3. Objectif -------------------------------------------------------
        if flags[GOAL_FLAG] and not ctx.finished_game:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True

        # --- 4. Écritures d'inventaire (jamais pendant une cinématique) -------
        if event_raw[0] != 0:
            return
        received = struct.unpack_from("<H", block, off(RECEIVED_COUNTER))[0]
        try:
            await self.sync_spells(ctx, received)
        except bizhawk.RequestFailedError:
            return
        to_deliver = ctx.items_received[received:]
        if not self.pending_removals and not to_deliver:
            return

        inventory = SlotList(block[off(INV_SLOTS):], struct.unpack_from("<I", block, off(INV_COUNT))[0],
                             INV_CAPACITY, is_key_list=False)
        key_items = SlotList(block[off(KEY_SLOTS):], struct.unpack_from("<I", block, off(KEY_COUNT))[0],
                             KEY_CAPACITY, is_key_list=True)
        gil = struct.unpack_from("<I", block, off(GIL))[0]
        messages: list[str] = []

        for data in self.pending_removals:
            if data.game_id == 0:
                gil = max(0, gil - data.quantity)
            elif is_key_item(data):
                key_items.remove(data.game_id, data.quantity)
            else:
                inventory.remove(data.game_id, data.quantity)

        delivered = 0
        for network_item in to_deliver:
            # Objet trouvé dans un de nos coffres et déjà donné par le jeu : rien à faire.
            if network_item.player == ctx.slot and network_item.location in self.native_found:
                delivered += 1
                continue
            sender = ctx.player_names.get(network_item.player, "?")
            if network_item.item in ITEM_SPELLS:
                # Sort : appris par sync_spells au tour suivant, une fois compté comme livré.
                delivered += 1
                messages.append(f"Reçu : {ctx.item_names.lookup_in_slot(network_item.item)} ({sender})")
                continue
            entry = ITEM_BY_AP_ID.get(network_item.item)
            if entry is None:
                logger.warning(f"Objet inconnu reçu : {network_item.item}")
                delivered += 1
                continue
            name, data = entry
            if data.game_id == 0:
                gil = min(MAX_GIL, gil + data.quantity)
            elif is_key_item(data):
                if not key_items.add(data.game_id, data.quantity):
                    break  # liste pleine : on réessaiera plus tard
            elif not inventory.add(data.game_id, data.quantity):
                break      # inventaire plein : on réessaiera plus tard
            delivered += 1
            messages.append(f"Reçu : {name} ({sender})")

        writes = [
            (INV_SLOTS, inventory.to_bytes(), MAIN_RAM),
            (INV_COUNT, struct.pack("<I", inventory.count), MAIN_RAM),
            (KEY_SLOTS, key_items.to_bytes(), MAIN_RAM),
            (KEY_COUNT, struct.pack("<I", key_items.count), MAIN_RAM),
            (GIL, struct.pack("<I", gil), MAIN_RAM),
            (RECEIVED_COUNTER, struct.pack("<HBB", received + delivered, 0, 0), MAIN_RAM),
        ]
        guards = [
            (BLOCK_START, block, MAIN_RAM),
            (RAM["event_running"], [0], MAIN_RAM),
        ]
        try:
            if await bizhawk.guarded_write(ctx.bizhawk_ctx, writes, guards):
                self.pending_removals = []
                for message in messages:
                    await bizhawk.display_message(ctx.bizhawk_ctx, message)
        except bizhawk.RequestFailedError:
            return
