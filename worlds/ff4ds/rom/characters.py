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
    "Rydia": Character(4, (0, 6801, 0, 8203, 8309), (5, 13, 1517, 1505)),
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
    leaves: bool       # part plus loin dans la tranche (départs « vanilla »)


# Emplacements de la tranche 1, dans l'ordre de l'histoire.
SLOTS: dict[str, Slot] = {
    "Starting Character": Slot("Kain", 10, 4, True),     # part au village de la Brume
    "Kaipo Character": Slot("Rydia", 7, 0, False),
    "Waterway Character": Slot("Tellah", 13, 0, True),   # part à Damcyan
    "Damcyan Character": Slot("Edward", 9, 0, False),
    "Rosa Character": Slot("Rosa", 15, 0, False),        # rejoint à l'objectif
}
GOAL_SLOT = "Rosa Character"
PARTY_MAX = 5


def vanilla_party() -> dict[str, str | None]:
    return {slot: data.vanilla for slot, data in SLOTS.items()}


def present_slots(party: dict[str, str | None], departures: str) -> list[str]:
    """Emplacements dont le personnage rejoint réellement l'équipe : sans départs, l'équipe
    est pleine (5) avant l'objectif et le dernier emplacement reste vide."""
    joined = 1   # Cecil
    present = []
    for slot in SLOTS:
        if party.get(slot) is None:
            continue
        if joined >= PARTY_MAX:
            continue
        present.append(slot)
        joined += 1
        if departures == "vanilla" and SLOTS[slot].leaves:
            joined -= 1
    return present


# ------------------------------------------------------------------ #
# Bytecode                                                            #
# ------------------------------------------------------------------ #
def join_code(name: str, slot: str) -> bytes:
    """op068 + op102 + op0AC + op17C : le personnage rejoint au niveau de l'emplacement."""
    c, s = CHARACTERS[name], SLOTS[slot]
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
