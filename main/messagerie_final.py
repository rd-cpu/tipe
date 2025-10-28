import string
import random
from module.el_gamal import *
from module.courbe_el_final import *

def extension(CE):
    return str(CE.a) + '_' + str(CE.b) + '_' + str(CE.c) + '_' + str(CE.o) 

def nom_fichier_points(CE):
    return "pointsCEs/points_" + extension(CE) + ".txt"

def nom_fichier_ordre(CE):
    return "ordreCEs/ordre_" + extension(CE) + ".csv"

def nom_fichier_dico_direct(CE):
    return "dicos/dico_direct_"+ extension(CE) + ".txt"

def nom_fichier_dico_recip(CE):
    return "dicos/dico_recip_" + extension(CE) + ".txt"

def nom_fichier_message_crypte(CE):
    return "messages_cryptes/message_crypte_" + extension(CE) + ".txt"

def text_to_pts(texte, dico):
    pts = []
    for e in texte:
        if e in dico:
            pts.append(dico[e])
    return pts

def pts_to_text(l, dico):
    texte = ''
    for e in l:
        if e in dico:
            texte += dico[e]
    return texte

def str_to_point(s, CE):
    s = s.strip()
    if not s.startswith("("):
        raise ValueError(f"Format invalide pour un point : {s}")
    coords = s.split(")")[0].replace("(", "").split(",")
    x, y = int(coords[0]), int(coords[1])
    return Point(x, y, CE)

def point_to_str(point):
    if not isinstance(point, Point):
        raise TypeError(f"Un objet de type Point est attendu, pas {type(point)}")
    return f"({point.x}, {point.y}) from {point.courbe_el}"

def cryptage_liste(message_pts, cle_publique):
    message_chiffre = []
    for pt in message_pts:
        message_chiffre.append(cryptage(cle_publique, pt))
    return message_chiffre

def decryptage_liste(message_chiffre, cle_secrete):
    message_dechiffre = []
    for couple in message_chiffre:
        message_dechiffre.append(decryptage(couple, cle_secrete))
    return message_dechiffre

def lire_dictionnaire(nom_fichier, CE=None):
    dico = {}
    with open(nom_fichier, "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            if ":" not in ligne:
                continue
            cle, valeur = ligne.strip().split(":", 1)
            cle = cle.strip()
            valeur = valeur.strip()
            
            # Si la valeur semble être un point "(x, y)"
            if valeur.startswith("(") and CE is not None:
                try:
                    valeur = str_to_point(valeur, CE)
                except Exception:
                    pass  # Si ce n’est pas un vrai point, on garde la chaîne
            dico[cle] = valeur
    print(f"✅ Le dictionnaire a été chargé depuis '{nom_fichier}'")
    return dico

def sauvegarder_message_crypte(message_crypte,CE):
    nom_fichier = nom_fichier_message_crypte(CE)
    with open(nom_fichier, "w", encoding="utf-8") as fichier:
        for couple in message_crypte:
            y1, y2 = couple
            fichier.write(f"{point_to_str(y1)},{point_to_str(y2)}\n")
    print(f"✅ Le message crypté a été sauvegardé dans '{nom_fichier}'")

def lire_message_crypte(nom_fichier, CE):
    message_crypte = []

    with open(nom_fichier, "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            ligne = ligne.strip()
            if not ligne:
                continue

            # Trouver la position du second point "(" (celui de y2)
            pos = ligne.find(") from Courbe elliptique")
            if pos == -1:
                raise ValueError(f"Ligne invalide (pas de point elliptique détecté) : {ligne}")

            # On cherche le début du deuxième point après le premier
            pos2 = ligne.find("(", pos + 1)
            if pos2 == -1:
                raise ValueError(f"Ligne invalide (2e point manquant) : {ligne}")

            y1_str = ligne[:pos + len(") from Courbe elliptique  y² = x³ + " + str(CE.a) + "x² + " + str(CE.c) + "mod " + str(CE.o))]
            y2_str = ligne[pos2:]

            try:
                y1 = str_to_point(y1_str, CE)
                y2 = str_to_point(y2_str, CE)
                message_crypte.append((y1, y2))
            except Exception as e:
                print(f"⚠️ Erreur lors du décodage d'une ligne : {e}\n{ligne}")

    print(f"✅ Le message crypté a été chargé depuis '{nom_fichier}'")
    return message_crypte

def envoyeur(message,cle_publique,CE):
    message = message.replace(" ", ";")
    nom_fichier = nom_fichier_message_crypte(CE)
    dico = lire_dictionnaire(nom_fichier_dico_direct(CE), CE)
    m2 = cryptage_liste(text_to_pts(message,dico), cle_publique)
    sauvegarder_message_crypte(m2,CE)

def receveur(CE,cle_secrete):
    message_recu = nom_fichier_message_crypte(CE)
    nom_dico_recip = nom_fichier_dico_recip(CE)
    dico_recip = lire_dictionnaire(nom_dico_recip, CEstand)
    message_crypte = lire_message_crypte(message_recu, CEstand)
    m4 = pts_to_text([str(p) for p in decryptage_liste(message_crypte,cle_secrete)], dico_recip)
    return m4.replace(";", " ")

def points_to_list(CE):
    nom_fichier = nom_fichier_points(CE)
    with open(nom_fichier, "r", encoding="utf-8") as fichier:
        lstr = [ligne.strip() for ligne in fichier.readlines() if ligne.strip()]
        l = [str_to_point(s,CE) for s in lstr]
        return l

def random_point(CE):
    nom_fichier = nom_fichier_points(CE)
    l = points_to_list(CE)
    i = randint(0,len(l)-1)
    return l[i]


CEstand = CourbeElliptique(2,0,2,49993) # Changer ordre et dico avec o = 49993,1193



cle_secrete = 1789
#l = find_points(CEstand)
#P= l[random.randint(0,len(l))]
P=Point(28,31632,CEstand)
cle_publique = generate_PK(cle_secrete, P, CEstand)


#envoyeur("coucou bg",cle_publique,CEstand)

#receveur(CEstand,cle_secrete)