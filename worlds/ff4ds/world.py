import json
import os
from collections.abc import Mapping
from typing import Any, ClassVar

from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld, World

from . import items, locations, regions, rules
from . import options as ff4ds_options
from .data import GOAL_FLAG

# Équipe pleine : jamais atteinte avec les départs de l'histoire (4 personnages au plus avec Cecil) ;
# option full_party retirée le 18/10/2026.
FULL_PARTY = "replace_oldest"
from .rom import FF4DSProcedurePatch, FF4DSSettings
from .rom.characters import (CHARACTERS, GOAL_SLOT, SLOTS, STORY, PartyPlan, fill_empty_slots, joined_slots,
                              plan_party, vanilla_party)
from .shops import SHOPS, describe, party_mask, randomize_shops
from .spells import itemized_spells


class FF4DSWebWorld(WebWorld):
    theme = "grass"
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "Guide d'installation de Final Fantasy IV DS pour Archipelago.",
            "Français",
            "setup_fr.md",
            "setup/fr",
            ["cercus"],
        )
    ]


class FF4DSWorld(World):
    """
    Final Fantasy IV, remake Nintendo DS (2007).
    Tranche 1 : de Baron jusqu'au soin de Rosa à Kaipo.
    """

    game = items.GAME
    web = FF4DSWebWorld()

    settings_key = "ff4ds_options"
    settings: ClassVar[FF4DSSettings]

    options_dataclass = ff4ds_options.FF4DSOptions
    options: ff4ds_options.FF4DSOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = "Baron"

    party: dict[str, str | None]

    shops: dict[int, list[int]]

    def generate_early(self) -> None:
        self.party = self.draw_party()
        mask = None
        if self.options.shop_party_equipment:
            members = [0] + [CHARACTERS[self.party[slot]].char_id      # 0 : Cecil (chevalier noir)
                             for slot in joined_slots(self.plan())]
            mask = party_mask(members)
        self.shops = randomize_shops(self.random, self.options.shop_randomization.current_key, mask)

    def draw_party(self) -> dict[str, str | None]:
        """Un personnage par emplacement (characters.SLOTS), sans doublon. Les personnages
        restreints ne servent que s'il n'y a pas assez d'autres personnages autorisés."""
        if not self.options.character_shuffle:
            return vanilla_party()
        allowed = sorted(self.options.allowed_characters.value)
        preferred = [name for name in allowed if name not in self.options.restricted_characters.value]
        restricted = [name for name in allowed if name not in preferred]
        self.random.shuffle(preferred)
        self.random.shuffle(restricted)
        order = preferred + restricted
        party = {slot: (order[i] if i < len(order) else None) for i, slot in enumerate(SLOTS)}
        if self.options.returning_characters:
            party = fill_empty_slots(party, self.departures(), FULL_PARTY,
                                     self.random.choice)
        return party

    def departures(self) -> str:
        # Toujours les départs de l'histoire (option character_departures retirée le 18/10/2026) : ainsi une
        # place reste libre pour l'arrivée scénarisée de Rydia pendant le combat contre Golbez.
        return "vanilla"

    def plan(self) -> PartyPlan:
        """Arrivées (et remplacements) et départs de personnages tout au long de l'histoire."""
        return plan_party(self.party, self.departures(), FULL_PARTY)

    def casters(self) -> list[int]:
        """Personnages qui rejoignent l'équipe avant l'objectif (identifiants op068), pour les sorts en objets."""
        before_goal = [slot for kind, slot in STORY if kind == "join"]
        if GOAL_SLOT in before_goal:
            before_goal = before_goal[:before_goal.index(GOAL_SLOT)]
        plan = self.plan()
        return [CHARACTERS[plan.joins[slot][0]].char_id for slot in before_goal if plan.joins.get(slot)]

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.FF4DSItem:
        return items.create_item(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def generate_output(self, output_directory: str) -> None:
        # Fichier .apff4ds : le joueur l'ouvre avec le Launcher, qui crée la ROM patchée
        # à partir de sa ROM d'origine (rom/patch_rom.py).
        patch = FF4DSProcedurePatch(player=self.player, player_name=self.player_name)
        patch.write_file("options.json", json.dumps({
            "seed": self.multiworld.seed_name,
            "spell_items": self.get_itemized_spells(),
            # Personnages qui perdent aussi leurs sorts de niveau 1 (option starting_spells désactivée).
            "level1_chars": [] if self.options.starting_spells else self.casters(),
            "party": self.party,
            "departures": self.departures(),
            "full_party": FULL_PARTY,
            "vehicle_items": True,             # véhicules posés par le client (objets Archipelago)
            "shops": {str(index): items for index, items in self.shops.items()},
        }).encode("utf-8"))
        file_name = self.multiworld.get_out_file_name_base(self.player) + patch.patch_file_ending
        patch.write(os.path.join(output_directory, file_name))

    def get_itemized_spells(self) -> list[int]:
        """Sorts devenus des objets (vide si l'option est désactivée)."""
        if not self.options.spell_items:
            return []
        return itemized_spells(bool(self.options.starting_spells), self.casters())

    def write_spoiler(self, spoiler_handle) -> None:
        plan = self.plan()
        spoiler_handle.write(f"\n\nPersonnages ({self.player_name}) :\n")
        for kind, slot in STORY:
            if kind == "join":
                joined = plan.joins.get(slot)
                if not joined:
                    text = "(vide)"
                else:
                    text = joined[0] + (f" (remplace {joined[1]})" if joined[1] else "")
                spoiler_handle.write(f"  {slot}: {text}\n")
            elif plan.leaves.get(slot):
                spoiler_handle.write(f"  {plan.leaves[slot]} quitte l'équipe ({slot})\n")
        if self.shops:
            spoiler_handle.write(f"\nMagasins ({self.player_name}) :\n")
            for index, items in sorted(self.shops.items()):
                spoiler_handle.write(f"  {SHOPS[index][0]}: {describe(items)}\n")

    def fill_slot_data(self) -> Mapping[str, Any]:
        # Envoyé au client à la connexion.
        return {
            "goal_flag": GOAL_FLAG,
            "spell_items": self.get_itemized_spells(),
            "party": {slot: self.plan().joins[slot][0] for slot in joined_slots(self.plan())},
            **self.options.as_dict("namingway_locations"),
        }
