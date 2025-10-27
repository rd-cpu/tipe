from messagerie_final import *
from module.courbe_el_final import *

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

def creation_dicos(CE):
    # Nom du fichier à lire
    fichier_points = nom_fichier_points(CE)
    fichier_dico_direct = nom_fichier_dico_direct(CE)
    fichier_dico_recip = nom_fichier_dico_recip(CE)

    # Lecture des éléments du fichier
    with open(fichier_points, "r", encoding="utf-8") as fichier:
        elements = [ligne.strip() for ligne in fichier.readlines() if ligne.strip()]

    # Minuscules, majuscules et chiffres
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits

    # Ponctuation standard et symbole de séparation pour les espaces
    alphabet += "@.,!?;:'\"()-_"

    # Lettres accentuées (majuscules et minuscules)
    alphabet += "éèêëàâäùûüôöç"
    dico = {}
    for i, element in enumerate(elements):
        if i < len(alphabet):  # si on a moins de 26 éléments
            dico[alphabet[i]] = element
        else:
            dico[f"_{i}"] = element  # identifiant alternatif si plus de 26

    # Affichage du dictionnaire
    sauvegarder_dictionnaire(dico,fichier_dico_direct)
    sauvegarder_dictionnaire(dico_reciproque(dico),fichier_dico_recip)
