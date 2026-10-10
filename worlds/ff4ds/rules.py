from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Has

if TYPE_CHECKING:
    from .world import FF4DSWorld


def set_all_rules(world: FF4DSWorld) -> None:
    # Le menu "utiliser un objet" devant Rosa n'apparaît qu'après l'Antlion
    # (flag 0x0CBDDB, garanti par la région), et il faut choisir la Sand Pearl.
    world.set_rule(world.get_location("Rosa soignee"), Has("Sand Pearl"))

    # Edward donne Item Lore après le soin de Rosa : même condition.
    world.set_rule(world.get_location("Kaipo - Edward donne Item Lore"), Has("Sand Pearl"))

    world.set_completion_rule(Has("Victoire"))
