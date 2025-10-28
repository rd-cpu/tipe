from module.courbe_el_final import *
from module.el_gamal import *
from module.trouve_points_ordres import *

'''
CEstand = CourbeElliptique(2,0,2,49993)
cle_secrete = 1789

print("début calcul points")
l=find_points(CEstand)
P = point_ordre_max(l,CEstand)
'''
# CEstand = CourbeElliptique(2,0,2,6482753)

# s = randint(0,CEstand.o - 1)
# print("clé secrète :",s)
# P = point_ordre_max_random(CEstand)
# pk = generate_PK(s,P,CEstand)
# Q = point_random(CEstand)


def crack_log_discret_force_brute(P,B,o):
    #On veut k tel que b^k = a mod p
    k = 1
    X = P
    while X != B:
        if k >= o:
           return None
        X = X+P
        k+=1
    return k

def crack_force_brute(pk):
    CE, P, B = pk
    s = crack_log_discret_force_brute(P,B,CE.o)
    return s

def crack_point_force_brute(message_chiffre,pk):
    return decryptage(message_chiffre,crack_force_brute(pk))

# def crack_message_force_brute(pk)