from module.courbe_el_final import *
from module.trouve_points_ordres import *
from sympy import primerange
from random import choice

def creationCE(a,b,p,ordre=None,nb_points=30000,cyclique=True):
    print("Création de la Courbe Elliptique")
    CE = CourbeElliptique(0,a,b,p)
    print("Courbe elliptique crée")
    if ordre == None:
        trouve_points(CE,nb_points=nb_points,cyclique=cyclique)
    else:
        trouve_points(CE,n=ordre,nb_points=nb_points,cyclique=cyclique)

def trouve_CE_viable(a,b,min,max,nb_points=30000,cyclique=True):
    l = list(primerange(min,max))
    p = None
    CE = None
    ordre = None
    found = False
    while not found:
        p = choice(l)
        CE = CourbeElliptique(0,a,b,p)
        ordre = CE.nombre_points_subprocess()
        print(f"ordre pour p = {p} : {ordre}")
        if courbe_cyclique(CE, ordre) == cyclique:
            found = True
            print(f"✓ Courbe viable trouvée: a={a}, b={b}, p={p}, ordre={ordre}, cyclique={cyclique}")

    creationCE(a,b,p,ordre,nb_points=nb_points,cyclique=cyclique)


# 6000000
# 7000000
