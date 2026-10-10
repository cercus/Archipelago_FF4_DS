# Point d'entrée du monde : Archipelago importe ce fichier et y trouve la classe du monde.
from .world import FF4DSWorld as FF4DSWorld

# Importer le client suffit à l'enregistrer auprès du BizHawk Client.
from .client import FF4DSClient as FF4DSClient
