"""Renommage d'objets "porteurs" dans la table de textes du jeu (bloc "MSDA" en RAM).

Format du bloc (observé) :
    +0x00 "MSDA"  +0x04 00 00 01 00  +0x08 nombre d'entrées  +0x0C pointeur vers les entrées
    +0x10 entrées de 12 octets : [ID du texte (4)] [01 00 CC CC] [décalage du texte depuis "MSDA" (4)]
Les textes sont en UTF-16LE terminés par 0. Nom d'un objet : ID = ID de l'objet ;
description : ID = ID de l'objet + 10000.

Pour afficher un nom quelconque, on écrit le texte voulu à la place de la description
du porteur, et on fait pointer l'entrée du nom vers ce texte. Tout est restauré ensuite.
"""
from __future__ import annotations

import struct
import unicodedata
from typing import NamedTuple

MSDA_MAGIC = b"MSDA\x00\x00\x01\x00"
FIRST_ITEM_TEXT_ID = 0x1389       # "Potion" : première entrée de la table des objets
DESCRIPTION_OFFSET = 10000
MAX_NAME_LENGTH = 30

# Objets de fin de jeu à longue description, jamais présents dans le pool de la tranche.
PLACEHOLDERS = [0x1FB6, 0x207F, 0x207C, 0x1FB7, 0x1F4B, 0x2020, 0x207A, 0x2079]


class Placeholder(NamedTuple):
    item_id: int
    name_offset_addr: int    # adresse du champ "décalage" de l'entrée du nom
    name_offset: int         # décalage d'origine du nom
    desc_offset: int         # décalage de la description (où l'on écrit le nouveau nom)
    desc_addr: int           # adresse de la description
    desc_original: bytes     # description d'origine (UTF-16LE, sans le 0 final)


def find_msda(window: bytes, window_start: int) -> int | None:
    """Cherche le bloc des textes d'objets dans une zone mémoire lue d'un coup."""
    index = window.find(MSDA_MAGIC)
    while index != -1:
        if index + 0x14 <= len(window) and struct.unpack_from("<I", window, index + 0x10)[0] == FIRST_ITEM_TEXT_ID:
            return window_start + index
        index = window.find(MSDA_MAGIC, index + 1)
    return None


def parse_entries(base: int, raw: bytes) -> dict[int, tuple[int, int]]:
    """raw = bloc lu depuis `base`. Renvoie {ID du texte: (adresse du champ décalage, décalage)}."""
    count = struct.unpack_from("<I", raw, 0x08)[0]
    entries = {}
    for i in range(count):
        position = 0x10 + 12 * i
        if position + 12 > len(raw):
            break
        text_id, _, offset = struct.unpack_from("<III", raw, position)
        entries[text_id] = (base + position + 8, offset)
    return entries


def read_string(raw: bytes, position: int) -> bytes:
    end = position
    while end + 1 < len(raw) and raw[end:end + 2] != b"\x00\x00":
        end += 2
    return raw[position:end]


def to_game_text(text: str, capacity: int) -> bytes:
    """Texte UTF-16LE limité aux caractères ASCII (police du jeu), terminé par 0."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text[:min(MAX_NAME_LENGTH, capacity - 1)]
    return ascii_text.encode("utf-16-le") + b"\x00\x00"
