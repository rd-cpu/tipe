from module.courbe_el_final import *
from module.el_gamal import *
from messagerie_final import *
'''
CEstand = CourbeElliptique(2,0,2,49993)
cle_secrete = 1789

print("début calcul points")
l=find_points(CEstand)
P = point_ordre_max(l,CEstand)
'''
s = randint(2000,CEstand.o - 1)
print("clé secrète :",s)
pk = generate_PK(s,P,CEstand)
P = point_random(CEstand,"points_CEstand.txt")

def crack_log_discret(P,B,o):
    #On veut k tel que b^k = a mod p
    k = 1
    X = P
    while X != B:
        if k >= o:
           return None
        X = X+P
        k+=1
    return k

def crack(pk):
    CE, P, B = pk
    s = crack_log_discret(P,B,CE.o)
    return s

def crack_message(message_chiffre,pk):
    receveur()
