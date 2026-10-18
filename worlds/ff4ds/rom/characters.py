"""Personnages de Final Fantasy IV DS et emplacements où ils rejoignent l'équipe.

Données pures, utilisées par le monde (tirage au sort) et par le patch de la ROM.
Relevé dans les scripts de la ROM US : chaque arrivée = op068 (rejoint), op102 (niveau),
op0AC (équipement) et parfois op17C (commandes, sorts).
"""
from __future__ import annotations

import struct
from typing import NamedTuple


class Character(NamedTuple):
    char_id: int                       # identifiant de op068 / op069
    equipment: tuple[int, ...]         # op0AC : bouclier, arme, casque, armure, bras
    abilities: tuple[int, ...] = ()    # op17C : commandes et sorts donnés à l'arrivée


# Équipement et capacités d'arrivée, copiés de leur arrivée d'origine.
# Cecil (0 et 1), Rydia adulte (5) et Golbez (14) ne sont pas tirés au sort.
CHARACTERS: dict[str, Character] = {
    "Kain": Character(2, (8001, 6101, 8104, 8206, 8303)),
    "Rosa": Character(3, (0, 6901, 0, 8208, 8301)),
    # Rydia : + Fire (4501), qu'elle apprend normalement au mur de glace du mont Hobs (fondu dès le départ).
    "Rydia": Character(4, (0, 6801, 0, 8203, 8309), (5, 13, 1517, 1505, 4501)),
    "Tellah": Character(6, (0, 6901, 0, 8205, 8305)),
    "Porom": Character(7, (0, 6902, 8105, 8205, 8309)),
    "Palom": Character(8, (0, 6802, 8105, 8205, 8309)),
    "Edward": Character(9, (0, 6301, 8103, 8204, 8301)),
    "Yang": Character(10, (0, 0, 0, 8209, 8305)),
    "Cid": Character(11, (0, 6501, 0, 8202, 0)),
    "Edge": Character(12, (6701, 6701, 8106, 8213, 8312)),
    "FuSoYa": Character(13, (0, 6905, 8109, 8215, 8313)),
}
CHARACTER_NAMES = {c.char_id: name for name, c in CHARACTERS.items()}


class Slot(NamedTuple):
    vanilla: str       # personnage d'origine
    level: int         # niveau à l'arrivée (op102 d'origine)
    join_arg: int      # second argument de op068 d'origine


# Emplacements, dans l'ordre de l'histoire.
SLOTS: dict[str, Slot] = {
    "Starting Character": Slot("Kain", 10, 4),
    "Kaipo Character": Slot("Rydia", 7, 0),
    "Waterway Character": Slot("Tellah", 13, 0),
    "Damcyan Character": Slot("Edward", 9, 0),
    "Rosa Character": Slot("Rosa", 15, 0),        # rejoint à l'objectif de la tranche 1
    "Mt Hobs Character": Slot("Yang", 20, 0),
    "Mysidia Character 1": Slot("Porom", 10, 0),  # l'Ancien de Mysidia confie les jumeaux
    "Mysidia Character 2": Slot("Palom", 10, 0),
    "Ordeals Character": Slot("Tellah", 20, 0),   # d'origine sans op102 : Tellah garde son niveau
    "Baron Character": Slot("Yang", 25, 0),       # auberge de Baron ; d'origine sans op102
    "Cid Character": Slot("Cid", 20, 0),          # après Cagnazzo
    "Zot Character 1": Slot("Kain", 32, 0),       # sommet de la tour de Zott
    "Zot Character 2": Slot("Rosa", 26, 0),
    "Dwarf Castle Character": Slot("Rydia", 30, 0),   # combat contre Golbez (Rydia adulte, perso 5)
}
GOAL_SLOT = None       # objectif (Golbez au château des nains) après toutes les arrivées
PARTY_MAX = 5          # Cecil compris

# Arrivées et départs de l'histoire, dans l'ordre. Un départ ("leave") ne se produit qu'avec
# departures = vanilla (toujours le cas dans le monde), et seulement si le personnage de l'emplacement est encore là.
STORY = [
    ("join", "Starting Character"),
    ("leave", "Starting Character"),     # village de la Brume
    ("join", "Kaipo Character"),
    ("join", "Waterway Character"),
    ("leave", "Waterway Character"),     # Damcyan
    ("join", "Damcyan Character"),
    ("join", "Rosa Character"),
    ("join", "Mt Hobs Character"),
    ("leave", "Rosa Character"),         # Fabul : Rosa enlevée par Kain
    ("leave", "Kaipo Character"),        # Léviathan : Rydia, Edward et Yang emportés
    ("leave", "Damcyan Character"),
    ("leave", "Mt Hobs Character"),
    ("join", "Mysidia Character 1"),
    ("join", "Mysidia Character 2"),
    ("join", "Ordeals Character"),
    ("join", "Baron Character"),
    ("leave", "Mysidia Character 1"),    # Cagnazzo : Porom et Palom pétrifiés
    ("leave", "Mysidia Character 2"),
    ("join", "Cid Character"),
    ("leave", "Ordeals Character"),      # tour de Zott : Tellah part après Golbez
    ("join", "Zot Character 1"),
    ("join", "Zot Character 2"),
    ("leave", "Cid Character"),          # château des nains : Cid part réparer l'Enterprise
    ("join", "Dwarf Castle Character"),
    ("leave", "Baron Character"),        # tour de Babil : Yang reste aux canons
]


class PartyPlan(NamedTuple):
    joins: dict[str, tuple[str, str | None] | None]   # emplacement -> (arrivant, remplacé) ou None
    leaves: dict[str, str | None]                      # emplacement -> personnage qui part, ou None


def vanilla_party() -> dict[str, str | None]:
    return {slot: data.vanilla for slot, data in SLOTS.items()}


def plan_party(party: dict[str, str | None], departures: str = "vanilla",
               full_party: str = "replace_oldest") -> PartyPlan:
    """Suit l'équipe tout au long de l'histoire. Quand l'équipe est pleine (5 avec Cecil) :
    replace_oldest = le nouveau remplace le membre arrivé le plus tôt ; skip = il ne vient pas."""
    members: list[str] = []
    joins: dict[str, tuple[str, str | None] | None] = {}
    leaves: dict[str, str | None] = {}
    for kind, slot in STORY:
        name = party.get(slot)
        if kind == "join":
            if name is None:
                joins[slot] = None
            elif len(members) + 1 < PARTY_MAX:
                members.append(name)
                joins[slot] = (name, None)
            elif full_party == "replace_oldest":
                replaced = members.pop(0)
                members.append(name)
                joins[slot] = (name, replaced)
            else:
                joins[slot] = None
        else:
            joined = joins.get(slot)
            if departures == "vanilla" and joined and joined[0] in members:
                members.remove(joined[0])
                leaves[slot] = joined[0]
            else:
                leaves[slot] = None
    return PartyPlan(joins, leaves)


def fill_empty_slots(party: dict[str, str | None], departures: str, full_party: str,
                     choose) -> dict[str, str | None]:
    """Emplacements vides (plus d'emplacements que de personnages) : un personnage déjà venu puis
    parti (départ de l'histoire ou remplacé) revient. choose(liste) tire le revenant."""
    party = dict(party)
    for index, (kind, slot) in enumerate(STORY):
        if kind != "join" or party.get(slot):
            continue
        before = plan_party({s: party.get(s) for _, s in STORY[:index]}, departures, full_party)
        came = [joined[0] for joined in before.joins.values() if joined]
        members = _members(before, STORY[:index])
        gone = sorted(set(came) - set(members))
        if gone:
            party[slot] = choose(gone)
    return party


def _members(plan: PartyPlan, story) -> list[str]:
    """Équipe (sans Cecil) après les étapes story, d'après le plan."""
    members: list[str] = []
    for kind, slot in story:
        if kind == "join":
            joined = plan.joins.get(slot)
            if joined:
                if joined[1] in members:
                    members.remove(joined[1])
                members.append(joined[0])
        elif plan.leaves.get(slot) in members:
            members.remove(plan.leaves[slot])
    return members


def joined_slots(plan: PartyPlan) -> list[str]:
    """Emplacements dont le personnage rejoint réellement l'équipe."""
    return [slot for slot in SLOTS if plan.joins.get(slot)]


# ------------------------------------------------------------------ #
# Bytecode                                                            #
# ------------------------------------------------------------------ #
# Rydia adulte (perso 5) : à partir du château des nains (flag 175), le jeu remplace Rydia enfant (4)
# par Rydia adulte. Équipement d'origine (t12_03, 00F3E).
ADULT_RYDIA = Character(5, (0, 7201, 8113, 8215, 8311))
ADULT_SLOTS = {"Dwarf Castle Character"}


def character(name: str, slot: str) -> Character:
    if name == "Rydia" and slot in ADULT_SLOTS:
        return ADULT_RYDIA
    return CHARACTERS[name]


def join_code(name: str, slot: str) -> bytes:
    """op068 + op102 + op0AC + op17C : le personnage rejoint au niveau de l'emplacement."""
    c, s = character(name, slot), SLOTS[slot]
    code = struct.pack("<HIB", 0x68, c.char_id, s.join_arg)
    code += struct.pack("<HIH", 0x102, c.char_id, s.level)
    code += struct.pack("<HIHHHHH", 0xAC, c.char_id, *c.equipment)
    for ability in c.abilities:
        code += struct.pack("<HII", 0x17C, c.char_id, ability)
    return code


def leave_code(name: str) -> bytes:
    """Le personnage rend son équipement (comme Kain au village de la Brume) et quitte l'équipe."""
    char_id = CHARACTERS[name].char_id
    return struct.pack("<HIHHHHH", 0xAC, char_id, 0, 0, 0, 0, 0) + struct.pack("<HIB", 0x69, char_id, 0)
