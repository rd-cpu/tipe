from module.courbe_el_final import *
from module.noms_fichiers import *
from module.trouve_points_ordres import *

def creationCE(a,b,p):
    print("Création de la Courbe Elliptique")
    CE = CourbeElliptique(a,0,b,p)
    print("Courbe elliptique crée")
    trouve_points(CE)

