from collections.abc import Mapping
from typing import Any

from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld, World

from . import items, locations, regions, rules
from . import options as ff4ds_options
from .data import GOAL_FLAG


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

    options_dataclass = ff4ds_options.FF4DSOptions
    options: ff4ds_options.FF4DSOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = "Baron"

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

    def fill_slot_data(self) -> Mapping[str, Any]:
        # Envoyé au client à la connexion.
        return {
            "goal_flag": GOAL_FLAG,
            **self.options.as_dict("namingway_locations"),
        }
