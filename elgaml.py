#/usr/bin/env python3
from random import randint

def bezout_fct(a, b):
    if b == 0:
        return 1, 0
    else:
        u, v = bezout_fct(b, a % b)
        return v, u - (a // b) * v

def inv_mod(a,b):
    u,v = bezout_fct(a,b)
    return u

def expo_discrete_rapide(b,k,p):
    if k == 0:
        return 1
    else:
        a = b*b % p
        if k%2 == 0:
            return (expo_discrete_rapide(a,k//2,p))%p
        else:
            return (b*expo_discrete_rapide(a,k//2,p))%p

def generate_PK(cle_secrete, n):
    H = range(1, n)
    g = randint(2, n - 1)
    A = expo_discrete_rapide(g,cle_secrete,n)
       return H, n, g, A


def cryptage(cle_publique, message):
    H, p, g, A = cle_publique
    k = randint(1, p - 1)
    y1 = expo_discrete_rapide(g,k,p)
    y2 = ((message % p) * expo_discrete_rapide(A,k,p)) % p
    return y1, y2


def decryptage(message_encrypte, cle_secrete, n):
    y1, y2 = message_encrypte
    inverse = inv_mod((y1**cle_secrete)%n,n)
    return (inverse * y2) % n


def is_prime(n):
    if n % 2 == 0:
        return False
    for i in range(3,int(n**(1/2)),2):
        if n % i == 0:
            return False
    return True


def crack_log_discret(a,b,p):
    #On veut k tel que b^k = a mod p
    k = 1
    A = b
    while b**k % p!= a % p:
        if A % p!= a % p:
            A = (A*b)%p
            k+=1
        if k >= p:
           return None
    return k

def crack(pk):
    H, n, g, A = pk
    s = crack_log_discret(A,g,n)
    return s