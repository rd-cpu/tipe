from module.courbe_el_final import *
from module.trouve_points_ordres import *
from sympy import primerange
from random import choice

def creationCE(b,c,o,ordre=None,nb_points=30000,cyclique=True, a = 0):
    print("Création de la Courbe Elliptique")
    CE = CourbeElliptique( a, b, c, o)
    print("Courbe elliptique crée")
    if ordre == None:
        trouve_points(CE,nb_points=nb_points,cyclique=cyclique)
    else:
        trouve_points(CE,n=ordre,nb_points=nb_points,cyclique=cyclique)

def trouve_CE_viable(b,c,min,max,nb_points=30000,cyclique=True,a = 0):
    l = list(primerange(min,max))
    p = None
    CE = None
    ordre = None
    found = False
    while not found:
        p = choice(l)
        CE = CourbeElliptique( a, b, c, p)
        ordre = CE.nombre_points_subprocess()
        print(f"ordre pour p = {p} : {ordre}")
        if courbe_cyclique(CE, ordre) == cyclique:
            found = True
            print(f"✓ Courbe viable trouvée: a={a}, b={b}, p={p}, ordre={ordre}, cyclique={cyclique}")

    creationCE(a,b,p,ordre,nb_points=nb_points,cyclique=cyclique)

#CE1

# 6000000
# 7000000
