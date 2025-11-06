from module.courbe_el_final import *
from module.trouve_points_ordres import *
from sympy import primerange
from random import choice

def creationCE(a,b,p,ordre=None):
    print("Création de la Courbe Elliptique")
    CE = CourbeElliptique(a,0,b,p)
    print("Courbe elliptique crée")
    if ordre == None:
        trouve_points(CE)
    else:
        trouve_points(CE,n=ordre)

def trouve_CE_viable(a,b,min,max):
    l = list(primerange(min,max))
    p = choice(l)
    CE = CourbeElliptique(0,a,b,p)
    try:
        ordre = CE.nombre_points_subprocess()
        print(n)

    except:
        print("Frero t'as installé pari-gp et implémenté nombre_points_subprocess pour windows ??")
    while not courbe_cyclique(CE,ordre):
        p = choice(l)
        CE = CourbeElliptique(0,a,b,p)
        ordre = CE.nombre_points_subprocess()
        print(ordre)

    creationCE(a,b,p,ordre)



# 6000000
# 7000000
