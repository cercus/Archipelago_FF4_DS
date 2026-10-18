from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

from .data import CONNECTIONS, REGIONS

if TYPE_CHECKING:
    from .world import FF4DSWorld


def create_and_connect_regions(world: FF4DSWorld) -> None:
    regions = {name: Region(name, world.player, world.multiworld) for name in REGIONS}
    world.multiworld.regions += regions.values()

    # Chemins de data.CONNECTIONS ; les objets nécessaires sont posés dans rules.py.
    for source, target, _ in CONNECTIONS:
        regions[source].connect(regions[target], f"{source} -> {target}")
