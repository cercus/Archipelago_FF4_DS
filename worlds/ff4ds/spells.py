"""Sorts de Final Fantasy IV DS devenus des objets Archipelago (option spell_items).

Fonctionnement :
- un objet par sort (« Sight », « Toad »…), ou un objet progressif pour les familles
  (« Progressive Cure » : Cure -> Cura -> Curaga -> Curaja) ;
- recevoir l'objet apprend le sort à tous les personnages qui l'apprennent normalement ;
- la ROM est patchée pour que ces sorts ne s'apprennent plus en montant de niveau ;
- les sorts de niveau 1 (sorts de départ) restent acquis, sauf si l'option starting_spells est désactivée.

Ce fichier ne contient que des données et des fonctions pures (pas de BizHawk).
Les tables viennent de la ROM US (player.chaindata.lz et N/babil_ability.msd).
"""
from __future__ import annotations

# Identifiant Archipelago d'un objet sort :
#   - sort seul           : SPELL_FLAG | ID du sort        ex. Sight -> 0x02000FB7
#   - famille progressive : PROGRESSIVE_FLAG | 1er sort    ex. Progressive Cure -> 0x02100FA1
SPELL_FLAG = 0x02000000
PROGRESSIVE_FLAG = 0x02100000

SPELL_IDS: dict[str, int] = {
    "Cure": 4001,
    "Cura": 4002,
    "Curaga": 4003,
    "Curaja": 4004,
    "Esuna": 4005,
    "Raise": 4006,
    "Arise": 4007,
    "Hold": 4008,
    "Silence": 4009,
    "Confuse": 4010,
    "Blink": 4011,
    "Protect": 4012,
    "Shell": 4013,
    "Slow": 4014,
    "Haste": 4015,
    "Berserk": 4016,
    "Reflect": 4017,
    "Holy": 4018,
    "Dispel": 4019,
    "Libra": 4020,
    "Mini": 4021,
    "Teleport": 4022,
    "Sight": 4023,
    "Float": 4024,
    "Bubble": 4025,
    "Bravery": 4026,
    "Faith": 4027,
    "Fire": 4501,
    "Fira": 4502,
    "Firaga": 4503,
    "Blizzard": 4504,
    "Blizzara": 4505,
    "Blizzaga": 4506,
    "Thunder": 4507,
    "Thundara": 4508,
    "Thundaga": 4509,
    "Sleep": 4510,
    "Poison": 4511,
    "Warp": 4512,
    "Toad": 4513,
    "Stop": 4514,
    "Osmose": 4515,
    "Bio": 4516,
    "Tornado": 4517,
    "Break": 4518,
    "Pig": 4519,
    "Quake": 4520,
    "Death": 4521,
    "Meteor": 4522,
    "Flare": 4523,
    "Drain": 4524,
    "Comet": 4525,
    "Twin Meteor": 4526,
    "Pyroblast": 4527,
    "Waterga": 4528,
    "Ultima": 4529,
}

# Apprentissage par niveau dans la ROM (player.chaindata, bloc 17 + personnage) : (niveau, sort).
LEARNSETS: dict[int, list[tuple[int, int]]] = {
    1: [  # Cecil (Paladin)
        (1, 4001), (3, 4023), (8, 4020), (10, 4012), (20, 4002), (29, 4022), (33, 4013), (35, 4005),
        (40, 4006),
    ],
    3: [  # Rosa
        (1, 4001), (1, 4008), (1, 4014), (1, 4020), (1, 4023), (11, 4006), (12, 4012), (13, 4002),
        (15, 4009), (18, 4005), (20, 4013), (23, 4011), (24, 4010), (26, 4022), (30, 4016),
        (31, 4003), (32, 4021), (33, 4019), (35, 4015), (38, 4024), (40, 4017), (45, 4004),
        (55, 4007), (60, 4018),
    ],
    4: [  # Rydia (child)
        (1, 4001), (4, 4023), (7, 4008), (8, 4010), (10, 4005), (12, 4002), (15, 4006), (1, 4504),
        (5, 4507), (8, 4510), (10, 4511), (12, 4512), (13, 4513), (15, 4514), (20, 4519),
        (26, 4516),
    ],
    5: [  # Rydia (adult)
        (1, 4501), (1, 4504), (1, 4507), (1, 4510), (1, 4511), (11, 4519), (12, 4505), (13, 4502),
        (14, 4508), (15, 4514), (19, 4516), (22, 4513), (23, 4520), (26, 4524), (30, 4512),
        (33, 4515), (38, 4506), (40, 4503), (41, 4509), (43, 4518), (55, 4521), (58, 4517),
        (60, 4523), (80, 4522),
    ],
    6: [  # Tellah
        (1, 4501), (1, 4504), (1, 4507), (1, 4510), (1, 4511), (1, 4515), (1, 4002), (1, 4005),
        (1, 4006), (1, 4009), (1, 4010), (1, 4011), (1, 4022),
    ],
    7: [  # Porom
        (1, 4001), (1, 4008), (1, 4014), (1, 4020), (1, 4023), (11, 4006), (12, 4012), (13, 4002),
        (15, 4009), (18, 4013), (19, 4022), (20, 4005), (23, 4011), (25, 4010), (29, 4016),
        (31, 4019), (32, 4021), (33, 4003), (38, 4015), (40, 4024), (44, 4017), (48, 4004),
        (52, 4018), (56, 4007),
    ],
    8: [  # Palom
        (1, 4501), (1, 4504), (1, 4507), (1, 4510), (1, 4511), (11, 4519), (12, 4505), (13, 4502),
        (14, 4508), (15, 4518), (19, 4516), (22, 4513), (23, 4515), (26, 4524), (29, 4512),
        (32, 4506), (33, 4503), (34, 4509), (36, 4520), (40, 4514), (46, 4521), (48, 4517),
        (50, 4523), (55, 4522),
    ],
    13: [  # FuSoYa
        (1, 4001), (1, 4008), (1, 4014), (1, 4020), (1, 4023), (1, 4006), (1, 4012), (1, 4002),
        (1, 4009), (1, 4016), (1, 4022), (1, 4005), (1, 4011), (1, 4010), (1, 4013), (1, 4019),
        (1, 4021), (1, 4003), (1, 4015), (1, 4024), (1, 4017), (1, 4004), (1, 4018), (1, 4007),
        (1, 4501), (1, 4504), (1, 4507), (1, 4510), (1, 4511), (1, 4519), (1, 4505), (1, 4502),
        (1, 4508), (1, 4514), (1, 4516), (1, 4513), (1, 4520), (1, 4524), (1, 4512), (1, 4506),
        (1, 4503), (1, 4509), (1, 4518), (1, 4515), (1, 4521), (1, 4517), (1, 4523), (1, 4522),
    ],
    14: [  # Golbez
        (1, 4501), (1, 4504), (1, 4507), (1, 4510), (1, 4511), (1, 4519), (1, 4505), (1, 4502),
        (1, 4508), (1, 4514), (1, 4516), (1, 4513), (1, 4520), (1, 4524), (1, 4512), (1, 4506),
        (1, 4503), (1, 4509), (1, 4518), (1, 4515), (1, 4521), (1, 4517), (1, 4523), (1, 4522),
    ],
}

# Personnages (identifiant de op068) dont les sorts sont dans la tranche, avec l'équipe d'origine.
# Rosa rejoint à l'objectif, Tellah ne connaît que des sorts de départ. Avec des personnages
# aléatoires, le monde passe la liste des personnages réellement présents.
SLICE_CASTERS = [4]   # Rydia (enfant)

# Familles progressives, dans l'ordre d'apprentissage.
CHAINS: dict[str, list[int]] = {
    "Progressive Cure": [4001, 4002, 4003, 4004],
    "Progressive Fire": [4501, 4502, 4503],
    "Progressive Blizzard": [4504, 4505, 4506],
    "Progressive Thunder": [4507, 4508, 4509],
}
CHAIN_OF = {spell: name for name, spells in CHAINS.items() for spell in spells}

SPELL_NAMES = {spell_id: name for name, spell_id in SPELL_IDS.items()}
LEARNABLE = sorted({spell for pairs in LEARNSETS.values() for _, spell in pairs})

# Tous les objets sorts possibles (enregistrés quelles que soient les options).
SPELL_ITEM_IDS: dict[str, int] = {
    **{SPELL_NAMES[s]: SPELL_FLAG | s for s in LEARNABLE if s not in CHAIN_OF},
    **{name: PROGRESSIVE_FLAG | spells[0] for name, spells in CHAINS.items()},
}
ITEM_SPELLS: dict[int, list[int]] = {   # identifiant AP -> sorts (dans l'ordre, pour une famille)
    **{SPELL_FLAG | s: [s] for s in LEARNABLE if s not in CHAIN_OF},
    **{PROGRESSIVE_FLAG | spells[0]: spells for spells in CHAINS.values()},
}

# Listes de sorts en RAM : un bloc de 0x1C0 octets par personnage.
#   blanche  : 40 cases de 2 octets + compteur (4 octets), à BLOCK_BASE + perso * 0x1C0
#   noire    : idem, 0x54 octets plus loin
#   invocations : 32 cases + compteur, 0xA8 octets plus loin
SPELL_BLOCK_BASE = 0x0D6174
SPELL_BLOCK_SIZE = 0x1C0
SCHOOLS = {  # école : (décalage dans le bloc, nombre de cases)
    "white": (0x00, 40),
    "black": (0x54, 40),
}


def school_of(spell: int) -> str:
    return "white" if spell < 4500 else "black"


def itemized_spells(starting_spells: bool, casters: list[int] | None = None) -> list[int]:
    """Sorts qui deviennent des objets : ceux que les lanceurs de la tranche apprennent
    en montant de niveau (et leurs sorts de départ si starting_spells est désactivé).
    casters : personnages de l'équipe (identifiants op068) ; par défaut, Rydia."""
    spells = set()
    for char in (SLICE_CASTERS if casters is None else casters):
        if char not in LEARNSETS:
            continue
        for level, spell in LEARNSETS[char]:
            if level > 1 or not starting_spells:
                spells.add(spell)
    return sorted(spells)


def spell_pool(itemized: list[int]) -> list[str]:
    """Noms des objets à mettre dans le pool : un par sort ; une famille donne autant
    d'objets progressifs que de sorts de la famille transformés en objets."""
    return [CHAIN_OF.get(spell, SPELL_NAMES[spell]) for spell in itemized]


def chain_spells(item_id: int, itemized: list[int]) -> list[int]:
    """Sorts appris successivement par les exemplaires d'un objet (famille : seulement
    les sorts transformés en objets, dans l'ordre)."""
    return [s for s in ITEM_SPELLS[item_id] if s in itemized]


def spells_from_items(item_ids: list[int], itemized: list[int]) -> set[int]:
    """Sorts appris par une liste d'objets reçus."""
    counts: dict[int, int] = {}
    for item_id in item_ids:
        if item_id in ITEM_SPELLS:
            counts[item_id] = counts.get(item_id, 0) + 1
    learned = set()
    for item_id, count in counts.items():
        learned.update(chain_spells(item_id, itemized)[:count])
    return learned


def learners(spell: int) -> list[int]:
    """Personnages qui apprennent ce sort normalement (à n'importe quel niveau)."""
    return [char for char, pairs in LEARNSETS.items()
            if char != 14 and any(s == spell for _, s in pairs)]   # 14 (Golbez) n'a pas de bloc


def add_spells(raw: bytes, spells: set[int]) -> bytes:
    """raw = listes de sorts des personnages 1 à 13 (lues à SPELL_BLOCK_BASE + 0x1C0).
    Ajoute chaque sort à la fin de la liste de ses personnages s'il n'y est pas déjà."""
    import struct
    data = bytearray(raw)
    for spell in sorted(spells):
        offset, capacity = SCHOOLS[school_of(spell)]
        for char in learners(spell):
            base = (char - 1) * SPELL_BLOCK_SIZE + offset
            count = struct.unpack_from("<I", data, base + capacity * 2)[0]
            known = struct.unpack_from(f"<{capacity}H", data, base)[:count]
            if spell in known or count >= capacity:
                continue
            struct.pack_into("<H", data, base + count * 2, spell)
            struct.pack_into("<I", data, base + capacity * 2, count + 1)
    return bytes(data)
