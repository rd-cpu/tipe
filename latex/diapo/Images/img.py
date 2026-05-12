from crack.module.trouve_points_ordres import ordre


class CourbeElliptique:
    def __init__(self, a, b, c, o):
        self.a = a
        self.b = b
        self.c = c
        self.o = o


    def __eq__(self, d):
        return self.a == d.a and self.b == d.b and self.c == d.c and self.o == d.o

class Point:
   def __init__(self, x, y, courbe_el):
       if not isinstance(courbe_el, CourbeElliptique):
           raise TypeError(f"courbe_el : a <CourbeElliptique> was expected, not a {type(courbe_el)}")
       
       self.CE = courbe_el

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

def generate_PK(cle_secrete, P, CE):
    if isinstance(cle_secrete,numbers.Integral):
        B = cle_secrete * P  # entier * point
        return CE, P, B      
    elif isinstance(cle_secrete,np.ndarray) and isinstance(P,np.ndarray):
        return np.array([generate_PK(cle_secrete[i],P[i],CE) for i in range(len(cle_secrete))])

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

def rho_de_pollard_CE(alpha, beta):
    if isinstance(alpha, Infini):
        raise ValueError("ordre(alpha) = 0 (point à l'infini)")

    n = ordre(alpha.CE)
    

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
            return (2 * a) % n
        elif r == 1:
            return (a + 1) % n
        else:
            return a

    def h(x, b, n):
        r = x.x % 3
        if r == 0:
            return (2 * b) % n
        elif r == 1:
            return b
        else:
            return (b + 1) % n

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
            inv_r = pow(r, -1, n)
            return (inv_r * ((A - a) % n)) % n

def kangourous(alpha: Point ,beta: Point ,a ,b ,p):
    
    N = int(np.sqrt(b-a)) + 1 
    
    # saut 
    def f(x:Point ):
        return (x.x + x.y) % N + 1
    
    # kangourous apprivoisés
    x = alpha*b
    dx = 0
    for i in range(N):
        fx = f(x)
        dx += fx
        x += alpha * fx
    
    
    # kangourous sauvages
    y = beta
    dy = 0
    for i in range(4*N):
        
        # les kangourous se rencontrent 
        if y==x :
            return (b+dx-dy)%p
        
        # saut du kangourou sauvage
        fy = f(y)
        dy += fy
        y += alpha * fy        
        
        # arrêt de la course entre les kangourous
        if dy>b-a+dx : 
            print("échec -> changer l'interval ou f")
            return None 

def extension(CE):
    return str(CE.a) + '_' + str(CE.b) + '_' + str(CE.c) + '_' + str(CE.o) 

def nom_fichier_points(CE):
    return "pointsCEs/points_" + extension(CE) + ".txt"

def nom_fichier_ordre(CE):
    return "ordreptsCEs/ordrepts_" + extension(CE) + ".csv"

def nom_fichier_dico_direct(CE):
    return "dicos/dico_direct_"+ extension(CE) + ".txt"

def nom_fichier_dico_recip(CE):
    return "dicos/dico_recip_" + extension(CE) + ".txt"

def nom_fichier_dico_ordre(CE):
    return "dicos_ordre/dico_ordre_" + extension(CE) + ".txt"

def nom_fichier_points_csv(CE):
    return "pointsCEs_csv/ordreptsliste_" + extension(CE) + ".csv"

def nom_fichier_point_ordre_max(CE):
    return "points_ordre_max/pt_om_" + extension(CE) + ".csv"


def nom_fichier_message_crypte(CE):
    return "messages_cryptes/message_crypte_" + extension(CE) + ".txt"

def text_to_pts(texte, dico):
    pts = []
    for e in texte:
        if e in dico:
            pts.append(dico[e])
    return pts

def pts_to_text(l, dico):
    texte = ''
    for e in l:
        if e in dico:
            texte += dico[e]
    return texte

def str_to_point(s, CE):
    s = s.strip()
    if not s.startswith("("):
        raise ValueError(f"Format invalide pour un point : {s}")
    coords = s.split(")")[0].replace("(", "").split(",")
    x, y = int(coords[0]), int(coords[1])
    return Point(x, y, CE)

def point_to_str(point):
    if not isinstance(point, Point):
        raise TypeError(f"Un objet de type Point est attendu, pas {type(point)}")
    return f"({point.x}, {point.y}) from {point.courbe_el}"

def points_to_list(CE):
    pts = []
    nom_f = nom_fichier_points(CE)
    try:
        with open(nom_f, "r", encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne:
                    continue
                try:
                    pt = str_to_point(ligne, CE)
                    pts.append(pt)
                except Exception:
                    # Ligne malformée ou non reconnue : on ignore
                    continue
    except FileNotFoundError:
        print(f"⚠️ Fichier de points introuvable : {nom_f}")
    return pts



def cryptage_liste(message_pts, cle_publique):
    message_chiffre = []
    for pt in message_pts:
        message_chiffre.append(cryptage(cle_publique, pt))
    return message_chiffre

def decryptage_liste(message_chiffre, cle_secrete):
    message_dechiffre = []
    for couple in message_chiffre:
        message_dechiffre.append(decryptage(couple, cle_secrete))
    return message_dechiffre

def lire_dictionnaire(nom_fichier, CE=None):
    dico = {}
    with open(nom_fichier, "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            if ":" not in ligne:
                continue
            cle, valeur = ligne.strip().split(":", 1)
            cle = cle.strip()
            valeur = valeur.strip()
            
            # Si la valeur semble être un point "(x, y)"
            if valeur.startswith("(") and CE is not None:
                try:
                    valeur = str_to_point(valeur, CE)
                except Exception:
                    pass  # Si ce n’est pas un vrai point, on garde la chaîne
            dico[cle] = valeur
    print(f"✅ Le dictionnaire a été chargé depuis '{nom_fichier}'")
    return dico

def sauvegarder_message_crypte(message_crypte,CE):
    nom_fichier = nom_fichier_message_crypte(CE)
    with open(nom_fichier, "w", encoding="utf-8") as fichier:
        for couple in message_crypte:
            y1, y2 = couple
            fichier.write(f"{point_to_str(y1)},{point_to_str(y2)}\n")
    print(f"✅ Le message crypté a été sauvegardé dans '{nom_fichier}'")

def lire_message_crypte(nom_fichier, CE):
    message_crypte = []

    with open(nom_fichier, "r", encoding="utf-8") as fichier:
        for ligne in fichier:
            ligne = ligne.strip()
            if not ligne:
                continue

            # Trouver la position du second point "(" (celui de y2)
            pos = ligne.find(") from Courbe elliptique")
            if pos == -1:
                raise ValueError(f"Ligne invalide (pas de point elliptique détecté) : {ligne}")

            # On cherche le début du deuxième point après le premier
            pos2 = ligne.find("(", pos + 1)
            if pos2 == -1:
                raise ValueError(f"Ligne invalide (2e point manquant) : {ligne}")

            y1_str = ligne[:pos + len(") from Courbe elliptique  y² = x³ + " + str(CE.a) + "x² + " + str(CE.c) + "mod " + str(CE.o))]
            y2_str = ligne[pos2:]

            try:
                y1 = str_to_point(y1_str, CE)
                y2 = str_to_point(y2_str, CE)
                message_crypte.append((y1, y2))
            except Exception as e:
                print(f"⚠️ Erreur lors du décodage d'une ligne : {e}\n{ligne}")

    print(f"✅ Le message crypté a été chargé depuis '{nom_fichier}'")
    return message_crypte

def envoyeur(message,cle_publique,CE,sauvarder=True):
    message = message.replace(" ", ";")
    nom_fichier = nom_fichier_message_crypte(CE)
    dico = lire_dictionnaire(nom_fichier_dico_direct(CE), CE)
    m2 = cryptage_liste(text_to_pts(message,dico), cle_publique)
    if sauvarder:
        sauvegarder_message_crypte(m2,CE)
    return m2

def receveur(CE,cle_secrete, message_crypte=None):
    nom_dico_recip = nom_fichier_dico_recip(CE)
    dico_recip = lire_dictionnaire(nom_dico_recip, CEstand)
    if message_crypte is None:
        message_recu = nom_fichier_message_crypte(CE)
        message_crypte = lire_message_crypte(message_recu, CEstand)
    else :  
        message_recu = message_crypte
    m4 = pts_to_text([str(p) for p in decryptage_liste(message_crypte,cle_secrete)], dico_recip)
    return m4.replace(";", " ")

def random_point(CE):
    nom_fichier = nom_fichier_points(CE)
    l = points_to_list(CE)
    if not l:
        raise ValueError(f"Aucun point trouvé dans '{nom_fichier}'")
    i = random.randint(0, len(l) - 1)
    return l[i]
