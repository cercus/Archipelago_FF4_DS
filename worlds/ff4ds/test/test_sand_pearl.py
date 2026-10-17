from . import FF4DSTestBase


class TestSandPearl(FF4DSTestBase):
    def test_rosa_needs_sand_pearl(self) -> None:
        """Soigner Rosa (l'objectif) est impossible sans la Sand Pearl."""
        self.assertFalse(self.can_reach_location("Rosa soignee"))
        self.collect_by_name("Sand Pearl")
        self.assertTrue(self.can_reach_location("Rosa soignee"))

    def test_baron_is_not_excluded(self) -> None:
        """Avec la ROM patchée, Baron reste accessible : ses locations peuvent tout recevoir."""
        from BaseClasses import LocationProgressType
        location = self.multiworld.get_location("Baron Castle - Coffre 1", self.player)
        self.assertEqual(location.progress_type, LocationProgressType.DEFAULT)


class TestWithoutNamingway(FF4DSTestBase):
    options = {"namingway_locations": False}

    def test_no_namingway_locations(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertFalse(any(name.startswith("Namingway") for name in names))
