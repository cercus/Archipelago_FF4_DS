"""Manipulation des listes d'objets de FF4 DS, sans dépendance à BizHawk.

Une liste (inventaire ou objets clés) est une suite de slots de 4 octets :
    ID (2 octets, little endian) | quantité (1 octet) | 0 (1 octet)
suivie d'un compteur de slots utilisés.

Règles observées dans le jeu (étape 3) :
- ajout : on empile si l'ID est déjà présent avec une quantité > 0, sinon on
  réutilise le premier slot à quantité 0, sinon on écrit au slot suivant et on
  incrémente le compteur ;
- inventaire : un objet épuisé garde son slot (quantité 0) ;
- objets clés : un objet retiré disparaît de la liste (compteur décrémenté).
"""
from __future__ import annotations

import struct

MAX_STACK = 99


class SlotList:
    def __init__(self, raw_slots: bytes, count: int, capacity: int, is_key_list: bool) -> None:
        self.capacity = capacity
        self.is_key_list = is_key_list
        self.slots: list[list[int]] = []
        for i in range(min(count, capacity)):
            item_id, qty = struct.unpack_from("<HB", raw_slots, i * 4)
            self.slots.append([item_id, qty])

    @property
    def count(self) -> int:
        return len(self.slots)

    def quantity(self, item_id: int) -> int:
        return sum(qty for sid, qty in self.slots if sid == item_id)

    def add(self, item_id: int, qty: int = 1) -> bool:
        """Ajoute un objet. Renvoie False si la liste est pleine."""
        limit = 1 if self.is_key_list else MAX_STACK
        for slot in self.slots:
            if slot[0] == item_id and slot[1] > 0:
                slot[1] = min(limit, slot[1] + qty)
                return True
        for slot in self.slots:
            if slot[1] == 0:
                slot[0], slot[1] = item_id, min(limit, qty)
                return True
        if self.count >= self.capacity:
            return False
        self.slots.append([item_id, min(limit, qty)])
        return True

    def remove(self, item_id: int, qty: int = 1) -> int:
        """Retire jusqu'à `qty` exemplaires. Renvoie le nombre réellement retiré."""
        removed = 0
        for index, slot in enumerate(self.slots):
            if slot[0] != item_id or slot[1] == 0:
                continue
            taken = min(slot[1], qty - removed)
            slot[1] -= taken
            removed += taken
            if self.is_key_list and slot[1] == 0:
                del self.slots[index]
            if removed >= qty:
                break
        return removed

    def to_bytes(self) -> bytes:
        """Slots utilisés, sérialisés (le reste de la zone mémoire n'est pas réécrit)."""
        return b"".join(struct.pack("<HBB", sid, qty, 0) for sid, qty in self.slots)
