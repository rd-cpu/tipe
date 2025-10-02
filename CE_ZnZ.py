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




class CourbeElliptique:
   def __init__(self, a, b, c, o):
       self.a = a
       self.b = b
       self.c = c
       self.o = o
       self.f = lambda x: x ** 3 + self.a * x ** 2 + self.b * x + self.c
       self.fp = lambda x: 3 * x ** 2 + 2 * self.a * x + self.b


   def __eq__(self, d):
       return self.a == d.a and self.b == d.b and self.c == d.c and self.o == d.o


   def __repr__(self):
       return "Courbe elliptique : y² = x³" + \
           (
               "" if self.a == 0 else " + x²" if self.a == 1 else " - x²" if self.a == -1 else f" + {self.a}x²" if self.a > 0 else f" - {-self.a}x²") + \
           ("" if self.b == 0 else " + x" if self.b == 1 else " - x" if self.b == -1 else f" + {self.b}x" if self.b > 0 else f" - {-self.b}x") + \
           ("" if self.c == 0 else f" + {self.c}" if self.c >= 0 else f" - {-self.c}") \
           + f" mod {self.o}"


   def __contains__(self, p):
       if not isinstance(p, Point):
           raise TypeError(f"in <CourbeElliptique> requires a point of type <Point> as left operand, not {type(p)}")
       return self.f(p.x) % self.o == p.y ** 2 % self.o




class Point:
   def __init__(self, x, y, courbe_el):
       if not isinstance(courbe_el, CourbeElliptique):
           raise TypeError(f"courbe_el : a <CourbeElliptique> was expected, not a {type(courbe_el)}")


       self.x = x % courbe_el.o
       self.y = y % courbe_el.o


       if x != float("inf") and self not in courbe_el:
           raise ValueError(f"{courbe_el} doesn't contains a point with ({x}, {y}) mod {courbe_el.o} = ({self.x}, {self.y}) coordinates")
       self.courbe_el = courbe_el


   def __add__(self, other):
       if self.courbe_el != other.courbe_el:
           raise ValueError(f"{self} and {other} aren't part of the same curb, they can't be add")


       return -(self*other)


   def __repr__(self):
       return f"({self.x}, {self.y}) from {self.courbe_el}"


   def __mul__(self, other):
       if isinstance(other, int):
           return self.mul_by_int(other)


       if isinstance(other, Point):
           return self.etoile(other)


       raise TypeError("a <Point> cannot be multiplied by something else than an <int> or a <Point>")


   def etoile(self, other):
       if self.courbe_el != other.courbe_el:
           raise ValueError(f"{self} and {other} aren't part of the same curb, * isn't defined for each other")
       if isinstance(other, Infini):
           return -self
       if self.x == other.x:
           if self.y != other.y or self.y == 0:
               return Infini(self.courbe_el)
           lamb = self.courbe_el.fp(self.x) * inv_mod(2*self.y, self.courbe_el.o)
       else:
           lamb = (self.y - other.y) * inv_mod(self.x - other.x, self.courbe_el.o)
       x3 = lamb ** 2 - self.courbe_el.a - self.x - other.x


       return Point(x3, lamb * x3 - lamb * self.x + self.y, self.courbe_el)


   def mul_by_int(self, other):
       if other < 0:
           return -self * (-other)


       if other == 0:
           return Infini(self.courbe_el)


       sub = self * (other // 2)
       if other % 2:
           return sub + sub + self
       return sub + sub


   def __rmul__(self, lamb):
       return self*lamb


   def __eq__(self, other):
       return (self.x, self.y, self.courbe_el) == (other.x, other.y, other.courbe_el)


   def __neg__(self):
       return Point(self.x, -self.y, self.courbe_el)


   def __sub__(self, other):
       return self + (-other)


   def ordre(self):
       k = 1
       inf = Infini(self.courbe_el)
       while self*k != inf:
           k += 1
       return k




class Infini(Point):
   def __init__(self, courbe_el):
       super().__init__(float("inf"), float("inf"), courbe_el)
       self.x = float("inf")
       self.y = float("inf")


   def etoile(self, other):
       return -other


   def __repr__(self):
       return f"Infini from {self.courbe_el}"


   def __neg__(self):
       return self




def find_points(c):
   l = []
   for x in range(c.o):
       for y in range(c.o):
           try:
               p = Point(x,y,c)
               l.append(p)
           except:
               pass
   return l



# Définir la liste
ma_liste = ["Pomme", "Banane", "Cerise", "Orange"]

# Nom du fichier de sortie
nom_fichier = "ma_liste.txt"

# Écriture dans le fichier
with open(nom_fichier, "w", encoding="utf-8") as fichier:
    for element in ma_liste:
        fichier.write(str(element) + "\n")  # chaque élément sur une nouvelle ligne

print(f"✅ La liste a été sauvegardée dans '{nom_fichier}'")






import string

# Nom du fichier à lire
nom_fichier = "ma_liste.txt"

# Lecture des éléments du fichier
with open(nom_fichier, "r", encoding="utf-8") as fichier:
    elements = [ligne.strip() for ligne in fichier.readlines() if ligne.strip()]

# Alphabet en minuscules
alphabet = string.ascii_lowercase

# Création du dictionnaire réciproque : lettre -> élément
dico = {}
for i, element in enumerate(elements):
    if i < len(alphabet):  # si on a moins de 26 éléments
        dico[alphabet[i]] = element
    else:
        dico[f"_{i}"] = element  # identifiant alternatif si plus de 26

# Affichage du dictionnaire
print("📘 Dictionnaire réciproque créé :")
print(dico)




def text_to_pts(str):
    l = []
    for e in str:
        if e in dico :
            l.append(dico[e])            
    return l


