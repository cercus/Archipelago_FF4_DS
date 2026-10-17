from random import Random

from . import FF4DSTestBase
from ..rom.shop_data import ITEM_INFO, SHOPS
from ..shops import party_mask, randomize_shops


class TestShops(FF4DSTestBase):
    run_default_tests = False

    def test_standard_keeps_kind_and_size(self) -> None:
        shops = randomize_shops(Random(1), "standard", None)
        for index, items in shops.items():
            vanilla = SHOPS[index][1]
            self.assertEqual(len(items), len(vanilla))
            self.assertEqual(len(items), len(set(items)))
            for old, new in zip(vanilla, items):
                if old in ITEM_INFO:
                    self.assertEqual(ITEM_INFO[old][0], ITEM_INFO[new][0])

    def test_party_equipment(self) -> None:
        mask = party_mask([0, 10, 11])          # Cecil, Yang, Cid
        weapons = usable = 0
        for seed in range(10):
            for items in randomize_shops(Random(seed), "standard", mask).values():
                for item in items:
                    kind, _, item_mask, _ = ITEM_INFO[item]
                    if kind == "weapon":
                        weapons += 1
                        usable += bool(item_mask & mask)
        # Presque toutes : une case bon marché sans arme utilisable à moins de 10 fois son prix
        # garde une arme quelconque plutôt qu'une arme de fin de jeu.
        self.assertGreater(usable / weapons, 0.95)

    def test_essentials_kept(self) -> None:
        for mode in ("standard", "wild"):
            shops = randomize_shops(Random(6), mode, None)
            self.assertIn(0x1389, shops[3])     # Baron Item1 : Potion
            self.assertIn(0x1390, shops[8])     # Kaipo Item : Phoenix Down

    def test_shuffle_and_wild(self) -> None:
        self.assertTrue(randomize_shops(Random(3), "shuffle", None))
        wild = randomize_shops(Random(4), "wild", None)
        self.assertNotIn(0, wild)                # magasin de débogage intact
        self.assertEqual(randomize_shops(Random(5), "vanilla", None), {})
