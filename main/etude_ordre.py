from module.el_gamal import *
from module.courbe_el_final import *
from messagerie_final import *
import csv
from collections import Counter
from creer_dico import *


CEstand = CourbeElliptique(2,0,2,49993)

def point_ordre_max_direct(CE):
    point_max = Infini(CE)
    ordre_max = 0
    for x in range(CE.o):
        for y in range(CE.o):
            try:
                p = Point(x, y, CE)
                ordre_p = p.ordre()
                if ordre_p > ordre_max:
                    point_max = p
                    ordre_max = ordre_p
                    print(ordre_max)
                    # Si on a atteint l'ordre maximal, on peut s'arrêter
                    if ordre_max == CE.o:
                        return point_max
            except:
                # Le point (x,y) n’est pas sur la courbe
                pass
    return point_max

import re


def ordre_distri(CE):
    l = points_to_list(CE)
    lo = []
    for e in l:
        o = e.ordre()
        #print("Point:", e, "Ordre:", o)
        lo.append(o)
    return lo        


def export_ordre_distribution(CE):

    liste_ordres = ordre_distri(CE)
    nom_fichier = nom_fichier_ordre(CE)
    # On compte combien de fois chaque ordre apparaît
    distribution = Counter(liste_ordres)

    # On écrit le CSV
    with open(nom_fichier, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Ordre", "Frequence"])
        for ordre, freq in sorted(distribution.items()):
            writer.writerow([ordre, freq])

    print(f"✅ Fichier '{nom_fichier}' créé avec succès ({len(distribution)} ordres distincts).")


def etude_ordre(CE):
    d = {}
    points = points_to_list(CE)
    lo = []

    for p in points:
        try:
            o = p.ordre()
            lo.append(o)
            d[(p.x, p.y)] = o
            print(f"Point {p} -> Ordre {o}")
        except Exception as e:
            print(f"Erreur pour le point {p}: {e}")

    nom_fichier = nom_fichier_ordre(CE)
    sauvegarder_dictionnaire(d, nom_fichier_dico_ordre(CE))
    
    distribution = Counter(lo)

    with open(nom_fichier, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Ordre", "Frequence"])
        for ordre, freq in sorted(distribution.items()):
            writer.writerow([ordre, freq])

    print(f"✅ Fichier '{nom_fichier}' créé avec succès ({len(distribution)} ordres distincts).")

