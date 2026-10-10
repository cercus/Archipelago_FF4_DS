"""Options proposées au joueur dans son fichier YAML."""
from dataclasses import dataclass

from Options import DefaultOnToggle, PerGameCommonOptions


class NamingwayLocations(DefaultOnToggle):
    """
    Ajoute les étapes de la quête de Namingway comme locations.
    """
    display_name = "Locations de Namingway"


@dataclass
class FF4DSOptions(PerGameCommonOptions):
    namingway_locations: NamingwayLocations
