from messagerie_final import *

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


CEstand = CourbeElliptique(2,0,2,49993) # Changer ordre et dico avec o = 49993,1193

cle_secrete = 1789
#l = find_points(CEstand)
#P= l[random.randint(0,len(l))]
P=Point(98, 29352,CEstand)
cle_publique = generate_PK(cle_secrete, P, CEstand)



'''
# Nom du fichier de sortie
nom_fichier = "points_CEstand.txt"

# Écriture dans le fichier
with open(nom_fichier, "w", encoding="utf-8") as fichier:
    for element in l:
        fichier.write(str(element) + "\n")  # chaque élément sur une nouvelle ligne

print(f"✅ La liste a été sauvegardée dans '{nom_fichier}'")
'''
# Nom du fichier à lire
nom_fichier = "points_CEstand.txt"

# Lecture des éléments du fichier
with open(nom_fichier, "r", encoding="utf-8") as fichier:
    elements = [ligne.strip() for ligne in fichier.readlines() if ligne.strip()]

# Alphabet en minuscules
alphabet = string.ascii_lowercase + string.digits + ".,!?;:'\""

dico = {}
for i, element in enumerate(elements):
    if i < len(alphabet):  # si on a moins de 26 éléments
        dico[alphabet[i]] = element
    else:
        dico[f"_{i}"] = element  # identifiant alternatif si plus de 26

# Affichage du dictionnaire
sauvegarder_dictionnaire(dico,"dico_direct.txt")
sauvegarder_dictionnaire(dico_reciproque(dico),"dico_récip.txt")
