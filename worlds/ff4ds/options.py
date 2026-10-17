"""Options proposées au joueur dans son fichier YAML."""
from dataclasses import dataclass

from Options import Choice, DefaultOnToggle, OptionSet, PerGameCommonOptions

from .rom.characters import CHARACTERS


class NamingwayLocations(DefaultOnToggle):
    """
    Ajoute les étapes de la quête de Namingway comme locations.
    """
    display_name = "Locations de Namingway"


class SpellItems(DefaultOnToggle):
    """
    Les sorts blancs et noirs ne s'apprennent plus en montant de niveau : ce sont des objets
    Archipelago. Recevoir un sort l'apprend à tous les personnages qui l'apprennent normalement.
    Les familles (Cure, Fire, Blizzard, Thunder) sont progressives.
    Tranche 1 : les sorts de Rydia (enfant).
    """
    display_name = "Sorts en objets"


class StartingSpells(DefaultOnToggle):
    """
    Avec les sorts en objets : les personnages gardent leurs sorts de départ (niveau 1).
    Désactivé : ces sorts deviennent aussi des objets (Rydia commence sans Cure ni Blizzard).
    """
    display_name = "Sorts de départ"


class CharacterShuffle(DefaultOnToggle):
    """
    Chaque personnage qui rejoint l'équipe est tiré au sort (Cecil reste le chef d'équipe).
    Il arrive au niveau prévu pour cet endroit, avec son propre équipement.
    Tranche 1 : départ (Kain), Kaipo (Rydia), Rivière souterraine (Tellah), Damcyan (Edward),
    objectif (Rosa). Un personnage n'apparaît qu'une fois.
    """
    display_name = "Personnages aléatoires"


class AllowedCharacters(OptionSet):
    """Personnages qui peuvent être tirés au sort. Un emplacement sans personnage reste vide."""
    display_name = "Personnages autorisés"
    valid_keys = list(CHARACTERS)
    default = frozenset(CHARACTERS)


class RestrictedCharacters(OptionSet):
    """Personnages placés en dernier recours (tous les emplacements de la tranche 1 sont au début
    du jeu) : ils n'apparaissent que s'il n'y a pas assez d'autres personnages autorisés."""
    display_name = "Personnages restreints"
    valid_keys = list(CHARACTERS)
    default = frozenset({"Edge", "FuSoYa"})


class CharacterDepartures(Choice):
    """
    never : personne ne quitte l'équipe (comme Free Enterprise). L'équipe est limitée à 5 :
            une fois pleine, les emplacements suivants restent vides.
    vanilla : les personnages des emplacements de Kain et de Tellah partent comme dans l'histoire
              (village de la Brume, Damcyan) en rendant leur équipement.
    """
    display_name = "Départs de personnages"
    option_never = 0
    option_vanilla = 1
    default = 0


class ShopRandomization(Choice):
    """
    vanilla : magasins d'origine.
    shuffle : les objets d'origine sont mélangés entre les magasins (une arme reste une arme…).
    standard : chaque case reçoit un objet du même type et d'un prix proche de l'objet d'origine
               (les magasins du début restent bon marché).
    wild : n'importe quel objet achetable dans n'importe quelle case.
    En standard et wild, les Potions et Phoenix Downs restent en vente là où ils l'étaient.
    """
    display_name = "Magasins aléatoires"
    option_vanilla = 0
    option_shuffle = 1
    option_standard = 2
    option_wild = 3
    default = 2


class ShopPartyEquipment(DefaultOnToggle):
    """
    Modes standard et wild : les armes et armures que l'équipe tirée (Cecil compris) peut porter
    sont choisies en priorité.
    """
    display_name = "Équipement adapté à l'équipe"


@dataclass
class FF4DSOptions(PerGameCommonOptions):
    namingway_locations: NamingwayLocations
    spell_items: SpellItems
    starting_spells: StartingSpells
    character_shuffle: CharacterShuffle
    allowed_characters: AllowedCharacters
    restricted_characters: RestrictedCharacters
    character_departures: CharacterDepartures
    shop_randomization: ShopRandomization
    shop_party_equipment: ShopPartyEquipment
