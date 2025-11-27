from random import randint
import numpy as np
from module.courbe_el_final import *
import numbers

def bezout_fct(a, b):
    if b == 0:
        return 1, 0
    else:
        u, v = bezout_fct(b, a % b)
        return v, u - (a // b) * v




def generate_PK(cle_secrete, P, CE):
    if isinstance(cle_secrete,numbers.Integral):
        B = cle_secrete * P  # entier * point
        return CE, P, B      
    # elif isinstance(cle_secrete,np.ndarray) and isinstance(P,Point):
    #     return np.array([generate_PK(s,P,CE) for s in cle_secrete])
    elif isinstance(cle_secrete,np.ndarray) and isinstance(P,np.ndarray):
        return np.array([generate_PK(cle_secrete[i],P[i],CE) for i in range(len(cle_secrete))])






def cryptage(cle_publique, message):
    CE, P, B = cle_publique
    k = randint(1, CE.o - 1)
    y1 = k*P
    y2 = message + k*B
    return y1, y2




def decryptage(message_encrypte, cle_secrete):
    y1, y2 = message_encrypte
    m = y2 - cle_secrete*y1
    return m




def est_premier(n):
    if n % 2 == 0:
        return False
    for i in range(3, int(n**(1/2)), 2):
        if n % i == 0:
            return False
    return True

def trouve_premier():
    i = randint(200,2000)
    while not est_premier(i):
        i+=1
    return i


def inv_mod(e, p):
    try:
        return pow(e % p, -1, p)
    except ValueError:
        raise ValueError(f"{e} isn't invertible mod {p}")
