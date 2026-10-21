from . import FF4DSTestBase


class TestVehicles(FF4DSTestBase):
    """Hauts-fonds : l'Antlion et le mont Hobs demandent l'hovercraft ou l'Enterprise ;
    l'Ancient Waterway demande la Baron Key ; Mysidia et le mont Ordeals sont à pied."""

    def test_antlion_needs_vehicle(self) -> None:
        self.assertFalse(self.can_reach_location("Antlion’s Den - Fourmillon defeated"))
        self.collect_by_name("Hovercraft")
        self.assertTrue(self.can_reach_location("Antlion’s Den - Fourmillon defeated"))

    def test_hobs_with_enterprise(self) -> None:
        self.assertFalse(self.can_reach_location("Mount Hobs Summit - Mom Bomb defeated"))
        self.collect_by_name("Enterprise")
        self.assertTrue(self.can_reach_location("Mount Hobs Summit - Mom Bomb defeated"))
        self.assertTrue(self.can_reach_location("Fabul - Castle defended"))

    def test_ordeals_on_foot(self) -> None:
        self.assertTrue(self.can_reach_location("Mount Ordeals Summit - Scarmiglione defeated"))

    def test_waterway_needs_key(self) -> None:
        self.assertFalse(self.can_reach_location("Ancient Waterway B1 - Coffre 1"))
        self.collect_by_name("Baron Key")
        self.assertTrue(self.can_reach_location("Ancient Waterway B1 - Coffre 1"))



class TestSlice4Logic(FF4DSTestBase):
    """Troia demande l'Enterprise ; l'Elfe noir la Whisperweed ; la tour de Zott la Terre."""

    def test_troia_needs_enterprise(self) -> None:
        self.assertFalse(self.can_reach_location("Troia - Coffre 1"))
        self.collect_by_name("Enterprise")
        self.assertTrue(self.can_reach_location("Troia - Coffre 1"))

    def test_dark_elf_needs_whisperweed(self) -> None:
        self.collect_by_name("Enterprise")
        self.assertFalse(self.can_reach_location("Lodestone Cavern - Earth Crystal"))
        self.collect_by_name("Whisperweed")
        self.assertTrue(self.can_reach_location("Lodestone Cavern - Earth Crystal"))

    def test_zot_needs_crystal(self) -> None:
        self.collect_by_name("Enterprise")
        self.assertFalse(self.can_reach_location("Tower of Zot - Magus Sisters defeated"))
        self.collect_by_name("Earth Crystal")
        self.assertTrue(self.can_reach_location("Tower of Zot - Magus Sisters defeated"))


class TestSlice5Logic(FF4DSTestBase):
    """Agart demande l'Enterprise ; le monde souterrain la Magma Stone (donnée après Valvalis)."""

    def test_agart_needs_enterprise(self) -> None:
        self.assertFalse(self.can_reach_location("Agart - Coffre 1"))
        self.collect_by_name("Enterprise")
        self.assertTrue(self.can_reach_location("Agart - Coffre 1"))

    def test_underworld_needs_magma_stone(self) -> None:
        self.collect_by_name("Enterprise")
        self.assertFalse(self.can_reach_location("Dwarf Castle - Calbrena defeated"))
        self.collect_by_name("Magma Stone")
        self.assertTrue(self.can_reach_location("Dwarf Castle - Calbrena defeated"))


class TestSlice6Logic(FF4DSTestBase):
    """Tour de Babil : depuis le monde souterrain ; l'objectif (canons) demande la Tower Key."""

    def test_babil_cannons(self) -> None:
        self.collect_by_name(["Enterprise", "Magma Stone"])
        self.assertTrue(self.can_reach_location("Tower of Babil B13 - Coffre 1"))
        self.assertFalse(self.can_reach_location("Tower of Babil - Cannons destroyed"))
        self.collect_by_name("Tower Key")
        self.assertTrue(self.can_reach_location("Tower of Babil - Cannons destroyed"))

    def test_eblan_needs_hook_and_hovercraft(self) -> None:
        enterprise = self.get_items_by_name("Enterprise")
        self.assertEqual(len(enterprise), 2)
        self.collect(enterprise[0])
        self.collect_by_name("Hovercraft")
        self.assertFalse(self.can_reach_location("Cave of Eblan B1 - Coffre 1"))
        self.collect(enterprise[1])
        self.assertTrue(self.can_reach_location("Cave of Eblan B1 - Coffre 1"))
        self.assertTrue(self.can_reach_location("Objectif"))


class TestFalcon(FF4DSTestBase):
    """Faucon progressif : la location du Faucon (chute) et celles de Cid suivent la tour de Babil (haut)."""

    def test_two_falcons(self) -> None:
        self.assertEqual(len(self.get_items_by_name("Falcon")), 2)

    def test_cid_after_babil(self) -> None:
        self.collect_by_name(["Hovercraft"])
        self.assertFalse(self.can_reach_location("Dwarf Castle - Cid upgrades the Falcon"))
        self.collect_by_name(["Enterprise"])
        self.assertTrue(self.can_reach_location("Tower of Babil - Falcon"))
        self.assertTrue(self.can_reach_location("Dwarf Castle - Luca's Necklace"))
        self.assertTrue(self.can_reach_location("Objectif"))
