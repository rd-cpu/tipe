from messagerie_final import *

def creer_fichier(CE):
    l = find_points(CE)
    print(l)
    nom_fichier = nom_fichier_points(CE)
    try:
        with open(nom_fichier, "w", encoding="utf-8") as fichier:
            for point in l:
                print(type(point))
                fichier.write(repr(point) + '\n')  
        print(f"✅ L'ensemble des points a été sauvegardé dans '{nom_fichier}' avec succès")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de l'ensemble des points : {e}")
