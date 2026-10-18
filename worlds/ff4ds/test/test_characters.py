from . import FF4DSTestBase
from ..rom.characters import SLOTS, STORY, joined_slots, plan_party, vanilla_party


class TestCharacterShuffle(FF4DSTestBase):
    def test_no_duplicates(self) -> None:
        """Un personnage ne revient que s'il n'est plus dans l'équipe."""
        world = self.multiworld.worlds[self.player]
        plan = world.plan()
        members: list[str] = []
        for kind, slot in STORY:
            if kind == "join" and plan.joins.get(slot):
                name, replaced = plan.joins[slot]
                self.assertNotIn(name, members)
                if replaced:
                    members.remove(replaced)
                members.append(name)
            elif kind == "leave" and plan.leaves.get(slot):
                members.remove(plan.leaves[slot])
        self.assertEqual(set(world.party), set(SLOTS))

    def test_restricted_last(self) -> None:
        """Edge et FuSoYa (restreints) ne servent qu'une fois les autres personnages placés :
        ils ne peuvent occuper que les derniers emplacements."""
        world = self.multiworld.worlds[self.player]
        drawn = list(dict.fromkeys(world.party[slot] for slot in SLOTS))   # premières venues
        restricted = {"Edge", "FuSoYa"}
        others = len([name for name in drawn if name and name not in restricted])
        self.assertFalse(restricted & set(drawn[:others]))

    def test_room_for_rydia(self) -> None:
        """Départs de l'histoire : avant le combat contre Golbez, l'équipe compte au plus 4 personnages
        (Cecil compris) : une place reste pour l'arrivée scénarisée de Rydia."""
        from ..rom.characters import _members
        plan = self.multiworld.worlds[self.player].plan()
        index = STORY.index(("join", "Dwarf Castle Character"))
        self.assertLessEqual(len(_members(plan, STORY[:index])), 3)


class TestVanillaDepartures(FF4DSTestBase):
    options = {}

    def test_departures(self) -> None:
        world = self.multiworld.worlds[self.player]
        plan = world.plan()
        self.assertEqual(plan.leaves["Starting Character"], world.party["Starting Character"])
        self.assertIn("Rosa Character", joined_slots(plan))
        self.assertIsNone(plan.joins["Mt Hobs Character"][1])   # place libre : personne ne part


class TestPlanVanilla(FF4DSTestBase):
    run_default_tests = False

    def test_vanilla_story(self) -> None:
        """Équipe d'origine avec les départs d'origine : Yang rejoint sans remplacer personne."""
        plan = plan_party(vanilla_party(), "vanilla", "replace_oldest")
        self.assertEqual(plan.leaves["Starting Character"], "Kain")
        self.assertEqual(plan.joins["Mt Hobs Character"], ("Yang", None))


class TestManyCasters(FF4DSTestBase):
    """Pire cas pour le pool : uniquement des lanceurs de sorts, sorts de départ compris."""
    options = {"allowed_characters": ["Rosa", "Porom", "Palom", "Rydia", "Tellah", "FuSoYa"],
               "restricted_characters": [], "starting_spells": False}

    def test_pool_fits_locations(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None]
        items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(locations), len(items))


class TestFewCharacters(FF4DSTestBase):
    options = {"allowed_characters": ["Yang", "Cid"], "restricted_characters": []}

    def test_empty_slots(self) -> None:
        world = self.multiworld.worlds[self.player]
        self.assertEqual({name for name in world.party.values() if name}, {"Yang", "Cid"})


class TestReturningCharacters(FF4DSTestBase):
    options = {}

    def test_zot_slots_filled(self) -> None:
        """11 personnages pour 13 emplacements : les deux derniers sont des revenants."""
        plan = self.multiworld.worlds[self.player].plan()
        self.assertTrue(plan.joins["Zot Character 1"])
        self.assertTrue(plan.joins["Zot Character 2"])


class TestNoReturningCharacters(FF4DSTestBase):
    options = {"returning_characters": False}

    def test_zot_slots_empty(self) -> None:
        world = self.multiworld.worlds[self.player]
        self.assertIsNone(world.party["Zot Character 1"])
        self.assertIsNone(world.party["Zot Character 2"])
