from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

from .data import REGIONS

if TYPE_CHECKING:
    from .world import FF4DSWorld


def create_and_connect_regions(world: FF4DSWorld) -> None:
    regions = [Region(name, world.player, world.multiworld) for name in REGIONS]
    world.multiworld.regions += regions

    # L'histoire est linéaire : chaque région mène à la suivante.
    # Les règles (ex. Sand Pearl) sont posées dans rules.py.
    for current, following in zip(regions, regions[1:]):
        current.connect(following, f"{current.name} -> {following.name}")
