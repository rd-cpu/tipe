from courbe_el_final import *
from el_gamal import *

def rho_de_pollard(n, f, x0, max_steps=10000):
    """
    Implements the Pollard's Rho algorithm for integer factorization.

    Parameters:
    n (int): The integer to be factored.
    f (function): The polynomial function used in the algorithm.
    x0 (int): The starting point for the sequence.
    max_steps (int): Maximum number of iterations to prevent infinite loops.

    Returns:
    int: A non-trivial factor of n if found, otherwise None.
    """
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    x = x0
    y = x0
    d = 1
    step = 0

    while d == 1 and step < max_steps:
        x = f(x) % n
        y = f(f(y)) % n
        d = gcd(abs(x - y), n)
        step += 1

    if d == n:
        return None  # Failure to find a factor
    return d  # Non-trivial factor found


def rho_de_pollard_CE(alpha, beta):
    a = 0
    b = 0
    x = 1
    n = alpha.o
    A = a
    B = b
    X = x
    def f(x,alpha,beta):
        r = x.x % 3
        if r == 0 :
            x = x*x
        elif r == 1 :
            x = x*alpha
        else: 
            x = x*beta
        return x
    def g(x,a,n):
        r = x.x % 3
        if r == 0 :
            a = a
        elif r == 1 :
            a = 2*a%n
        else: 
            a = (a+1)%n
        return a
    def h(x,b,n):
        r = x.x % 3
        if r == 0 :
            b = b 
        elif r == 1 :
            b = 2*b%n
        else: 
            b = (b+1)%n
        return b
    def appliquer(x,a,b):
        x = f(x,alpha,beta)
        a = g(x,a,n)
        b = h(x,b,n)
    while True:
        appliquer(x,a,b)
        appliquer(X,A,B)
        appliquer(X,A,B)
        if x == X:
            r = b-B 
            if r == 0:
                return None
            return inv_mod(r,n) * (A-a)  % n

def crack_rho_de_pollard(pk):
    CE, P, B = pk
    s = rho_de_pollard(P,B,CE.o)
    return s

def crack_point_rho_de_pollard(message_chiffre,pk):
    return decryptage(message_chiffre,crack_rho_de_pollard(pk))


'''CEstand = CourbeElliptique(2,0,2,6482753)

s = randint(0,CEstand.o - 1)
print("clé secrète :",s)
P = point_random(CEstand)
pk = generate_PK(s,P,CEstand)
Q = point_random(CEstand)
M = cryptage(pk,Q)
Md = crack_point_rho_de_pollard(M,pk)
'''