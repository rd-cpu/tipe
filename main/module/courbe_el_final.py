from module.el_gamal import inv_mod
from random import randint

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
       return "Courbe elliptique  y² = x³" + \
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
        inf = Infini(self.courbe_el)
        if self == inf:
            return 0
        k = 1
        while self*k != inf:
            k += 1
        return k

def point_ordre_max(l,CE):
    point = Infini(CE)
    ordre_point = 0
    for p in l:
        print("etude du point",p)
        if ordre_point == CE.o: return point
        ordretemp = p.ordre()
        if ordretemp > ordre_point: 
            point = p
            ordre_point = ordretemp
    return point



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
            if y**2 % c.o == c.f(x) % c.o:
                print(f"Point trouvé : ({x},{y})")
                p = Point(x,y,c)
                l.append(p)
            if len(l) > 10000:
                return l
    return l

