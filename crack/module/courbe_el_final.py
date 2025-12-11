#from module.el_gamal import inv_mod
from random import randint
import subprocess
import numbers
import platform
from module.el_gamal import inv_mod

class CourbeElliptique:
    def __init__(self, a, b, c, o):
        self.a = a
        self.b = b
        self.c = c
        self.o = o
        # Use methods for f and fp instead of lambdas so the object is picklable
        # (lambdas are not picklable and break multiprocessing on Windows)


    def __eq__(self, d):
        return self.a == d.a and self.b == d.b and self.c == d.c and self.o == d.o


    def __repr__(self):
        return "Courbe elliptique  y² = x³" + \
            ("" if self.a == 0 else " + x²" if self.a == 1 else " - x²" if self.a == -1 else f" + {self.a}x²" if self.a > 0 else f" - {-self.a}x²") + \
            ("" if self.b == 0 else " + x" if self.b == 1 else " - x" if self.b == -1 else f" + {self.b}x" if self.b > 0 else f" - {-self.b}x") + \
            ("" if self.c == 0 else f" + {self.c}" if self.c >= 0 else f" - {-self.c}") \
            + f" mod {self.o}"


    def __contains__(self, p):
        if not isinstance(p, Point):
            raise TypeError(f"in <CourbeElliptique> requires a point of type <Point> as left operand, not {type(p)}")
        return self.f(p.x) % self.o == p.y ** 2 % self.o

    def legendre_symbol(self, n):
        """Retourne 0 si n ≡ 0 mod p, 1 si n est un carré mod p, -1 sinon"""
        n = n % self.o
        if n == 0:
            return 0
        return pow(n, (self.o - 1) // 2, self.o) if pow(n, (self.o - 1) // 2, self.o) != self.o - 1 else -1

    def nombre_points(self):
        """Retourne le nombre exact de points sur la courbe elliptique mod p"""
        count = 0
        for x in range(self.o):
            rhs = (self.f(x)) % self.o
            ls = self.legendre_symbol(rhs)
            if ls == 1:
                count += 2  # deux solutions pour y
            elif ls == 0:
                count += 1  # une solution pour y
            # ls == -1 => aucune solution
        return count + 1  # ajouter le point à l'infini
    
    
    def nombre_points_subprocess(self):
        """Compute number of points on curve using PARI/GP (Linux) or Python fallback (Windows)"""
        os_type = platform.system()

        if os_type == "Linux":
            # Linux: use PARI/GP via shell pipe
            cmd = "echo 'E = ellinit([0," + str(self.a) + ",0," + str(self.b) + "," + str(self.c) + "]," + str(self.o) + "); print(ellcard(E));' | gp -q -f"
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=60)
                try:
                    return int(result.stdout.strip())
                except ValueError:
                    print(f"Failed to parse PARI/GP output: {result.stdout}")
                    if result.stderr:
                        print(f"stderr: {result.stderr}")
                    print("Falling back to Python calculation")
                    return self.nombre_points()
            except subprocess.TimeoutExpired:
                print("PARI/GP timeout; falling back to Python calculation")
                return self.nombre_points()

        elif os_type == "Windows":
            # Windows: try gp.exe if installed, else fall back to Python
            pari_cmd = f"E = ellinit([0,{self.a},0,{self.b},{self.c}],{self.o}); print(ellcard(E));"
            try:
                result = subprocess.run(
                    ['gp', '-q', '-f'],
                    input=pari_cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                try:
                    return int(result.stdout.strip())
                except ValueError:
                    print(f"Failed to parse PARI/GP output: {result.stdout}")
                    if result.stderr:
                        print(f"stderr: {result.stderr}")
                    print("Falling back to Python calculation")
                    return self.nombre_points()
            except FileNotFoundError:
                # gp not found; fall back to Python calculation
                print("gp.exe not found on Windows; using Python fallback for point counting")
                return self.nombre_points()
            except subprocess.TimeoutExpired:
                print("PARI/GP timeout on Windows; falling back to Python calculation")
                return self.nombre_points()

        else:
            # Unknown OS; fall back to Python
            print(f"Unknown OS: {os_type}; using Python fallback")
            return self.nombre_points()

    # --- polynomial and derivative as methods (picklable) ---
    def f(self, x):
        """Polynomial f(x) = x^3 + a x^2 + b x + c (mod p)."""
        return x ** 3 + self.a * x ** 2 + self.b * x + self.c

    def fp(self, x):
        """Derivative f'(x) = 3 x^2 + 2 a x + b (mod p)."""
        return 3 * x ** 2 + 2 * self.a * x + self.b



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
       if isinstance(other, numbers.Integral):
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
            print(ordre_point)
    return point


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

