from . import FF4DSTestBase
from ..rom.characters import GOAL_SLOT, SLOTS, present_slots


class TestCharacterShuffle(FF4DSTestBase):
    def test_no_duplicates(self) -> None:
        world = self.multiworld.worlds[self.player]
        drawn = [name for name in world.party.values() if name]
        self.assertEqual(len(drawn), len(set(drawn)))
        self.assertEqual(set(world.party), set(SLOTS))

    def test_restricted_last(self) -> None:
        world = self.multiworld.worlds[self.player]
        self.assertFalse({"Edge", "FuSoYa"} & set(world.party.values()))

    def test_never_fills_party(self) -> None:
        """Sans départs, Cecil + 4 arrivées = 5 : l'emplacement de Rosa reste vide."""
        world = self.multiworld.worlds[self.player]
        self.assertNotIn(GOAL_SLOT, present_slots(world.party, world.departures()))


class TestVanillaDepartures(FF4DSTestBase):
    options = {"character_departures": "vanilla"}

    def test_goal_slot_joins(self) -> None:
        world = self.multiworld.worlds[self.player]
        self.assertIn(GOAL_SLOT, present_slots(world.party, world.departures()))


class TestManyCasters(FF4DSTestBase):
    """Pire cas pour le pool : uniquement des lanceurs de sorts, sorts de départ compris."""
    options = {"allowed_characters": ["Rosa", "Porom", "Palom", "Rydia", "Tellah"], "restricted_characters": [],
               "starting_spells": False, "character_departures": "vanilla"}

    def test_pool_fits_locations(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(locations), len(items))


class TestFewCharacters(FF4DSTestBase):
    options = {"allowed_characters": ["Yang", "Cid"], "restricted_characters": []}

    def test_empty_slots(self) -> None:
        world = self.multiworld.worlds[self.player]
        self.assertEqual(sum(1 for name in world.party.values() if name), 2)
