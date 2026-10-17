"""Patch de la ROM dans Archipelago.

La génération ne touche pas à la ROM : elle écrit un petit fichier `.apff4ds`
(les options de la partie). Le joueur l'ouvre avec le Launcher (ou le BizHawk Client),
qui demande la ROM d'origine une fois, applique `patch_rom.patch` et lance BizHawk
avec la ROM patchée.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os

import settings
import Utils
from worlds.Files import APPatchExtension, APProcedurePatch

from . import patch_rom

GAME = "Final Fantasy IV DS"
# MD5 des dumps connus de la ROM US (Final Fantasy IV (USA) (En,Fr,Es)).
US_MD5S = ["68c977b762d5e95f43a3a39026421c04"]

logger = logging.getLogger("FF4DS")


class FF4DSSettings(settings.Group):
    class RomFile(settings.UserFilePath):
        """Chemin de la ROM US de Final Fantasy IV DS"""
        copy_to = "Final Fantasy IV (USA) (En,Fr,Es).nds"
        description = "ROM US de Final Fantasy IV DS"

    rom_file: RomFile = RomFile(RomFile.copy_to)


def get_base_rom_path() -> str:
    file_name = settings.get_settings()["ff4ds_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name


def get_base_rom_bytes() -> bytes:
    with open(get_base_rom_path(), "rb") as f:
        data = f.read()
    if data[0x0C:0x10] != patch_rom.GAME_CODE:
        raise Exception("Cette ROM n'est pas Final Fantasy IV DS version US (code YF4E).")
    if hashlib.md5(data).hexdigest() not in US_MD5S:
        # Les patchs vérifient eux-mêmes les octets qu'ils remplacent : un autre dump US convient.
        logger.warning("MD5 de la ROM inconnu : on tente quand même le patch.")
    return data


class FF4DSPatchExtension(APPatchExtension):
    game = GAME

    @staticmethod
    def apply_ff4ds_patches(caller: APProcedurePatch, rom: bytes, options_file: str) -> bytes:
        options = json.loads(caller.get_file(options_file).decode("utf-8"))
        return patch_rom.patch(rom, options)


class FF4DSProcedurePatch(APProcedurePatch):
    game = GAME
    hash = US_MD5S[0]
    patch_file_ending = ".apff4ds"
    result_file_ending = ".nds"
    procedure = [("apply_ff4ds_patches", ["options.json"])]

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()
