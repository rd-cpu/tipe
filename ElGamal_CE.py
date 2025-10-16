from random import randint
from modules.CE_ZnZ import *

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
