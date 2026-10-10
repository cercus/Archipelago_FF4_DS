# Final Fantasy IV DS (US) — Carte mémoire et recettes

Référence technique du monde Archipelago `ff4ds`. Tout ce qui est marqué **vérifié** a été testé en jeu ;
le reste est indiqué comme hypothèse.

## 1. Conventions

- **ROM** : `Final Fantasy IV (USA) (En,Fr,Es).nds`, code jeu `YF4E` (en-tête recopié en RAM à `0x3FFE00`, code à `+0x0C`).
- **Adresses** : décalages dans le domaine BizHawk `Main RAM` (4 Mo). Une adresse DS `0x02xxxxxx` correspond à `Main RAM` `0x0xxxxxx` (retirer `0x02000000`).
- **Version EU** (`Final Fantasy IV (Europe) (En,Fr,De,Es,It)`) : adresse EU = adresse US + `0x1E0` pour le bloc de sauvegarde et les flags (vérifié sur l'or, l'inventaire et les coffres).
- **Nombres** : little endian. Coordonnées en virgule fixe 20.12 (`0x1000` = 1,0).

## 2. Bloc de sauvegarde en RAM

| Élément | Adresse | Format | Statut |
|---|---|---|---|
| Étiquette `PRTY` (présente seulement en jeu) | `0x0D7A78` | 4 octets ASCII | vérifié |
| Inventaire | `0x0D7A80` | 384 slots × 4 octets : ID (2), quantité (1), 0 (1) | vérifié |
| Compteur de slots d'inventaire | `0x0D8080` | 4 octets | vérifié |
| Objets clés (+ augments) | `0x0D8084` | 128 slots, même format | vérifié |
| Compteur d'objets clés | `0x0D8284` | 4 octets | vérifié |
| Or | `0x0D8288` | 4 octets | vérifié |
| Compteur d'objets AP reçus (client) | `0x0D807C` | 2 octets, dernier slot d'inventaire (383) | hypothèse : persistance à vérifier |

### Règles de l'inventaire (vérifiées)

- **Ajout** : empiler si l'ID est déjà présent avec une quantité > 0 (max 99) ; sinon réutiliser le premier slot à quantité 0 ; sinon écrire au slot `compteur` et incrémenter le compteur.
- Un objet épuisé **garde son slot** (quantité 0), même après le tri.
- Le menu n'affiche que les slots `< compteur`. Écrire au-delà sans incrémenter le compteur n'a aucun effet.
- **Objets clés** : un objet consommé disparaît (compteur décrémenté). Quantité 0 avec compteur inchangé = affiché « … 0 ».
- Un ID invalide dans un slot affiché fait planter le menu (ex. `0x13A7`, `0x232B`).

## 3. Identifiants d'objets

Identiques en US et EU. Liste complète : `ff4ds_item_ids.csv` (issue des codes Action Replay, vérifiée partiellement).

| Plage | Contenu |
|---|---|
| `0x1389`–`0x13A6` | Consommables (Potion → Lustful Lali-Ho) |
| `0x13AB`–`0x13C6` | Objets de combat |
| `0x1771`–`0x1CEA` | Armes, par centaine : épées 6000, lances 6100, dagues 6200, harpes 6300, griffes 6400, marteaux 6500, haches 6600, katanas 6700, baguettes 6800, bâtons 6900, arcs 7000, flèches 7100, fouets 7200… |
| `0x1F41`–`0x2081` | Boucliers 8000, casques 8100, armures 8200, bras 8300 |
| `0x2329`–`0x2337` | Objets clés (Baron Key `0x2330`, Magma Stone `0x2334`, Sand Pearl `0x232C`, Carnelian Signet `0x2333`…) |
| `0x2390`–`0x23CE` | Augments (Auto-Potion `0x23B0`, Item Lore `0x23B2`…), rangés dans les objets clés |
| `0x23CF`–`0x23D5` | Queues |

## 4. Flags

Zone des flags : **un octet par flag** (0/1).

**Formule générale (lue dans le code du jeu, vérifiée sur tous les flags connus)** :
adresse = `0x0CBDAC` + banque × 1000 + numéro (la banque 10 est traitée comme la banque 2).

| Banque | Plage | Contenu |
|---|---|---|
| 0 | `0x0CBDAC`–`0x0CC193` | Histoire, véhicules, Namingway… (Dragon des Brumes = 23, Rosa soignée = 49) |
| 1 | `0x0CC194`–`0x0CC57B` | Coffres (numéro = celui du script), cartes complétées |
| 2 | `0x0CC57C`–… | Mémoire de travail des scripts (`0x0CC57C` = événement en cours) |

### Coffres et objets cachés

- **Formule (vérifiée)** : flag = `0x0CC194` + numéro stocké dans l'objet coffre (`+0x48`).
- Les coffres d'une même carte ont des numéros consécutifs.

### Événements (scène terminée)

| Adresse | Événement |
|---|---|
| `0x0CBDB6` | Le roi remet la Carnelian Signet |
| `0x0CBDB9`–`0x0CBDBE` | Château de Baron : Rosa, Cid, la dame, la chambre, sortie |
| `0x0CBDC2` / `0x0CBDC3` | Dragon des Brumes : apparition / vaincu |
| `0x0CBDC9`, `0x0CBDCB` | Nommage de Whyt |
| `0x0CBDCA` | Rosa donne l'augment Auto-Potion |
| `0x0CBDD1` | Octomammoth vaincu |
| `0x0CBDD5`–`0x0CBDD7` | Damcyan |
| `0x0CBDD8` | Scène de l'hovercraft |
| `0x0CBDD9` / `0x0CBDDA` / `0x0CBDDB` | Antre de l'Antlion : entrée / début du combat / Antlion vaincu + Sand Pearl |
| `0x0CBDDD` | **Rosa soignée (objectif de la tranche 1)** |
| `0x0CBDDE` / `0x0CBDDF` | Combat d'Edward contre le Sahagin |
| `0x0CBF76` | Edward donne l'augment Item Lore |
| `0x0CBFA2`, `0x0CBFB2` | Kaipo (rôle exact à préciser) |
| `0x0CC008`–`0x0CC016`, `0x0CC01A`… | Chaîne de scénario (étapes globales) |

Activer le flag d'une scène **avant** qu'elle se joue la saute (vérifié sur la tente de Tellah). Remettre un flag à 0 peut la rejouer (vérifié sur l'hovercraft).

### Autres tables

| Adresse | Contenu |
|---|---|
| `0x0CC145`–`0x0CC147` et `0x0CC159`–`0x0CC15B` | Quête de Namingway (deux tables parallèles, écart `0x14`) |
| `0x0CC130` | **Hovercraft disponible** (vérifié) |
| `0x0CC131` | **Enterprise disponible** (vérifié) |
| `0x0CC132`, `0x0CC133`… | Falcon, Baleine Lunaire ? (hypothèse) |
| `0x0CC453`… et `0x0CC4E9`… | Cartes complétées : deux tables parallèles (écart `0x96`), une entrée par carte |
| `0x0CC57C` | **Événement en cours** (1 pendant un dialogue ou une cinématique) |
| `0x0CB93C`–`0x0CB957`, `0x0CCE0C`–`0x0CCE3F`, `0x0CBBFC` | Mémoire de travail (à ignorer) |

## 5. Objets de la carte courante

| Adresse | Contenu |
|---|---|
| `0x0CF460` | Pointeur vers le premier objet de la carte (le joueur) |
| `0x0CF464` | Nom de la carte en texte (`d00_00` Grotte de la Brume, `d01_04` Underground Waterway B3, `f00_00` carte du monde…) |
| `0x0CF6A4` | Objet avec lequel le joueur interagit (remis à 0 après interaction) |
| `0x1388D8` / `0x1388DC` / `0x1388E0` | Dernier objet / premier objet / nombre d'objets |

Liste chaînée, structure d'un objet :

| Décalage | Contenu |
|---|---|
| `+0x00` | Type (adresse de la table de méthodes) |
| `+0x04` | Objet suivant (0 = fin) |
| `+0x08` | Objet précédent |
| `+0x14` | Nom interne (`player`, `j001`, `ib_10`, `gb_03`…) |
| `+0x48` | Numéro de flag (coffres) |
| `+0x7C` | Contenu : ID de l'objet, ou montant (coffre de gils) |
| `+0x80` | Quantité (coffres d'objets) |

| Type | Objet |
|---|---|
| `0x02138A98` | Joueur |
| `0x02138C54` | Sortie (`jxxx`) |
| `0x02138B58` | Coffre d'objet (`ib_xx`) |
| `0x02138B90` | Coffre de gils (`gb_xx`) |

Les objets sont recréés à chaque chargement de carte : une modification du contenu ne dure que tant qu'on reste sur la carte. Les données sources sont compressées dans la ROM.

## 6. Table des textes d'objets (« MSDA »)

- Bloc en RAM (`0x250EA8` dans les sessions observées) : `"MSDA"`, `00 00 01 00`, nombre d'entrées (717), pointeur, puis entrées de 12 octets `[ID texte (4)] [01 00 CC CC] [décalage depuis "MSDA" (4)]`.
- Textes en UTF-16LE terminés par 0, précédés d'une icône (caractère `0xE0xx`).
- Nom d'un objet : ID texte = ID de l'objet. Description : ID + 10000.
- Le message « Obtained … » lit le nom **au moment de l'affichage** (vérifié).

## 7. Véhicules

| Élément | Adresse | Statut |
|---|---|---|
| Hovercraft X, Y, Z (vivant) | `0x0D05F8`, `0x0D05FC`, `0x0D0600` | vérifié |
| Enterprise X, Y, Z (vivant) | `0x0D060C`, `0x0D0610`, `0x0D0614` | position vérifiée, affichage non |
| Joueur à bord (1 = hovercraft) | `0x0D067D` | vérifié |
| Orientation de l'hovercraft | `0x0D05B5` | hypothèse |
| Pointeurs d'objets 3D (module `vehicle`) | `0x0D0590`… | `0x0D0590` créé par la scène de l'hovercraft |

Blocs de `0x14` octets par véhicule, dans la mémoire vivante comme dans la sauvegarde. Le point (0, 0, 0) se trouve vers le centre de la carte du monde.

## 8. Fichier de sauvegarde (`.SaveRAM`, emplacement 1)

- Somme de contrôle à `0x1C` = somme des mots de 4 octets de `0x30` à `0x30 + 0x3D90` (vérifiée).
- Sections étiquetées : `PRTY` `0x19D8`, `WRLD` `0x2224`, `VSTY` `0x22DC`, `BTTL` `0x235C`, `EVNT` `0x2361` (flags compressés en bits), `PLSR` `0x246C`, `NAVI` `0x2674`.
- Correspondance avec la RAM pour `PRTY` et `WRLD` : adresse RAM = position dans le fichier + `0x0D60A0`.
- Positions dans `WRLD` : joueur `0x2238`, hovercraft `0x224C`, Enterprise `0x2260` (blocs de `0x14`). Orientation de l'hovercraft `0x22AF`.
- Outil : `read_save.py` (`info`, `diff`, `hover`, `veh`, `gil`, `fix`).

## 9. Objets clés analysés

| Objet | Donné par (flag) | Utilisé à | Vérifié par le jeu ? | Consommé ? |
|---|---|---|---|---|
| Carnelian Signet | Le roi (`0x0CBDB6`) | Village de la Brume | **Non** (scénaristique) | Oui |
| Sand Pearl | Antlion (`0x0CBDDB`) | Rosa à Kaipo | **Oui** : `0x0CBDDB` ouvre le menu, il faut choisir la perle | Oui |

## 10. Recettes

**Donner un objet** : appliquer la règle d'ajout (section 2) dans l'inventaire ou les objets clés, hors cinématique (`0x0CC57C` = 0), avec une écriture gardée.

**Retirer un objet** : inventaire → décrémenter la quantité (le slot reste) ; objets clés → supprimer le slot en décalant les suivants et décrémenter le compteur.

**Remplir un coffre** : lire `0x0CF460`, parcourir la liste, repérer les types `0x02138B58` / `0x02138B90`, écrire `+0x7C` (et `+0x80`) avant l'ouverture, à chaque nouvelle carte.

**Afficher un nom quelconque dans un coffre** : mettre un objet porteur dans le coffre, écrire le texte voulu à la place de sa description dans MSDA, faire pointer l'entrée de son nom vers ce texte ; retirer le porteur après ouverture et restaurer la table en changeant de carte.

**Donner l'hovercraft** : `0x0CC130` = 1, `0x0CBDD8` = 1, position à `0x0D05F8` / `0x0D0600`, de préférence depuis une ville (l'objet 3D est créé au chargement de la carte du monde).

**Sauter une scène** : activer son flag avant qu'elle se déclenche, en reproduisant ses effets secondaires (flags, objets, équipe).

## 11. ROM (décodée le 10/10/2026)

Outil : `outils_rom/ff4ds_rom.py` (`dump`, `carte`, `flag`, `coffres`) + `opcodes_signatures.json`. Prérequis : `pip install ndspy`.

- **Système de fichiers** : NitroFS standard. Archives `SSAM` (`"SSAM"`, nombre d'entrées, puis entrées de `0x28` octets `[décalage (4)][taille (4)][nom (0x20)]`, décalages relatifs à la fin de l'en-tête). Fichiers `.lz` = compression **LZ10**.
- **Textes** : dossiers `N/` = anglais, `F/` = français, `S/` = espagnol. Noms d'objets dans `<langue>/babil_item.msd` (même format MSDA qu'en RAM). Dialogues des scènes : `<langue>/CAST_EVENT_MSD.dat`.
- **Cartes** : `STAGEMNG_D.dat` (donjons `dxx_yy`), `STAGEMNG_T.dat` (villes `txx_yy`), `STAGEMNG_f0x.dat` (cartes du monde), `MAPPARAMETER.dat` (un `.pak` par carte).
- **Scripts d'événements** : `CAST_SCRIPT.dat`, un `<carte>.script.lz` par carte (389). Format `MHCS` :
  - en-tête de `0x10` octets (nombre de segments en u16 à `0x0E`), puis segments de 16 octets `[id (4)][-1][début (4)][fin (4)]` ; segment 1 = arrivée sur la carte, les autres = déclencheurs (PNJ, zones, sorties) ;
  - bytecode : opcode u16 + arguments (u8, u16, u32, texte terminé par 0), sauts en adresse absolue dans le fichier ;
  - table des 500 opcodes dans l'ARM9 à `0x020A5CF4` ; lecteurs d'arguments : texte `0x0207CEE4`, u32 `0x0207CF24`, u16 `0x0207CF3C`, u8 `0x0207CF54` ;
  - signatures déduites automatiquement : 96 % des segments se décodent entièrement.

| Opcode | Rôle | Arguments |
|---|---|---|
| `0x0B` | aller à | cible |
| `0x0C` / `0x0D` | si flag activé / désactivé, aller à | banque, numéro, cible |
| `0x11` | fin | — |
| `0x14` / `0x15` / `0x16` | activer / désactiver / inverser un flag | banque, numéro |
| `0x44` | donner un objet | ID, quantité |
| `0x45` | coffre d'objet | objet carte (70+), ID, quantité, numéro (banque 1), ?, ? |
| `0x66` | coffre de gils | objet carte, montant, ?, numéro (banque 1), ?, ? |
| `0x05` | retour (fin du segment ou de la fonction appelée) | — |
| `0x06` / `0x07` | fin du segment si flag activé / désactivé (conditions de déclenchement) | banque, numéro |
| `0x08` | attendre | nombre d'images |
| `0x0E` | appeler une fonction (banque 0 = carte, 2 = commune) ; `(2, 3061075315)` / `(2, 3281906294)` = début / fin d'événement | banque, n° |
| `0x0F` | si flag … appeler une fonction | banque, numéro, ?, n° |
| `0x43` | changer de carte | carte, x, y, z, ?, ?, ? |
| `0x64` / `0xB1` / `0x14F` | dialogue / attendre la fin du dialogue / nom du locuteur | ID de texte |
| `0x68` / `0x69` | un personnage rejoint / quitte l'équipe (0 Cecil chevalier noir, 1 Cecil paladin, 2 Kain, 6 Rydia) | perso (u32), ? (u8) |
| `0xAC` | équipement d'un personnage | perso, bouclier, arme, casque, armure, bras |
| `0xC9` / `0x5D` / `0xCA` | charger / jouer / libérer un son | n° |
| `0xC5` / `0x5B` / `0xC6` | charger / jouer / arrêter une musique | n° |
| `0xCB` | fondu | ?, durée, sens, … |
| `0xCC` | musique de la carte | n°, … |
| `0x14D` / `0x14E` | définir une sortie de carte (vers un lieu / vers la carte du monde) | nom `jxxx`, carte, x, y, z, sens, zone… |
| `0x1BB` | activer un flag quand on emprunte une sortie | sortie, banque, numéro |
| `0x1A2` | relier une porte `Dxx` à une sortie | porte, sortie, son ?, type ? |
| `0x151` | lancer une cinématique | n°, ?, carte, x, y, z |
| `0x16D` / `0x16E` | charger / libérer une image 2D | … |
| `0x28` / `0x29` / `0xC2` | placer / afficher un objet ou PNJ de carte | … |

- **Coffres** : 418 coffres extraits statiquement (`outils_rom/coffres_rom.csv`, noms anglais et français). Le coffre `0x0CC2D3` (Waterway North B1) contient un Ether.
- Où se joue une scène : `ff4ds_rom.py flag <rom> 0x0CBDDD` → `t03_01` segment 3 (Kaipo, maison) active le flag 49.

## 12. Patch de la ROM (`outils_rom/patch_rom.py`, vérifié en jeu le 10/10/2026)

- Reconstruction : décompresser le fichier (LZ10), modifier, recompresser, reconstruire l'archive SSAM (chaque fichier à un décalage ≡ `0x1F8` modulo `0x200`), puis `ndspy` réécrit la ROM. Le jeu accepte la ROM reconstruite.
- **Méthode qui marche pour sauter une scène** : ne jamais sauter au milieu d'une scène qui se termine par un changement de carte. Les scènes se passent le relais (écran noir, joueur bloqué) et la suivante rétablit l'état. Il faut remplacer la scène dès son début par : effets (objets, équipe, flags) → fin d'une scène connue (fondu, arrêt musique) → `op043` → fin d'événement.
- **Nouvelle partie** (cour `t00_00`, segment 3) : à la place de `op151` (cinématique d'ouverture), saut vers un bloc qui donne la Carnelian Signet, fait rejoindre Kain avec son équipement, active les flags 7, 8, 10, 11, 13–18, 602, 604, 605, 622 et banque 1 : 615, désactive le flag 6, puis `op043('t00_00', 106496, -20480, +1105920)` (devant la porte, côté sortie). Les flags ont été relevés par comparaison mémoire avec une partie normale. Sans eux, les collisions de la carte du monde ne se chargent pas.
- Entrée du château sur la carte du monde (`f00`, sortie `j000`) → intérieur `t00_01` (0, 0, -409600). Sortie de l'intérieur (`t00_01`, `j001`) → cour, côté sortie.
- Lit de Cecil (`t00_14`, segment 20) : saut vers la version « simple repos » (03 1F3).
- **Coordonnées** : `op14D` / `op14E` inversent le signe de z, `op043` non. Position d'arrivée sur la carte courante : `0x0CF484` / `0x0CF488` / `0x0CF48C`. Un `op043` direct vers `f00` place le joueur au bon endroit mais le décor ne suit pas : passer par une carte de lieu.
- Outils mémoire : `dump_objets_carte.lua` (objets de la carte), `dump_etat.lua` (0x0CB000–0x0DA000, pour comparer deux parties).

## 13. Points ouverts

- Flags non identifiés : `0x0CC404`, `0x0CC415` (et `0x0CC461`, probablement une carte complétée).
- Persistance du compteur d'objets reçus à `0x0D807C` après sauvegarde et rechargement.
- Affichage de l'Enterprise hors du centre de la carte (l'objet 3D n'est pas créé).
- Objets cachés : ce sont des `0x45` (coffres) avec un dernier argument 1 ou 2 ; déjà dans `coffres_rom.csv`.
- Verrou de la grande porte de la cour (`D07`, réglages `10, 2`) : non trouvé, contourné.
- Opcodes restants à nommer (dialogue, déplacements, combat, équipe, changement de carte).
- Identifiant de carte pour la téléportation : `0x0CF464` donne le nom, mécanisme de transition à trouver.
