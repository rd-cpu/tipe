import string
import random
from module.el_gamal import *
from module.courbe_el_final import *

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



CEstand = CourbeElliptique(2,0,2,49993) # Changer ordre et dico avec o = 49993,1193

cle_secrete = 1789
#l = find_points(CEstand)
#P= l[random.randint(0,len(l))]
P=Point(98, 29352,CEstand)
cle_publique = generate_PK(cle_secrete, P, CEstand)

'''
# enlever les commentaires pour créer un nouveau fichier point et des nouveaux dico 

# Nom du fichier de sortie
nom_fichier = "points_CEstand.txt"

# Écriture dans le fichier
with open(nom_fichier, "w", encoding="utf-8") as fichier:
    for element in l:
        fichier.write(str(element) + "\n")  # chaque élément sur une nouvelle ligne

print(f"✅ La liste a été sauvegardée dans '{nom_fichier}'")


# Nom du fichier à lire
nom_fichier = "points_CEstand.txt"

# Lecture des éléments du fichier
with open(nom_fichier, "r", encoding="utf-8") as fichier:
    elements = [ligne.strip() for ligne in fichier.readlines() if ligne.strip()]

# Alphabet en minuscules
alphabet = string.ascii_lowercase + string.digits + " .,!?;:'\""

dico = {}
for i, element in enumerate(elements):
    if i < len(alphabet):  # si on a moins de 26 éléments
        dico[alphabet[i]] = element
    else:
        dico[f"_{i}"] = element  # identifiant alternatif si plus de 26

# Affichage du dictionnaire
sauvegarder_dictionnaire(dico,"dico_direct.txt")
sauvegarder_dictionnaire(dico_reciproque(dico),"dico_récip.txt")

print("Dictionnaire crée")
#print(dico)
'''


def dico_reciproque(dico):
    return {valeur: cle for cle, valeur in dico.items()}

def sauvegarder_dictionnaire(dico, nom_fichier):
    try:
        with open(nom_fichier, "w", encoding="utf-8") as fichier:
            for cle, valeur in dico.items():
                fichier.write(f"{cle}:{valeur}\n")  # Format clé:valeur par ligne
        print(f"✅ Le dictionnaire a été sauvegardé dans '{nom_fichier}'")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du dictionnaire : {e}")



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



def sauvegarder_message_crypte(message_crypte, nom_fichier="message_crypte.txt"):
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

            y1_str = ligne[:pos + len(") from Courbe elliptique  y² = x³ + 2x² + 2 mod 1193")]
            y2_str = ligne[pos2:]

            try:
                y1 = str_to_point(y1_str, CE)
                y2 = str_to_point(y2_str, CE)
                message_crypte.append((y1, y2))
            except Exception as e:
                print(f"⚠️ Erreur lors du décodage d'une ligne : {e}\n{ligne}")

    print(f"✅ Le message crypté a été chargé depuis '{nom_fichier}'")
    return message_crypte



def envoyeur(message,cle_publique,nom_dico,nom_fichier,CEstand):
    dico = lire_dictionnaire(nom_dico, CEstand)
    m2 = cryptage_liste(text_to_pts(message,dico), cle_publique)
    sauvegarder_message_crypte(m2, nom_fichier)


def receveur(message_reçu,CEstand,nom_dico_recip,cle_secrete):
    dico_recip = lire_dictionnaire(nom_dico_recip, CEstand)
    message_crypte = lire_message_crypte(message_reçu, CEstand)
    m4 = pts_to_text([str(p) for p in decryptage_liste(message_crypte,cle_secrete)], dico_recip)
    return m4

#envoyeur("coucou bg",cle_publique,"dico_direct.txt","mc.txt",CEstand)

#receveur("mc.txt",CEstand,"dico_récip.txt",cle_secrete)