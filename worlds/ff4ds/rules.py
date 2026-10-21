from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Has, HasAny

from .data import CONNECTION_COUNTS, CONNECTIONS

if TYPE_CHECKING:
    from .world import FF4DSWorld


def set_all_rules(world: FF4DSWorld) -> None:
    # Le menu "utiliser un objet" devant Rosa n'apparaît qu'après l'Antlion
    # (flag 0x0CBDDB, garanti par la région), et il faut choisir la Sand Pearl.
    world.set_rule(world.get_location("Rosa soignee"), Has("Sand Pearl"))

    # Edward donne Item Lore après le soin de Rosa : même condition.
    world.set_rule(world.get_location("Kaipo - Edward donne Item Lore"), Has("Sand Pearl"))

    # Tranche 4 : l'Elfe noir ne se combat qu'en montrant la Whisperweed (op076(9009)) ; la Terre, le
    # coffre-fort de Troia (ouvert après la voix de Kain, qui suit la Terre) en dépendent. L'augment
    # Whirlwind n'apparaît qu'après Valvalis (tour de Zott, donc la Terre).
    from .data import LOCATIONS
    for name in ("Lodestone Cavern - Dark Elf defeated", "Lodestone Cavern - Earth Crystal"):
        world.set_rule(world.get_location(name), Has("Whisperweed"))
    for name, data in LOCATIONS.items():
        if name.startswith("Troia Castle Vault"):
            world.set_rule(world.get_location(name), Has("Whisperweed"))
    world.set_rule(world.get_location("Lodestone Cavern - Whirlwind augment"), Has("Earth Crystal"))

    # Chemins qui demandent un objet (véhicule, Baron Key...) : l'un des objets suffit.
    for source, target, needed in CONNECTIONS:
        if needed:
            rule = Has(needed[0]) if len(needed) == 1 else HasAny(*needed)
            for item, count in CONNECTION_COUNTS.get((source, target), []):
                rule = rule & Has(item, count)
            world.set_rule(world.get_entrance(f"{source} -> {target}"), rule)

    # Tranche 6 : les portes des canons s'ouvrent avec la Tower Key (op076(9015)) ; l'ingénieur de Baron
    # (crochet) n'apparaît qu'après les canons.
    for name in ("Tower of Babil - Cannons destroyed", "Baron Castle - Enterprise hook"):
        world.set_rule(world.get_location(name), Has("Tower Key"))

    world.set_completion_rule(Has("Victoire"))
