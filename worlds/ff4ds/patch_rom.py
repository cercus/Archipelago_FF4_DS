"""Patcheur de ROM pour Final Fantasy IV DS (US, YF4E).

Utilisation :
  python patch_rom.py <rom_origine.nds> <rom_patchee.nds>

Ne modifie jamais la ROM d'origine : une nouvelle ROM est écrite.

Patchs actuels :
  - Étape B : nouvelle partie -> dans la cour du château, devant la sortie, avec Kain
    et la Carnelian Signet ; toute l'introduction est sautée.
  - Étape C : l'entrée du château de Baron sur la carte du monde mène à l'intérieur (t00_01) ;
    en ressortant, on arrive dans la cour du bon côté de la grande porte.
  - Étape D : le lit de Cecil ne relance plus la nuit (Rosa) ni le départ ; simple repos.
  - Étape E : Grotte de la Brume : plus de voix, Dragon des Brumes sans dialogue.
  - Étape F : Village de la Brume : Signet retirée, Kain part, réveil directement dans le désert.
"""
import struct, sys

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ndspy.rom

from ff4ds_rom import lz10, load_rom

ALIGN = 0x200          # dans une archive SSAM, chaque fichier commence à un décalage = 0x1F8 modulo 0x200
ALIGN_REST = 0x1F8


# --------------------------------------------------------------------------- #
# Compression LZ10 (l'inverse de lz10() dans ff4ds_rom.py)                    #
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
    assert data[:4] == b"SSAM"
    count = struct.unpack_from("<I", data, 4)[0]
    header_end = 8 + count * 0x28
    entries = []
    for i in range(count):
        o = 8 + i * 0x28
        offset, size = struct.unpack_from("<II", data, o)
        name = bytes(data[o + 8:o + 0x28])
        entries.append([name, bytes(data[header_end + offset:header_end + offset + size])])
    return entries


def ssam_write(entries):
    header = bytearray(b"SSAM" + struct.pack("<I", len(entries)))
    body, offset = bytearray(), 0
    for name, blob in entries:
        while offset % ALIGN != ALIGN_REST:
            offset += 1
        body += bytes(offset - len(body))
        header += struct.pack("<II", offset, len(blob)) + name
        body += blob
        offset += len(blob)
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


# --------------------------------------------------------------------------- #
# Patchs                                                                      #
# --------------------------------------------------------------------------- #
def apply_patches(rom):
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
    block += t00_14[0x03191:0x031A8]                         # op068(2, 4) Kain + op0AC(2, ...) équipement
    # Flags : relevés en comparant la mémoire d'une partie normale (devant Baron après le départ)
    # avec la nôtre. Namingway (921 / 941) est volontairement laissé à 0 : c'est une location AP.
    for number in (7, 8, 10, 11, 13, 14, 15, 16, 17, 18, 602, 604, 605, 622):
        block += struct.pack("<HHH", 0x14, 0, number)        # flag_on(0, number)
    block += struct.pack("<HHH", 0x14, 1, 615)               # flag_on(1, 615)
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
    block = t02_02[0x00754:0x007F7]
    block += t00_04[0x0095F:0x00963]                          # op0C6(), op0C6() arrêt musique
    block += t02_02[0x007F7:0x00813]                          # op043('f00', -1044480, 0, -40960, ...)
    block += t00_04[0x009A7:0x009B3]                          # fin d'événement + op005
    target = append_script(rom, "t02_00", block)
    patch_script(rom, "t02_00", 0x00420, goto(target), expected=bytes.fromhex("51 01 04 00 65 30"))

    # (Essai retiré : ne plus placer l'éboulement du Titan sur la carte du monde (f00, 003D2).
    #  Les rochers disparaissaient mais une barrière invisible restait : la collision fait partie
    #  du décor. Le village reste accessible par la Grotte de la Brume.)


def main(argv):
    if len(argv) != 3:
        print(__doc__); return
    rom = load_rom(argv[1])
    apply_patches(rom)
    rom.saveToFile(argv[2])
    print("ROM patchée écrite :", argv[2])


if __name__ == "__main__":
    main(sys.argv)
