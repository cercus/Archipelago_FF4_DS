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
    "Antarctic Wind": ItemData(0x13B0),
    "Bronze Hourglass": ItemData(0x13BD),
    "Eye Drops x5": ItemData(0x1396, 5),
    "Antidote x5": ItemData(0x1397, 5),
    "Tent x3": ItemData(0x139C, 3),
    "Phoenix Down x3": ItemData(0x1390, 3),
    "Potion x5": ItemData(0x1389, 5),
    "Zeus's Wrath x3": ItemData(0x13B2, 3),
    "480 Gil": ItemData(0, 480),
    "580 Gil": ItemData(0, 580),
    # Objets des coffres ajoutés (relevés dans la ROM, outils_rom/coffres_rom.csv)
    "Unicorn Horn": ItemData(0x139B),
    "Bacchus's Wine": ItemData(0x13C0),
    "Hermes Sandals": ItemData(0x13C1),
    "Hi-Potion": ItemData(0x138A),
    "Elixir": ItemData(0x138E),
    "Gold Needle": ItemData(0x1391),
    "Gnomish Bread": ItemData(0x139F),
    "2000 Gil": ItemData(0, 2000),
    "Gold Hairpin": ItemData(0x1FB1, kind="useful"),
    "Clothing": ItemData(0x2009, kind="useful"),
    "Ruby Ring": ItemData(0x206D, kind="useful"),
    "Polymorph Rod": ItemData(0x1A96, kind="useful"),
    "Power Bow": ItemData(0x1B5A, kind="useful"),
    "Iron Arrows": ItemData(0x1BBE, kind="useful"),
    "Holy Arrows": ItemData(0x1BBF, kind="useful"),
    "Ice Rod": ItemData(0x1A93, kind="useful"),
    "X-Potion": ItemData(0x138B),
    "Dry Ether": ItemData(0x138D),
    "Hades Helm": ItemData(0x1FAC, kind="useful"),
    "Hades Gloves": ItemData(0x2073, kind="useful"),
    "Hades Armor": ItemData(0x2012, kind="useful"),
    "Spider Silk": ItemData(0x13B9),
    "Lamia Harp": ItemData(0x189E, kind="useful"),
    "Emergency Exit": ItemData(0x139E),
}

# Objets de remplissage tirés au hasard quand il manque des objets dans le pool.
FILLER_ITEMS = ["Potion", "Ether", "Tent", "Phoenix Down", "Antidote", "Eye Drops"]

# --------------------------------------------------------------------------- #
# Régions (dans l'ordre de l'histoire)                                        #
# --------------------------------------------------------------------------- #
# Chaque région mène à la suivante. "Kaipo (retour)" est le retour à Kaipo
# après l'Antlion’s Den, là où l'on soigne Rosa.
# Avec la ROM patchée, Baron (château + ville) reste accessible pendant toute la partie.
REGIONS = [
    "Baron",
    "Mist cave",
    "Mist Village",
    "Kaipo",
    "Canal souterrain",
    "Damcyan",
    "Antlion’s Den",
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

    # --- Baron ---
    "Baron Castle - Coffre 1": LocationData("Baron", 0x0CC195, "480 Gil", "coffre"),
    "Baron Castle - Coffre 2": LocationData("Baron", 0x0CC196, "Ether", "coffre"),
    "Baron Castle - Coffre 3": LocationData("Baron", 0x0CC197, "Tent", "coffre"),
    "Baron Castle - Coffre 4": LocationData("Baron", 0x0CC198, "Ether", "coffre"),
    "Baron Castle - Coffre 5": LocationData("Baron", 0x0CC199, "Ether", "coffre"),
    "Baron Castle - Coffre 6": LocationData("Baron", 0x0CC19A, "Unicorn Horn", "coffre"),
    "Baron Castle - Coffre 7": LocationData("Baron", 0x0CC19B, "Unicorn Horn", "coffre"),
    "Baron Castle - Coffre 8": LocationData("Baron", 0x0CC19C, "Phoenix Down", "coffre"),
    "Baron Castle - Coffre 9": LocationData("Baron", 0x0CC19D, "Phoenix Down", "coffre"),
    "Baron Castle - Coffre 10": LocationData("Baron", 0x0CC19E, "Bacchus's Wine", "coffre"),
    "Baron Castle - Coffre 11": LocationData("Baron", 0x0CC19F, "Hermes Sandals", "coffre"),
    "Baron Castle - Coffre 13": LocationData("Baron", 0x0CC1A0, "Bacchus's Wine", "coffre"),
    "Baron Castle - Coffre 14": LocationData("Baron", 0x0CC1A1, "Hermes Sandals", "coffre"),
    "Baron Castle - Coffre 15": LocationData("Baron", 0x0CC1A2, "Hi-Potion", "coffre"),
    "Baron Castle - Coffre 16": LocationData("Baron", 0x0CC1A3, "Hi-Potion", "coffre"),
    "Baron Castle - Coffre 17": LocationData("Baron", 0x0CC1A4, "Ether", "coffre"),
    "Baron Castle - Coffre 18": LocationData("Baron", 0x0CC1A5, "Tent", "coffre"),
    "Baron Castle - Coffre 19": LocationData("Baron", 0x0CC1A6, "Tent", "coffre"),
    "Baron Castle - Coffre 20": LocationData("Baron", 0x0CC1A7, "Ether", "coffre"),
    "Baron Castle - Coffre 21": LocationData("Baron", 0x0CC1A8, "Elixir", "coffre"),
    "Baron - Coffre 1": LocationData("Baron", 0x0CC1AD, "Phoenix Down", "coffre"),
    "Baron - Coffre 2": LocationData("Baron", 0x0CC1AE, "Gold Needle", "coffre"),
    "Baron - Coffre 3": LocationData("Baron", 0x0CC1AF, "Phoenix Down", "coffre"),
    "Baron - Coffre 4": LocationData("Baron", 0x0CC1B0, "Potion", "coffre"),
    "Baron - Coffre 5": LocationData("Baron", 0x0CC1B1, "Potion", "coffre"),
    "Baron - Coffre 6": LocationData("Baron", 0x0CC1B2, "Tent", "coffre"),
    "Baron - Coffre 7": LocationData("Baron", 0x0CC1B4, "Gnomish Bread", "coffre"),
    "Baron - Coffre 8": LocationData("Baron", 0x0CC1B5, "Tent", "coffre"),
    "Baron - Coffre 9": LocationData("Baron", 0x0CC1B6, "Eye Drops", "coffre"),
    "Baron - Coffre 10": LocationData("Baron", 0x0CC1B7, "Potion", "coffre"),
    "Baron - Coffre 11": LocationData("Baron", 0x0CC1B8, "Zeus's Wrath", "coffre"),
    "Baron - Coffre 12": LocationData("Baron", 0x0CC1B9, "2000 Gil", "coffre"),
    "Baron - Coffre 13": LocationData("Baron", 0x0CC1BB, "Eye Drops", "coffre"),
    "Baron - Hidden chest in water": LocationData("Baron", 0x0CC1B3, "Bronze Hourglass", "coffre"),
    "Baron - Hidden chest near chariot": LocationData("Baron", 0x0CC1BA, "Potion", "coffre"),

    # --- Namingway 
    "Namingway - Premiere rencontre": LocationData("Baron", 0x0CC145, None, "namingway"),
    "Namingway - Donne la carte": LocationData("Mist cave", 0x0CC146, None, "namingway"),
    "Namingway - Devient Livingway": LocationData("Kaipo", 0x0CC147, None, "namingway"),

    # --- Mist cave ------------------------------------------------------------
    "Mist cave - Coffre 1": LocationData("Mist cave", 0x0CC2C0, "Potion", "coffre"),
    "Mist cave - Coffre 2": LocationData("Mist cave", 0x0CC2C1, "Eye Drops", "coffre"),
    "Mist cave - Coffre 3": LocationData("Mist cave", 0x0CC2C2, "Tent", "coffre"),
    "Mist cave - Coffre 4": LocationData("Mist cave", 0x0CC2C3, "Potion", "coffre"),
    "Mist cave - Dragon des Brumes vaincu": LocationData("Mist cave", 0x0CBDC3, None, "boss"),
    
    # --- Kaipo ----------------------------------------------------------------
    "Kaipo - Rosa donne Auto-Potion": LocationData("Kaipo", 0x0CBDCA, "Auto-Potion", "evenement"),
    

    # --- Canal souterrain --------------------------------------------------
    "Waterway Entrance South B1 - Coffre 1": LocationData("Canal souterrain", 0x0CC2C7, "Tent", "coffre"),
    "Waterway Entrance South B1 - Coffre 2": LocationData("Canal souterrain", 0x0CC2C6, "Potion", "coffre"),
    "Waterway Entrance South B1 - Coffre 3": LocationData("Canal souterrain", 0x0CC2C5, "Maiden's Kiss", "coffre"),
    "Waterway Entrance South B1 - Coffre 4": LocationData("Canal souterrain", 0x0CC2C8, "Ether", "coffre"),
    "Underground Waterway South B2 - Coffre 1": LocationData("Canal souterrain", 0x0CC2C9, "Potion", "coffre"),
    "Underground Waterway South B2 - Coffre 2": LocationData("Canal souterrain", 0x0CC2CA, "Ether", "coffre"),
    "Underground Waterway South B2 - Coffre 3": LocationData("Canal souterrain", 0x0CC2CB, "Ice Rod", "coffre"),
    "Underground Waterway Secret Room - Coffre 1": LocationData("Canal souterrain", 0x0CC2CC, "X-Potion", "coffre"),
    "Underground Waterway Secret Room - Coffre 2": LocationData("Canal souterrain", 0x0CC2CD, "Dry Ether", "coffre"),
    "Underground Waterway Secret Room - Coffre 3": LocationData("Canal souterrain", 0x0CC2CE, "Phoenix Down", "coffre"),
    "Underground Waterway B3 - Coffre 1": LocationData("Canal souterrain", 0x0CC2CF, "580 Gil", "coffre"),
    "Underground Waterway B3 - Coffre 2": LocationData("Canal souterrain", 0x0CC2D0, "Bomb Fragment", "coffre"),
    "Underground Waterway North B2 - Coffre 1": LocationData("Canal souterrain", 0x0CC2D1, "Potion", "coffre"),
    "Underground Waterway North B2 - Coffre 2": LocationData("Canal souterrain", 0x0CC2D2, "Feathered Cap", "coffre"),
    "Waterway Entrance North B1 - Coffre 1": LocationData("Canal souterrain", 0x0CC2D3, "Ether", "coffre"),
    "Waterway Entrance North B1 - Coffre 2": LocationData("Canal souterrain", 0x0CC2D4, "Zeus's Wrath", "coffre"),
    "Waterway Entrance North B1 - Coffre 3": LocationData("Canal souterrain", 0x0CC2D6, "Shadowblade", "coffre"),
    "Waterway Entrance North B1 - Coffre 4": LocationData("Canal souterrain", 0x0CC2D5, "Bronze Hourglass", "coffre"),
    "Underground Lake B2 - Coffre 1": LocationData("Canal souterrain", 0x0CC2D7, "Hades Helm", "coffre"),
    "Underground Lake B2 - Coffre 2": LocationData("Canal souterrain", 0x0CC2D8, "Hades Gloves", "coffre"),
    "Underground Lake B1 - Coffre 1": LocationData("Canal souterrain", 0x0CC2D9, "Hades Armor", "coffre"),
    "Underground Lake B1 - Coffre 2": LocationData("Canal souterrain", 0x0CC2DA, "Hermes Sandals", "coffre"),
    "Underground Lake - Octomammoth defeated": LocationData("Canal souterrain", 0x0CBDD1, None, "boss"),

    # --- Antlion’s Den ---------------------------------------------------
    "Antlion’s Den - Coffre": LocationData("Antlion’s Den", 0x0CC2E6, "Antarctic Wind", "coffre"),
    "Antlion’s Den - Coffre 1": LocationData("Antlion’s Den", 0x0CC2DE, "Spider Silk", "coffre"),
    "Antlion’s Den - Coffre 2": LocationData("Antlion’s Den", 0x0CC2DF, "Potion", "coffre"),
    "Antlion’s Den - Coffre 3": LocationData("Antlion’s Den", 0x0CC2E0, "Potion", "coffre"),
    "Antlion’s Den - Coffre 4": LocationData("Antlion’s Den", 0x0CC2E1, "Gold Needle", "coffre"),
    "Antlion’s Den - Coffre 5": LocationData("Antlion’s Den", 0x0CC2E2, "Potion", "coffre"),
    "Antlion’s Den - Coffre 6": LocationData("Antlion’s Den", 0x0CC2E3, "Tent", "coffre"),
    "Antlion’s Den - Coffre 7": LocationData("Antlion’s Den", 0x0CC2E4, "Spider Silk", "coffre"),
    "Antlion’s Den - Coffre 8": LocationData("Antlion’s Den", 0x0CC2E5, "Potion", "coffre"),
    "Antlion’s Den - Coffre 9": LocationData("Antlion’s Den", 0x0CC2E7, "Lamia Harp", "coffre"),
    "Antlion’s Den - Coffre 10": LocationData("Antlion’s Den", 0x0CC2E8, "Emergency Exit", "coffre"),
    "Antlion’s Den - Coffre 11": LocationData("Antlion’s Den", 0x0CC2E9, "Ether", "coffre"),
    "Antlion’s Den - Coffre 12": LocationData("Antlion’s Den", 0x0CC2EA, "Phoenix Down", "coffre"),
    "Antlion’s Den - Coffre 13": LocationData("Antlion’s Den", 0x0CC2EB, "Shadowblade", "coffre"),
    "Antlion’s Den - Coffre 14": LocationData("Antlion’s Den", 0x0CC2EC, "Ice Rod", "coffre"),

    "Antlion’s Den - Fourmillon defeated": LocationData("Antlion’s Den", 0x0CBDDB, "Sand Pearl", "boss"),

    

    # --- Mist Village (coffres relevés dans la ROM) ---
    "Mist Village - Coffre 1": LocationData("Mist Village", 0x0CC1BC, "Bomb Fragment", "coffre"),
    "Mist Village - Coffre 2": LocationData("Mist Village", 0x0CC1BD, "Bomb Fragment", "coffre"),
    "Mist Village - Coffre 3": LocationData("Mist Village", 0x0CC1BE, "Bomb Fragment", "coffre"),
    "Mist Village - Coffre 4": LocationData("Mist Village", 0x0CC1BF, "Gold Hairpin", "coffre"),
    "Mist Village - Coffre 5": LocationData("Mist Village", 0x0CC1C0, "Clothing", "coffre"),
    "Mist Village - Coffre 6": LocationData("Mist Village", 0x0CC1C1, "Ruby Ring", "coffre"),
    "Mist Village - Coffre 7": LocationData("Mist Village", 0x0CC1C2, "Polymorph Rod", "coffre"),

    # --- Damcyan (coffres relevés dans la ROM) ---
    "Damcyan Castle - Coffre 1": LocationData("Damcyan", 0x0CC1C6, "Tent", "coffre"),
    "Damcyan Castle - Coffre 2": LocationData("Damcyan", 0x0CC1C7, "Power Bow", "coffre"),
    "Damcyan Castle - Coffre 3": LocationData("Damcyan", 0x0CC1C8, "Feathered Cap", "coffre"),
    "Damcyan Castle - Coffre 4": LocationData("Damcyan", 0x0CC1C9, "Ruby Ring", "coffre"),
    "Damcyan Castle - Coffre 5": LocationData("Damcyan", 0x0CC1CA, "Potion", "coffre"),
    "Damcyan Castle - Coffre 6": LocationData("Damcyan", 0x0CC1CB, "Antidote", "coffre"),
    "Damcyan Castle - Coffre 7": LocationData("Damcyan", 0x0CC1CC, "Eye Drops", "coffre"),
    "Damcyan Castle - Coffre 8": LocationData("Damcyan", 0x0CC1CD, "Ether", "coffre"),
    "Damcyan Castle - Coffre 9": LocationData("Damcyan", 0x0CC1CE, "Phoenix Down", "coffre"),
    "Damcyan Castle - Coffre 10": LocationData("Damcyan", 0x0CC1CF, "Gold Needle", "coffre"),
    "Damcyan Castle - Coffre 11": LocationData("Damcyan", 0x0CC1D0, "Iron Arrows", "coffre"),
    "Damcyan Castle - Coffre 12": LocationData("Damcyan", 0x0CC1D1, "Holy Arrows", "coffre"),
    "Damcyan Castle - Coffre 13": LocationData("Damcyan", 0x0CC1D2, "Elixir", "coffre"),
    
    

    # --- Kaipo (retour) -------------------------------------------------------
    "Kaipo - Edward donne Item Lore": LocationData("Kaipo (retour)", 0x0CBF76, "Item Lore", "evenement"),



    # --- Cartes complétés -----------------------------------------------------
    "Waterway Entrance South B1 - Map completed": LocationData("Canal souterrain", 0x0CC4E9, "Eye Drops x5", "carte"),
    "Underground Waterway South B2 - Map completed": LocationData("Canal souterrain", 0x0CC4EA, "Antidote x5", "carte"),
    "Underground Waterway B3 - Map completed": LocationData("Canal souterrain", 0x0CC4ED, "Tent x3", "carte"),
    "Underground Waterway North B2 - Map completed": LocationData("Canal souterrain", 0x0CC4EE, "Phoenix Down x3", "carte"),
    "Waterway Entrance North B1 - Map completed": LocationData("Canal souterrain", 0x0CC4EF, "Ether", "carte"),
    "Underground Lake B2 - Map completed": LocationData("Canal souterrain", 0x0CC4F1, "Potion x5", "carte"),
    "Underground Lake B1 - Map completed": LocationData("Canal souterrain", 0x0CC4F2, "Zeus's Wrath x3", "carte"),


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
