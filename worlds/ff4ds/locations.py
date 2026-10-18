from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location, LocationProgressType

from .data import GOAL_REGION, LOCATIONS
from .items import GAME, FF4DSItem

if TYPE_CHECKING:
    from .world import FF4DSWorld

# L'identifiant Archipelago d'une location est l'adresse de son flag :
# le client n'a besoin d'aucune table de correspondance.
LOCATION_NAME_TO_ID = {name: data.flag for name, data in LOCATIONS.items()}


class FF4DSLocation(Location):
    game = GAME


def create_all_locations(world: FF4DSWorld) -> None:
    for name, data in LOCATIONS.items():
        if data.category == "namingway" and not world.options.namingway_locations:
            continue
        region = world.get_region(data.region)
        location = FF4DSLocation(world.player, name, data.flag, region)
        if data.excluded:
            location.progress_type = LocationProgressType.EXCLUDED
        region.locations.append(location)

    # Événement de victoire (pas d'identifiant, pas d'objet à mélanger) : voir GOAL_FLAG.
    region = world.get_region(GOAL_REGION)
    goal = FF4DSLocation(world.player, "Objectif", None, region)
    goal.place_locked_item(FF4DSItem("Victoire", ItemClassification.progression, None, world.player))
    region.locations.append(goal)
