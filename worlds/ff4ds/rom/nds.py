"""Lecture et réécriture minimales d'une ROM Nintendo DS (système de fichiers NitroFS).

Remplace ndspy pour le patch : Archipelago ne fournit pas ndspy, et le patch doit
pouvoir s'appliquer sur la machine du joueur avec Python seul.

Seuls les fichiers sont modifiables. Un fichier qui garde sa taille ou rétrécit reste
à sa place ; un fichier qui grandit est déplacé dans l'espace libre à la fin de la ROM.
"""
from __future__ import annotations

import struct

FNT_OFFSET, FAT_OFFSET = 0x40, 0x48
USED_SIZE = 0x80             # taille utilisée de la ROM (en-tête)
CAPACITY_SHIFT = 0x14        # capacité de la cartouche = 128 Ko << valeur
HEADER_CRC = 0x15E           # CRC16 des octets 0x000 à 0x15D
FILE_ALIGN = 0x200


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


class NDSRom:
    def __init__(self, data: bytes) -> None:
        self.data = bytearray(data)
        self.id_code = bytes(self.data[0x0C:0x10])
        fnt, _ = struct.unpack_from("<II", self.data, FNT_OFFSET)
        self.fat, fat_size = struct.unpack_from("<II", self.data, FAT_OFFSET)
        self.file_count = fat_size // 8
        self.names = self._read_names(fnt)

    @classmethod
    def from_file(cls, path: str) -> NDSRom:
        with open(path, "rb") as f:
            return cls(f.read())

    # ------------------------------------------------------------------ #
    def _read_names(self, fnt: int) -> dict[str, int]:
        """{chemin: identifiant de fichier}, en parcourant la table des noms."""
        names: dict[str, int] = {}

        def walk(dir_id: int, prefix: str) -> None:
            sub_offset, first_file = struct.unpack_from("<IH", self.data, fnt + (dir_id & 0xFFF) * 8)
            p, file_id = fnt + sub_offset, first_file
            while True:
                length = self.data[p]
                p += 1
                if length == 0:
                    return
                name = self.data[p:p + (length & 0x7F)].decode("latin1")
                p += length & 0x7F
                if length & 0x80:
                    sub_dir = struct.unpack_from("<H", self.data, p)[0]
                    p += 2
                    walk(sub_dir, prefix + name + "/")
                else:
                    names[prefix + name] = file_id
                    file_id += 1

        walk(0xF000, "")
        return names

    def _bounds(self, file_id: int) -> tuple[int, int]:
        return struct.unpack_from("<II", self.data, self.fat + file_id * 8)

    def get_file(self, name: str) -> bytes:
        start, end = self._bounds(self.names[name])
        return bytes(self.data[start:end])

    def set_file(self, name: str, content: bytes) -> None:
        file_id = self.names[name]
        start, end = self._bounds(file_id)
        if len(content) > end - start:
            # Le fichier grandit : on le place après la fin des données utilisées.
            used = struct.unpack_from("<I", self.data, USED_SIZE)[0]
            start = (used + FILE_ALIGN - 1) // FILE_ALIGN * FILE_ALIGN
            capacity = 0x20000 << self.data[CAPACITY_SHIFT]
            if start + len(content) > capacity:
                raise ValueError(f"Plus de place dans la ROM pour {name}")
            if start + len(content) > len(self.data):
                self.data += b"\xFF" * (start + len(content) - len(self.data))
            struct.pack_into("<I", self.data, USED_SIZE, start + len(content))
        self.data[start:start + len(content)] = content
        struct.pack_into("<II", self.data, self.fat + file_id * 8, start, start + len(content))
        struct.pack_into("<H", self.data, HEADER_CRC, crc16(self.data[:HEADER_CRC]))

    def to_bytes(self) -> bytes:
        return bytes(self.data)

    # Noms compatibles avec ndspy, pour que le code de patch fonctionne avec les deux.
    getFileByName = get_file
    setFileByName = set_file
