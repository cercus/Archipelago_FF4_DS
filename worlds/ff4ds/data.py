"""Données brutes de Final Fantasy IV DS (version US), tranche 1 : de Baron au soin de Rosa.

Toutes les adresses sont relatives au domaine "Main RAM" de BizHawk.
Ce fichier ne contient que des données : pas de logique Archipelago.
Pour ajouter une location, il suffit d'ajouter une ligne dans LOCATIONS.
"""
from typing import NamedTuple

# --------------------------------------------------------------------------- #
# Objets                                                                      #
# --------------------------------------------------------------------------- #
# Identifiant Archipelago d'un objet :
#   - objet du jeu : (quantité << 16) | ID du jeu      ex. 5 Eye Drops -> 0x00051396
#   - gils         : GIL_FLAG | montant                ex. 480 gils   -> 0x010001E0
# Le client décode cet identifiant pour savoir quoi écrire en mémoire.
GIL_FLAG = 0x01000000


class ItemData(NamedTuple):
    game_id: int          # ID de l'objet dans le jeu (0 pour les gils)
    quantity: int = 1     # quantité donnée (ou montant pour les gils)
    kind: str = "filler"  # "progression", "useful" ou "filler"
    key_item: bool = False  # True : va dans la liste des objets clés (0x0D8084)

    @property
    def ap_id(self) -> int:
        if self.game_id == 0:
            return GIL_FLAG | self.quantity
        return (self.quantity << 16) | self.game_id


ITEMS: dict[str, ItemData] = {
    # Progression
    "Sand Pearl": ItemData(0x232C, kind="progression", key_item=True),
    # Utiles
    "Auto-Potion": ItemData(0x23B0, kind="useful", key_item=True),   # augment
    "Item Lore": ItemData(0x23B2, kind="useful", key_item=True),     # augment
    "Shadowblade": ItemData(0x1772, kind="useful"),
    "Feathered Cap": ItemData(0x1FA7, kind="useful"),
    # Remplissage
    "Potion": ItemData(0x1389),
    "Ether": ItemData(0x138C),
    "Phoenix Down": ItemData(0x1390),
    "Maiden's Kiss": ItemData(0x1392),
    "Eye Drops": ItemData(0x1396),
    "Antidote": ItemData(0x1397),
    "Tent": ItemData(0x139C),
    "Bomb Fragment": ItemData(0x13AE),
    "Zeus's Wrath": ItemData(0x13B2),
    "Bronze Hourglass": ItemData(0x13BD),
    "Eye Drops x5": ItemData(0x1396, 5),
    "Antidote x5": ItemData(0x1397, 5),
    "Tent x3": ItemData(0x139C, 3),
    "Phoenix Down x3": ItemData(0x1390, 3),
    "480 Gil": ItemData(0, 480),
    "580 Gil": ItemData(0, 580),
}

# Objets de remplissage tirés au hasard quand il manque des objets dans le pool.
FILLER_ITEMS = ["Potion", "Ether", "Tent", "Phoenix Down", "Antidote", "Eye Drops"]

# --------------------------------------------------------------------------- #
# Régions (dans l'ordre de l'histoire)                                        #
# --------------------------------------------------------------------------- #
# Chaque région mène à la suivante. "Kaipo (retour)" est le retour à Kaipo
# après l'Antre de l'Antlion, là où l'on soigne Rosa.
REGIONS = [
    "Baron",
    "Grotte de la Brume",
    "Kaipo",
    "Riviere souterraine",
    "Damcyan",
    "Antre de l'Antlion",
    "Kaipo (retour)",
]

# --------------------------------------------------------------------------- #
# Locations                                                                   #
# --------------------------------------------------------------------------- #
# flag     : adresse de l'octet qui passe à 1 quand la location est validée.
#            Elle sert aussi d'identifiant Archipelago de la location.
# vanilla  : objet d'origine (None s'il n'y en a pas ou s'il est inconnu).
# category : "coffre", "boss", "evenement", "namingway", "carte".
# excluded : True si la location n'est accessible qu'au début du jeu
#            (le générateur n'y mettra jamais d'objet de progression).


class LocationData(NamedTuple):
    region: str
    flag: int
    vanilla: str | None
    category: str
    excluded: bool = False


LOCATIONS: dict[str, LocationData] = {
    # --- Baron (accessible seulement au début : fenêtre) --------------------
    "Chateau de Baron - Coffre 1": LocationData("Baron", 0x0CC195, "480 Gil", "coffre", True),
    "Chateau de Baron - Coffre 2": LocationData("Baron", 0x0CC196, "Ether", "coffre", True),
    "Chateau de Baron - Coffre 3": LocationData("Baron", 0x0CC197, "Tent", "coffre", True),
    "Ville de Baron - Objet cache dans l'eau": LocationData("Baron", 0x0CC1B3, "Bronze Hourglass", "coffre", True),
    "Ville de Baron - Objet cache pres du chariot": LocationData("Baron", 0x0CC1BA, "Potion", "coffre", True),
    "Namingway - Premiere rencontre": LocationData("Baron", 0x0CC145, None, "namingway", True),

    # --- Grotte de la Brume ---------------------------------------------------
    "Grotte de la Brume - Coffre": LocationData("Grotte de la Brume", 0x0CC2C0, "Potion", "coffre"),
    "Grotte de la Brume - Coffre 2": LocationData("Grotte de la Brume", 0x0CC2C1, "Eye Drops", "coffre"),
    "Grotte de la Brume - Coffre 3": LocationData("Grotte de la Brume", 0x0CC2C2, "Tent", "coffre"),
    "Grotte de la Brume - Coffre 4": LocationData("Grotte de la Brume", 0x0CC2C3, "Potion", "coffre"),
    "Grotte de la Brume - Dragon des Brumes vaincu": LocationData("Grotte de la Brume", 0x0CBDC3, None, "boss"),
    "Namingway - Donne la carte": LocationData("Grotte de la Brume", 0x0CC146, None, "namingway"),

    # --- Kaipo ----------------------------------------------------------------
    "Kaipo - Rosa donne Auto-Potion": LocationData("Kaipo", 0x0CBDCA, "Auto-Potion", "evenement"),
    "Namingway - Devient Livingway": LocationData("Kaipo", 0x0CC147, None, "namingway"),

    # --- Rivière souterraine --------------------------------------------------
    "Waterway Entrance South B1 - Coffre 1": LocationData("Riviere souterraine", 0x0CC2C7, "Tent", "coffre"),
    "Waterway Entrance South B1 - Coffre 2": LocationData("Riviere souterraine", 0x0CC2C6, "Potion", "coffre"),
    "Waterway Entrance South B1 - Coffre 3": LocationData("Riviere souterraine", 0x0CC2C5, "Maiden's Kiss", "coffre"),
    "Waterway Entrance South B1 - Coffre 4": LocationData("Riviere souterraine", 0x0CC2C8, "Ether", "coffre"),
    "Underground Waterway South B2 - Coffre": LocationData("Riviere souterraine", 0x0CC2C9, "Potion", "coffre"),
    "Underground Waterway B3 - Coffre 1": LocationData("Riviere souterraine", 0x0CC2CF, "580 Gil", "coffre"),
    "Underground Waterway B3 - Coffre 2": LocationData("Riviere souterraine", 0x0CC2D0, "Bomb Fragment", "coffre"),
    "Underground Waterway North B2 - Coffre 1": LocationData("Riviere souterraine", 0x0CC2D1, "Potion", "coffre"),
    "Underground Waterway North B2 - Coffre 2": LocationData("Riviere souterraine", 0x0CC2D2, "Feathered Cap", "coffre"),
    "Waterway Entrance North B1 - Coffre 1": LocationData("Riviere souterraine", 0x0CC2D4, "Zeus's Wrath", "coffre"),
    "Waterway Entrance North B1 - Coffre 2": LocationData("Riviere souterraine", 0x0CC2D3, None, "coffre"),
    "Waterway Entrance North B1 - Coffre 3": LocationData("Riviere souterraine", 0x0CC2D6, "Shadowblade", "coffre"),
    "Waterway Entrance North B1 - Coffre 4": LocationData("Riviere souterraine", 0x0CC2D5, "Bronze Hourglass", "coffre"),
    "Waterway Entrance South B1 - Carte completee": LocationData("Riviere souterraine", 0x0CC4E9, "Eye Drops x5", "carte"),
    "Underground Waterway South B2 - Carte completee": LocationData("Riviere souterraine", 0x0CC4EA, "Antidote x5", "carte"),
    "Underground Waterway B3 - Carte completee": LocationData("Riviere souterraine", 0x0CC4ED, "Tent x3", "carte"),
    "Underground Waterway North B2 - Carte completee": LocationData("Riviere souterraine", 0x0CC4EE, "Phoenix Down x3", "carte"),
    "Waterway Entrance North B1 - Carte completee": LocationData("Riviere souterraine", 0x0CC4EF, "Ether", "carte"),
    "Riviere souterraine - Octomammoth vaincu": LocationData("Riviere souterraine", 0x0CBDD1, None, "boss"),

    # --- Antre de l'Antlion ---------------------------------------------------
    "Antre de l'Antlion - Coffre": LocationData("Antre de l'Antlion", 0x0CC2E6, None, "coffre"),
    "Antre de l'Antlion - Antlion vaincu": LocationData("Antre de l'Antlion", 0x0CBDDB, "Sand Pearl", "boss"),

    # --- Kaipo (retour) -------------------------------------------------------
    "Kaipo - Edward donne Item Lore": LocationData("Kaipo (retour)", 0x0CBF76, "Item Lore", "evenement"),
}

# Objectif : la scène de soin de Rosa est terminée.
GOAL_FLAG = 0x0CBDDD

# --------------------------------------------------------------------------- #
# Adresses mémoire utiles au client (étape 6)                                 #
# --------------------------------------------------------------------------- #
RAM = {
    "inventory": 0x0D7A80,         # 384 slots de 4 octets : ID (2), quantité (1), 0 (1)
    "inventory_count": 0x0D8080,
    "key_items": 0x0D8084,         # 128 slots, même format
    "key_items_count": 0x0D8284,
    "gil": 0x0D8288,               # 4 octets
    "event_running": 0x0CC57C,     # 1 pendant une cinématique / un dialogue
    "object_list": 0x0CF460,       # pointeur vers le premier objet de la carte (le joueur)
    "map_name": 0x0CF464,          # nom de la carte en texte, ex. "d00_00", "f00_00"
}

# Flag d'un coffre = CHEST_FLAG_BASE + numéro stocké dans l'objet coffre (+0x48).
CHEST_FLAG_BASE = 0x0CC194

# Objets de carte (liste chaînée) :
#   +0x00 type (adresse de la table de méthodes), +0x04 objet suivant,
#   +0x14 nom interne ("ib_10", "gb_03"...), +0x48 numéro du flag,
#   +0x7C contenu (ID de l'objet, ou montant pour les gils), +0x80 quantité (coffres d'objets).
ITEM_BOX_TYPE = 0x02138B58         # "ib_xx" : coffre d'objet
GIL_BOX_TYPE = 0x02138B90          # "gb_xx" : coffre de gils
