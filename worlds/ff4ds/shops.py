"""Magasins aléatoires (option shop_randomization).

Chaque case de magasin garde le type de son objet d'origine (arme, armure, objet), sauf en
mode « wild ». Le résultat ({numéro de magasin: objets}) est écrit dans options.json et le patch
réécrit MENU/babil_shop.bbd.
"""
from __future__ import annotations

from random import Random

from .rom.shop_data import ITEM_INFO, SHOPS

DEBUG_SHOP = 0
MIN_PRICE = 2            # prix 0 ou 1 : objet qui ne se vend pas
# Objets indispensables : gardés là où ils sont vendus à l'origine (modes standard et wild).
ESSENTIALS = {0x1389, 0x1390}   # Potion, Phoenix Down
# Mode standard : prix toléré autour du prix de l'objet d'origine, élargi s'il manque des candidats.
PRICE_WINDOWS = [(0.5, 2.0), (0.25, 4.0), (0.1, 10.0), (0.0, float("inf"))]


def buyable(kind: str | None = None) -> list[int]:
    return [item for item, (k, price, _, _) in ITEM_INFO.items()
            if price >= MIN_PRICE and (kind is None or k == kind)]


def usable(item: int, party_mask: int) -> bool:
    kind, _, mask, _ = ITEM_INFO[item]
    return kind == "item" or bool(mask & party_mask)


def party_mask(char_ids: list[int]) -> int:
    mask = 0
    for char_id in char_ids:
        mask |= 1 << char_id
    return mask


def pick(random: Random, candidates: list[int], taken: set[int], mask: int | None) -> int | None:
    """Un objet au hasard parmi les candidats, sans doublon dans le magasin. Avec `mask`,
    seulement les objets utilisables par l'équipe."""
    free = [item for item in candidates if item not in taken
            and (mask is None or usable(item, mask))]
    return random.choice(free) if free else None


def randomize_shops(random: Random, mode: str, mask: int | None) -> dict[int, list[int]]:
    """mode : vanilla, shuffle, standard ou wild. mask : personnages de l'équipe (None = sans
    préférence). Renvoie les magasins modifiés."""
    if mode == "vanilla":
        return {}
    shops = {index: list(items) for index, (_, items) in SHOPS.items() if index != DEBUG_SHOP}

    if mode == "shuffle":
        # Les objets d'origine sont redistribués entre les cases de même type.
        for kind in ("item", "weapon", "armor"):
            slots = [(index, i) for index, items in shops.items() for i, item in enumerate(items)
                     if ITEM_INFO.get(item, ("item",))[0] == kind]
            pool = [shops[index][i] for index, i in slots]
            random.shuffle(pool)
            for (index, i), item in zip(slots, pool):
                shops[index][i] = item
        for index, items in shops.items():            # doublons éventuels : on garde une seule fois
            shops[index] = list(dict.fromkeys(items))
        return shops

    result: dict[int, list[int]] = {}
    for index, vanilla in shops.items():
        taken: set[int] = {item for item in vanilla if item in ESSENTIALS}
        new_items = []
        for item in vanilla:
            if item in ESSENTIALS:
                new_items.append(item)
                continue
            kind, price, _, _ = ITEM_INFO.get(item, ("item", 0, 0, ""))
            choice = None
            # D'abord un objet utilisable par l'équipe (si demandé), sinon n'importe lequel.
            for wanted in ([mask, None] if mask is not None else [None]):
                if mode == "wild":
                    choice = pick(random, buyable(), taken, wanted)
                else:  # standard : même type, prix proche, fenêtre élargie si besoin
                    # (pour l'équipement de l'équipe, pas au-delà de 10 fois le prix d'origine :
                    # mieux vaut un objet que l'équipe ne peut pas porter qu'une arme de fin de jeu)
                    windows = PRICE_WINDOWS[:-1] if wanted is not None else PRICE_WINDOWS
                    for low, high in windows:
                        candidates = [c for c in buyable(kind) if low * price <= ITEM_INFO[c][1] <= high * price]
                        choice = pick(random, candidates, taken, wanted)
                        if choice is not None:
                            break
                if choice is not None:
                    break
            if choice is None:
                choice = item
            taken.add(choice)
            new_items.append(choice)
        result[index] = new_items
    return result


def describe(items: list[int]) -> str:
    return ", ".join(ITEM_INFO[item][3] if item in ITEM_INFO else str(item) for item in items)
