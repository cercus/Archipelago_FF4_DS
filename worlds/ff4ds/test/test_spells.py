from . import FF4DSTestBase
from ..spells import SPELL_ITEM_IDS, SPELL_NAMES, itemized_spells, learners, spells_from_items


class TestSpellItems(FF4DSTestBase):
    options = {"character_shuffle": False}      # équipe d'origine : Rydia est la lanceuse de sorts
    def test_spells_in_pool(self) -> None:
        """Les sorts de Rydia (enfant) appris après le niveau 1 sont dans le pool."""
        names = [item.name for item in self.multiworld.itempool if item.player == self.player]
        for name in ("Sight", "Hold", "Toad", "Progressive Cure", "Progressive Thunder"):
            self.assertIn(name, names)
        self.assertNotIn("Progressive Blizzard", names)   # Blizzard est un sort de départ

    def test_pool_fits_locations(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(locations), len(items))


class TestWithoutStartingSpells(FF4DSTestBase):
    options = {"starting_spells": False, "character_shuffle": False}

    def test_cure_chain(self) -> None:
        names = [item.name for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(names.count("Progressive Cure"), 2)       # Cure puis Cura
        self.assertIn("Progressive Blizzard", names)


class TestWithoutSpellItems(FF4DSTestBase):
    options = {"spell_items": False}

    def test_no_spells(self) -> None:
        names = {item.name for item in self.multiworld.itempool if item.player == self.player}
        self.assertFalse(names & set(SPELL_ITEM_IDS))


class TestSpellLogic(FF4DSTestBase):
    run_default_tests = False

    def test_progressive_order(self) -> None:
        itemized = itemized_spells(False)
        cure = SPELL_ITEM_IDS["Progressive Cure"]
        self.assertEqual({SPELL_NAMES[s] for s in spells_from_items([cure], itemized)}, {"Cure"})
        self.assertEqual({SPELL_NAMES[s] for s in spells_from_items([cure, cure], itemized)}, {"Cure", "Cura"})

    def test_learners(self) -> None:
        self.assertIn(4, learners(4023))       # Sight : Rydia (enfant)
        self.assertIn(3, learners(4023))       # … et Rosa
        self.assertNotIn(14, learners(4507))   # Golbez n'a pas de liste de sorts


class TestAddSpells(FF4DSTestBase):
    run_default_tests = False

    def test_add_once(self) -> None:
        import struct
        from ..spells import SPELL_BLOCK_SIZE, add_spells
        raw = bytes(13 * SPELL_BLOCK_SIZE)
        data = add_spells(raw, {4519})                     # Pig
        rydia_black = 3 * SPELL_BLOCK_SIZE + 0x54          # personnage 4, liste noire
        self.assertEqual(struct.unpack_from("<H", data, rydia_black)[0], 4519)
        self.assertEqual(struct.unpack_from("<I", data, rydia_black + 80)[0], 1)
        self.assertEqual(add_spells(data, {4519}), data)  # pas de doublon
