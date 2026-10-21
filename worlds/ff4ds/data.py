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
VEHICLE_FLAG = 0x03000000     # véhicule : VEHICLE_FLAG | numéro (1 hovercraft, 2 Enterprise)


class ItemData(NamedTuple):
    game_id: int          # ID de l'objet dans le jeu (0 pour les gils)
    quantity: int = 1     # quantité donnée (ou montant pour les gils)
    kind: str = "filler"  # "progression", "useful" ou "filler"
    key_item: bool = False  # True : va dans la liste des objets clés (0x0D8084)
    vehicle: int = 0      # véhicule (VEHICLES) : posé par le client, pas mis dans l'inventaire

    @property
    def ap_id(self) -> int:
        if self.vehicle:
            return VEHICLE_FLAG | self.vehicle
        if self.game_id == 0:
            return GIL_FLAG | self.quantity
        return (self.quantity << 16) | self.game_id


ITEMS: dict[str, ItemData] = {
    # Progression
    "Hovercraft": ItemData(0, kind="progression", vehicle=1),
    "Enterprise": ItemData(0, kind="progression", vehicle=2),
    "Falcon": ItemData(0, kind="progression", vehicle=5),        # progressif : Faucon, puis traversée de la lave
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
    # Tranche 2
    "960 Gil": ItemData(0, 960),
    "Hi-Potion x3": ItemData(0x138A, 3),
    "Bomb Core x3": ItemData(0x13B5, 3),
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
    # Fabul
    "Deathbringer": ItemData(0x1773, kind="useful"),
    "Demon Shield": ItemData(0x1F43, kind="useful"),
    "Counter": ItemData(0x23B3, kind="useful", key_item=True),     # augment
    # Mont Ordeals
    "Red Fang": ItemData(0x13AB),
    "Curse": ItemData(0x23BD, kind="useful", key_item=True),       # augment
    # Tranche 3 : Baron, Ancient Waterway
    "Baron Key": ItemData(0x2330, kind="progression", key_item=True),  # ouvre l'Ancient Waterway
    "Tsunami": ItemData(0x23BE, kind="useful", key_item=True),     # augment
    "Ancient Sword": ItemData(0x1778, kind="useful"),
    "Remedy x3": ItemData(0x1399, 3),
    "1000 Gil": ItemData(0, 1000),
    # Tranche 4 : Troia, caverne magnétique, tour de Zott
    "Whisperweed": ItemData(0x2331, kind="progression", key_item=True),   # Elfe noir (op076(9009))
    "Earth Crystal": ItemData(0x232E, kind="progression", key_item=True), # accès à Zott (op076(9006))
    "Decoy": ItemData(0x13C2),
    "Remedy": ItemData(0x1399),
    "Echo Herbs": ItemData(0x1395),
    "Great Bow": ItemData(0x1B5B, kind="useful"),
    "Fire Arrows": ItemData(0x1BC0, kind="useful"),
    "5000 Gil": ItemData(0, 5000),
    "Silver Apple": ItemData(0x13A3),
    "Ice Arrows": ItemData(0x1BC1, kind="useful"),
    "50000 Gil": ItemData(0, 50000),
    "Lightning Arrows": ItemData(0x1BC2, kind="useful"),
    "Gysahl Greens": ItemData(0x13A0),
    "Faerie Claws": ItemData(0x1904, kind="useful"),
    "Flame Mail": ItemData(0x2019, kind="useful"),
    "Flame Sword": ItemData(0x177C, kind="useful"),
    "Hell Claws": ItemData(0x1905, kind="useful"),
    "Gaia Hammer": ItemData(0x1967, kind="useful"),
    "Sage's Surplice": ItemData(0x2010, kind="useful"),
    "Flame Shield": ItemData(0x1F46, kind="useful"),
    "Whirlwind": ItemData(0x23BF, kind="useful", key_item=True),
    "Vampire Fang": ItemData(0x13B8),
    "Vampire Fang x3": ItemData(0x13B8, 3),
    "Silent Bell": ItemData(0x13BA),
    "Silent Bell x3": ItemData(0x13BA, 3),
    "Zeus's Wrath x5": ItemData(0x13B2, 5),
    "Heavenly Wrath": ItemData(0x13B3),
    # Tranche 5 : Agart, monde souterrain
    "Magma Stone": ItemData(0x2334, kind="progression", key_item=True),   # puits d'Agart (op076(9012))
    "Gaia Drum": ItemData(0x13B4),
    "Cottage": ItemData(0x139D),
    "Dwarven Axe": ItemData(0x19C9, kind="useful"),
    "Silver Hourglass": ItemData(0x13BE),
    "Power Armlet": ItemData(0x2072, kind="useful"),
    "Black Belt Gi": ItemData(0x2015, kind="useful"),
    "Draw Attacks": ItemData(0x23C1, kind="useful", key_item=True),   # augment (Giott)
    "Adrenaline": ItemData(0x239B, kind="useful", key_item=True),     # augments de Cid (lettre)
    "Luca's Necklace": ItemData(0x2336, kind="progression", key_item=True),   # clé de la grotte scellée
    # Tranche 6 : tour de Babil
    "Tower Key": ItemData(0x2337, kind="progression", key_item=True),     # portes des canons (op076(9015))
    "Green Beret": ItemData(0x1FAA, kind="useful"),
    "Cat Claws": ItemData(0x1906, kind="useful"),
    "Icebrand": ItemData(0x177D, kind="useful"),
    "Ice Lance": ItemData(0x17D8, kind="useful"),
    "Killer Bow": ItemData(0x1B5C, kind="useful"),
    "Ice Shield": ItemData(0x1F47, kind="useful"),
    "Ice Armor": ItemData(0x201B, kind="useful"),
    "Arctic Wind": ItemData(0x13B1),
    "Antarctic Wind x5": ItemData(0x13B0, 5),
    "Arctic Wind x3": ItemData(0x13B1, 3),
    "White Fang": ItemData(0x13AC),
    "Hi-Potion x5": ItemData(0x138A, 5),
    "Remedy x5": ItemData(0x1399, 5),
    "Ether x2": ItemData(0x138C, 2),
    "Shuriken": ItemData(0x1CE9, kind="useful"),
    "Bomb Core": ItemData(0x13B5),
    "Blood Sword": ItemData(0x1779, kind="useful"),
    "Ninja Sutra": ItemData(0x13A7),
    "Inferno": ItemData(0x23C0, kind="useful", key_item=True),
    "Ogrekiller": ItemData(0x19CA, kind="useful"),
    "Lilith's Kiss": ItemData(0x13B7),
    "Ashura": ItemData(0x1A2E, kind="useful"),
    "Bomb Crank": ItemData(0x13AF),
    "Bacchus's Wine x3": ItemData(0x13C0, 3),
    "Hermes Sandals x3": ItemData(0x13C1, 3),
    "Decoy x3": ItemData(0x13C2, 3),
    "Bomb Fragment x5": ItemData(0x13AE, 5),
    "Bomb Crank x3": ItemData(0x13AF, 3),
    "X-Potion x3": ItemData(0x138B, 3),
    "10000 Gil": ItemData(0, 10000),
    "Heavenly Wrath x3": ItemData(0x13B3, 3),
    "Blue Fang": ItemData(0x13AD),
    "Bronze Hourglass x3": ItemData(0x13BD, 3),
}

# Véhicules : le client active le flag « disponible » et écrit la position (vérifié le 18/10/2026 :
# depuis une ville, le véhicule apparaît à la sortie sur la carte du monde, même loin du centre).
class VehicleData(NamedTuple):
    flag: int                     # octet « véhicule disponible »
    position: int | None          # X, Y, Z (u32 chacun) en RAM ; None : amélioration, flag seul
    coords: tuple[int, int | None, int] | None   # Y None : on ne l'écrit pas ; None : position de l'Enterprise


VEHICLES: dict[int, VehicleData] = {
    1: VehicleData(0x0CC130, 0x0D05F8, (81920, None, -3153920)),     # hovercraft, devant Damcyan
    2: VehicleData(0x0CC131, 0x0D0604, (-978944, 0, 1658880)),       # Enterprise, devant Baron
    # Enterprise avec crochet (véhicule 4, flag 903) : remplace l'Enterprise là où elle se trouve.
    4: VehicleData(0x0CC133, 0x0D061C, None),
    # Faucon (véhicule 5, flag 904) : position en 0x0D0610 (écrite par op0B3(5, …), vérifié en émulateur),
    # sous la surface, devant la tour de Babil (carte du véhicule : sous la surface par défaut).
    5: VehicleData(0x0CC134, 0x0D0610, (-1228800, 102400, -2682880)),
    # Traversée de la lave (flag 902, posé d'origine par Cid au château des nains) : flag seul.
    3: VehicleData(0x0CC132, None, None),
}
# Véhicules progressifs : n-ième exemplaire reçu de l'objet -> véhicule (Enterprise, puis avec crochet).
PROGRESSIVE_VEHICLES: dict[int, list[int]] = {2: [2, 4], 5: [5, 3]}

# Chemins qui demandent en plus plusieurs exemplaires d'un objet (tous requis).
CONNECTION_COUNTS: dict[tuple[str, str], list[tuple[str, int]]] = {
    ("Baron", "Cave of Eblan"): [("Enterprise", 2)],   # l'Enterprise avec crochet porte l'hovercraft
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
    "Mount Hobs",
    "Fabul",
    "Mount Ordeals",
    "Baron (retour)",
    "Ancient Waterway",
    "Troia",
    "Lodestone Cavern",
    "Tower of Zot",
    "Agart",
    "Underworld",
    "Dwarf Castle",
    "Tower of Babil",
    "Cave of Eblan",
    "Tower of Babil (upper)",
    "Dwarf Castle (Cid)",
]

# Chemins entre régions (départ : Baron) et objets nécessaires (l'un d'eux suffit).
# Monde ouvert : le chemin maudit (Baron <-> Mysidia) est ouvert dès le départ ; les hauts-fonds
# (Antlion, mont Hobs) demandent l'hovercraft ou l'Enterprise.
CONNECTIONS: list[tuple[str, str, tuple[str, ...]]] = [
    ("Baron", "Mist cave", ()),
    ("Mist cave", "Mist Village", ()),
    ("Mist Village", "Kaipo", ()),
    ("Kaipo", "Canal souterrain", ()),
    ("Canal souterrain", "Damcyan", ()),
    ("Kaipo", "Kaipo (retour)", ()),
    ("Damcyan", "Antlion’s Den", ("Hovercraft", "Enterprise")),
    ("Kaipo", "Mount Hobs", ("Hovercraft", "Enterprise")),
    ("Mount Hobs", "Fabul", ()),
    ("Baron", "Fabul", ("Enterprise",)),
    ("Baron", "Mount Ordeals", ()),            # chemin maudit -> Mysidia -> mont Ordeals
    ("Baron", "Baron (retour)", ()),
    ("Baron (retour)", "Ancient Waterway", ("Baron Key",)),
    ("Baron", "Troia", ("Enterprise",)),       # continent de Troia : par les airs
    ("Troia", "Lodestone Cavern", ()),         # île de la caverne : chocobo noir (village des chocobos)
    ("Troia", "Tower of Zot", ("Earth Crystal",)),   # une Épopte téléporte à la tour (étape X2)
    ("Baron", "Agart", ("Enterprise",)),       # île d'Agart : par les airs
    ("Agart", "Underworld", ("Magma Stone",)), # puits d'Agart -> trou, avec l'Enterprise (jamais abîmée)
    ("Underworld", "Dwarf Castle", ()),
    ("Underworld", "Tower of Babil", ()),      # toujours accessible (le chemin des nains ou l'Enterprise)
    ("Baron", "Cave of Eblan", ("Hovercraft",)),   # + Enterprise avec crochet : CONNECTION_COUNTS
    ("Cave of Eblan", "Tower of Babil (upper)", ()),
    # Après la chute (sous la surface, à bord du Faucon ou de l'Enterprise avec crochet) : Cid à l'infirmerie.
    ("Tower of Babil (upper)", "Dwarf Castle (Cid)", ()),
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
    "Damcyan - Hovercraft": LocationData("Damcyan", 0x0CBDD8, "Hovercraft", "evenement"),    # flag 44
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

    # --- Tranche 2 : Mount Hobs (d03_00 à d03_03) --------------------------------
    "Mount Hobs Vista - Coffre 1": LocationData("Mount Hobs", 0x0CC2ED, "Tent", "coffre"),
    "Mount Hobs Vista - Coffre 2": LocationData("Mount Hobs", 0x0CC2EE, "Potion", "coffre"),
    "Mount Hobs Vista - Coffre 3": LocationData("Mount Hobs", 0x0CC2EF, "Gold Needle", "coffre"),
    "Mount Hobs Vista - Coffre 4": LocationData("Mount Hobs", 0x0CC2F0, "960 Gil", "coffre"),
    "Mount Hobs Summit - Coffre 1": LocationData("Mount Hobs", 0x0CC2F1, "Holy Arrows", "coffre"),
    "Mount Hobs Summit - Mom Bomb defeated": LocationData("Mount Hobs", 0x0CBDE5, None, "boss"),
    "Mount Hobs West Slope - Map completed": LocationData("Mount Hobs", 0x0CC4F8, "Hi-Potion x3", "carte"),
    "Mount Hobs Vista - Map completed": LocationData("Mount Hobs", 0x0CC4F9, None, "carte"),
    "Mount Hobs Summit - Map completed": LocationData("Mount Hobs", 0x0CC4FA, None, "carte"),
    "Mount Hobs East Slope - Map completed": LocationData("Mount Hobs", 0x0CC4FB, "Bomb Core x3", "carte"),

    # --- Tranche 2 : Fabul (t05_xx) -------------------------------------------
    "Fabul Throne Room - Coffre 1": LocationData("Fabul", 0x0CC1D5, "Hermes Sandals", "coffre"),   # caché
    "Fabul Throne Room - Coffre 2": LocationData("Fabul", 0x0CC1D6, "Spider Silk", "coffre"),
    "Fabul Throne Room - Coffre 3": LocationData("Fabul", 0x0CC1D7, "Demon Shield", "coffre"),
    "Fabul Throne Room - Coffre 4": LocationData("Fabul", 0x0CC1D8, "Ether", "coffre"),
    "Fabul Tower - Coffre 1": LocationData("Fabul", 0x0CC1D9, "Potion", "coffre"),                # t05_04
    "Fabul Tower - Coffre 2": LocationData("Fabul", 0x0CC1DA, "Antarctic Wind", "coffre"),
    "Fabul Tower - Coffre 3": LocationData("Fabul", 0x0CC1DB, "Bomb Fragment", "coffre"),
    "Fabul Tower - Coffre 4": LocationData("Fabul", 0x0CC1DC, "Zeus's Wrath", "coffre"),          # caché
    "Fabul Royal Tower - Coffre 1": LocationData("Fabul", 0x0CC1DD, "Bacchus's Wine", "coffre"),  # t05_08, caché
    "Fabul King's Bedchamber - Coffre 1": LocationData("Fabul", 0x0CC1DE, "Tent", "coffre"),       # t05_09
    "Fabul - Castle defended": LocationData("Fabul", 0x0CBDF2, None, "boss"),                     # flag 70
    "Fabul - King gives Deathbringer": LocationData("Fabul", 0x0CBDF6, "Deathbringer", "evenement"),  # flag 74
    "Fabul - Counter augment": LocationData("Fabul", 0x0CBDF7, "Counter", "evenement"),           # flag 75

    # --- Tranche 2 : Mount Ordeals (d04_00 à d04_03) ---------------------------
    "Mount Ordeals Entrance - Coffre 1": LocationData("Mount Ordeals", 0x0CC2F7, "Potion", "coffre"),
    "Mount Ordeals Entrance - Coffre 2": LocationData("Mount Ordeals", 0x0CC2F8, "Potion", "coffre"),
    "Mount Ordeals Crossing - Coffre 1": LocationData("Mount Ordeals", 0x0CC2F9, "Ether", "coffre"),
    "Mount Ordeals Crossing - Coffre 2": LocationData("Mount Ordeals", 0x0CC2FA, "Ether", "coffre"),
    "Mount Ordeals Crossing - Curse augment": LocationData("Mount Ordeals", 0x0CC3EE, "Curse", "coffre"),  # après Scarmiglione
    "Mount Ordeals Summit - Scarmiglione defeated": LocationData("Mount Ordeals", 0x0CBE10, None, "boss"),    # flag 100
    "Mount Ordeals Summit - Scarmiglione Z defeated": LocationData("Mount Ordeals", 0x0CBE12, None, "boss"),  # flag 102
    "Mount Ordeals Entrance - Map completed": LocationData("Mount Ordeals", 0x0CC4FC, "Antidote x5", "carte"),
    "Mount Ordeals Trail - Map completed": LocationData("Mount Ordeals", 0x0CC4FD, "Hi-Potion x3", "carte"),
    "Mount Ordeals Crossing - Map completed": LocationData("Mount Ordeals", 0x0CC4FE, "Ether", "carte"),
    "Mount Ordeals Summit - Map completed": LocationData("Mount Ordeals", 0x0CC4FF, "Red Fang", "carte"),

    # --- Tranche 3 : Baron (retour), Ancient Waterway (d05_xx) -----------------
    "Baron Inn - Yang gives Baron Key": LocationData("Baron (retour)", 0x0CBE1E, "Baron Key", "evenement"),  # flag 114
    "Baron Castle - Baigan defeated": LocationData("Baron (retour)", 0x0CBE21, None, "boss"),               # flag 117
    "Baron Castle - Cagnazzo defeated": LocationData("Baron (retour)", 0x0CBE23, None, "boss"),             # flag 119
    "Baron Castle - Enterprise": LocationData("Baron (retour)", 0x0CBE28, "Enterprise", "evenement"),      # flag 124
    "Ancient Waterway B5 - Coffre 1": LocationData("Ancient Waterway", 0x0CC2FC, "1000 Gil", "coffre"),     # d05_00
    "Ancient Waterway B4 - Coffre 1": LocationData("Ancient Waterway", 0x0CC2FD, "Hi-Potion", "coffre"),    # d05_01
    "Ancient Waterway B4 - Coffre 2": LocationData("Ancient Waterway", 0x0CC2FE, "Ether", "coffre"),
    "Ancient Waterway B4 - Coffre 3": LocationData("Ancient Waterway", 0x0CC2FF, "Zeus's Wrath", "coffre"),
    "Ancient Waterway B3 - Coffre 1": LocationData("Ancient Waterway", 0x0CC300, "Bronze Hourglass", "coffre"),  # d05_02
    "Ancient Waterway B3 - Coffre 2": LocationData("Ancient Waterway", 0x0CC301, "Spider Silk", "coffre"),
    "Ancient Waterway B3 - Coffre 3": LocationData("Ancient Waterway", 0x0CC302, "Hermes Sandals", "coffre"),
    "Ancient Waterway B3 - Tsunami augment": LocationData("Ancient Waterway", 0x0CC3EF, "Tsunami", "coffre"),  # après Cagnazzo
    "Ancient Waterway B2 - Coffre 1": LocationData("Ancient Waterway", 0x0CC303, "Ether", "coffre"),       # d05_03
    "Ancient Waterway B1 - Coffre 1": LocationData("Ancient Waterway", 0x0CC304, "Ancient Sword", "coffre"),  # d05_05
    "Ancient Waterway B4 - Map completed": LocationData("Ancient Waterway", 0x0CC502, "Hi-Potion x3", "carte"),
    "Ancient Waterway B3 - Map completed": LocationData("Ancient Waterway", 0x0CC503, "Ether", "carte"),
    "Ancient Waterway B2 - Map completed": LocationData("Ancient Waterway", 0x0CC504, "Remedy x3", "carte"),

    # --- Tranche 4 : Troia (t10, t11, t22), Lodestone Cavern (d06), Tower of Zot (d07) ---
    "Troia Castle - Edward gives Whisperweed": LocationData("Troia", 0x0CBE2C, "Whisperweed", "evenement"),  # flag 128
    "Lodestone Cavern - Dark Elf defeated": LocationData("Lodestone Cavern", 0x0CBE34, None, "boss"),         # flag 136
    "Lodestone Cavern - Earth Crystal": LocationData("Lodestone Cavern", 0x0CBE35, "Earth Crystal", "evenement"),  # flag 137
    "Tower of Zot - Magus Sisters defeated": LocationData("Tower of Zot", 0x0CBE43, None, "boss"),            # flag 151
    "Baron Castle - Baron liberated": LocationData("Baron (retour)", 0x0CBE26, None, "evenement"),             # flag 122
    "Troia - Coffre 1": LocationData("Troia", 0x0CC207, "1000 Gil", "coffre"),
    "Troia - Coffre 2": LocationData("Troia", 0x0CC208, "Decoy", "coffre"),
    "Troia - Coffre 3": LocationData("Troia", 0x0CC209, "Ether", "coffre"),
    "Troia - Coffre 4": LocationData("Troia", 0x0CC20A, "Dry Ether", "coffre"),
    "Troia Castle B1 West - Coffre 1": LocationData("Troia", 0x0CC211, "Bacchus's Wine", "coffre"),
    "Troia Castle Vault - Coffre 1": LocationData("Troia", 0x0CC212, "Hi-Potion", "coffre"),
    "Troia Castle Vault - Coffre 2": LocationData("Troia", 0x0CC213, "Remedy", "coffre"),
    "Troia Castle Vault - Coffre 3": LocationData("Troia", 0x0CC214, "Ether", "coffre"),
    "Troia Castle Vault - Coffre 4": LocationData("Troia", 0x0CC215, "Dry Ether", "coffre"),
    "Troia Castle Vault - Coffre 5": LocationData("Troia", 0x0CC216, "Elixir", "coffre"),
    "Troia Castle Vault - Coffre 6": LocationData("Troia", 0x0CC217, "Echo Herbs", "coffre"),
    "Troia Castle Vault - Coffre 7": LocationData("Troia", 0x0CC218, "Great Bow", "coffre"),
    "Troia Castle Vault - Coffre 8": LocationData("Troia", 0x0CC219, "Fire Arrows", "coffre"),
    "Troia Castle Vault - Coffre 9": LocationData("Troia", 0x0CC21A, "5000 Gil", "coffre"),
    "Troia Castle Vault - Coffre 10": LocationData("Troia", 0x0CC21B, "Hi-Potion", "coffre"),
    "Troia Castle Vault - Coffre 11": LocationData("Troia", 0x0CC21C, "Remedy", "coffre"),
    "Troia Castle Vault - Coffre 12": LocationData("Troia", 0x0CC21D, "Ether", "coffre"),
    "Troia Castle Vault - Coffre 13": LocationData("Troia", 0x0CC21E, "Dry Ether", "coffre"),
    "Troia Castle Vault - Coffre 14": LocationData("Troia", 0x0CC21F, "Silver Apple", "coffre"),
    "Troia Castle Vault - Coffre 15": LocationData("Troia", 0x0CC220, "Echo Herbs", "coffre"),
    "Troia Castle Vault - Coffre 16": LocationData("Troia", 0x0CC221, "Ice Arrows", "coffre"),
    "Troia Castle Vault - Coffre 17": LocationData("Troia", 0x0CC222, "50000 Gil", "coffre"),
    "Troia Castle Vault - Coffre 18": LocationData("Troia", 0x0CC223, "Lightning Arrows", "coffre"),
    "Troia Castle B1 East - Coffre 1": LocationData("Troia", 0x0CC224, "Tent", "coffre"),
    "Troia Castle B1 East - Coffre 2": LocationData("Troia", 0x0CC225, "Tent", "coffre"),
    "Troia Castle B1 East - Coffre 3": LocationData("Troia", 0x0CC226, "Hi-Potion", "coffre"),
    "Troia Castle B1 East - Coffre 4": LocationData("Troia", 0x0CC227, "Hi-Potion", "coffre"),
    "Troia Castle B1 East - Coffre 5": LocationData("Troia", 0x0CC228, "Ether", "coffre"),
    "Troia Castle B1 East - Coffre 6": LocationData("Troia", 0x0CC229, "Ether", "coffre"),
    "Troia Castle B1 East - Coffre 7": LocationData("Troia", 0x0CC22A, "Ruby Ring", "coffre"),
    "Troia Castle B1 East - Coffre 8": LocationData("Troia", 0x0CC22B, "Ruby Ring", "coffre"),
    "Troia - Coffre 5": LocationData("Troia", 0x0CC243, "Phoenix Down", "coffre"),
    "Troia - Coffre 6": LocationData("Troia", 0x0CC244, "Hi-Potion", "coffre"),
    "Troia - Coffre 7": LocationData("Troia", 0x0CC245, "Hi-Potion", "coffre"),
    "Troia - Coffre 8": LocationData("Troia", 0x0CC246, "Tent", "coffre"),
    "Chocobo Village - Coffre 1": LocationData("Troia", 0x0CC266, "Gysahl Greens", "coffre"),
    "Chocobo Village - Coffre 2": LocationData("Troia", 0x0CC267, "Gysahl Greens", "coffre"),
    "Chocobo Village - Coffre 3": LocationData("Troia", 0x0CC268, "Gysahl Greens", "coffre"),
    "Lodestone Cavern B1 - Coffre 1": LocationData("Lodestone Cavern", 0x0CC306, "Hi-Potion", "coffre"),
    "Lodestone Cavern B1 - Coffre 2": LocationData("Lodestone Cavern", 0x0CC307, "Unicorn Horn", "coffre"),
    "Lodestone Cavern B2 - Coffre 1": LocationData("Lodestone Cavern", 0x0CC308, "Ether", "coffre"),
    "Lodestone Cavern B2 Room - Coffre 1": LocationData("Lodestone Cavern", 0x0CC309, "2000 Gil", "coffre"),
    "Lodestone Cavern B2 Room - Coffre 2": LocationData("Lodestone Cavern", 0x0CC30A, "Ether", "coffre"),
    "Lodestone Cavern B3 Room - Coffre 1": LocationData("Lodestone Cavern", 0x0CC30B, "Hi-Potion", "coffre"),
    "Lodestone Cavern B3 Room - Coffre 2": LocationData("Lodestone Cavern", 0x0CC30C, "Spider Silk", "coffre"),
    "Lodestone Cavern B3 Room - Coffre 3": LocationData("Lodestone Cavern", 0x0CC30D, "Bronze Hourglass", "coffre"),
    "Lodestone Cavern B4 Room - Coffre 1": LocationData("Lodestone Cavern", 0x0CC30E, "Faerie Claws", "coffre"),
    "Lodestone Cavern B4 - Coffre 1": LocationData("Lodestone Cavern", 0x0CC30F, "Emergency Exit", "coffre"),
    "Tower of Zot 1F - Coffre 1": LocationData("Tower of Zot", 0x0CC315, "Flame Mail", "coffre"),
    "Tower of Zot 2F - Coffre 1": LocationData("Tower of Zot", 0x0CC316, "Flame Sword", "coffre"),
    "Tower of Zot 5F - Coffre 1": LocationData("Tower of Zot", 0x0CC317, "Hell Claws", "coffre"),
    "Tower of Zot 5F - Coffre 2": LocationData("Tower of Zot", 0x0CC318, "Gaia Hammer", "coffre"),
    "Tower of Zot 5F - Coffre 3": LocationData("Tower of Zot", 0x0CC319, "Sage's Surplice", "coffre"),
    "Tower of Zot 5F - Coffre 4": LocationData("Tower of Zot", 0x0CC31A, "Flame Shield", "coffre"),
    "Lodestone Cavern - Whirlwind augment": LocationData("Lodestone Cavern", 0x0CC3F0, "Whirlwind", "coffre"),
    "Lodestone Cavern B1 - Map completed": LocationData("Lodestone Cavern", 0x0CC507, "Ether", "carte"),
    "Lodestone Cavern B2 - Map completed": LocationData("Lodestone Cavern", 0x0CC508, "Vampire Fang x3", "carte"),
    "Lodestone Cavern B3 - Map completed": LocationData("Lodestone Cavern", 0x0CC50A, "Silent Bell x3", "carte"),
    "Lodestone Cavern B4 - Map completed": LocationData("Lodestone Cavern", 0x0CC50E, "Dry Ether", "carte"),
    "Tower of Zot 1F - Map completed": LocationData("Tower of Zot", 0x0CC511, "Zeus's Wrath x5", "carte"),
    "Tower of Zot 2F - Map completed": LocationData("Tower of Zot", 0x0CC512, "Heavenly Wrath x3", "carte"),
    "Tower of Zot 3F - Map completed": LocationData("Tower of Zot", 0x0CC513, "Blue Fang", "carte"),
    "Tower of Zot 4F - Map completed": LocationData("Tower of Zot", 0x0CC514, "Elixir", "carte"),
    "Tower of Zot 5F - Map completed": LocationData("Tower of Zot", 0x0CC516, "Bronze Hourglass x3", "carte"),

    # --- Tranche 5 : Magma Stone (Baron, après Valvalis), Agart (t07) ---------------
    "Baron Castle - Kain gives Magma Stone": LocationData("Tower of Zot", 0x0CBE4C, "Magma Stone", "evenement"),  # flag 160, chambre de Cecil après Valvalis
    "Agart - Coffre 1": LocationData("Agart", 0x0CC1E4, "Antarctic Wind", "coffre"),
    "Agart - Coffre 2": LocationData("Agart", 0x0CC1E5, "Potion", "coffre"),
    "Agart - Coffre 3": LocationData("Agart", 0x0CC26A, "Hi-Potion", "coffre"),
    "Agart - Coffre 4": LocationData("Agart", 0x0CC26B, "Gaia Drum", "coffre"),
    "Agart - Coffre 5": LocationData("Agart", 0x0CC26C, "Phoenix Down", "coffre"),
    "Agart - Coffre 6": LocationData("Agart", 0x0CC26D, "Phoenix Down", "coffre"),
    "Agart - Coffre 7": LocationData("Agart", 0x0CC26E, "Cottage", "coffre"),
    "Tower of Zot - Valvalis defeated": LocationData("Tower of Zot", 0x0CBE49, None, "boss"),             # flag 157
    # Monde souterrain : château des nains (t12)
    "Dwarf Castle - Calbrena defeated": LocationData("Dwarf Castle", 0x0CBE5D, None, "boss"),             # flag 177
    "Dwarf Castle - Giott gives Draw Attacks": LocationData("Dwarf Castle", 0x0CBE5E, "Draw Attacks", "evenement"),  # flag 178, après Golbez
    "Dwarf Castle - Coffre 1": LocationData("Dwarf Castle", 0x0CC22F, "Dwarven Axe", "coffre"),          # t12_04
    "Dwarf Castle - Coffre 2": LocationData("Dwarf Castle", 0x0CC230, "Bacchus's Wine", "coffre"),       # t12_05
    "Dwarf Castle - Coffre 3": LocationData("Dwarf Castle", 0x0CC231, "Ether", "coffre"),                # t12_06
    "Dwarf Castle - Coffre 4": LocationData("Dwarf Castle", 0x0CC232, "Silver Hourglass", "coffre"),
    "Dwarf Castle - Coffre 5": LocationData("Dwarf Castle", 0x0CC233, "Power Armlet", "coffre"),
    "Dwarf Castle - Coffre 6": LocationData("Dwarf Castle", 0x0CC234, "Elixir", "coffre"),
    "Dwarf Castle - Coffre 7": LocationData("Dwarf Castle", 0x0CC235, "Bacchus's Wine", "coffre"),       # t12_08
    "Dwarf Castle - Coffre 8": LocationData("Dwarf Castle", 0x0CC236, "Elixir", "coffre"),               # t12_09
    "Dwarf Castle - Coffre 9": LocationData("Dwarf Castle", 0x0CC237, "Ether", "coffre"),
    "Dwarf Castle - Coffre 10": LocationData("Dwarf Castle", 0x0CC238, "Hi-Potion", "coffre"),
    "Dwarf Castle - Coffre 11": LocationData("Dwarf Castle", 0x0CC239, "Black Belt Gi", "coffre"),
    "Dwarf Castle - Coffre 12": LocationData("Dwarf Castle", 0x0CC23A, "Cottage", "coffre"),             # t12_12
    "Dwarf Castle - Coffre 13": LocationData("Dwarf Castle", 0x0CC23B, "Cottage", "coffre"),
    "Dwarf Castle - Coffre 14": LocationData("Dwarf Castle", 0x0CC23C, "Cottage", "coffre"),
    "Dwarf Castle - Coffre 15": LocationData("Dwarf Castle", 0x0CC23D, "Gysahl Greens", "coffre"),       # t12_13
    "Dwarf Castle - Coffre 16": LocationData("Dwarf Castle", 0x0CC23E, "Gysahl Greens", "coffre"),
    "Dwarf Castle - Coffre 17": LocationData("Dwarf Castle", 0x0CC23F, "Gysahl Greens", "coffre"),
    "Dwarf Castle - Coffre 18": LocationData("Dwarf Castle", 0x0CC241, "5000 Gil", "coffre"),            # t12_30
    "Underworld - Tank base chest": LocationData("Underworld", 0x0CC24F, "Bomb Fragment", "coffre"),     # t12_10
    # Tranche 6 : tour de Babil, partie souterraine (d08_00 à d08_14)
    "Tower of Babil B13 - Coffre 1": LocationData("Tower of Babil", 0x0CC31F, "Emergency Exit", "coffre"),  # d08_00
    "Tower of Babil B13 - Coffre 2": LocationData("Tower of Babil", 0x0CC320, "Hi-Potion", "coffre"),
    "Tower of Babil B13 - Coffre 3": LocationData("Tower of Babil", 0x0CC321, "Ether", "coffre"),
    "Tower of Babil B12 - Coffre 1": LocationData("Tower of Babil", 0x0CC322, "Green Beret", "coffre"),     # d08_01
    "Tower of Babil B11 - Coffre 1": LocationData("Tower of Babil", 0x0CC323, "Cat Claws", "coffre"),       # d08_02
    "Tower of Babil B11 - Coffre 2": LocationData("Tower of Babil", 0x0CC324, "Hi-Potion", "coffre"),
    "Tower of Babil B11 - Coffre 3": LocationData("Tower of Babil", 0x0CC325, "Phoenix Down", "coffre"),
    "Tower of Babil Lower - Coffre 1": LocationData("Tower of Babil", 0x0CC326, "Icebrand", "coffre"),      # d08_03
    "Tower of Babil Lower - Coffre 2": LocationData("Tower of Babil", 0x0CC327, "Ice Lance", "coffre"),     # d08_04
    "Tower of Babil B10 - Coffre 1": LocationData("Tower of Babil", 0x0CC328, "Killer Bow", "coffre"),      # d08_05
    "Tower of Babil B10 - Coffre 2": LocationData("Tower of Babil", 0x0CC329, "Antarctic Wind", "coffre"),
    "Tower of Babil Lower - Coffre 3": LocationData("Tower of Babil", 0x0CC32A, "Ice Shield", "coffre"),    # d08_06
    "Tower of Babil Lower - Coffre 4": LocationData("Tower of Babil", 0x0CC32B, "Ice Armor", "coffre"),     # d08_08
    "Tower of Babil B9 - Coffre 1": LocationData("Tower of Babil", 0x0CC32C, "Arctic Wind", "coffre"),      # d08_10
    "Tower of Babil B9 - Coffre 2": LocationData("Tower of Babil", 0x0CC32D, "Hi-Potion", "coffre"),
    # B8 et B7 (d08_11, d08_12) : traversés après le piège de Golbez (chute en d08_14 -> hangar).
    "Tower of Babil B8 - Coffre 1": LocationData("Tower of Babil (upper)", 0x0CC32E, "Hi-Potion", "coffre"),        # d08_11
    "Tower of Babil B7 - Coffre 1": LocationData("Tower of Babil (upper)", 0x0CC32F, "Dry Ether", "coffre"),        # d08_12
    "Tower of Babil B13 - Map completed": LocationData("Tower of Babil", 0x0CC519, "Antarctic Wind x5", "carte"),
    "Tower of Babil B12 - Map completed": LocationData("Tower of Babil", 0x0CC51A, "Arctic Wind x3", "carte"),
    "Tower of Babil B11 - Map completed": LocationData("Tower of Babil", 0x0CC51B, "White Fang", "carte"),
    "Tower of Babil B10 - Map completed": LocationData("Tower of Babil", 0x0CC51E, "Hi-Potion x5", "carte"),
    "Tower of Babil B9 - Map completed": LocationData("Tower of Babil", 0x0CC523, "Remedy x5", "carte"),
    "Tower of Babil B8 - Map completed": LocationData("Tower of Babil (upper)", 0x0CC525, "Ether x2", "carte"),
    "Tower of Babil B7 - Map completed": LocationData("Tower of Babil (upper)", 0x0CC526, "Elixir", "carte"),
    "Tower of Babil - Dr. Lugae defeated": LocationData("Tower of Babil", 0x0CBE67, None, "boss"),          # flag 187
    "Tower of Babil - Tower Key": LocationData("Tower of Babil", 0x0CBE68, "Tower Key", "evenement"),       # flag 188
    "Tower of Babil - Cannons destroyed": LocationData("Tower of Babil", 0x0CBE6A, None, "evenement"),     # flag 190
    # Ingénieur du château de Baron après les canons (flag 202) : 2e Enterprise = Enterprise avec crochet.
    "Baron Castle - Enterprise hook": LocationData("Tower of Babil", 0x0CBE76, "Enterprise", "evenement"),
    # Grotte d'Eblan (d09)
    "Cave of Eblan B1 - Coffre 1": LocationData("Cave of Eblan", 0x0CC33D, "Shuriken", "coffre"),          # d09_00
    "Cave of Eblan B1 - Coffre 2": LocationData("Cave of Eblan", 0x0CC33E, "Remedy", "coffre"),
    "Cave of Eblan B1 - Coffre 3": LocationData("Cave of Eblan", 0x0CC33F, "Vampire Fang", "coffre"),
    "Cave of Eblan B2 - Coffre 1": LocationData("Cave of Eblan", 0x0CC340, "Potion", "coffre"),            # d09_02
    "Cave of Eblan B2 - Coffre 2": LocationData("Cave of Eblan", 0x0CC341, "Potion", "coffre"),
    "Cave of Eblan First Passage - Coffre 1": LocationData("Cave of Eblan", 0x0CC342, "Ether", "coffre"),  # d09_04
    "Cave of Eblan First Passage - Coffre 2": LocationData("Cave of Eblan", 0x0CC343, "Tent", "coffre"),
    "Cave of Eblan First Passage - Coffre 3": LocationData("Cave of Eblan", 0x0CC344, "Hi-Potion", "coffre"),
    "Cave of Eblan First Passage - Coffre 4": LocationData("Cave of Eblan", 0x0CC345, "Hi-Potion", "coffre"),
    "Cave of Eblan First Passage - Coffre 5": LocationData("Cave of Eblan", 0x0CC346, "Cottage", "coffre"),
    "Cave of Eblan First Passage - Coffre 6": LocationData("Cave of Eblan", 0x0CC347, "Hi-Potion", "coffre"),
    "Cave of Eblan First Passage - Coffre 7": LocationData("Cave of Eblan", 0x0CC348, "Spider Silk", "coffre"),
    "Cave of Eblan First Passage - Coffre 8": LocationData("Cave of Eblan", 0x0CC349, "Elixir", "coffre"),
    "Cave of Eblan First Passage - Coffre 9": LocationData("Cave of Eblan", 0x0CC34A, "Elixir", "coffre"),
    "Cave of Eblan First Passage - Coffre 10": LocationData("Cave of Eblan", 0x0CC34B, "Silver Hourglass", "coffre"),
    "Cave of Eblan First Passage - Coffre 11": LocationData("Cave of Eblan", 0x0CC34C, "Phoenix Down", "coffre"),
    "Cave of Eblan First Passage - Coffre 12": LocationData("Cave of Eblan", 0x0CC34D, "Phoenix Down", "coffre"),
    "Cave of Eblan Second Passage - Coffre 1": LocationData("Cave of Eblan", 0x0CC34E, "Bomb Core", "coffre"),  # d09_05
    "Cave of Eblan Second Passage - Coffre 2": LocationData("Cave of Eblan", 0x0CC34F, "Shuriken", "coffre"),
    "Cave of Eblan Second Passage - Coffre 3": LocationData("Cave of Eblan", 0x0CC350, "Gold Needle", "coffre"),
    "Cave of Eblan Second Passage - Coffre 4": LocationData("Cave of Eblan", 0x0CC351, "Dry Ether", "coffre"),
    "Cave of Eblan - Coffre 1": LocationData("Cave of Eblan", 0x0CC352, "Blood Sword", "coffre"),          # d09_06
    "Cave of Eblan - Coffre 2": LocationData("Cave of Eblan", 0x0CC353, "Ninja Sutra", "coffre"),          # d09_30
    "Cave of Eblan Second Passage - Inferno augment": LocationData("Tower of Babil (upper)", 0x0CC3F1, "Inferno", "coffre"),  # après Rubicante
    "Cave of Eblan B1 - Map completed": LocationData("Cave of Eblan", 0x0CC530, "Bacchus's Wine x3", "carte"),
    "Cave of Eblan First Passage - Map completed": LocationData("Cave of Eblan", 0x0CC534, "Hermes Sandals x3", "carte"),
    "Cave of Eblan Second Passage - Map completed": LocationData("Cave of Eblan", 0x0CC535, "Decoy x3", "carte"),
    "Cave of Eblan - Edge joins": LocationData("Cave of Eblan", 0x0CBE7A, None, "evenement"),              # flag 206
    # Tour de Babil, partie haute (d08_15 à d08_20)
    "Tower of Babil B1 - Coffre 1": LocationData("Tower of Babil (upper)", 0x0CC333, "Unicorn Horn", "coffre"),   # d08_15
    "Tower of Babil B1 - Coffre 2": LocationData("Tower of Babil (upper)", 0x0CC334, "Silver Hourglass", "coffre"),
    "Tower of Babil B2 - Coffre 1": LocationData("Tower of Babil (upper)", 0x0CC335, "Ogrekiller", "coffre"),     # d08_16
    "Tower of Babil B3 - Coffre 1": LocationData("Tower of Babil (upper)", 0x0CC336, "Lilith's Kiss", "coffre"),  # d08_17
    "Tower of Babil B4 - Coffre 1": LocationData("Tower of Babil (upper)", 0x0CC337, "Ashura", "coffre"),         # d08_19
    "Tower of Babil B5 - Coffre 1": LocationData("Tower of Babil (upper)", 0x0CC338, "10000 Gil", "coffre"),      # d08_20
    "Tower of Babil B1 - Map completed": LocationData("Tower of Babil (upper)", 0x0CC529, "Bomb Fragment x5", "carte"),
    "Tower of Babil B2 - Map completed": LocationData("Tower of Babil (upper)", 0x0CC52A, "Bomb Crank x3", "carte"),
    "Tower of Babil B3 - Map completed": LocationData("Tower of Babil (upper)", 0x0CC52B, "Red Fang", "carte"),
    "Tower of Babil B4 - Map completed": LocationData("Tower of Babil (upper)", 0x0CC52D, "X-Potion x3", "carte"),
    "Tower of Babil B5 - Map completed": LocationData("Tower of Babil (upper)", 0x0CC52E, "Elixir", "carte"),
    "Tower of Babil - Edge's parents defeated": LocationData("Tower of Babil (upper)", 0x0CBE7F, None, "boss"),   # flag 211 (après le combat)
    "Tower of Babil - Rubicante defeated": LocationData("Tower of Babil (upper)", 0x0CBE81, None, "boss"),        # flag 213
    "Tower of Babil - Falcon": LocationData("Tower of Babil (upper)", 0x0CBE85, "Falcon", "evenement"),          # flag 217 (chute)
    # Cid à l'infirmerie (t12_11) : traversée de la lave (2e Faucon) et l'augment Adrenaline.
    "Dwarf Castle - Cid upgrades the Falcon": LocationData("Dwarf Castle (Cid)", 0x0CBE8A, "Falcon", "evenement"),  # flag 222
    "Dwarf Castle - Cid's Adrenaline augment": LocationData("Dwarf Castle (Cid)", 0x0CBE89, "Adrenaline", "evenement"),  # flag 221
    # Giott après la chute (t12_02) : Luca donne son collier.
    "Dwarf Castle - Luca's Necklace": LocationData("Dwarf Castle (Cid)", 0x0CBE88, "Luca's Necklace", "evenement"),  # flag 220

    # --- Ancien objectif de la tranche 1, devenu une location ------------------
    "Rosa soignee": LocationData("Kaipo (retour)", 0x0CBDDD, None, "evenement"),                  # flag 49
    # --- Ancien objectif de la tranche 2 -----------------------------------------
    "Mount Ordeals - Cecil becomes Paladin": LocationData("Mount Ordeals", 0x0CBE17, None, "evenement"),  # flag 107


}

# Objectif : Cid a amélioré le Faucon (flag 222, infirmerie du château des nains), dans la région GOAL_REGION.
GOAL_FLAG = 0x0CBE8A
GOAL_REGION = "Dwarf Castle (Cid)"

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
