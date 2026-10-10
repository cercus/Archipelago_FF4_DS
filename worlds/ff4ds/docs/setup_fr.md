# Final Fantasy IV DS : guide d'installation

## Prérequis

- La ROM US de Final Fantasy IV DS (`Final Fantasy IV (USA) (En,Fr,Es).nds`), obtenue légalement.
- BizHawk, avec le cœur melonDS.
- Archipelago, avec ce monde installé (`worlds/ff4ds` ou `ff4ds.apworld`).

## Générer et héberger une partie

1. Place ton fichier YAML dans le dossier `Players`.
2. Lance `python Generate.py` : un `.zip` apparaît dans `output`.
3. Héberge la partie en local avec `python MultiServer.py output/AP_xxxx.zip`
   (le serveur écoute sur `localhost:38281`), ou envoie le `.zip` sur archipelago.gg.

## Jouer

1. Ouvre la ROM dans BizHawk.
2. Lance le client : `python Launcher.py`, puis **BizHawk Client**.
3. Dans BizHawk : *Tools > Lua Console > Script > Open Script*, puis choisis
   `data/lua/connector_bizhawk_generic.lua` dans le dossier d'Archipelago.
4. Dans le client, connecte-toi au serveur (`localhost:38281`) avec le nom du joueur du YAML.
5. Commence une nouvelle partie ou charge ta sauvegarde.

## Fonctionnement

- Ouvrir un coffre (ou vaincre un boss, compléter une carte…) envoie un check.
  L'objet d'origine s'affiche, puis le client le retire de l'inventaire.
- Les objets reçus arrivent hors combat et hors cinématique.
- La partie est gagnée quand Rosa est soignée à Kaipo.

## Limites connues

- Le message du coffre affiche l'objet d'origine, pas l'objet Archipelago.
- Si le client n'est pas connecté au moment où tu ouvres un coffre, le check est envoyé
  plus tard, mais l'objet d'origine n'est pas retiré.
