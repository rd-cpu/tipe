from module.courbe_el_final import *
from module.noms_fichiers import *
from module.trouve_points_ordres import *

def creationCE(a,b,c,p):
    print("Création de la Courbe Elliptique")
    CE = CourbeElliptique(a,b,c,p)
    print("Courbe elliptique crée")
    etude_ordre_rapide_et_export(CE)
