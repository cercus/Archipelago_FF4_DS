import struct
import unittest

from ..inventory import SlotList


def raw(*slots):
    return b"".join(struct.pack("<HBB", i, q, 0) for i, q in slots) + bytes(64)


class TestInventory(unittest.TestCase):
    def test_stack_existing(self) -> None:
        inv = SlotList(raw((0x1389, 19)), 1, 383, False)
        inv.add(0x1389, 2)
        self.assertEqual(inv.slots, [[0x1389, 21]])

    def test_reuse_empty_slot(self) -> None:
        inv = SlotList(raw((0x1389, 5), (0x138A, 0)), 2, 383, False)
        inv.add(0x1390)
        self.assertEqual(inv.slots, [[0x1389, 5], [0x1390, 1]])

    def test_append_new_slot(self) -> None:
        inv = SlotList(raw((0x1389, 5)), 1, 383, False)
        inv.add(0x1397)
        self.assertEqual(inv.count, 2)

    def test_stack_limit(self) -> None:
        inv = SlotList(raw((0x1389, 98)), 1, 383, False)
        inv.add(0x1389, 5)
        self.assertEqual(inv.slots[0][1], 99)

    def test_inventory_remove_keeps_slot(self) -> None:
        inv = SlotList(raw((0x1389, 1), (0x138C, 1)), 2, 383, False)
        inv.remove(0x1389)
        self.assertEqual(inv.slots, [[0x1389, 0], [0x138C, 1]])

    def test_key_remove_shifts(self) -> None:
        keys = SlotList(raw((0x2333, 1), (0x232C, 1), (0x23B0, 1)), 3, 128, True)
        keys.remove(0x232C)
        self.assertEqual(keys.slots, [[0x2333, 1], [0x23B0, 1]])

    def test_full(self) -> None:
        inv = SlotList(raw((0x1389, 1)), 1, 1, False)
        self.assertFalse(inv.add(0x1397))
