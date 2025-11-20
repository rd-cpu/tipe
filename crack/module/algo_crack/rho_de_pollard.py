from module.courbe_el_final import *
from module.el_gamal import *
from random import randint
from module.trouve_points_ordres import ordre_rapide

def rho_de_pollard_CE(alpha, beta):

    n = alpha.ordre()

    if n == 0:
        raise ValueError("ordre(alpha) = 0 (point à l'infini)")

    a = randint(0, n-1)
    b = randint(0, n-1)
    x = a*alpha + b*beta
    A = a
    B = b
    X = x

    def f(x, alpha, beta):
        r = x.x % 3
        if r == 0:
            return x + x       
        elif r == 1:
            return x + alpha
        else:
            return x + beta
        
    def g(x, a, n):
        r = x.x % 3
        if r == 0:
            return (2*a) % n
        elif r == 1:
            return (a+1) % n
        else:
            return a

    def h(x, b, n):
        r = x.x % 3
        if r == 0:
            return (2*b) % n
        elif r == 1:
            return b
        else:
            return (b+1) % n

    def appliquer(x, a, b):
        x2 = f(x, alpha, beta)
        a2 = g(x, a, n)
        b2 = h(x, b, n)
        return x2, a2, b2

    while True:
        x, a, b = appliquer(x, a, b)

        X, A, B = appliquer(X, A, B)
        X, A, B = appliquer(X, A, B)

        if x == X:
            r = (b - B) % n
            if r == 0:
                return "échec"
            inv_r = inv_mod(r, n)
            return (inv_r * (A - a)) % n
        


def crack_rho_de_pollard(pk):
    CE, P, B = pk
    s = rho_de_pollard_CE(P,B)
    return s

def crack_point_rho_de_pollard(message_chiffre,pk):
    s = crack_rho_de_pollard(pk) 
    print(s)
    return decryptage(message_chiffre,s)


'''CEstand = CourbeElliptique(2,0,2,6482753)

s = randint(0,CEstand.o - 1)
print("clé secrète :",s)
P = point_random(CEstand)
pk = generate_PK(s,P,CEstand)
Q = point_random(CEstand)
M = cryptage(pk,Q)
Md = crack_point_rho_de_pollard(M,pk)
'''