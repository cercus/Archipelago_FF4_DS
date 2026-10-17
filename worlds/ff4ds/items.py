from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .data import FILLER_ITEMS, ITEMS, LOCATIONS
from .spells import SPELL_ITEM_IDS, spell_pool

if TYPE_CHECKING:
    from .world import FF4DSWorld

GAME = "Final Fantasy IV DS"

ITEM_NAME_TO_ID = {name: data.ap_id for name, data in ITEMS.items()} | SPELL_ITEM_IDS

CLASSIFICATIONS = {
    "progression": ItemClassification.progression,
    "useful": ItemClassification.useful,
    "filler": ItemClassification.filler,
}


class FF4DSItem(Item):
    game = GAME


def create_item(world: FF4DSWorld, name: str) -> FF4DSItem:
    if name in SPELL_ITEM_IDS:
        # Aucun sort n'est exigé par la logique de la tranche 1 : utiles, pas progression.
        return FF4DSItem(name, ItemClassification.useful, SPELL_ITEM_IDS[name], world.player)
    data = ITEMS[name]
    return FF4DSItem(name, CLASSIFICATIONS[data.kind], data.ap_id, world.player)


def get_random_filler_item_name(world: FF4DSWorld) -> str:
    return world.random.choice(FILLER_ITEMS)


def create_all_items(world: FF4DSWorld) -> None:
    # Le pool contient les objets d'origine des locations créées...
    itempool = []
    for location in world.multiworld.get_locations(world.player):
        if location.address is None:  # les événements n'ont pas d'objet à mélanger
            continue
        vanilla = LOCATIONS[location.name].vanilla
        if vanilla is not None:
            itempool.append(world.create_item(vanilla))

    # Sorts devenus des objets : ils prennent la place d'objets de remplissage.
    if world.options.spell_items:
        spells = [world.create_item(name) for name in spell_pool(world.get_itemized_spells())]
        slots = len(world.multiworld.get_unfilled_locations(world.player))
        excess = len(itempool) + len(spells) - slots
        if excess > 0:
            fillers = [item for item in itempool if item.classification == ItemClassification.filler]
            world.random.shuffle(fillers)
            for item in fillers[:excess]:
                itempool.remove(item)
        itempool += spells

    # ... complété par du remplissage pour les locations sans objet connu.
    missing = len(world.multiworld.get_unfilled_locations(world.player)) - len(itempool)
    itempool += [world.create_filler() for _ in range(missing)]

    world.multiworld.itempool += itempool
