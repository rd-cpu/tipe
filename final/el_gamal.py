from random import randint

def bezout_fct(a, b):
   if b == 0:
       return 1, 0
   else:
       u, v = bezout_fct(b, a % b)
       return v, u - (a // b) * v




def generate_PK(cle_secrete, P, CE):
   B = cle_secrete * P  # entier * point
   return CE, P, B




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
   unm1, un = 1, 0
   vnm1, vn = 0, 1
   a = p
   b = e % p
   while b != 0:
       q, r = a // b, a % b
       temp = unm1, vnm1
       unm1, vnm1 = un, vn
       un, vn = -q*un + temp[0], -q*vn + temp[1]
       a, b = b, r


   if a != 1:
       raise ValueError(f"{e} isn't invertible mod {p}")
   return vnm1


