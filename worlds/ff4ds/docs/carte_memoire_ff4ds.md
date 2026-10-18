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
| `0x0CBDE0` (52) | Matin à Kaipo (« Best be moving ») |
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
| Enterprise X, Y, Z (vivant) | `0x0D0604`, `0x0D0608`, `0x0D060C` | vérifié le 17/10/2026 (dump avant / après Enterprise, journal en descendant : Y = 102400 en vol, 0 posée). Les triplets X, Y, Z des véhicules se suivent (pas de `0x0C`) |
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
| Sand Pearl | Antlion (`0x0CBDDB`) | Rosa à Kaipo | **Oui** : `0x0CBDDB` ouvre le menu, il faut choisir la perle (`op106` + `op076(9004, cible)`) | Oui |

## 10. Recettes

**Donner un objet** : appliquer la règle d'ajout (section 2) dans l'inventaire ou les objets clés, hors cinématique (`0x0CC57C` = 0), avec une écriture gardée.

**Retirer un objet** : inventaire → décrémenter la quantité (le slot reste) ; objets clés → supprimer le slot en décalant les suivants et décrémenter le compteur.

**Remplir un coffre** : lire `0x0CF460`, parcourir la liste, repérer les types `0x02138B58` / `0x02138B90`, écrire `+0x7C` (et `+0x80`) avant l'ouverture, à chaque nouvelle carte.

**Afficher un nom quelconque dans un coffre** : mettre un objet porteur dans le coffre, écrire le texte voulu à la place de sa description dans MSDA, faire pointer l'entrée de son nom vers ce texte ; retirer le porteur après ouverture et restaurer la table en changeant de carte.

**Donner l'hovercraft** : `0x0CC130` = 1, `0x0CBDD8` = 1, position à `0x0D05F8` / `0x0D0600`, de préférence depuis une ville (l'objet 3D est créé au chargement de la carte du monde).

**Sauter une scène** : activer son flag avant qu'elle se déclenche, en reproduisant ses effets secondaires (flags, objets, équipe). Dans la ROM : voir les trois recettes de la section 12.

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
| `0x09` | attendre qu'un flag soit activé | banque, numéro |
| `0x0E` | appeler une fonction (banque 0 = carte, 2 = commune) ; `(2, 3061075315)` / `(2, 3281906294)` = début / fin d'événement ; `(2, 612018759)` avec le flag 990 = repos (soins) | banque, n° |
| `0x0F` | si flag … appeler une fonction | banque, numéro, ?, n° |
| `0x24` / `0x25` | ouvrir / fermer l'écran (fondu) ; `(2, 10, 0)` en fin de scène | écran, durée, ? |
| `0x2B` | retirer un acteur de la scène | acteur (u16), ? (u8) |
| `0x43` | changer de carte | carte, x, y, z, ?, ?, ? |
| `0x64` / `0xB1` / `0x14F` | dialogue / attendre la fin du dialogue / nom du locuteur | ID de texte |
| `0x68` / `0x69` | un personnage rejoint / quitte l'équipe (0 Cecil chevalier noir, 1 Cecil paladin, 2 Kain, 3 Rosa, 4 Rydia enfant, 6 Tellah, 9 Edward) | perso (u32), ? (u8) |
| `0x76` | choisir un objet dans le menu ; si c'est le bon, aller à | ID, cible |
| `0x83` | ne fait rien (2 octets) | — |
| `0xAC` | équipement d'un personnage | perso, bouclier, arme, casque, armure, bras |
| `0xB3` | placer un véhicule (1 = hovercraft) | véhicule, x, y, z, … |
| `0xC9` / `0x5D` / `0xCA` | charger / jouer / libérer un son | n° |
| `0xC5` / `0x5B` / `0xC6` | charger / jouer / arrêter une musique | n° |
| `0xCB` | fondu | ?, durée, sens, … |
| `0xCC` | musique de la carte | n°, … |
| `0x102` | niveau d'un personnage (?) | perso, niveau |
| `0x124` | zone de déclenchement | … |
| `0x14D` / `0x14E` | définir une sortie de carte (vers un lieu / vers la carte du monde) | nom `jxxx`, carte, x, y, z, sens, zone… |
| `0x15C` | réglage d'une sortie | sortie, … |
| `0x17C` | apprendre un sort | perso, sort |
| `0x1BB` | activer un flag quand on emprunte une sortie | sortie, banque, numéro |
| `0x1A2` | relier une porte `Dxx` à une sortie | porte, sortie, son ?, type ? |
| `0x151` | lancer une cinématique | n°, ?, carte, x, y, z |
| `0x16D` / `0x16E` | charger / libérer une image 2D | … |
| `0x42` | lancer un combat | groupe de monstres (u16, ex. 901 = Dragon des Brumes, 906 = Antlion, 907 = Sahagin), décor, … (u8) |
| `0x73` | retirer un objet | ID, quantité |
| `0x28` / `0x29` / `0xC2` | placer / afficher un objet ou PNJ de carte | … |

- **Coffres** : 418 coffres extraits statiquement (`outils_rom/coffres_rom.csv`, noms anglais et français). Le coffre `0x0CC2D3` (Waterway North B1) contient un Ether.
- Où se joue une scène : `ff4ds_rom.py flag <rom> 0x0CBDDD` → `t03_01` segment 3 (Kaipo, maison) active le flag 49.

## 12. Patch de la ROM (`worlds/ff4ds/rom/patch_rom.py`, tranche 1 vérifiée en jeu le 12/10/2026)

- Archipelago : la génération écrit un `.apff4ds` (options) ; le Launcher applique `patch_rom.patch()` sur la ROM du joueur. `rom/nds.py` remplace ndspy (fichier agrandi = déplacé en fin de ROM, FAT et CRC de l'en-tête mis à jour).

- Reconstruction : décompresser le fichier (LZ10), modifier, recompresser, reconstruire l'archive SSAM (chaque fichier à un décalage ≡ `0x1F8` modulo `0x200`), puis `ndspy` réécrit la ROM. Le jeu accepte la ROM reconstruite.
- **Méthode qui marche pour sauter une scène** : ne jamais sauter au milieu d'une scène qui se termine par un changement de carte. Les scènes se passent le relais (écran noir, joueur bloqué) et la suivante rétablit l'état. Il faut remplacer la scène dès son début par : effets (objets, équipe, flags) → fin d'une scène connue (fondu, arrêt musique) → `op043` → fin d'événement.
- **Nouvelle partie** (cour `t00_00`, segment 3) : à la place de `op151` (cinématique d'ouverture), saut vers un bloc qui donne la Carnelian Signet, fait rejoindre Kain avec son équipement, active les flags 7, 8, 10, 11, 13–18, 602, 604, 605, 622 et banque 1 : 615, désactive le flag 6, puis `op043('t00_00', 106496, -20480, +1105920)` (devant la porte, côté sortie). Les flags ont été relevés par comparaison mémoire avec une partie normale. Sans eux, les collisions de la carte du monde ne se chargent pas.
- Entrée du château sur la carte du monde (`f00`, sortie `j000`) → intérieur `t00_01` (0, 0, -409600). Sortie de l'intérieur (`t00_01`, `j001`) → cour, côté sortie.
- Lit de Cecil (`t00_14`, segment 20) : saut vers la version « simple repos » (03 1F3).
- **Coordonnées** : `op14D` / `op14E` inversent le signe de z, `op043` non. Position d'arrivée sur la carte courante : `0x0CF484` / `0x0CF488` / `0x0CF48C`. Un `op043` direct vers `f00` place le joueur au bon endroit mais le décor ne suit pas : passer par une carte de lieu.
- **Grotte de la Brume** : voix sautées (flags 20, 21) ; Dragon des Brumes : on garde la mise en scène (acteurs, caméra, fondu) et on ne saute que les dialogues et le choix (00B1D → 00CF7). Sauter jusqu'au combat lui-même cassait le retour de combat (joueur au centre de la carte du monde, flag 23 jamais activé).
- **Village de la Brume** (`t02_00`, segment 3) : Signet retirée (`op073`), puis à la place de `op151` saut vers un bloc **ajouté à la fin du script** (après la table des fonctions) : fin d'origine du réveil (`t02_02`, Kain déséquipé et `op069(2)`, flags 24 / 26) + flags 614 et banque 1 : 617 + `op043('f00', -1044480, 0, -40960)`.
- **Règle** : les cinématiques (`op151`) activent elles-mêmes des flags absents des scripts, notamment la famille 6xx (« chaîne de scénario ») qui fixe l'état de la carte du monde (collisions, éboulement du Titan, décors de combat). À chaque cinématique sautée, comparer la mémoire avec une partie normale (`dump_etat.lua`) et reporter ces flags.
- Retirer les rochers du Titan sur la carte du monde laisse une barrière invisible (la collision fait partie du décor) : essai abandonné.
- **Kaipo** (`t03_00`, segment 3, scène des gardes) : remplacée par les effets d'arrivée à l'auberge (Rydia rejoint : `op068(4)`, `op102`, `op0AC`, 4 × `op17C`, copiés de `t03_30`) + flags 28, 31, 29, 753, 754 + `op005`. Le joueur reste à l'entrée de Kaipo. Première visite à Rosa (`t03_01`, segment 3, zone) : `donner_objet(9136 Auto-Potion)` + `op15C('j001', 1, 0, 0)` + flag 30. Explication de l'augment par Namingway (`t03_00`, segment 8) : flag 966.
- **Rivière souterraine** : Tellah (`d01_00`) et Octomammoth (`d01_07`, `d01_09`) par `strip_scene` (mise en scène et combat gardés, dialogues retirés) ; haltes `d01_03` (flag 33) et `d01_06` (flag 34) remplacées par leur flag + `op005`.
- **Damcyan** (`t04_04`, segment 3, après `op009(10, 11)`) : Tellah part, Edward rejoint (copié de `t04_04` 00838), flags 41–44 et 900, hovercraft posé devant le château (`op0B3(1, …)` copié de `f00` 01B55), puis `op024(2, 10, 0)`, `attendre(15)`, fin d'événement.
- **Antre de l'Antlion** (`d02_04`, segment 3) : `strip_scene` de 00132 à 00A8D (combat `op042(906)` gardé, Sand Pearl et flag 47 donnés par la fin de scène).
- **Rosa soignée** (`t03_01`, segment 3, après `op009(10, 5)`) : saut vers un bloc ajouté : fondu au noir `op025(2, 10, 0)`, Rosa rejoint (`op068(3)`, `op102`, `op0AC`), `op073(9004)` (Sand Pearl retirée), `op02B(20, 0)` (Rosa endormie retirée), flags 49, 50, 52 (la nuit à Kaipo et le combat contre les Sahagin sont sautés), repos (flag 990 + `op00E(2, 612018759)`), `op024(2, 10, 0)`, attendre, fin d'événement.
- **Mont Hobs** (tranche 2, vérifié le 17/10/2026) : mur de glace (`d03_00` 000F4) : flag 54 activé à chaque arrivée sur la carte. Sommet (`d03_02`, segment 3 ; flag 57 → fin, flag 56 → fonction 00ACF après-combat, flag 58 → fonction 0068E Mom Bomb, sinon zone de l'escalier → 0025E) : la zone saute vers un bloc ajouté = début d'événement + `op025(2, 10, 0)` + attendre (copiés de 0025E), arrivée du personnage tiré, `op1B9(0, 0)` (sauvegarde de l'équipe), flags 55, 444, 58, 56, `op1BA(0, 0)` + attendre(3), `op1AE(1, 1)`, `op042(909)`, fin d'événement. 00ACF remplacée par : début d'événement, fondu au noir, joueur replacé (`op105`, `op09F`, `op02C`, `op087` copiés de 013DF), `op024(2, 10, 0)`, flag 57, fin d'événement.
  - `op1BA(0, 0)` fixe le point de retour du combat : sans lui, retour sur la carte précédente. Il fige le jeu si l'écran n'est pas déjà noir.
  - Une fonction de scène appelée par le chargement de carte (`op00F` flag → fonction) ne se rejoue pas si on active son flag en cours de route : l'appeler directement ou reproduire sa fin.
  - Activer le flag « scène terminée » avant le combat saute l'après-combat, mais aussi le replacement du joueur.
- **Fabul** (vérifié le 17/10/2026) : salle du trône (`t05_03`, segment 3, à la place de `op006(0, 62)`) → aiguillage ajouté, rejoué à chaque chargement de la carte : six combats enchaînés (911, 912, 911, 913, 912, 911 ; chacun = début d'événement, flag compteur 63/64/66/67/68, flag 444, `op1AE(0, 0)`, `op042(n°, 26, 0, 1, 0)`, fin d'événement). Le flag 65 est évité pendant la chaîne (il réveille le segment 4 d'origine). Avant le dernier combat : flags 65, 69, 70 (Kain sauté). Au retour (flag 70) : `op025(2, 10, 0)`, départ de l'emplacement de Rosa, flag 62, `op024(2, 10, 0)`. Nuit de `t05_30` (segment 3) neutralisée. Roi dans sa chambre (`t05_09`, segment 21, 0074B) : Deathbringer (`op044(6003)`, flag 74), Counter (`op044(9139)`, flag 75), flags 73, 78–83, 85, 444, 448, départs du Léviathan, `op043('f00', 1495040, 0, 3932160)` (côte de Mysidia, copié de `t05_92`). Aucun problème de carte du monde constaté sans la cinématique du Léviathan.
  - Des combats déclenchés au chargement de la carte, sans mise en scène, n'ont besoin ni de `op1BA` ni de fondu : au retour de chaque combat, la carte se recharge et l'aiguillage lance le suivant.
- **Mysidia** (vérifié le 17/10/2026) : maison de l'Ancien (`t06_01`, segment 3, zone, 00445) → les deux personnages tirés (emplacements de Porom et Palom, niveau 10) + flag 90 + `op005` (recette 1). Pas de coffre à Mysidia. Magasins 11, 12, 13.
- **Chemin maudit** (vérifié) : ouvert sans le flag 110 (paladin revenu voir l'Ancien) : `t06_00` 0032C `op006(0, 110)` → `op005` (garde non placé), 0051F `op00D(0, 110, …)` neutralisé (sortie j006 toujours définie), `t01_03` 0024A `op00C(0, 110, 973)` → `aller_a(973)` (côté Baron). Le flag 110 lui-même n'est pas activé (il change l'état de Baron).
- **Mont Ordeals** (vérifié le 17/10/2026) : feu du pied (`d04_00` segment 1, placé sans le flag 94) jamais placé ; zone du segment 3 → flags 93, 94, 95. Tellah (`d04_01`, zone 00190) → personnage tiré (niveau 20) + flag 96. Sommet `d04_03` : zones « *hiss* » désactivées ; les deux zones de Scarmiglione → fondu + flag 99 + `op042(915, 11, 0, 0, 0)` ; segment 4 arrêté par le flag 99 ; segment 5 → aiguillage (102 fin ; 101 → fondu, `op17B(0, 0)`, flag 102, écran rouvert ; 99 → flags 100, 101, `op042(916, 11, 1, 0, 0)`). Antre (segment 6, zone 0198E) → fondu, Cecil paladin (copié de 01C2F : repos, `op069(0)`, `op068(1)`, `op0AC(1, 0, 6004, …)`), sorts de Tellah (copiés de `d04_04` 00BBE), flags 104, 105, 714 (posé par la cinématique e10_01), 106, 107. **Objectif de la tranche 2 = flag 107** (`0x0CBE17`).
  - Récompenses de carte complétée = segment 9 de chaque carte (`op006(1, n)`, `op044(objet, quantité)`, flag banque 1 n) : mont Hobs 868–871, mont Ordeals 872–875 (`0x0CC4FC`–`0x0CC4FF`).
- **Tranche 3** (vérifié le 17/10/2026) : auberge de Baron (`t01_30`, segment 3 ; condition du flag 110 retirée à 00450) : fonctions 00484 (gardes, flag 112, `op042(918)`), 006EC (Yang, flag 113, `op1AE(0, 1)`, `op042(919)`), 008BA (arrivée + Baron Key `op044(9008)` + repos + flag 114). Baigan (`t00_01` 00592 → flag 116, `op042(920)` ; 00B43 → fin d'origine 00D73 + flag 117). Cagnazzo (`t00_06` segment 4 : condition 110 remplacée par 117 ; 012EC → flag 118, `op042(921)` ; 019FB → départs des jumeaux, arrivée de Cid, flags 119, 121–124, 629, 633, 716, 901, `op0B3(2, -978944, 102400, 1658880)` copié de f00 01E43). Les flags 123, 124, 629, 633, 716 sont posés par la cinématique op151(12) au-dessus de Baron (relevés par comparaison mémoire). Ancien de Mysidia après le paladin (`t06_01` zone 0363B et réplique 058DD) → flags 109, 110 ; une réplique doit garder début et fin d'événement.
- **Trois recettes de saut (vérifiées)** :
  1. *Scène déclenchée par une zone, sans changement de carte ni combat* : la remplacer par ses effets + flag + `op005`.
  2. *Scène avec combat ou changement de carte* : `strip_scene` (on garde la mise en scène, on retire les dialogues et on raccourcit les attentes). Ne jamais sauter directement au combat.
  3. *Scène déclenchée en parlant à un PNJ* : le segment du PNJ ouvre l'événement et active un flag temporaire (banque 10), le segment 3 attend ce flag (`op009`). Juste après l'attente : effets + (fondu au noir) + `op024(2, 10, 0)` + `attendre(15)` + fin d'événement + `op005`. Remplacer par les effets seuls, sans réouvrir l'écran, fige le jeu.
- Ne jamais ajouter une fin d'événement sans début correspondant.
- **Savestates** : le jeu garde en mémoire la table de l'archive. Un savestate fait avec une autre version de la ROM peut donner un écran noir : utiliser les sauvegardes du jeu quand la ROM change. `ssam_write` garde les décalages d'origine pour limiter le problème.
- Fin de script : table des fonctions (en-tête `+0x08` = sa position ; entrées `[n° (4)][position (4)]`), appelée par `op00E(0, n°)`.
- Outils mémoire : `dump_objets_carte.lua` (objets de la carte), `dump_etat.lua` (0x0CB000–0x0DA000, pour comparer deux parties), `donner_objets_test.lua` (objets de test).

## 13. Points ouverts

- Flags non identifiés : `0x0CC404`, `0x0CC415` (et `0x0CC461`, probablement une carte complétée).
- Persistance du compteur d'objets reçus à `0x0D807C` après sauvegarde et rechargement.
- Affichage de l'Enterprise hors du centre de la carte (l'objet 3D n'est pas créé).
- Objets cachés : ce sont des `0x45` (coffres) avec un dernier argument 1 ou 2 ; déjà dans `coffres_rom.csv`.
- Verrou de la grande porte de la cour (`D07`, réglages `10, 2`) : non trouvé, contourné.
- Opcodes restants à nommer (dialogue, déplacements, combat, équipe, changement de carte).
- Identifiant de carte pour la téléportation : `0x0CF464` donne le nom, mécanisme de transition à trouver.
- Bestiaire des combats sautés (gardes de Kaipo, Sahagin) : à marquer par le client AP ; disposition des bits vers `0x0D8450`–`0x0D84A0` à mesurer.
- Flags 6xx éventuellement posés par la cinématique de l'hovercraft (Damcyan) : non vérifiés, aucun problème constaté.

## 14. Sorts (vérifié dans la ROM et en RAM le 13/10/2026)

- **Identifiants** (`N/babil_ability.msd`) : blancs 4001 Cure … 4027, noirs 4501 Fire … 4529, invocations 1501 Goblin … 1516 Bahamut (1517 = invocation spéciale de Rydia), ninjutsu 4901–4909. Commandes : 5 = Magie noire, 6 = Magie blanche, 13 = Invocation.
- **Apprentissage par niveau** : `player.chaindata.lz`, bloc 17 + identifiant du personnage (0 Cecil chevalier noir, 1 Cecil paladin, 2 Kain, 3 Rosa, 4 Rydia enfant, 5 Rydia adulte, 6 Tellah, 7 Porom, 8 Palom, 9 Edward, 10 Yang, 11 Cid, 12 Edge, 13 FuSoYa, 14 Golbez). Un bloc = suite de paires u16 (niveau, capacité) ; commandes, sorts et invocations mélangés. Mettre le niveau à 100 empêche l'apprentissage.
- `op102(perso, niveau)` règle le niveau à l'arrivée et donne (hypothèse, à vérifier en jeu) les sorts jusqu'à ce niveau ; `op17C(perso, capacité)` donne une commande ou un sort (Rydia : commandes 5 et 13, Chocobo, 1517).
- **Listes en RAM** (= sauvegarde + `0x0D60A0`) : un bloc de `0x1C0` par personnage. Liste blanche à `0x0D6174 + perso × 0x1C0` : 40 cases u16 + compteur u32 ; liste noire `+0x54` (même format) ; invocations `+0xA8` : 32 cases + compteur ; puis augments. Les sorts sont dans l'ordre d'apprentissage. Golbez (14) n'a pas de bloc.
- **Sorts en objets** (option `spell_items`, monde `spells.py`) : un objet par sort, familles progressives (Cure, Fire, Blizzard, Thunder), sort appris par tous les personnages qui l'apprennent normalement. Le client complète les listes en RAM (écriture idempotente, refaite si le jeu reconstruit une liste). Tranche 1 : sorts de Rydia enfant appris après le niveau 1.

## 15. Personnages aléatoires (vérifié en jeu le 16/10/2026)

- Arrivée d'un personnage = `op068(perso, ?)` + `op102(perso, niveau)` + `op0AC(perso, bouclier, arme, casque, armure, bras)` + éventuels `op17C(perso, capacité)` (Rydia : commandes 5 et 13, 1517, Chocobo). Départ = `op0AC(perso, 0, 0, 0, 0, 0)` (équipement rendu) + `op069(perso, 0)`. Identifiants : 2 Kain, 3 Rosa, 4 Rydia, 6 Tellah, 7 Porom, 8 Palom, 9 Edward, 10 Yang, 11 Cid, 12 Edge, 13 FuSoYa.
- Tous les blocs de personnages existent dès la nouvelle partie (sorts de niveau 1 déjà présents) : un personnage peut rejoindre n'importe où.
- Monde : `rom/characters.py` (emplacements de la tranche 1 : Starting/Kain niv. 10, Kaipo/Rydia 7, Waterway/Tellah 13, Damcyan/Edward 9, Rosa 15). Options `character_shuffle`, `allowed_characters`, `restricted_characters` (Edge, FuSoYa), `character_departures` (`never` comme Free Enterprise : équipe pleine à 5, emplacements suivants vides ; `vanilla` : les emplacements de Kain et Tellah partent). Pas de doublons (un bloc par personnage). Cecil fixe.
- Free Enterprise : 18 emplacements de personnage (objets verrouillés), personne ne part à cause de l'histoire, menu pour renvoyer quelqu'un quand l'équipe est pleine (absent sur DS).

## 16. Magasins (vérifié en jeu le 16/10/2026)

- `op047(n° magasin, 0)` ouvre un magasin (43 magasins, 0 = débogage). Données : `MENU/babil_shop.bbd`, non compressé, 43 fiches de 124 octets : nom (32), 7 identifiants de textes (u32), 16 objets (u32, 0 = vide). Tranche 1 : Baron (1 armes, 2 armures, 3 objets, 40 objets 2), Mist (4, 5), Kaipo (6, 7, 8).
- Fiches des objets : `item_parameter.pak.lz`, 4 blocs (consommables 48 octets, armes 88, armures 84, objets clés 32). Mot 1 = ID, mots 14–15 = prix d'achat u32 (0 ou 1 = invendable), mots 16–17 = prix de vente, mot 22 = masque d'équipement (bit = identifiant de personnage, ex. Rod : Rydia, Rydia adulte, Tellah, Palom, FuSoYa, Golbez).
- Monde : `shops.py` + `rom/shop_data.py`. Options `shop_randomization` (vanilla / shuffle / standard / wild, défaut standard : même type et prix proche de l'objet d'origine) et `shop_party_equipment` (équipement portable par l'équipe tirée en priorité). Potion et Phoenix Down restent en vente là où ils l'étaient.