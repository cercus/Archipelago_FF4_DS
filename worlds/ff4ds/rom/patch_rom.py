"""Patcheur de ROM pour Final Fantasy IV DS (US, YF4E).

Utilisation :
  python patch_rom.py <rom_origine.nds> <rom_patchee.nds>

Aucune dépendance : seulement Python (fonctionne dans Archipelago).

Ne modifie jamais la ROM d'origine : une nouvelle ROM est écrite.

Patchs actuels :
  - Étape B : nouvelle partie -> dans la cour du château, devant la sortie, avec Kain
    et la Carnelian Signet ; toute l'introduction est sautée.
  - Étape C : l'entrée du château de Baron sur la carte du monde mène à l'intérieur (t00_01) ;
    en ressortant, on arrive dans la cour du bon côté de la grande porte.
  - Étape D : le lit de Cecil ne relance plus la nuit (Rosa) ni le départ ; simple repos.
  - Étape E : Grotte de la Brume : plus de voix, Dragon des Brumes sans dialogue.
  - Étape F : Village de la Brume : Signet retirée, Kain part, réveil directement dans le désert.
  - Étape G : Kaipo : arrivée, nuit à l'auberge et combat des soldats sautés ; Rydia rejoint directement.
  - Étape H : première visite à Rosa sautée ; l'augment Auto-Potion est donné directement.
  - Étape I : Rivière souterraine : Tellah sans dialogue, haltes sautées, Octomammoth sans dialogue.
  - Étape J : Damcyan : Anna, combat Tellah / Edward et cinématique sautés ; Edward rejoint, hovercraft donné.
  - Étape K : Antre de l'Antlion : combat gardé, dialogues retirés.
  - Étape L : Rosa soignée : Rosa rejoint, nuit à Kaipo (Sahagin) et matin sautés.
  - Étape M (tranche 2) : mont Hobs : mur de glace fondu, mise en scène et cinématique du sommet
    sautées ; le personnage tiré rejoint, combat contre Mom Bomb direct, discussion d'après-combat sautée.
  - Étape N : Fabul : les six combats de la défense s'enchaînent dans la salle du trône ; Kain sauté.
  - Étape O : le roi (dans sa chambre) donne Deathbringer et Counter, puis arrivée directe sur la côte
    de Mysidia (bateau et Léviathan sautés).
  - Étape P : Mysidia : audience de l'Ancien sautée, les deux personnages tirés rejoignent directement.
  - Étape Q : chemin maudit (Mysidia <-> Baron) ouvert dès le départ, dans les deux sens.
  - Étape R : mont Ordeals : pas de feu au pied, Tellah (personnage tiré) rejoint directement, les deux
    combats contre Scarmiglione enchaînés, Cecil devient paladin en entrant dans l'antre.
  - Étapes S à U (tranche 3) : auberge de Baron (gardes, Yang, Baron Key), Baigan, Cagnazzo : combats
    seuls ; après Cagnazzo, départ des jumeaux, arrivée de Cid.
  - Étapes V à Y (tranche 4) : Troia (Whisperweed, voix de Kain), Elfe noir (dragon seul, avec la
    Whisperweed), accès permanent à Zott par une Épopte (avec la Terre), sœurs Magus, Golbez sauté,
    Kain et Rosa, Valvalis (objectif).
"""
from __future__ import annotations

import json
import os
import pkgutil
import struct
import sys

try:                                   # dans le monde Archipelago (worlds/ff4ds/rom)
    from .nds import NDSRom
    from .characters import join_code, leave_code, plan_party, vanilla_party
except ImportError:                    # lancé directement : python patch_rom.py ...
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from nds import NDSRom
    from characters import join_code, leave_code, plan_party, vanilla_party

GAME_CODE = b"YF4E"

# Signatures des opcodes de script (types des arguments), lues à côté de ce fichier
# (pkgutil fonctionne aussi quand le monde est empaqueté dans un .apworld).
_SIG_RAW = None
if __name__ != "__main__":
    try:
        _SIG_RAW = pkgutil.get_data(__name__, "opcodes_signatures.json")   # aussi dans un .apworld
    except (ImportError, ValueError, OSError):
        _SIG_RAW = None
if _SIG_RAW is None:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "opcodes_signatures.json"), "rb") as _f:
        _SIG_RAW = _f.read()
SIG = {int(k): v for k, v in json.loads(_SIG_RAW).items()}


def lz10(d):
    """Décompression LZ10."""
    assert d[0] == 0x10, "compression LZ10 attendue"
    size = d[1] | d[2] << 8 | d[3] << 16
    out, p = bytearray(), 4
    while len(out) < size:
        flags = d[p]; p += 1
        for b in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> b):
                x = d[p] << 8 | d[p + 1]; p += 2
                for _ in range((x >> 12) + 3):
                    out.append(out[-((x & 0xFFF) + 1)])
            else:
                out.append(d[p]); p += 1
    return bytes(out)


def step(d, p):
    """Décode l'instruction à la position p : (opcode, arguments, position suivante)."""
    op = struct.unpack_from("<H", d, p)[0]
    if op >= 500:
        return None
    p += 2
    args = []
    for t in SIG.get(op, []):
        if t == "s":
            e = d.index(b"\0", p)
            args.append(d[p:e].decode("latin1")); p = e + 1
        else:
            n = {"I": 4, "H": 2, "B": 1}[t]
            args.append(int.from_bytes(d[p:p + n], "little")); p += n
    return op, args, p


def load_rom(path):
    rom = NDSRom.from_file(path)
    assert rom.id_code == GAME_CODE, "ROM US (YF4E) attendue"
    return rom


ALIGN = 0x200          # dans une archive SSAM, chaque fichier commence à un décalage = 0x1F8 modulo 0x200
ALIGN_REST = 0x1F8


# --------------------------------------------------------------------------- #
# Compression LZ10 (l'inverse de lz10())                                      #
# --------------------------------------------------------------------------- #
def lz10_compress(data):
    out = bytearray([0x10, len(data) & 0xFF, (len(data) >> 8) & 0xFF, (len(data) >> 16) & 0xFF])
    positions = {}          # 3 octets -> dernières positions où on les a vus
    p, n = 0, len(data)
    while p < n:
        flag_index = len(out); out.append(0)
        for bit in range(8):
            if p >= n:
                break
            best_len, best_disp = 0, 0
            for q in reversed(positions.get(data[p:p + 3], [])[-16:]):
                disp = p - q
                if disp > 0x1000:
                    continue
                length = 0
                while length < 18 and p + length < n and data[q + length] == data[p + length]:
                    length += 1
                if length > best_len:
                    best_len, best_disp = length, disp
                    if length == 18:
                        break
            if best_len >= 3:
                out[flag_index] |= 0x80 >> bit
                x = ((best_len - 3) << 12) | (best_disp - 1)
                out += bytes([x >> 8, x & 0xFF])
                step = best_len
            else:
                out.append(data[p])
                step = 1
            for i in range(p, p + step):
                positions.setdefault(data[i:i + 3], []).append(i)
            p += step
    while len(out) % 4:
        out.append(0)
    return bytes(out)


# --------------------------------------------------------------------------- #
# Archives SSAM                                                               #
# --------------------------------------------------------------------------- #
def ssam_read(data):
    """Entrées [nom (0x20 octets), contenu, décalage d'origine, place disponible d'origine]."""
    assert data[:4] == b"SSAM"
    count = struct.unpack_from("<I", data, 4)[0]
    header_end = 8 + count * 0x28
    raw = []
    for i in range(count):
        o = 8 + i * 0x28
        offset, size = struct.unpack_from("<II", data, o)
        raw.append((bytes(data[o + 8:o + 0x28]), offset, size))
    total = len(data) - header_end
    entries = []
    for i, (name, offset, size) in enumerate(raw):
        following = [r[1] for r in raw if r[1] > offset]
        slot = (min(following) if following else total) - offset
        entries.append([name, bytes(data[header_end + offset:header_end + offset + size]), offset, slot])
    return entries


def ssam_write(entries):
    """Reconstruit l'archive en gardant chaque fichier à son décalage d'origine quand il tient
    dans sa place : la disposition de la ROM change le moins possible (les savestates d'une
    version précédente restent plus souvent utilisables). Un fichier devenu trop grand est
    déplacé à la fin de l'archive."""
    header = bytearray(b"SSAM" + struct.pack("<I", len(entries)))
    end = max(e[2] + e[3] for e in entries)
    placed = []
    for name, blob, offset, slot in entries:
        if len(blob) > slot:
            while end % ALIGN != ALIGN_REST:
                end += 1
            offset, end = end, end + len(blob)
        placed.append((name, blob, offset))
    body = bytearray(max(off + len(b) for _, b, off in placed))
    for name, blob, offset in placed:
        header += struct.pack("<II", offset, len(blob)) + name
        body[offset:offset + len(blob)] = blob
    return bytes(header + body)


def ssam_get(entries, filename):
    for e in entries:
        if e[0].split(b"\0")[0].decode() == filename:
            return e
    raise KeyError(filename)


# --------------------------------------------------------------------------- #
# Textes MSDA                                                                 #
# --------------------------------------------------------------------------- #
def msda_set_text(d, text_id, text):
    """Remplace le texte <text_id>. En place s'il tient, sinon ajouté à la fin du fichier."""
    d = bytearray(d)
    count = struct.unpack_from("<I", d, 8)[0]
    new = text.encode("utf-16-le") + b"\0\0"
    found = False
    for i in range(count):
        entry = 0x10 + 12 * i
        tid, _, offset = struct.unpack_from("<III", d, entry)
        if tid != text_id:
            continue
        found = True
        end = offset
        while d[end:end + 2] != b"\0\0":
            end += 2
        if len(new) <= end + 2 - offset:
            d[offset:offset + len(new)] = new
        else:
            struct.pack_into("<I", d, entry + 8, len(d))
            d += new
    if not found:
        raise KeyError(text_id)
    return bytes(d)


def replace_text(rom, lang, map_name, text_id, text):
    archive_name = f"{lang}/CAST_EVENT_MSD.dat"
    entries = ssam_read(rom.getFileByName(archive_name))
    entry = ssam_get(entries, f"{map_name}.msd.lz")
    entry[1] = lz10_compress(msda_set_text(lz10(entry[1]), text_id, text))
    rom.setFileByName(archive_name, ssam_write(entries))


# --------------------------------------------------------------------------- #
# Scripts d'événements                                                        #
# --------------------------------------------------------------------------- #
def goto(target):
    """Instruction aller_a(target) : opcode 0x000B + adresse u32 (6 octets)."""
    return struct.pack("<HI", 0x0B, target)


def load_script(rom, map_name):
    """Script décompressé (tel qu'il est actuellement dans la ROM)."""
    entries = ssam_read(rom.getFileByName("CAST_SCRIPT.dat"))
    return lz10(ssam_get(entries, f"{map_name}.script.lz")[1])


def patch_script(rom, map_name, position, new_bytes, expected):
    """Écrit new_bytes à <position> dans le script de <map_name>.
    expected = octets d'origine attendus à cet endroit (sécurité : refuse une mauvaise ROM)."""
    entries = ssam_read(rom.getFileByName("CAST_SCRIPT.dat"))
    entry = ssam_get(entries, f"{map_name}.script.lz")
    script = bytearray(lz10(entry[1]))
    actual = bytes(script[position:position + len(expected)])
    if actual != expected:
        raise ValueError(f"{map_name} {position:05X} : attendu {expected.hex(' ')}, trouvé {actual.hex(' ')}")
    script[position:position + len(new_bytes)] = new_bytes
    entry[1] = lz10_compress(bytes(script))
    rom.setFileByName("CAST_SCRIPT.dat", ssam_write(entries))


BEGIN_EVENT = struct.pack("<HII", 0x0E, 2, 3061075315)     # op00E(2, …) : début d'événement
END_EVENT = struct.pack("<HII", 0x0E, 2, 3281906294)       # op00E(2, …) : fin d'événement


def append_position(rom, map_name):
    """Position à laquelle append_script() placera le prochain bloc (pour y calculer des sauts)."""
    size = len(load_script(rom, map_name))
    return size + (-size) % 4


def append_script(rom, map_name, code):
    """Ajoute du code à la fin du script de <map_name> (après la table des fonctions)
    et renvoie sa position, à utiliser comme cible d'un aller_a."""
    entries = ssam_read(rom.getFileByName("CAST_SCRIPT.dat"))
    entry = ssam_get(entries, f"{map_name}.script.lz")
    script = bytearray(lz10(entry[1]))
    while len(script) % 4:
        script.append(0)
    position = len(script)
    script += code
    entry[1] = lz10_compress(bytes(script))
    rom.setFileByName("CAST_SCRIPT.dat", ssam_write(entries))
    return position


NOP = struct.pack("<H", 0x83)          # opcode sans argument et sans effet
DIALOGUE_OPS = {0x5F, 0x60, 0x64, 0xB0, 0xB1, 0xB2, 0x14F, 0x150}   # fenêtres, textes, noms, attentes de bouton


def strip_scene(rom, map_name, start, end, extra_ops=(), max_wait=10):
    """Accélère une scène sans toucher à sa mise en scène :
    - les instructions de dialogue (et extra_ops) entre start et end sont neutralisées ;
    - les attentes (op008) de plus de max_wait images sont ramenées à max_wait.
    Renvoie le nombre d'instructions modifiées."""
    entries = ssam_read(rom.getFileByName("CAST_SCRIPT.dat"))
    entry = ssam_get(entries, f"{map_name}.script.lz")
    script = bytearray(lz10(entry[1]))
    remove = DIALOGUE_OPS | set(extra_ops)
    p, changed = start, 0
    while p < end:
        op, args, nxt = step(bytes(script), p)
        length = nxt - p
        if op in remove:
            if length % 2 == 0:
                script[p:nxt] = NOP * (length // 2)
            else:
                script[p:p + 6] = goto(nxt)           # instruction de longueur impaire (>= 7)
            changed += 1
        elif op == 0x08 and args[0] > max_wait:
            struct.pack_into("<H", script, p + 2, max_wait)
            changed += 1
        p = nxt
    entry[1] = lz10_compress(bytes(script))
    rom.setFileByName("CAST_SCRIPT.dat", ssam_write(entries))
    return changed


# --------------------------------------------------------------------------- #
# Patchs                                                                      #
# --------------------------------------------------------------------------- #
def apply_patches(rom, party=None, departures="vanilla", full_party="replace_oldest", vehicle_items=False):
    """party : {emplacement: personnage ou None} (characters.SLOTS) ; par défaut, l'équipe d'origine.
    departures : "vanilla" (départs de l'histoire) ou "never" (personne ne part, comme Free Enterprise).
    full_party : équipe pleine -> "replace_oldest" (le plus ancien part) ou "skip" (le nouveau ne vient pas).
    vehicle_items : True (partie Archipelago) = l'hovercraft et l'Enterprise sont des objets posés par le
    client ; False (patch lancé seul) = la ROM les donne comme dans le jeu d'origine."""
    plan = plan_party(party or vanilla_party(), departures, full_party)

    def join(slot):
        joined = plan.joins.get(slot)
        if not joined:
            return b""
        name, replaced = joined
        return (leave_code(replaced) if replaced else b"") + join_code(name, slot)

    def leave(slot):
        name = plan.leaves.get(slot)
        return leave_code(name) if name else b""

    # Étape B : nouvelle partie -> directement sur la carte du monde, devant le château de Baron,
    # avec Kain dans l'équipe. Toute l'introduction est sautée.
    # Historique : essais 1-3 (scène du roi seule) = jeu figé ; essai 4 = arrivée dans le couloir (OK) ;
    # essai 5 = cinématique d'ouverture sautée aussi (OK).
    #
    # Essai 6 (actuel), dans la cour (t00_00, segment 3) :
    #   00B2A : à la place de op151 (cinématique d'ouverture) -> aller_a(00B57)
    #   00B57 : notre bloc :
    #     - Carnelian Signet ; Kain rejoint l'équipe + son équipement (copiés de t00_14, 03191)
    #     - flags de l'intro (voir plus bas) + flag_off(0, 6)
    #     - fondu + arrêt de la musique (copiés de t00_04, 00947)
    #     - changement de carte vers la cour (t00_00), juste devant la sortie vers la carte du monde
    #       Essais 6a / 6b : op043 directement vers f00 -> joueur à la bonne position (-983040, -1814528)
    #       mais dans la mer : la carte du monde charge son décor autour d'une position mémorisée,
    #       vide en début de partie. En passant par la sortie normale de la cour, le jeu fait le
    #       nécessaire lui-même.
    #       Essai 7 : les sorties (op14D / op14E) inversent le signe de z, op043 non.
    #       La position "devant la porte, côté sortie" vaut donc z = +1105920 pour op043
    #       (avec -1105920, le joueur apparaissait de l'autre côté, dans les murs).
    #     - fin d'événement
    t00_04 = load_script(rom, "t00_04")
    t00_14 = load_script(rom, "t00_14")
    block = bytes.fromhex("44 00 33 23 01")                  # donner_objet(0x2333 Carnelian Signet, 1)
    block += join("Starting Character")                     # d'origine : Kain (t00_14, 03191)
    # Flags : relevés en comparant la mémoire d'une partie normale (devant Baron après le départ)
    # avec la nôtre. Namingway (921 / 941) est volontairement laissé à 0 : c'est une location AP.
    for number in (7, 8, 10, 11, 13, 14, 15, 16, 17, 18, 602, 604, 605, 622):
        block += struct.pack("<HHH", 0x14, 0, number)        # flag_on(0, number)
    block += struct.pack("<HHH", 0x14, 1, 615)               # flag_on(1, 615)
    # Tranche 2 : mur de glace du mont Hobs fondu dès le départ (flag 54), comme Free Enterprise :
    # sinon il faudrait Rydia dans l'équipe. Fire, qu'elle apprend dans cette scène, lui est donné
    # à son arrivée (characters.py) : un op17C ici était effacé quand op102 règle son niveau.
    block += struct.pack("<HHH", 0x14, 0, 54)
    block += struct.pack("<HHH", 0x15, 0, 6)                 # flag_off(0, 6)
    block += t00_04[0x00947:0x00963]                         # op0CB fondu, attendre, op05C, op0C6, op0C6
    block += (struct.pack("<H", 0x43) + b"t00_00\0"         # op043('t00_00', x, y, z, 0, 0, 0)
              + struct.pack("<iiiiiH", 106496, -20480, 1105920, 0, 0, 0))
    block += t00_04[0x009A7:0x009B3]                         # op00E(2, fin d'événement) + op005
    patch_script(rom, "t00_00", 0x00B57, block, expected=bytes.fromhex("2c 00 00 00 00 00"))
    patch_script(rom, "t00_00", 0x00B2A, goto(0x00B57), expected=bytes.fromhex("51 01 01 00 65 30"))

    # Étape C : entrer dans le château de Baron après le départ.
    # La grande porte de la cour (D07 -> j001) reste fermée ; essai 1 (objet 30) sans effet.
    # Essai 2 (actuel) : sur la carte du monde (f00), l'entrée du château (sortie j000) mène
    # directement à l'intérieur (t00_01), à l'endroit où l'on arrive en passant la grande porte.
    patch_script(rom, "f00", 0x00483,
                 b"t00_01\0" + struct.pack("<iii", 0, 0, -409600),
                 expected=b"t00_00\0" + struct.pack("<iii", 106496, -20480, -1105920))
    # Essai 3 : en ressortant de l'intérieur (t00_01, sortie j001), on arrivait dans la cour
    # derrière la grande porte fermée. On arrive maintenant devant la porte, côté sortie
    # (même position que celle utilisée par la carte du monde à l'origine).
    patch_script(rom, "t00_01", 0x003E4,
                 b"t00_00\0" + struct.pack("<iii", 106496, -20480, -1105920),
                 expected=b"t00_00\0" + struct.pack("<iii", 106496, -16384, 0))

    # Étape D : le lit de la chambre de Cecil (t00_14, segment 20).
    # op00F(0, 110, 0, ...) : tant que le flag 110 est à 0, le lit lance la nuit (Rosa) puis le départ
    # avec Kain (cinématique e03_00). On saute directement à la version "simple repos" du lit (031F3),
    # celle que le jeu utilise plus tard dans l'histoire.
    patch_script(rom, "t00_14", 0x03101, goto(0x031F3),
                 expected=bytes.fromhex("0f 00 00 00 6e 00 00 00 00 00 d9 b1 bf f6"))

    # Étape E : Grotte de la Brume (d00_00).
    # Segment 3 : la voix « Leave this place. » (deux zones, flags 20 et 21). Pas de changement de
    # carte : on remplace le début par flag_on(0, 20), flag_on(0, 21), retour.
    patch_script(rom, "d00_00", 0x002D1,
                 struct.pack("<HHH", 0x14, 0, 20) + struct.pack("<HHH", 0x14, 0, 21) + struct.pack("<H", 0x05),
                 expected=bytes.fromhex("08 00 01 00 0c 00 0a 00 00 00 d1 02 00 00"))
    # Segment 4 : le Dragon des Brumes.
    # Essai 1 : saut de 0093A à 00DD1 (juste avant le combat) -> après le combat, retour raté :
    #   joueur au centre de la carte du monde, flag 23 jamais activé, collisions absentes.
    # Essai 2 (actuel) : on garde toute la mise en scène (acteurs, caméra, fondu) et on ne saute
    #   que les dialogues et le choix oui / non : 00B1D -> 00CF7 (son, apparition du dragon,
    #   fondu, flag_on(0, 22), combat op042(901, ...)).
    patch_script(rom, "d00_00", 0x00B1D, goto(0x00CF7), expected=bytes.fromhex("5f 00 00 00 64 00"))

    # Étape F : Village de la Brume (t02_00) -> directement dans le désert, côté Kaipo.
    # À l'arrivée au village (segment 3, flag 24 à 0), le jeu retire la Carnelian Signet
    # (op073(9011, 1)) puis lance la cinématique de l'incendie (op151 'e04_01'), suivie du réveil
    # de Cecil dans le désert (t02_02, segment 3) : Kain quitte l'équipe, flags 24 et 26,
    # changement de carte vers la carte du monde.
    # On garde le retrait de la Signet et on remplace op151 par un saut vers un bloc ajouté à la
    # fin du script : la fin d'origine du réveil (t02_02, 0076A à 007F7 : op04A, op0D1, op1C0,
    # op059, Kain déséquipé + op069(2) départ, flags 24 / 26), fondu, arrêt de la musique,
    # op043 vers la carte du monde à l'endroit du réveil, fin d'événement.
    t02_02 = load_script(rom, "t02_02")
    # Essai 1 : fondu op0CB + attendre(25) -> écran noir prolongé.
    # Essai 2 : sans fondu -> écran noir quand même.
    # Essai 3 (actuel) : on reprend exactement la transition d'origine du réveil :
    #   op025(0, 10, 0), op0BA(12, 0, 10), attendre(12) (t02_02, 00754 à 0076A).
    block = t02_02[0x00754:0x007D4]                           # transition d'origine du réveil
    block += leave("Starting Character")                      # d'origine : Kain déséquipé, op069(2)
    block += t02_02[0x007EB:0x007F7]                          # flags 24, 26
    # Flags normalement activés par la cinématique (comparaison mémoire avec une partie normale) :
    # 614 = état de la carte du monde après le Titan (éboulement visible et solide), banque 1 : 617.
    block += struct.pack("<HHH", 0x14, 0, 614) + struct.pack("<HHH", 0x14, 1, 617)
    block += t00_04[0x0095F:0x00963]                          # op0C6(), op0C6() arrêt musique
    block += t02_02[0x007F7:0x00813]                          # op043('f00', -1044480, 0, -40960, ...)
    block += t00_04[0x009A7:0x009B3]                          # fin d'événement + op005
    target = append_script(rom, "t02_00", block)
    patch_script(rom, "t02_00", 0x00420, goto(target), expected=bytes.fromhex("51 01 04 00 65 30"))

    # Étape G : Kaipo.
    # Essai 1 : strip_scene (dialogues retirés) sur l'arrivée et la nuit à l'auberge -> fonctionnel,
    #   mais on veut sauter toute la séquence (et le combat contre les soldats).
    # Essai 2 (actuel) : à l'arrivée à Kaipo (t03_00, segment 3, après les tests des flags 29 et 28),
    #   à la place du "début d'événement", on exécute directement les effets de toute la séquence
    #   de l'auberge (t03_30) puis on rend la main : le joueur reste à l'entrée de Kaipo.
    #     - Rydia rejoint l'équipe : op068(4), op102(4, 7), équipement, sorts (op17C) — copiés de t03_30
    #     - flags 28 (soldiers), 31 (Whyt), 29 (Rydia), 753, 754
    block = join("Kaipo Character")                           # d'origine : Rydia (t03_30, 0124C)
    for number in (28, 31, 29, 753, 754):
        block += struct.pack("<HHH", 0x14, 0, number)
    block += struct.pack("<H", 0x05)                          # retour
    patch_script(rom, "t03_00", 0x00A16, goto(append_script(rom, "t03_00", block)),
                 expected=bytes.fromhex("0e 00 02 00 00 00 73 4d 74 b6"))

    # Étape H : première visite à Rosa (t03_01, segment 3, 00328 à 00653).
    # Déclenchée en entrant dans la zone près du lit (op124). Pas de changement de carte ni de combat :
    # on remplace la scène par ses effets : donner l'augment Auto-Potion (location AP, le client
    # retire l'objet d'origine), op15C('j001', 1, 0, 0) comme à la fin de la scène, flag 30, retour.
    t03_01 = load_script(rom, "t03_01")
    block = t03_01[0x005AC:0x005B1]                           # donner_objet(9136 Auto-Potion, 1)
    block += t03_01[0x00622:0x00631]                          # op15C('j001', 1, 0, 0)
    block += struct.pack("<HHH", 0x14, 0, 30) + struct.pack("<H", 0x05)
    patch_script(rom, "t03_01", 0x00328, block, expected=bytes.fromhex("0e 00 02 00 00 00 73 4d 74 b6"))
    # Namingway explique l'augment en sortant de la pièce (t03_00, segment 8, conditions : flag 966 à 0,
    # flags 30 et 29 à 1). On le marque comme fait : flag_on(0, 966), retour.
    patch_script(rom, "t03_00", 0x012E8, struct.pack("<HHH", 0x14, 0, 966) + struct.pack("<H", 0x05),
                 expected=bytes.fromhex("0e 00 02 00 00 00 73 4d 74 b6"))

    # Étape I : Rivière souterraine (d01_xx).
    # d01_00 segment 3 : rencontre de Tellah. Mécanisme : parler à Tellah (segment 20) ouvre un
    #   événement et active le flag temporaire (10, 6) ; la boucle du segment 3 attend ce flag puis
    #   appelle la scène (fonction en 002E3), qui se termine par la fin d'événement.
    #   Essais 1 et 2 (remplacer la scène par ses effets, avec ou sans fin d'événement) : jeu figé.
    #   Essai 3 (actuel) : on garde toute la mise en scène et on retire seulement les dialogues.
    strip_scene(rom, "d01_00", 0x0027B, 0x00865)
    # Arrivée de Tellah (00806 : op068(6), op102(6, 13), op0AC(6, ...), jusqu'à 00825) remplacée
    # par celle du personnage tiré au sort, dans un bloc ajouté.
    block = join("Waterway Character") + goto(0x00825)
    patch_script(rom, "d01_00", 0x00806, goto(append_script(rom, "d01_00", block)),
                 expected=struct.pack("<HIB", 0x68, 6, 0)[:6])
    # d01_03 segment 3 : halte de Cecil et Tellah (« We can rest here. »), flag 33. Rien d'autre.
    patch_script(rom, "d01_03", 0x001A7, struct.pack("<HHH", 0x14, 0, 33) + struct.pack("<H", 0x05),
                 expected=bytes.fromhex("0e 00 02 00 00 00 73 4d 74 b6"))
    # d01_06 segment 3 : « From here we must travel outside for a time. », flag 34.
    patch_script(rom, "d01_06", 0x00234, struct.pack("<HHH", 0x14, 0, 34) + struct.pack("<H", 0x05),
                 expected=bytes.fromhex("0e 00 02 00 00 00 73 4d 74 b6"))
    # d01_07 segment 3 : scène avant le boss, avec changements de carte vers d01_08 -> on ne retire
    #   que les dialogues. d01_09 segment 3 : Octomammoth -> idem, le combat (op042(904)) est gardé.
    strip_scene(rom, "d01_07", 0x00164, 0x01380)
    strip_scene(rom, "d01_09", 0x00274, 0x00900)

    # Étape J : château de Damcyan (t04_04, sommet). Mécanisme identique à Tellah : parler à Anna
    #   (segment 32 ou 48) ouvre un événement et active le flag temporaire (10, 11) ; le segment 3
    #   attend ce flag (op009) puis joue : mort d'Anna, combat Tellah contre Edward (op042(905)),
    #   Tellah part, Edward rejoint, cinématique de l'hovercraft (op151(5, ..., 'f00')), puis sur la
    #   carte du monde la scène de l'hovercraft (f00, segment 6 : flags 44 et 900, op0B3 = position).
    # Essai 1 : juste après l'attente (0037D), on exécute directement les effets, puis la fermeture
    #   d'écran d'origine (op024(2, 10, 0), attendre) et la fin d'événement (ouverte en parlant à Anna) :
    #     - Tellah part, Edward rejoint (niveau, équipement) — copiés de t04_04 00838
    #     - flags 41, 42 (scène), 43, 44 (hovercraft), 900 (hovercraft disponible)
    #     - op0B3(1, ...) : hovercraft posé devant Damcyan — copié de f00 01B55
    t04_04 = load_script(rom, "t04_04")
    f00 = load_script(rom, "f00")
    block = leave("Waterway Character") + join("Damcyan Character")   # d'origine : t04_04 00838
    # Véhicules en objets (18/10/2026) : l'hovercraft n'est plus donné ici (ni flag 900, ni op0B3) ;
    #   le flag 44 sert de location, le client pose l'hovercraft quand l'objet est reçu.
    for number in (41, 42, 43, 44):
        block += struct.pack("<HHH", 0x14, 0, number)
    if not vehicle_items:                                      # patch seul : hovercraft donné ici
        block += struct.pack("<HHH", 0x14, 0, 900) + f00[0x01B55:0x01B73]   # op0B3(1, 81920, 8192, -3153920)
    block += f00[0x01B8D:0x01B97]                              # op024(2, 10, 0)
    block += struct.pack("<HH", 0x08, 15)                      # attendre(15)
    block += t00_04[0x009A7:0x009B3]                           # fin d'événement + op005
    patch_script(rom, "t04_04", 0x0037D, block, expected=bytes.fromhex("25 00 02 00 00 00 0a 00 00 00"))

    # Étape K : Antre de l'Antlion (d02_04, segment 3, zone près du nid). Même approche que
    #   l'Octomammoth : on garde la mise en scène et le combat (op042(906)), on retire les dialogues.
    #   La fin de la scène donne la Sand Pearl (donner_objet(9004)) et active le flag 47.
    strip_scene(rom, "d02_04", 0x00132, 0x00A8D)

    # Étape L : Rosa soignée à Kaipo (t03_01). Mécanisme comme Damcyan : parler à Rosa (segment 20)
    #   ouvre un événement et le menu Objets ; utiliser la Sand Pearl (op076(9004, 0205E)) active le
    #   flag temporaire (10, 5) sans fermer l'événement. Le segment 3 attend ce flag (op009) puis
    #   appelle la scène de guérison (00655, se termine par op043 vers t03_00), la nuit à Kaipo
    #   (t03_00 segment 4 : Edward, combat contre les Sahagin op042(907), flag 50, cinématique),
    #   puis le matin (01061 : repos, « Best be moving », flag 52).
    # Essai 1 : à la place de l'appel de la scène (002DE), on saute vers un bloc ajouté :
    #     - fondu au noir (copié de d02_04 009EB), attendre(12)
    #     - Rosa rejoint l'équipe (niveau, équipement), Sand Pearl retirée — copiés de t03_01 00FFC
    #     - Rosa endormie (acteur 20) retirée de la pièce : op02B(20, 0)
    #     - flags 49 (objectif), 50 (nuit faite), 52 (matin fait)
    #     - repos (soins) : flag 990 + fonction globale, copiés de t03_01 010A5
    #     - réouverture de l'écran op024(2, 10, 0), attendre(15), fin d'événement, retour
    block = load_script(rom, "d02_04")[0x009EB:0x009F5] + struct.pack("<HH", 0x08, 12)
    block += join("Rosa Character")                            # d'origine : t03_01 00FFC
    block += t03_01[0x0101D:0x0102C]                           # op073(9004, 1), op00E(2, 3278489185)
    block += struct.pack("<HHB", 0x2B, 20, 0)                  # op02B(20, 0)
    for number in (49, 50, 52):
        block += struct.pack("<HHH", 0x14, 0, number)
    block += t03_01[0x010A5:0x010BB]                           # repos
    block += f00[0x01B8D:0x01B97] + struct.pack("<HH", 0x08, 15)
    block += t00_04[0x009A7:0x009B3]                           # fin d'événement + op005
    patch_script(rom, "t03_01", 0x002DE, goto(append_script(rom, "t03_01", block)),
                 expected=bytes.fromhex("0e 00 00 00 00 00 0e 6d 4f 97"))

    # Étape M0 : mur de glace du mont Hobs (d03_00, segment 1). D'origine, en 000F4 : op006(0, 54)
    #   (si le mur a fondu, retour) puis le mur est placé (op028(47) …). On active le flag 54 juste
    #   avant ce test : le mur n'est jamais placé, même avec une sauvegarde d'avant le patch.
    block = struct.pack("<HHH", 0x14, 0, 54) + struct.pack("<H", 0x05)      # flag_on(0, 54), retour
    patch_script(rom, "d03_00", 0x000F4, goto(append_script(rom, "d03_00", block)),
                 expected=bytes.fromhex("06 00 00 00 36 00"))

    # Étape M : sommet du mont Hobs (d03_02, segment 3). Le segment 3 : flag 57 -> fin ; flag 56 -> fonction
    #   00ACF (après le combat, discussion avec Yang, flag 57) ; flag 58 -> fonction 0068E (Mom Bomb :
    #   op1AE(1, 1) restauration de l'équipe, flag 56, op042(909, 10, 0, 1, 0)) ; sinon zone (op124) ->
    #   0025E : mise en scène, op1B9(0, 0) sauvegarde de l'équipe, Yang rejoint, op069(0, 3, 4, 9),
    #   flags 55 et 444, cinématique op151(7) (c'est elle qui active le flag 58), fin d'événement.
    # Essai 1 : op1B9 / op1AE neutralisés -> écran noir. Essai 2 : seule la cinématique sautée -> écran noir :
    #   le flag 58 n'était jamais activé, Mom Bomb ne se déclenchait pas.
    # Essai 3 : dialogues retirés partout (strip_scene) ; dès l'entrée dans la zone (0025E, à la
    #   place du début d'événement) : arrivée du personnage tiré (et départ du plus ancien si l'équipe est
    #   pleine), op1B9(0, 0) (l'équipe complète est sauvegardée pour le combat), flags 55, 444, 58, retour.
    #   Puis appel direct de la partie Mom Bomb (combat gardé).
    strip_scene(rom, "d03_02", 0x0025E, 0x01E5E)
    # Essai 3 : Mom Bomb n'arrivait qu'après être sorti et revenu (le segment ne teste le flag 58 qu'au
    #   chargement de la carte). Essai 4 : appel direct de 0068E -> le début de sa mise en scène (caméra,
    #   personnages qui avancent) se voyait, et la discussion d'après-combat (00ACF) restait.
    # Essai 5 : plus de mise en scène ; flag 57 activé avant le combat pour sauter 00ACF -> après le
    #   combat, le joueur réapparaissait sur le pont (c'est 00ACF qui le replace au sommet).
    # Essai 6 : 00ACF remplacée (ci-dessous), mais le joueur revenait du combat sur la carte précédente
    #   (le pont) : op1BA(0, 0) de 0068E (00875) manquait. Sans lui, le point de retour du combat n'est
    #   pas mis à jour. Il n'existe que deux fois dans le jeu (ici et d04_04, avant un changement de carte).
    # Essai 7 : op1BA(0, 0) ajouté juste avant op1AE -> le jeu se fige : à l'origine l'écran est déjà
    #   noir (la zone commence par op025(2, 10, 0), retiré depuis l'essai 3).
    # Essai 8 (actuel) : début d'origine de la zone gardé (événement + fondu au noir), op1BA. Avant le combat (zone 0025E), dans un événement : arrivée du personnage,
    #   op1B9(0, 0), flags 55, 444, 58, 56, puis la fin de 0068E : op1AE(1, 1) et le combat.
    #   Au retour (flag 56 -> 00ACF), 00ACF est remplacée par un bloc court : écran fermé, joueur
    #   replacé comme à l'origine (op105, op09F, op02C, op087 copiés de 013DF), écran rouvert, flag 57.
    script = load_script(rom, "d03_02")
    begin, end = script[0x0025E:0x00268], script[0x01446:0x01452]      # début / fin d'événement + op005
    block = script[0x0025E:0x00276]                            # début d'événement, op025(2, 10, 0) (fondu au noir), attendre
    block += join("Mt Hobs Character")
    block += struct.pack("<HII", 0x1B9, 0, 0)                 # op1B9(0, 0) : sauvegarde de l'équipe
    for number in (55, 444, 58, 56):
        block += struct.pack("<HHH", 0x14, 0, number)
    block += script[0x00875:0x00883]                           # op1BA(0, 0), attendre(3) : point de retour du combat
    block += script[0x00AB7:0x00ACF]                           # op1AE(1, 1), op042(909, ...), fin d'événement, op005
    patch_script(rom, "d03_02", 0x0025E, goto(append_script(rom, "d03_02", block)),
                 expected=bytes.fromhex("0e 00 02 00 00 00 73 4d 74 b6"))

    block = begin + script[0x00AD9:0x00AE7]                    # op025(2, 10, 0), attendre(12)
    block += script[0x013DF:0x01418]                           # joueur replacé, caméra
    block += script[0x01432:0x01440]                           # op024(2, 10, 0), attendre(15)
    block += struct.pack("<HHH", 0x14, 0, 57) + end            # flag 57, fin d'événement, op005
    patch_script(rom, "d03_02", 0x00ACF, goto(append_script(rom, "d03_02", block)),
                 expected=bytes.fromhex("0e 00 02 00 00 00 73 4d 74 b6"))

    # Étape N : défense de Fabul (t05_03, salle du trône). D'origine : à l'arrivée (segment 3, flag 62 non
    #   activé), audience avec le roi, Rosa et Rydia restent en arrière (op069(3), op069(4)), flag 62, retour
    #   à l'entrée (t05_00) ; puis six combats répartis sur t05_00, t05_01, t05_02 et t05_03 (flags 63 à 68,
    #   chacun déclenché au chargement de la carte), Kain (t05_10, op042(914), défaite scénarisée, flags 69,
    #   70, cinématique op151(8) : Rosa enlevée), nuit (t05_30, flag 73), le roi donne Deathbringer (t05_09,
    #   flag 74), port (t05_90 : augment Counter, flag 75), bateau (f00, t05_91), Léviathan (t05_92 : Rydia,
    #   Edward, Yang partent, flag 85) et arrivée sur la côte de Mysidia.
    # Essai 1 (actuel) : à l'arrivée dans la salle du trône, les six combats s'enchaînent, sans rien d'autre.
    #   Le segment 3 de t05_03 saute vers un aiguillage ajouté, rejoué à chaque chargement de la carte (donc
    #   au retour de chaque combat) : chaque combat active son flag puis lance le combat (op1AE(0, 0) +
    #   op042, comme à l'origine). Les flags 63, 64, 66, 67, 68 servent de compteur (65 est évité : il
    #   réveille le segment 4 d'origine). Avant le dernier combat : flags 65, 69, 70 (défense et Kain
    #   terminés ; Kain est sauté, comme dans Free Enterprise). Au retour : fondu, départ du personnage de
    #   l'emplacement de Rosa (enlevée), flag 62, écran rouvert.
    base = append_position(rom, "t05_03")
    battle = lambda flag, group: (struct.pack("<HHH", 0x14, 0, flag) + struct.pack("<HHH", 0x14, 0, 444)
                                  + struct.pack("<HBB", 0x1AE, 0, 0) + struct.pack("<HHBBBB", 0x42, group, 26, 0, 1, 0))
    begin, end = BEGIN_EVENT, END_EVENT + struct.pack("<H", 0x05)
    steps = [(None, 63, 911), (63, 64, 912), (64, 66, 911), (66, 67, 913), (67, 68, 912)]
    bodies = [begin + battle(flag, group) + end for _, flag, group in steps]
    last = begin
    for number in (65, 69, 70):
        last += struct.pack("<HHH", 0x14, 0, number)
    last += battle(68, 911)[6:] + end                          # flag 68 déjà actif : on ne garde que 444 + combat
    post = begin + struct.pack("<HIHH", 0x25, 2, 10, 0) + struct.pack("<HH", 0x08, 10)
    post += leave("Rosa Character") + struct.pack("<HHH", 0x14, 0, 62)
    post += struct.pack("<HIHH", 0x24, 2, 10, 0) + struct.pack("<HH", 0x08, 10) + end
    # Aiguillage : op006(62) fin ; si 70 -> post ; si 68 -> dernier ; si 67, 66, 64, 63 -> combat suivant.
    tests = [(70, "post"), (68, "last"), (67, 4), (66, 3), (64, 2), (63, 1)]
    head_size = 6 + 10 * len(tests)
    blocks = {0: bodies[0], 1: bodies[1], 2: bodies[2], 3: bodies[3], 4: bodies[4], "last": last, "post": post}
    position, where = base + head_size, {}
    for key in (0, 1, 2, 3, 4, "last", "post"):
        where[key] = position
        position += len(blocks[key])
    code = struct.pack("<HHH", 0x06, 0, 62)
    for flag, key in tests:
        code += struct.pack("<HHHI", 0x0C, 0, flag, where[key])
    for key in (0, 1, 2, 3, 4, "last", "post"):
        code += blocks[key]
    assert append_script(rom, "t05_03", code) == base
    patch_script(rom, "t05_03", 0x002EF, goto(base), expected=bytes.fromhex("06 00 00 00 3e 00"))

    # Étape N2 : la nuit dans la grande salle (t05_30, zone, flag 70 sans 73) ne se joue plus : elle mène à la
    #   scène automatique de l'épée (t05_09, segment 3, flag 73). C'est le roi qui s'en charge (étape O).
    patch_script(rom, "t05_30", 0x0025A, struct.pack("<H", 0x05) + NOP + NOP,
                 expected=bytes.fromhex("06 00 00 00 49 00"))

    # Étape O : parler au roi dans sa chambre (t05_09, segment 21 ; il n'est là qu'après la défense).
    #   D'origine : flag 122 -> réplique tardive, flag 74 -> « le bateau vous attend », sinon (0074B)
    #   « reposez-vous ». À la place de 0074B, saut vers un bloc ajouté :
    #     - Deathbringer (op044(6003), flag 74) et augment Counter (op044(9139), flag 75, d'origine au port) :
    #       ce sont deux locations, le client remplace les objets ;
    #     - flags du voyage en bateau et du Léviathan : 73, 78 à 83, 85, 444, 448 (relevés dans f00, t05_91,
    #       t05_92 ; le flag 6, posé juste avant chaque cinématique op151, n'est pas repris) ;
    #     - départs du Léviathan (emplacements de Rydia, Edward, Yang), avec character_departures = vanilla ;
    #     - fondu, op043 vers la côte de Mysidia (copié de t05_92 00453), fin d'événement.
    block = BEGIN_EVENT + struct.pack("<HHB", 0x44, 6003, 1) + struct.pack("<HHH", 0x14, 0, 74)
    block += struct.pack("<HHB", 0x44, 9139, 1) + struct.pack("<HHH", 0x14, 0, 75)
    for number in (73, 78, 79, 80, 81, 82, 83, 85, 444, 448):
        block += struct.pack("<HHH", 0x14, 0, number)
    block += leave("Kaipo Character") + leave("Damcyan Character") + leave("Mt Hobs Character")
    block += struct.pack("<HIHH", 0x25, 2, 10, 0) + struct.pack("<HH", 0x08, 15)
    block += load_script(rom, "t05_92")[0x00453:0x0046F]      # op043('f00', 1495040, 0, 3932160, 0, 0, 0)
    block += END_EVENT + struct.pack("<H", 0x05)
    patch_script(rom, "t05_09", 0x0074B, goto(append_script(rom, "t05_09", block)),
                 expected=BEGIN_EVENT)

    # Étape P : Mysidia, maison de l'Ancien (t06_01, segment 3). D'origine : zone (op124) à l'entrée de la
    #   salle (flags 358 et 90 non activés) -> longue audience, Porom (op068(7)) et Palom (op068(8)) rejoignent
    #   au niveau 10 avec leur équipement, flag 90 (le reste du village et la sortie vers le mont Ordeals en
    #   dépendent). Recette 1 : à la place du début d'événement (00445), les deux arrivées + flag 90 + op005.
    block = join("Mysidia Character 1") + join("Mysidia Character 2")
    block += struct.pack("<HHH", 0x14, 0, 90) + struct.pack("<H", 0x05)
    patch_script(rom, "t06_01", 0x00445, goto(append_script(rom, "t06_01", block)), expected=BEGIN_EVENT)

    # Étape P2 : retour du paladin chez l'Ancien (t06_01, segment 4 : flag 107 activé, 110 non activé, zone
    #   03611). D'origine : longue scène, flag 109, cinématique op151(26), puis la suite (fonction au flag
    #   109) qui active le flag 110 (chemin maudit rouvert). Aucun effet sur l'équipe. Recette 1 : à la place
    #   du début d'événement (0363B), flags 109 et 110, retour.
    block = struct.pack("<HHH", 0x14, 0, 109) + struct.pack("<HHH", 0x14, 0, 110) + struct.pack("<H", 0x05)
    elder_flags = append_script(rom, "t06_01", block)
    patch_script(rom, "t06_01", 0x0363B, goto(elder_flags), expected=BEGIN_EVENT)
    #   Essai 1 : jeu figé en parlant ensuite à l'Ancien : sa réplique (segment 22, branche flag 107, 058DD)
    #   ouvre un événement et active le flag temporaire (10, 5), attendus par la seconde partie de la scène
    #   (supprimée), qui fermait l'événement. L'Ancien reste dans la pièce jusqu'au prochain chargement.
    #   Essai 2 : cette réplique sautait vers les flags 109 et 110, sans événement -> écran noir (une
    #   discussion avec un personnage doit ouvrir puis fermer un événement).
    #   Essai 3 (actuel) : début d'événement, flags 109 et 110, fin d'événement.
    block = BEGIN_EVENT + struct.pack("<HHH", 0x14, 0, 109) + struct.pack("<HHH", 0x14, 0, 110)
    block += END_EVENT + struct.pack("<H", 0x05)
    patch_script(rom, "t06_01", 0x058DD, goto(append_script(rom, "t06_01", block)), expected=BEGIN_EVENT)

    # Étape Q : chemin maudit (Devil's Road) ouvert dès le départ (monde ouvert). D'origine, il n'ouvre
    #   qu'avec le flag 110 (Cecil paladin, revenu voir l'Ancien) :
    #     - Mysidia (t06_00, segment 1) : 0032C op006(0, 110) -> sans le flag, le garde (acteur 25) est placé
    #       devant la porte ; 0051F op00D(0, 110, …) -> sans le flag, la sortie j006 vers t06_04 n'existe pas ;
    #     - Baron (t01_03, segment 3) : 0024A op00C(0, 110, 973) -> sans le flag, « The Mysidian exit is
    #       sealed » et le joueur est repoussé.
    #   On fait comme si le flag était activé : retour avant le garde, sortie toujours définie, saut direct
    #   vers la zone du passage côté Baron.
    patch_script(rom, "t06_00", 0x0032C, struct.pack("<H", 0x05) + NOP + NOP, expected=bytes.fromhex("06 00 00 00 6e 00"))
    patch_script(rom, "t06_00", 0x0051F, NOP * 5, expected=bytes.fromhex("0d 00 00 00 6e 00 76 05 00 00"))
    patch_script(rom, "t01_03", 0x0024A, goto(973) + NOP * 2, expected=bytes.fromhex("0c 00 00 00 6e 00 cd 03 00 00"))

    # Étape R : mont Ordeals (d04_00 à d04_04).
    flag_on = lambda number: struct.pack("<HHH", 0x14, 0, number)
    fade_out = struct.pack("<HIHH", 0x25, 2, 10, 0) + struct.pack("<HH", 0x08, 10)    # op025(2, 10, 0), attendre
    fade_in = struct.pack("<HIHH", 0x24, 2, 10, 0) + struct.pack("<HH", 0x08, 10)     # op024(2, 10, 0), attendre
    end = END_EVENT + struct.pack("<H", 0x05)
    # R1 : pied de la montagne (d04_00). D'origine, le feu (effet e469 + obstacle, acteur 30) est placé tant
    #   que le flag 94 n'est pas activé (segment 1, deux copies : 00138, 0026B) ; la zone du segment 3
    #   (00 2BC, flags 95/94/90) joue la scène où Palom fait fondre le feu (carte d07_07, flags 143, 93, 94),
    #   puis la suite (flag 95). Monde ouvert : le feu n'est jamais placé, et la zone active les flags 93, 94,
    #   95 sans rien jouer (même sans Palom dans l'équipe).
    for position in (0x00138, 0x0026B):
        patch_script(rom, "d04_00", position, struct.pack("<H", 0x05) + NOP + NOP, expected=bytes.fromhex("06 00 00 00 5e 00"))
    block = flag_on(93) + flag_on(94) + flag_on(95) + struct.pack("<H", 0x05)
    patch_script(rom, "d04_00", 0x002BC, goto(append_script(rom, "d04_00", block)), expected=bytes.fromhex("06 00 00 00 5f 00"))
    # R2 : Tellah (d04_01, segment 3, zone) : à la place de la scène (00190), le personnage tiré rejoint,
    #   flag 96 (recette 1).
    block = join("Ordeals Character") + flag_on(96) + struct.pack("<H", 0x05)
    patch_script(rom, "d04_01", 0x00190, goto(append_script(rom, "d04_01", block)), expected=BEGIN_EVENT)
    # R3 : sommet (d04_03). Segment 3 (zones des « *hiss* », flags 97, 98) : désactivé (001AC op006(0, 100)
    #   -> retour).
    patch_script(rom, "d04_03", 0x001AC, struct.pack("<H", 0x05) + NOP + NOP, expected=bytes.fromhex("06 00 00 00 64 00"))
    # R4 : Scarmiglione, les deux combats enchaînés. D'origine : segment 4 = zone -> mise en scène, flag 99,
    #   op042(915) ; au retour (flag 99) fonction 00C85 (fondu, flag 100). Segment 5 = autre zone -> mise en
    #   scène, flag 101, op042(916, 11, 1) ; au retour (flag 101) fonction 010C5 (mort de Scarmiglione,
    #   op17B(0, 0), flag 102).
    #   Essai 1 (actuel) : les deux zones (0085E, 00D36) lancent le premier combat sans mise en scène
    #   (fondu, flag 99, op042(915)). Le segment 4 s'arrête dès le flag 99 (0081C). Le segment 5 saute vers un
    #   aiguillage : flag 102 -> fin ; flag 101 -> après-combat court (fondu, op17B(0, 0), flag 102, écran
    #   rouvert) ; flag 99 -> second combat (flags 100, 101, op042(916)) ; sinon sa zone d'origine.
    d04_03 = load_script(rom, "d04_03")
    first = BEGIN_EVENT + fade_out + flag_on(99) + struct.pack("<HHBBBB", 0x42, 915, 11, 0, 0, 0) + end
    first_at = append_script(rom, "d04_03", first)
    patch_script(rom, "d04_03", 0x0085E, goto(first_at), expected=BEGIN_EVENT)
    patch_script(rom, "d04_03", 0x00D36, goto(first_at), expected=BEGIN_EVENT)
    patch_script(rom, "d04_03", 0x0081C, struct.pack("<HHH", 0x06, 0, 99) + NOP * 4,
                 expected=bytes.fromhex("0f 00 00 00 63 00 00 00 00 00 d1 fe 17 d8"))
    second = BEGIN_EVENT + flag_on(100) + flag_on(101) + struct.pack("<HHBBBB", 0x42, 916, 11, 1, 0, 0) + end
    after = BEGIN_EVENT + fade_out + d04_03[0x01426:0x01430] + fade_in + flag_on(102) + end   # op17B(0, 0)
    base = append_position(rom, "d04_03")
    head = struct.pack("<HHH", 0x06, 0, 102)
    head_size = len(head) + 10 + 10 + 6
    second_at, after_at = base + head_size, base + head_size + len(second)
    head += struct.pack("<HHHI", 0x0C, 0, 101, after_at) + struct.pack("<HHHI", 0x0C, 0, 99, second_at) + goto(0x00D06)
    assert append_script(rom, "d04_03", head + second + after) == base
    patch_script(rom, "d04_03", 0x00CEE, goto(base), expected=bytes.fromhex("06 00 00 00 66 00"))
    # R5 : l'antre (d04_03, segment 6, zone 0198E). D'origine : mise en scène, la voix, Cecil devient paladin
    #   (repos, op0AC + op069(0), op068(1), op0AC(1, 0, 6004, …)), op1B9 et départ de Tellah, Porom, Palom
    #   (Cecil seul pour l'épreuve), cinématique op151(10, 'e10_01') (elle active les flags 714 et 105 et mène
    #   à d04_04), d04_04 segment 3 : scène du paladin, Tellah retrouve ses sorts (op17C), repos, flag 106,
    #   retour à d04_03 ; fonction 01CE4 : op1D1 (équipe rétablie), flag 107 (Cecil paladin).
    #   À la place : fondu, Cecil devient paladin (copié de 01C2F), sorts de Tellah (copiés de d04_04 00BBE),
    #   flags 104, 105, 714, 106, 107, écran rouvert. L'équipe reste au complet.
    block = BEGIN_EVENT + fade_out + d04_03[0x01C2F:0x01C8D]
    block += load_script(rom, "d04_04")[0x00BBE:0x00D08]
    for number in (104, 105, 714, 106, 107):
        block += flag_on(number)
    block += fade_in + end
    patch_script(rom, "d04_03", 0x0198E, goto(append_script(rom, "d04_03", block)), expected=BEGIN_EVENT)

    # ===================================================================== #
    # Tranche 3 : Baron (auberge, Ancient Waterway, château) jusqu'à l'Enterprise
    # ===================================================================== #
    # Étape S : auberge de Baron (t01_30, segment 3). D'origine (flags 114 non activé et 110 activé) : en
    #   parlant à l'aubergiste (flag temporaire 10, 5), fonction 00484 : gardes, flag 112, op042(918) ;
    #   au retour (flag 112) fonction 006EC : Yang, flag 113, op1AE(0, 1), op042(919) ; au retour (flag 113)
    #   fonction 008BA : Yang rejoint (op068(10)), Baron Key (op044(9008)), repos, flag 114.
    #   Monde ouvert : la condition du flag 110 (paladin revenu à Mysidia) est retirée. Les trois fonctions
    #   ne gardent que les combats ; à la fin, le personnage tiré (emplacement de Yang) rejoint et la
    #   Baron Key est donnée (location : le client la remplace).
    patch_script(rom, "t01_30", 0x00450, NOP * 3, expected=bytes.fromhex("07 00 00 00 6e 00"))
    block = fade_out + flag_on(112) + flag_on(444) + struct.pack("<HBB", 0x1AE, 0, 0)
    block += struct.pack("<HHBBBB", 0x42, 918, 26, 0, 1, 0) + end
    patch_script(rom, "t01_30", 0x00484, goto(append_script(rom, "t01_30", block)),
                 expected=bytes.fromhex("25 00 02 00 00 00 0a 00 00 00"))
    block = BEGIN_EVENT + flag_on(113) + struct.pack("<HBB", 0x1AE, 0, 1)
    block += struct.pack("<HHBBBB", 0x42, 919, 26, 0, 1, 0) + end
    patch_script(rom, "t01_30", 0x006EC, goto(append_script(rom, "t01_30", block)), expected=BEGIN_EVENT)
    t01_30 = load_script(rom, "t01_30")
    block = BEGIN_EVENT + fade_out + join("Baron Character") + struct.pack("<HHB", 0x44, 9008, 1)
    block += t01_30[0x014FD:0x01513] + fade_in + flag_on(114) + end            # repos (flag 990)
    patch_script(rom, "t01_30", 0x008BA, goto(append_script(rom, "t01_30", block)), expected=BEGIN_EVENT)

    # Étape T : Baigan (t00_01, segment 4 : flags 117 non activé et 114 activé, zone). Fonction 00592
    #   (mise en scène, puis 00DED : flag 116, op042(920)) remplacée par : fondu, flag 116, combat. Au retour
    #   (flag 116) fonction 00B43 : à la place de la mise en scène, sa fin (00D73 : fondu, joueur replacé,
    #   écran rouvert) et le flag 117.
    block = BEGIN_EVENT + fade_out + flag_on(116) + struct.pack("<HHBBBB", 0x42, 920, 26, 0, 0, 0) + end
    patch_script(rom, "t00_01", 0x00592, goto(append_script(rom, "t00_01", block)), expected=BEGIN_EVENT)
    block = BEGIN_EVENT + load_script(rom, "t00_01")[0x00D73:0x00DDB] + flag_on(117) + end
    patch_script(rom, "t00_01", 0x00B43, goto(append_script(rom, "t00_01", block)), expected=BEGIN_EVENT)

    # Étape U : Cagnazzo (t00_06, salle du trône, segment 4, au chargement de la carte). D'origine : flags
    #   119 non activé et 110 activé ; fonction 012EC (mise en scène, flag 118, op042(921)) ; au retour
    #   (flag 118) fonction 019FB : Palom et Porom pétrifiés (op069(7), op069(8)), Cid rejoint (op068(11),
    #   niveau 20), cinématique op151(11) (flag 119), scène de Golbez (d07_07, flag 121), Cid ouvre le hangar
    #   (t00_04), l'Enterprise (t19_04 : flag 901), décollage (f00 segment 6 : flag 122, op0B3(2, …)).
    #   Monde ouvert : Cagnazzo attend Baigan (flag 117) au lieu du flag 110. Avant : fondu, flag 118, combat.
    #   Après : fondu, départs des emplacements de Porom et Palom, arrivée du personnage tiré (emplacement de
    #   Cid), flags 119, 121, 122, 901, Enterprise posée devant le château (op0B3 copié de f00 01E43),
    #   écran rouvert.
    patch_script(rom, "t00_06", 0x012CC, struct.pack("<HHH", 0x07, 0, 117), expected=bytes.fromhex("07 00 00 00 6e 00"))
    block = BEGIN_EVENT + flag_on(118) + flag_on(444) + struct.pack("<HHBBBB", 0x42, 921, 26, 0, 0, 0) + end
    patch_script(rom, "t00_06", 0x012EC, goto(append_script(rom, "t00_06", block)), expected=BEGIN_EVENT)
    block = BEGIN_EVENT + fade_out + leave("Mysidia Character 1") + leave("Mysidia Character 2")
    block += join("Cid Character")
    #   Essai 1 : en ressortant du château, la cinématique de l'Enterprise (f00 segment 6, flag 122 sans 123 :
    #   op151(12), Kain et le message de Golbez) se jouait. Essai 2 (actuel) : flags relevés par comparaison
    #   mémoire avant / après cette scène (17/10/2026) : 123, 124, 629, 633 (chaîne de scénario), 716.
    #   Véhicules en objets (18/10/2026) : l'Enterprise n'est plus donnée ici (ni flag 901, ni op0B3) ;
    #   le flag 124 sert de location, le client pose l'Enterprise quand l'objet est reçu.
    for number in (119, 121, 122, 123, 124, 629, 633, 716):
        block += flag_on(number)
    if not vehicle_items:                                      # patch seul : Enterprise donnée ici
        block += flag_on(901) + load_script(rom, "f00")[0x01E43:0x01E61]   # op0B3(2, -978944, 102400, 1658880)
    block += fade_in + end
    patch_script(rom, "t00_06", 0x019FB, goto(append_script(rom, "t00_06", block)), expected=BEGIN_EVENT)

    # ===================================================================== #
    # Tranche 4 : Troia, caverne magnétique, tour de Zott                    #
    # ===================================================================== #
    battle = lambda group, scene, flag_a, flag_b: struct.pack("<HHBBBB", 0x42, group, scene, flag_a, flag_b, 0)
    # Étape V : Edward (t11_03, chambre d'Edward, segment 3, zone) donne la Whisperweed (op044(9009)),
    #   flag 128 (location). Recette 1. Sa seconde scène (segment 5, retour avec la Terre : augments,
    #   flag 140) est remplacée par le flag 140.
    block = struct.pack("<HHB", 0x44, 9009, 1) + flag_on(128) + struct.pack("<H", 0x05)
    patch_script(rom, "t11_03", 0x002A8, goto(append_script(rom, "t11_03", block)), expected=BEGIN_EVENT)
    block = flag_on(140) + struct.pack("<H", 0x05)
    patch_script(rom, "t11_03", 0x01E22, goto(append_script(rom, "t11_03", block)), expected=BEGIN_EVENT)

    # Étape W : l'Elfe noir (d06_09, segment 3). D'origine : parler à l'Elfe noir (segment 20, flag temporaire
    #   10, 10) -> fonction 0046C : combat perdu d'avance (op042(922 ou 923)), flags 131, 132, Edward joue de
    #   la harpe à Troia (t11_03 segment 4, flag 133), retour, flag 134, dragon (flags 135, op1AE(1, 1),
    #   op042(924)) ; au retour (flag 135) fonction 00F9B (flag 136) ; la Terre (segment 30 : op044(9006),
    #   flag 137).
    #   À la place de 0046C : menu des objets (op106) et op076(9009) : avec la Whisperweed, fondu, flags 131
    #   à 135, fin du champ magnétique (flag 915 désactivé), dragon ; sinon fin de l'événement. Au retour :
    #   fondu, Elfe noir retiré (acteur 20), flag 136, écran rouvert.
    base = append_position(rom, "d06_09")
    fail = END_EVENT + struct.pack("<H", 0x05)
    head_size = 2 + 8 + len(fail)
    block = struct.pack("<H", 0x106) + struct.pack("<HHI", 0x76, 9009, base + head_size) + fail
    block += fade_out
    for number in (131, 132, 133, 134, 135):
        block += flag_on(number)
    #   Essai 1 : combat sans musique. La musique de la harpe (18) est lancée par Edward à Troia, puis par la
    #   salle à son chargement (segment 1, 00106) ; comme on enchaîne sans recharger la salle, on la lance ici
    #   (op0C6, op0C6, op0C5(18), op05B(18, …), copiés de 00106).
    block += load_script(rom, "d06_09")[0x00106:0x00119]
    block += struct.pack("<HHH", 0x15, 0, 915) + struct.pack("<HBB", 0x1AE, 1, 1) + battle(924, 25, 0, 1) + end
    assert append_script(rom, "d06_09", block) == base
    patch_script(rom, "d06_09", 0x0046C, goto(base), expected=bytes.fromhex("25 00 02 00 00 00 0a 00 00 00"))
    block = BEGIN_EVENT + fade_out + struct.pack("<HHB", 0x2B, 20, 0) + fade_in + flag_on(136) + end
    patch_script(rom, "d06_09", 0x00F9B, goto(append_script(rom, "d06_09", block)), expected=BEGIN_EVENT)

    # Étape X : Troia, salle des Épopts (t11_02).
    #   X1 : la voix de Kain (segment 3, zone, flag 137 sans 141) -> flags 141 (le coffre-fort du sous-sol
    #   s'ouvre : garde de t11_07), 447, et 144, 145, 146 : le vol de l'Enterprise vers Zott (f00 segment 6)
    #   et l'apparition de la tour ne se jouent pas.
    #   Le flag 447 (musique coupée à bord de l'Enterprise jusqu'à la scène d'embarquement, que l'on saute)
    #   n'est plus activé (18/10/2026 : plus de musique en Enterprise ensuite).
    block = b"".join(flag_on(n) for n in (141, 144, 145, 146)) + struct.pack("<H", 0x05)
    patch_script(rom, "t11_02", 0x003A8, goto(append_script(rom, "t11_02", block)), expected=BEGIN_EVENT)
    #   X2 : accès permanent à Zott (monde ouvert). Parler à la première Épopte (segment 22) : après Golbez
    #   (flag 154, la Terre a été prise) téléportation directe ; sinon menu des objets et op076(9006) : avec la
    #   Terre, téléportation. Téléportation : fondu, flags 141, 144, 145, 146, 447, flag 148 désactivé (la
    #   tour rouvre l'écran à l'arrivée), op043 vers l'entrée de la tour (copié de f00 05D56).
    #   Essai 1 : musique de Troia dans la tour : avec le flag 444, l'arrivée (d07_00 segment 1) saute le
    #   réglage de la musique (op0CC(39)). Essai 2 (actuel) : pas de flag 444.
    warp = fade_out + b"".join(flag_on(n) for n in (141, 144, 145, 146))
    warp += struct.pack("<HHH", 0x15, 0, 148) + load_script(rom, "f00")[0x05D56:0x05D75] + end
    base = append_position(rom, "t11_02")
    head = BEGIN_EVENT
    head_size = len(head) + 10 + 2 + 8 + len(fail)
    head += struct.pack("<HHHI", 0x0C, 0, 154, base + head_size) + struct.pack("<H", 0x106)
    head += struct.pack("<HHI", 0x76, 9006, base + head_size) + fail
    assert len(head) == head_size
    assert append_script(rom, "t11_02", head + warp) == base
    patch_script(rom, "t11_02", 0x00A2D, goto(base) + NOP * 2, expected=bytes.fromhex("0c 00 00 00 9d 00 a1 0a 00 00"))
    #   X3 : la tour n'est plus quittée en Enterprise : f00 segment 9 (vol d'entrée quand on monte dans
    #   l'Enterprise, atterrissage à la sortie) désactivé. La sortie de la tour (d07_00) mène devant Troia.
    patch_script(rom, "f00", 0x05BB3, struct.pack("<H", 0x05) + NOP + NOP, expected=bytes.fromhex("06 00 00 00 9d 00"))

    # Étape Y : tour de Zott.
    #   Y1 : arrivée (d07_00, segment 3, flag 149 non activé : Kain, voix de Golbez) -> flag 149.
    block = flag_on(149) + struct.pack("<H", 0x05)
    patch_script(rom, "d07_00", 0x0019B, goto(append_script(rom, "d07_00", block)), expected=BEGIN_EVENT)
    #   Y2 : les trois sœurs Magus (d07_05, zone 004D8 : flags 150, 444, op042(925)) ; au retour (00B6A) :
    #   fondu, sœurs retirées (acteurs 20 à 22), flag 151.
    #   Essai 1 : combat sans musique : op042(925, 14, 0, 1) garde la musique en cours, lancée par la mise en
    #   scène (op0C6, op0C6, op0C5(13) en 004F8 ; op05B(13, …) en 00B1B). Essai 2 (actuel) : on la lance.
    d07_05 = load_script(rom, "d07_05")
    block = BEGIN_EVENT + fade_out + d07_05[0x004F8:0x00500] + d07_05[0x00B1B:0x00B26]
    block += flag_on(150) + flag_on(444) + battle(925, 14, 0, 1) + end
    patch_script(rom, "d07_05", 0x004D8, goto(append_script(rom, "d07_05", block)), expected=BEGIN_EVENT)
    block = BEGIN_EVENT + fade_out + b"".join(struct.pack("<HHB", 0x2B, a, 0) for a in (20, 21, 22))
    block += fade_in + flag_on(151) + end
    patch_script(rom, "d07_05", 0x00B6A, goto(append_script(rom, "d07_05", block)), expected=BEGIN_EVENT)
    #   Y3 : Golbez (d07_06, zone 00417) : d'origine, Tellah seul contre Golbez (op042(926), défaite
    #   scénarisée), Tellah part, Golbez prend la Terre (op073(9006)), cinématique op151(13), augments,
    #   flags 152 à 154, 158. À la place (combat sauté, comme Kain à Fabul) : fondu, départ de l'emplacement de
    #   Tellah, Terre retirée, flags 152, 153, 154, 158, écran rouvert.
    #   Essai 1 : jeu figé en parlant à Golbez : on restait sur la carte, Golbez toujours affiché mais sans
    #   segment de dialogue (son segment vaut -1). Essai 2 (actuel) : comme la cinématique d'origine
    #   (op151 vers d07_06, z = 491520 inversé), on recharge la carte juste avant la zone (op043, z = -491520),
    #   avec les flags 2 et 444 (pas de bandeau ni de relance de la musique) ; Golbez n'est plus chargé.
    #   Kain (acteur 52, segment 1 en 00304, flag 153) n'est plus placé : il rejoint en haut (Y4).
    block = BEGIN_EVENT + fade_out + leave("Ordeals Character") + struct.pack("<HHB", 0x73, 9006, 1)
    #   Essai 2 : porte du sommet fermée (« The door is locked. ») : les portes (acteurs 20 et 21, segments 4
    #   et 5) se verrouillent après Golbez (flags 153, 154) ou avant Kain (flag 155), on montait en parlant à
    #   Kain. Essai 3 (actuel) : portes ouvertes au rechargement (flags 266, 267 de la banque 1) et plus de
    #   verrou (sauts conditionnels remplacés par des NOP).
    block += b"".join(flag_on(n) for n in (152, 153, 154, 158, 2, 444))
    block += struct.pack("<HHH", 0x14, 1, 266) + struct.pack("<HHH", 0x14, 1, 267)
    block += struct.pack("<H", 0x43) + b"d07_06\0" + struct.pack("<IIIIIH", 0, 0, (-491520) & 0xFFFFFFFF, 0, 0, 0)
    block += end
    patch_script(rom, "d07_06", 0x00417, goto(append_script(rom, "d07_06", block)), expected=BEGIN_EVENT)
    patch_script(rom, "d07_06", 0x00304, struct.pack("<H", 0x05), expected=bytes.fromhex("29 00"))
    patch_script(rom, "d07_06", 0x02B2D, NOP * 10, expected=bytes.fromhex("0c 00 00 00 9a 00"))
    patch_script(rom, "d07_06", 0x02BD3, NOP * 5, expected=bytes.fromhex("0d 00 00 00 9b 00"))
    #   Y4 : sommet (d07_07, segment 5, au chargement, flag 155 non activé) : Kain (op068(2), niveau 32) et
    #   Rosa (op068(3), niveau 26) rejoignent -> les deux personnages tirés, flag 155.
    block = BEGIN_EVENT + fade_out + join("Zot Character 1") + join("Zot Character 2") + fade_in + flag_on(155) + end
    patch_script(rom, "d07_07", 0x01B2A, goto(append_script(rom, "d07_07", block)), expected=BEGIN_EVENT)
    #   Y5 : Valvalis (d07_07, segment 6, zone 040BC : flag 156, op042(927)) ; au retour (047AD) : d'origine,
    #   Rosa apprend un sort, flag 157, téléportation à Baron (t00_14, suite de l'histoire : tranche 5).
    #   Essai 1 : fondu, flag 157, écran rouvert ; on restait dans la tour. Essai 2 (actuel, demandé) : comme
    #   à l'origine, téléportation dans la chambre de Cecil (op043('t00_14') de 04DA6, joueur à la position de
    #   fin de la scène d'origine, x = -122880), où la Magma Stone est donnée (Z1). Sort de Rosa (op17C) non repris.
    block = BEGIN_EVENT + fade_out + flag_on(156) + battle(927, 14, 0, 0) + end
    patch_script(rom, "d07_07", 0x040BC, goto(append_script(rom, "d07_07", block)), expected=BEGIN_EVENT)
    block = BEGIN_EVENT + fade_out + flag_on(157)
    block += struct.pack("<H", 0x43) + b"t00_14\0" + struct.pack("<IIIIIH", (-122880) & 0xFFFFFFFF, 0, 0, 0, 0, 0) + end
    patch_script(rom, "d07_07", 0x047AD, goto(append_script(rom, "d07_07", block)), expected=BEGIN_EVENT)

    # Étape Z : tranche 5 (Magma Stone, Agart, monde souterrain).
    #   Z1 : chambre de Cecil à Baron (t00_14, segment 2, au chargement, flag 157 activé et 160 non) :
    #   d'origine, longue scène où Kain donne la Magma Stone (op044(9012)), flags 900, 901, 160.
    #   À la place : Magma Stone + flag 160 (recette 1). Les flags 900 / 901 (véhicules) ne sont pas repris.
    #   Écran rouvert à la fin (arrivée par la téléportation de Valvalis, écran noir).
    #   Essai 2 : l'Enterprise restait près de Troia (joueur bloqué à Baron). D'origine, Cid l'a ramenée :
    #   si elle est disponible (flag 901 = 0x0CC131), elle est posée devant le château (op0B3 de f00 01E43).
    base = append_position(rom, "t00_14")
    head = struct.pack("<HHB", 0x44, 9012, 1) + flag_on(160)
    place = load_script(rom, "f00")[0x01E43:0x01E61]                  # op0B3(2, -978944, 102400, 1658880)
    skip = base + len(head) + 10 + len(place)
    block = head + struct.pack("<HHHI", 0x0D, 0, 901, skip) + place + fade_in + struct.pack("<H", 0x05)
    assert append_script(rom, "t00_14", block) == base
    patch_script(rom, "t00_14", 0x001AA, goto(base), expected=BEGIN_EVENT)
    #   Z2 : puits d'Agart (t07_00 segment 11 et t07_01 segment 2 ; menu des objets, op076(9012)) : d'origine,
    #   scène du puits, Magma Stone retirée, flags 909, 164, 166, cinématique op151(14) (flag 718 : éruption,
    #   le trou s'ouvre). Puis, en entrant dans le trou avec l'Enterprise (f01, segment 3 au chargement) :
    #   descente (flag 170), combat des Red Wings (cinématique op151(15), flags 719, 700 ; flag 171), chute
    #   (flag 173 : Enterprise posée à Y = -409600, inutilisable) et réveil (flag 172).
    #   À la place, tout est fait au puits : fondu, Magma Stone retirée, flags 909, 164, 166, 718, 170 à 173,
    #   719, 700, écran rouvert. Dans le monde souterrain, plus aucune scène : l'Enterprise reste utilisable.
    block = fade_out + struct.pack("<HHB", 0x73, 9012, 1)
    #   Flag 700 retiré (20/10/2026) : posé par les cinématiques pendant qu'elles jouent ; resté activé, la
    #   cinématique suivante (Rubicante) se jouait en mode « théâtre » (retour au menu des cinématiques).
    block += b"".join(flag_on(n) for n in (909, 164, 166, 718, 170, 171, 172, 173, 719)) + fade_in + end
    patch_script(rom, "t07_00", 0x00A89, goto(append_script(rom, "t07_00", block)), expected=bytes.fromhex("25 00 02 00"))
    patch_script(rom, "t07_01", 0x0019F, goto(append_script(rom, "t07_01", block)), expected=bytes.fromhex("25 00 02 00"))
    #   Z3 : deux Enterprise dans le monde souterrain : f01 segment 1 (001E0, flag 171 sans 196) affiche
    #   l'épave posée au sol (acteur 21, op028(21, 1) + op0C2). Jamais affichée : aller_a(00211).
    #   + flag 447 désactivé (musique coupée à bord, voir X1), pour les parties où il était resté activé.
    clear447 = struct.pack("<HHH", 0x15, 0, 447) + struct.pack("<HHH", 0x15, 0, 700)   # + 700 (voir Z2)
    patch_script(rom, "f01", 0x001E0, goto(append_script(rom, "f01", clear447 + goto(0x00211))) + NOP * 2,
                 expected=bytes.fromhex("0c 00 00 00 c4 00 11 02 00 00"))
    #   Même chose sur la carte du monde de la surface (f00 segment 1, 002E4 : op015(0, 445)).
    patch_script(rom, "f00", 0x002E4, goto(append_script(rom, "f00", struct.pack("<HHH", 0x15, 0, 445) + clear447
                                                          + goto(0x002EA))), expected=bytes.fromhex("15 00 00 00 bd 01"))
    #   Z4 : plus de musique en Enterprise après Golbez (château des nains) : f01 segment 1 (00258, flag 178
    #   activé et 193 non : entre Golbez et la fuite de la tour de Babil, l'Enterprise est censée être au sol)
    #   met l'acteur 16 (le véhicule) dans l'état 1 (op028(16, 1) + op0C2). Sauté : aller_a(0026D).
    patch_script(rom, "f01", 0x00258, goto(0x0026D), expected=bytes.fromhex("28 00 10 00 01"))

    # Étape AA : château des nains (t12_02 salle du trône, t12_03 salle du cristal).
    #   AA1 : Giott (t12_02 segment 3, zone 0034E, flag 172 activé et 175 non) : d'origine, longue scène,
    #   départ de Cid (op0AC + op069(11)), flag 175 (le jeu passe à Rydia adulte), op043 vers t12_03.
    #   À la place : fondu, départ de l'emplacement de Cid, flag 175, même op043 (copié de 010A2).
    t12_02 = load_script(rom, "t12_02")
    block = BEGIN_EVENT + fade_out + leave("Cid Character") + flag_on(175) + t12_02[0x010A2:0x010C1] + end
    patch_script(rom, "t12_02", 0x0034E, goto(append_script(rom, "t12_02", block)), expected=BEGIN_EVENT)
    #   AA2 : poupées Calbrena (t12_03 segment 3, au chargement, 001C9) : d'origine, mise en scène, musique 38
    #   (00565), flag 176, op1AE(1, 1), op042(928, 25, 0, 1) (garde la musique). À la place : musique + combat.
    t12_03 = load_script(rom, "t12_03")
    block = BEGIN_EVENT + fade_out + t12_03[0x00565:0x00580] + flag_on(176) + struct.pack("<HBB", 0x1AE, 1, 1)
    block += battle(928, 25, 0, 1) + end
    patch_script(rom, "t12_03", 0x001C9, goto(append_script(rom, "t12_03", block)), expected=BEGIN_EVENT)
    #   AA3 : Golbez (fonction 008C4, flag 176) : d'origine, scène, musique 23 (00D78), flag 177, préparation de
    #   Rydia adulte (perso 5) : op06D(5, 4, 5, 4, 3, 0) (niveau de Rydia enfant repris s'il est plus haut),
    #   op102(5, 30), op0AC(5, …), op1D1(4, 5, …) (capacités de Rydia enfant copiées), puis op042(930, 25, 0, 1) :
    #   le combat lui-même fait entrer Rydia adulte après le Dragon noir.
    #   Essai 1 : personnage de l'emplacement ajouté avant le combat, sans op06D / op1D1 : jeu figé au Dragon noir
    #   (l'entrée de Rydia ne se fait pas : place prise ou Rydia déjà là). Essai 2 (actuel) : préparation et combat
    #   d'origine (copiés de 00F1C à 00FAE) ; l'échange avec le personnage tiré se fait après le combat (AA4).
    block = BEGIN_EVENT + fade_out + t12_03[0x00D78:0x00D93] + flag_on(177)
    block += t12_03[0x00F1C:0x00FAE] + battle(930, 25, 0, 1) + end
    patch_script(rom, "t12_03", 0x008C4, goto(append_script(rom, "t12_03", block)), expected=BEGIN_EVENT)
    #   AA4 : après Golbez (fonction 00FC2, flag 177) : d'origine, retour de Rydia, cristal volé, op043 vers
    #   t12_02. À la place : si l'emplacement n'est pas Rydia, Rydia adulte repart (équipement rendu) et le
    #   personnage tiré arrive ; puis op043 (copié de 01A75).
    swap = b""
    dwarf = plan.joins.get("Dwarf Castle Character")
    if not dwarf or dwarf[0] != "Rydia":
        swap = struct.pack("<HIHHHHH", 0xAC, 5, 0, 0, 0, 0, 0) + struct.pack("<HIB", 0x69, 5, 0)
        swap += join("Dwarf Castle Character")
    block = BEGIN_EVENT + fade_out + swap + t12_03[0x01A75:0x01A94] + end
    patch_script(rom, "t12_03", 0x00FC2, goto(append_script(rom, "t12_03", block)), expected=BEGIN_EVENT)
    #   AA5 : Giott après Golbez (t12_02 segment 4, au chargement, flag 177 activé et 178 non) : d'origine,
    #   scène, augment Draw Attacks (op044(9153)), flag 178. À la place : augment, flag 178, écran rouvert.
    #   + flags 181, 182, 183 : scènes des chars des nains près de la tour de Babil (f01 segment 2) sautées.
    block = struct.pack("<HHB", 0x44, 9153, 1) + flag_on(178) + flag_on(181) + flag_on(182) + flag_on(183)
    block += fade_in + struct.pack("<H", 0x05)
    patch_script(rom, "t12_02", 0x010DB, goto(append_script(rom, "t12_02", block)), expected=BEGIN_EVENT)

    # Étape AB : tranche 6, tour de Babil (partie souterraine, d08_00 à d08_14, d08_21).
    #   AB1 : Dr Lugae (d08_14 segment 3, zone 002C7) : d'origine, scène, musique 38 (005F2), flags 186, 444,
    #   op1AE(0, 0), op042(931, 15, 0, 1) ; après (fonction 009A0) : flags 187, 444, op042(933, 15, 0, 0) ;
    #   après (00A9E) : Tower Key (op044(9015)), flag 188. À la place : les combats seuls.
    d08_14 = load_script(rom, "d08_14")
    block = BEGIN_EVENT + fade_out + d08_14[0x005F2:0x0060D] + flag_on(186) + flag_on(444)
    block += struct.pack("<HBB", 0x1AE, 0, 0) + battle(931, 15, 0, 1) + end
    patch_script(rom, "d08_14", 0x002C7, goto(append_script(rom, "d08_14", block)), expected=BEGIN_EVENT)
    block = BEGIN_EVENT + fade_out + flag_on(187) + flag_on(444) + battle(933, 15, 0, 0) + end
    patch_script(rom, "d08_14", 0x009A0, goto(append_script(rom, "d08_14", block)), expected=BEGIN_EVENT)
    block = BEGIN_EVENT + fade_out + struct.pack("<HHB", 0x44, 9015, 1) + flag_on(188) + fade_in + end
    patch_script(rom, "d08_14", 0x00A9E, goto(append_script(rom, "d08_14", block)), expected=BEGIN_EVENT)
    #   AB2 : canons (d08_21 segment 3, au chargement, 00144) : d'origine, scène, flag 189, op042(958, 15, 0, 0) ;
    #   après (fonction 005A8) : Yang reste (op0AC + op069(10)), flags 190, 6, cinématique op151(16) vers d08_10
    #   (e16_00 : flags 720, 700). Ensuite, d'origine : Golbez à l'entrée (d08_00, flag 193 ; il faut le flag
    #   192, posé par la cinématique), poursuite en Enterprise et Cid qui revient (t19_02, flags 196, 197),
    #   retour à la surface (f01, flag 198, cinématique 17 : 721), Cid qui referme le trou (t19_01 : 199).
    #   À la place : combat seul ; après : départ de l'emplacement de Yang, flags 190, 6, 720, 700, 192, 193,
    #   196, 197, 198, 199, 721, op043 vers d08_10 (z de la cinématique inversé). On ressort de la tour à pied ;
    #   l'Enterprise du joueur reste dans le monde souterrain et le trou reste ouvert (Z2, AB4).
    block = BEGIN_EVENT + fade_out + flag_on(189) + battle(958, 15, 0, 0) + end
    patch_script(rom, "d08_21", 0x00144, goto(append_script(rom, "d08_21", block)), expected=BEGIN_EVENT)
    block = BEGIN_EVENT + fade_out + leave("Baron Character")
    block += b"".join(flag_on(n) for n in (190, 6, 720, 192, 193, 196, 197, 198, 199, 721))   # pas 700 (Z2)
    block += struct.pack("<H", 0x43) + b"d08_10\0" + struct.pack("<IIIIIH", 0, 0, (-139264) & 0xFFFFFFFF, 0, 0, 0) + end
    patch_script(rom, "d08_21", 0x005A8, goto(append_script(rom, "d08_21", block)), expected=BEGIN_EVENT)
    #   AB3 : crochet de l'Enterprise (château de Baron, t00_00 segment 5, après op009(10, 10) : un ingénieur) :
    #   d'origine, scène, flags 202, 444, op043 vers t19_00 (scène du crochet : flag 903 = Enterprise avec
    #   crochet, véhicule 4, puis op0A7('f00', devant Baron, …, 4)). À la place : fondu, flags 202, 203, 444, 903,
    #   op0A7 (copié de t19_00 00BAB) : on repart directement à bord de l'Enterprise avec crochet.
    #   Partie Archipelago (vehicle_items) : le crochet est le 2e exemplaire de l'objet Enterprise (posé par le
    #   client) ; l'ingénieur ne fait qu'activer les flags 202, 203 (location).
    if vehicle_items:
        block = fade_out + flag_on(202) + flag_on(203) + fade_in + end
    else:
        block = fade_out + b"".join(flag_on(n) for n in (202, 203, 444, 903))
        #   Essai 1 : plus de musique à bord (flag 444 : la carte du monde ne relance pas la sienne). Essai 2 :
        #   musique de l'Enterprise (30) lancée avant op0A7, comme à l'origine (copiée de t19_00 00B8C).
        block += load_script(rom, "t19_00")[0x00B8C:0x00BC7] + end
    patch_script(rom, "t00_00", 0x02316, goto(append_script(rom, "t00_00", block)), expected=bytes.fromhex("25 00 02 00"))
    #   AB4 : trou d'Agart : d'origine, refermé par Cid (f00 segment 1 : flag 198 -> op028(23, 1), le
    #   couvercle). Le test du flag 198 est retiré : le trou reste ouvert.
    patch_script(rom, "f00", 0x0043F, NOP * 5, expected=bytes.fromhex("0c 00 00 00 c6 00"))
    #   AB5 : tour de Babil toujours accessible depuis le monde souterrain : d'origine, la sortie j002 de f01
    #   (vers d08_00) n'est plus définie avec le flag 253 (grotte scellée, plus tard). Test retiré.
    patch_script(rom, "f01", 0x00311, NOP * 5, expected=bytes.fromhex("0c 00 00 00 fd 00 6f 03 00 00"))

    # Étape AC : tranche 6, grotte d'Eblan et tour de Babil (partie haute, d08_15 à d08_20, d08_22, d08_23).
    #   AC1 : Edge contre Rubicante (d09_05 segment 3, zone 0070D) : d'origine, scène, Edge rejoint (op068(12),
    #   op102(12, 35)), combat d'Edge seul (op042(934), scénarisé), retour de l'équipe, flags 205, 206.
    #   À la place : personnage de l'emplacement « Eblan Character », flags 205, 206 (combat scénarisé sauté).
    #   Essai 1 : jeu figé en parlant ensuite à Rubicante, resté affiché (acteur 20, sans dialogue). Essai 2 :
    #   Rubicante retiré (op02B(20, 0)), comme à la fin de la scène d'origine (016EB). Essai 3 : Edge restait
    #   (acteur 61, même problème) : retiré aussi.
    block = BEGIN_EVENT + fade_out + join("Eblan Character") + flag_on(205) + flag_on(206)
    block += struct.pack("<HHB", 0x2B, 20, 0) + struct.pack("<HHB", 0x2B, 61, 0) + fade_in + end
    patch_script(rom, "d09_05", 0x0070D, goto(append_script(rom, "d09_05", block)), expected=BEGIN_EVENT)
    #   AC2 : entrée de la tour (d08_15 segment 3) : à chaque passage, scène du ninja qui fait passer l'équipe
    #   (vers l'intérieur 0023B, flag 209 ; vers l'extérieur 0054E). À la place : fondu et joueur replacé
    #   de l'autre côté (copiés de 004E9 et 006FD).
    d08_15 = load_script(rom, "d08_15")
    block = BEGIN_EVENT + fade_out + d08_15[0x004E9:0x00522] + flag_on(209) + fade_in + END_EVENT + goto(461)
    patch_script(rom, "d08_15", 0x0023B, goto(append_script(rom, "d08_15", block)), expected=BEGIN_EVENT)
    block = BEGIN_EVENT + fade_out + d08_15[0x006FD:0x00736] + fade_in + END_EVENT + goto(461)
    patch_script(rom, "d08_15", 0x0054E, goto(append_script(rom, "d08_15", block)), expected=BEGIN_EVENT)
    #   AC3 : parents d'Edge et Rubicante (d08_20, B5) : zone 00330 -> scène, flag 210, op042(935) ; après
    #   (fonction 00808) : ninjutsu d'Edge (op17C(12, 4902 / 4903)), flags 211, 212, cinématique op151(18)
    #   (Rubicante soigne l'équipe, combat op042(936)) ; après (fonction 011B2) : scène, flag 213.
    #   À la place : combats seuls (Rubicante : soins op1AE(0, 1) puis op042(936, 15, 0, 0)), flag 213 après.
    block = BEGIN_EVENT + fade_out + flag_on(210) + battle(935, 15, 0, 0) + end
    patch_script(rom, "d08_20", 0x00330, goto(append_script(rom, "d08_20", block)), expected=BEGIN_EVENT)
    #   Essai 11 : après la cinématique, menu des cinématiques au lieu du combat : flag 700 resté activé par
    #   nos sauts (Z2, AB2). Flag 700 désactivé juste avant la cinématique (et sur les cartes du monde).
    d08_20 = load_script(rom, "d08_20")
    block = BEGIN_EVENT + struct.pack("<HHH", 0x15, 0, 700) + d08_20[0x00812:0x00863]
    patch_script(rom, "d08_20", 0x00808, goto(append_script(rom, "d08_20", block)), expected=BEGIN_EVENT)
    #   Rubicante (fonction 00808) : essais 1 à 9 (combat lancé directement, musique 39 / 29 lancée avant,
    #   musique 29 mise dans les données du combat, avec ou sans op1AE) : combat silencieux, ou sans fanfare de
    #   victoire. Essai 10 (actuel, idée du joueur) : fonction d'origine gardée (ninjutsu op17C(12, …), flags
    #   211, 212, cinématique op151(18) : Rubicante soigne l'équipe et le combat suit, avec la musique de la
    #   cinématique). La cinématique se passe avec Start, comme dans le jeu d'origine.
    #   Essai 1 : Rubicante restait affiché (acteur 22, jeu figé en lui parlant) et plus de musique de la tour.
    #   Essai 2 : Rubicante retiré (op02B(22, 0), comme 01572) et musique de la carte relancée (op0CC(33), 0212C).
    d08_20 = load_script(rom, "d08_20")
    block = BEGIN_EVENT + fade_out + flag_on(213) + struct.pack("<HHB", 0x2B, 22, 0) + d08_20[0x0212C:0x02136]
    block += fade_in + end
    patch_script(rom, "d08_20", 0x011B2, goto(append_script(rom, "d08_20", block)), expected=BEGIN_EVENT)
    #   AC4 : piège de Golbez (d08_23, zones 00194 et 00277, flag 213 activé et 214 non) : scène, flag 214,
    #   chute vers d08_14 (op043). Puis d08_14 segment 4 (00F95 / 0142D, flag 214 sans 215) : scène, flag 215,
    #   joueur replacé, musique 33. À la place : chute directe ; à l'arrivée, flag 215 + replacement (013B0).
    d08_23 = load_script(rom, "d08_23")
    for position, jump in ((0x00194, 0x00212), (0x00277, 0x003EC)):
        block = BEGIN_EVENT + fade_out + flag_on(214) + d08_23[jump:jump + 0x1F] + end
        patch_script(rom, "d08_23", position, goto(append_script(rom, "d08_23", block)), expected=BEGIN_EVENT)
    #   Essai 2 : plus de bruitages en combat ensuite : la copie contenait op0CA (libère la banque de sons
    #   chargée par la scène d'origine avec op0C9, ici celle des combats). op0CA retiré (013E9).
    #   Essai 3 (20/10/2026) : le hangar du Faucon (d08_22) reste noir en y entrant par la porte du B8, et son
    #   segment 3 ne se lance pas (flags 215 = 1, 216 = 0, aucun événement en cours). À la place, la chute mène
    #   directement au Faucon : flag 215, puis fin d'origine du hangar (flags 216, 444, 904, op0A7 vers f01 à
    #   bord du Faucon, copiés de d08_22 008AE) ; la courte scène du Faucon qui sort du volcan (f01) est gardée.
    #   Essai 4 : la scène de f01 (segment 5) restait bloquée (événement en cours, écran du haut noir, joueur
    #   à pied loin du Faucon). Elle est court-circuitée (flag 217) : le Faucon est placé (op0B3 comme f01
    #   02862), musique 30 (copiée de t19_00 00B8C) et sortie op0A7 à bord du Faucon, à sa position.
    #   Partie Archipelago (vehicle_items) : le Faucon est un objet (location : flag 217). Sans lui (flag 904),
    #   le joueur repart à bord de l'Enterprise avec crochet (véhicule 4), posée au même endroit.
    #   Ce bloc remplace la scène du hangar (AC5, d08_22 segment 1, au chargement, flag 215 sans 216).
    def falcon_arrival(map_name, extra=b""):
        x, y, z = -1228800, 102400, -2682880
        music = load_script(rom, "t19_00")[0x00B8C:0x00BAB]

        def board(vehicle):
            place = struct.pack("<HIiiiIII", 0xB3, vehicle, x, y, z, 0, 0, 0)
            return (place + music
                    + struct.pack("<H", 0xA7) + b"f01\0" + struct.pack("<iiiIIH", x, y, z, 0, vehicle, 0))

        head = BEGIN_EVENT + flag_on(215) + flag_on(216) + flag_on(217) + flag_on(444) + extra
        if not vehicle_items:
            return append_script(rom, map_name, head + flag_on(904) + board(5) + end)
        base = append_position(rom, map_name)
        falcon = board(5) + end
        jump = base + len(head) + 10
        block = head + struct.pack("<HHHI", 0x0C, 0, 904, jump + len(board(4) + end)) + board(4) + end + falcon
        assert append_script(rom, map_name, block) == base
        return base

    #   Essai 5 (21/10/2026) : la chute ne mène plus directement au Faucon (B8 et B7 restaient inaccessibles :
    #   2 coffres et 2 cartes). Atterrissage d'origine sans la scène (flag 215, écran rouvert), puis à pied
    #   B7 -> B8 -> porte du hangar : falcon_arrival (vérifié en émulateur par la porte j003 de d08_11).
    #   Essai 6 : on atterrissait au centre de la salle ; d'origine, la fin de scène replace le joueur à gauche
    #   (op105(0, -827392, 0, -131072), op09F, op02C, op087 : 013B0-013E9) et relance la musique 33 (013EF,
    #   sans l'op0CA de 013E9 qui libère la banque de sons des combats).
    #   Écrans noirs chez le joueur (hangar, puis après les combats) avec des savestates faites sur d'anciennes
    #   ROM ; essai 7 (porte du hangar vers f01) et retour à la chute -> Faucon abandonnés (21/10/2026) : retour
    #   à l'essai 6, à tester depuis une sauvegarde en jeu.
    d08_14 = load_script(rom, "d08_14")
    fallen = append_script(rom, "d08_14", BEGIN_EVENT + flag_on(215) + d08_14[0x013B0:0x013E9]
                           + d08_14[0x013EF:0x013F9] + fade_in + end)
    for position in (0x00F95, 0x0142D):
        patch_script(rom, "d08_14", position, goto(fallen), expected=BEGIN_EVENT)
    patch_script(rom, "d08_22", 0x00150, goto(falcon_arrival("d08_22")), expected=BEGIN_EVENT)

    #   AD0 : Giott après la chute (t12_02 segment 3, zone devant le trône, flag 217 activé et 220 non) :
    #   d'origine, scène (Luca donne son collier, clé de la grotte scellée), op044(9014), flag 220.
    #   À la place : collier (location AP, flag 220), écran rouvert. Deux variantes (début 01F9C et 02B64).
    block = BEGIN_EVENT + fade_out + struct.pack("<HHB", 0x44, 9014, 1) + flag_on(220) + fade_in + end
    luca = append_script(rom, "t12_02", block)
    for position in (0x01FD6, 0x02B9E):
        patch_script(rom, "t12_02", position, goto(luca), expected=BEGIN_EVENT)

    #   AD : Cid à l'infirmerie du château des nains (t12_11 segment 1, zone devant son lit, flag 199 activé et
    #   222 non) : d'origine, longue scène (Cid améliore le Faucon pour la lave, nuit, lettre), augments
    #   Adrenaline, Upgrade, Analyze (op044(9115 / 9114 / 9113)), flags 454, 902 (le Faucon traverse la lave,
    #   vérifié en émulateur : 902 seul suffit), 221, 222. Cid n'est là qu'après la chute (seg. 0 : flag 217).
    #   Upgrade et Analyze ne sont rendus que selon les augments confiés à Cid (op1C4(11, …)) : seul Adrenaline
    #   est gardé (21/10/2026). À la place : si flag 217, Adrenaline, flags 221, 222, 454,
    #   902 seulement hors Archipelago (sinon : 2e exemplaire de l'objet Faucon).
    block = (struct.pack("<HHH", 0x07, 0, 217) + BEGIN_EVENT + fade_out
             + struct.pack("<HHB", 0x44, 9115, 1)
             + flag_on(221) + flag_on(222) + flag_on(454)
             + (b"" if vehicle_items else flag_on(902)) + fade_in + end)
    cid = append_script(rom, "t12_11", block)
    for position in (0x002A8, 0x02047, 0x02A25):
        patch_script(rom, "t12_11", position, goto(cid), expected=BEGIN_EVENT)

    # (Essai retiré : ne plus placer l'éboulement du Titan sur la carte du monde (f00, 003D2).
    #  Les rochers disparaissaient mais une barrière invisible restait : la collision fait partie
    #  du décor. Le village reste accessible par la Grotte de la Brume.)


# --------------------------------------------------------------------------- #
# Musique des combats (monster_party_table.bbd.lz)                             #
# --------------------------------------------------------------------------- #
PARTY_TABLE_FILE = "monster_party_table.bbd.lz"


def set_battle_music(rom, group, music):
    """Chaque groupe de monstres commence par 8 octets FF, puis [décor u16][musique u16][groupe u16] ;
    musique = numéro de music_player.bbd (8 combat, 13 boss, 29 archidémons, 65535 = garder la musique)."""
    data = bytearray(lz10(bytes(rom.getFileByName(PARTY_TABLE_FILE))))
    found = [i for i in range(8, len(data) - 6, 2)
             if data[i - 8:i] == b"\xff" * 8 and struct.unpack_from("<H", data, i + 4)[0] == group]
    assert len(found) == 1, (group, found)
    struct.pack_into("<H", data, found[0] + 2, music)
    rom.setFileByName(PARTY_TABLE_FILE, lz10_compress(bytes(data)))


# --------------------------------------------------------------------------- #
# Sorts en objets : retirer des sorts de l'apprentissage par niveau            #
# --------------------------------------------------------------------------- #
LEARNSET_FILE = "player.chaindata.lz"
LEARNSET_FIRST_CHUNK = 17       # bloc 17 + identifiant du personnage (0 Cecil … 14 Golbez)
LEARNSET_CHARACTERS = 15
NEVER = 100                     # niveau jamais atteint (maximum 99)


def remove_learned_spells(rom, spells, level1_chars=()):
    """Les sorts de `spells` ne s'apprennent plus en montant de niveau : leur niveau
    d'apprentissage passe à 100. Les sorts de niveau 1 (de départ) sont gardés, sauf pour
    les personnages de `level1_chars`.
    Format : player.chaindata = nombre de blocs (4), …, table [décalage (4), taille (4)] à 0x10 ;
    un bloc = suite de paires u16 (niveau, capacité) : commandes, sorts, invocations."""
    data = bytearray(lz10(rom.getFileByName(LEARNSET_FILE)))
    changed = 0
    for char in range(LEARNSET_CHARACTERS):
        offset, size = struct.unpack_from("<II", data, 0x10 + 8 * (LEARNSET_FIRST_CHUNK + char))
        for p in range(offset, offset + size - 3, 4):
            level, ability = struct.unpack_from("<HH", data, p)
            if ability in spells and (level > 1 or char in level1_chars):
                struct.pack_into("<H", data, p, NEVER)
                changed += 1
    rom.setFileByName(LEARNSET_FILE, lz10_compress(bytes(data)))
    return changed


# --------------------------------------------------------------------------- #
# Coffres de gils -> coffres d'objets                                         #
# --------------------------------------------------------------------------- #
# Un coffre de gils (op066) ne sait afficher qu'un montant : le client ne peut pas y
# mettre le nom d'un objet Archipelago. On les transforme en coffres d'objets (op045,
# mêmes arguments : objet de carte, contenu, quantité, flag, ?, caché). Le contenu par
# défaut est une Potion ; le client le remplace (objet natif, ou porteur renommé « 480 Gil »).
# (carte, position, objet de carte, montant d'origine, flag banque 1, caché)
GIL_CHESTS = [
    ("d01_04", 0x000A4, 70, 580, 315, 0), ("d03_01", 0x00145, 73, 960, 348, 0),
    ("d05_00", 0x000AE, 70, 1000, 360, 0), ("d06_02", 0x000BE, 70, 2000, 373, 0),
    ("d08_20", 0x00212, 70, 10000, 420, 0), ("d10_00", 0x00192, 76, 1000, 456, 0),
    ("d10_01", 0x00179, 73, 2000, 463, 0), ("d10_01", 0x00186, 74, 3000, 464, 0),
    ("t00_01", 0x00237, 70, 480, 1, 0), ("t01_40", 0x000BF, 71, 2000, 37, 0),
    ("t08_00", 0x00158, 70, 5000, 85, 2), ("t09_05", 0x000F4, 71, 10000, 100, 0),
    ("t10_00", 0x00188, 70, 1000, 115, 1), ("t11_08", 0x001E0, 78, 5000, 134, 0),
    ("t11_08", 0x00248, 86, 50000, 142, 0), ("t12_30", 0x000E8, 70, 5000, 173, 2),
    ("t13_01", 0x00109, 73, 2000, 185, 0), ("t14_00", 0x0011B, 73, 5000, 193, 0),
    ("t14_00", 0x00128, 74, 6000, 194, 0),
]
GIL_CHEST_DEFAULT_ITEM = 0x1389     # Potion


def convert_gil_chests(rom):
    for map_name, position, actor, amount, flag, hidden in GIL_CHESTS:
        expected = struct.pack("<HHHHHHB", 0x66, actor, amount, 1, flag, 0, hidden)
        new = struct.pack("<HHHHHHB", 0x45, actor, GIL_CHEST_DEFAULT_ITEM, 1, flag, 0, hidden)
        patch_script(rom, map_name, position, new, expected=expected)


# --------------------------------------------------------------------------- #
# Magasins                                                                    #
# --------------------------------------------------------------------------- #
SHOP_FILE = "MENU/babil_shop.bbd"
SHOP_SIZE = 124              # nom (32), textes (7 × 4), objets (16 × 4)
SHOP_ITEMS = 60
SHOP_SLOTS = 16


def write_shops(rom, shops):
    """shops : {numéro de magasin: [objets]} (16 au plus). Les autres magasins ne changent pas."""
    data = bytearray(rom.getFileByName(SHOP_FILE))
    for index, items in shops.items():
        items = list(items)[:SHOP_SLOTS]
        items += [0] * (SHOP_SLOTS - len(items))
        struct.pack_into(f"<{SHOP_SLOTS}I", data, int(index) * SHOP_SIZE + SHOP_ITEMS, *items)
    rom.setFileByName(SHOP_FILE, bytes(data))


def patch(base: bytes, options: dict | None = None) -> bytes:
    """ROM d'origine -> ROM patchée (utilisé par Archipelago au moment du patch).
    options : options de la partie (options.json du fichier .apff4ds)."""
    options = options or {}
    rom = NDSRom(base)
    if rom.id_code != GAME_CODE:
        raise ValueError("ROM US de Final Fantasy IV DS (YF4E) attendue")
    apply_patches(rom, options.get("party"), options.get("departures", "vanilla"),
                  options.get("full_party", "replace_oldest"), options.get("vehicle_items", False))
    convert_gil_chests(rom)
    if options.get("shops"):
        write_shops(rom, options["shops"])
    if options.get("spell_items"):
        remove_learned_spells(rom, set(options["spell_items"]), set(options.get("level1_chars", [])))
    return rom.to_bytes()


def main(argv):
    if len(argv) != 3:
        print(__doc__); return
    with open(argv[1], "rb") as f:
        data = patch(f.read())
    with open(argv[2], "wb") as f:
        f.write(data)
    print("ROM patchée écrite :", argv[2])


if __name__ == "__main__":
    main(sys.argv)
