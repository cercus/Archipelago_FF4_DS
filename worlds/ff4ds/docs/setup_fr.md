# Final Fantasy IV DS : guide d'installation

## Prérequis

- La ROM US de Final Fantasy IV DS (`Final Fantasy IV (USA) (En,Fr,Es).nds`), obtenue légalement.
- BizHawk, avec le cœur melonDS.
- Archipelago 0.6.7 ou plus, avec ce monde installé (`ff4ds.apworld` dans `custom_worlds`).

## Générer et héberger une partie

1. Place ton fichier YAML dans le dossier `Players`.
2. Lance la génération (`Generate` dans le Launcher, ou `python Generate.py`) : un `.zip` apparaît
   dans `output`. Il contient un fichier `.apff4ds` par joueur de Final Fantasy IV DS.
3. Héberge la partie : envoie le `.zip` sur archipelago.gg, ou lance `MultiServer` en local
   (le serveur écoute sur `localhost:38281`).

La génération n'a pas besoin de la ROM.

## Jouer

1. Dans le Launcher, choisis **Open Patch** et sélectionne ton fichier `.apff4ds`.
   - La première fois, le Launcher demande la ROM d'origine (elle n'est jamais modifiée).
   - Il crée à côté du `.apff4ds` une ROM `.nds` patchée (cinématiques sautées, départ devant
     le château de Baron), puis ouvre le BizHawk Client.
2. Ouvre la ROM **patchée** dans BizHawk (ou laisse le client la lancer, si
   `bizhawkclient_options` > `rom_start` est réglé dans `host.yaml`).
3. Dans BizHawk : *Tools > Lua Console > Script > Open Script*, puis choisis
   `data/lua/connector_bizhawk_generic.lua` dans le dossier d'Archipelago.
4. Dans le client, connecte-toi au serveur avec le nom du joueur du YAML.
5. Commence une nouvelle partie.

## Fonctionnement

- Ouvrir un coffre (ou vaincre un boss, compléter une carte…) envoie un check.
  Le coffre affiche l'objet Archipelago ; si c'est un objet d'un autre jeu, un objet
  « porteur » renommé s'affiche puis est retiré.
- Les objets reçus arrivent hors combat et hors cinématique.
- La partie est gagnée quand Rosa est soignée à Kaipo (parler à Rosa et utiliser la Sand Pearl).

## Limites connues

- Les sauvegardes rapides (savestates) d'une ancienne version de la ROM patchée peuvent donner
  un écran noir : utilise les sauvegardes du jeu quand tu changes de version.
- Si le client n'est pas connecté au moment où tu ouvres un coffre, le check est envoyé
  plus tard, mais l'objet d'origine n'est pas retiré.
- Les combats sautés (gardes de Kaipo, Sahagin) ne sont pas encore inscrits au bestiaire.
