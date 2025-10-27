from module.el_gamal import *
from module.courbe_el_final import *

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

