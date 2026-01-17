from module.courbe_el_final import CourbeElliptique, Point, Infini
from collections import Counter
import csv
import math
from module.noms_fichiers import *
#from creer_dico import *
from random import randint
import sympy as sp
# from sage.all import * #On triche c'est la biblio qui a déjà les courbes elliptiques mais c'est pour calculer l'ordre plus facilement


def factorint(n):
    i = 2
    factors = {}
    while i * i <= n:
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n //= i
        i += 1 if i == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


# ============================================================
# --- Tonelli–Shanks (pour tout p premier) ---
# ============================================================

def tonelli_shanks(n, p):
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None  # pas de racine

    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)

    # factorisation p-1 = q * 2^s
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1

    # trouver un non-residu quadratique z
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)

    while True:
        if t == 0:
            return 0
        if t == 1:
            return r
        i = 0
        t2i = t
        while t2i != 1:
            t2i = pow(t2i, 2, p)
            i += 1
            if i == m:
                return None
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p


# ============================================================
# --- Recherche rapide des points (Tonelli–Shanks) ---
# ============================================================

def find_points_fast(CE,n):
    p = CE.o
    pts = []
    # for x in range(p):
    #     fx = CE.f(x) % p
    #     y = tonelli_shanks(fx, p)
    #     if y is None:
    #         continue
    #     pts.append(Point(x, y, CE))
    #     if y != 0:
    #         pts.append(Point(x, (-y) % p, CE))
    # return pts
    x = 0
    i = 0
    x_dejavus = []
    #m = min(n,CE.o)
    m = CE.o
    while i < n and i < m:
        x = randint(0,CE.o - 1)
        while x in x_dejavus:
            x = randint(0,CE.o - 1)
        x_dejavus.append(x)
        fx = CE.f(x) % p
        y = tonelli_shanks(fx, p)
        if y is None:
            continue
        pts.append(Point(x, y, CE))
        if y != 0:
            pts.append(Point(x, (-y) % p, CE))
            print(f"Point ajouté : ({x},{-y})   pt n°{i}   progrès = {int(i/n*100)}%")
            i += 1
        i += 1
    return pts


# ============================================================
# --- Multiplication rapide de point (double-and-add) ---
# ============================================================

def mult_point(P, k):
    CE = P.courbe_el
    R = Infini(CE)
    Q = P
    kk = k
    if kk < 0:
        Q = -Q
        kk = -kk
    while kk > 0:
        if kk & 1:
            R = R + Q
        Q = Q + Q
        kk >>= 1
    return R


# ============================================================
# --- Calcul rapide de l’ordre ---
# ============================================================

def ordre_rapide(P, n=None):
    CE = P.courbe_el
    if isinstance(P, Infini):
        return 0

    if n is None:
        pts = find_points_fast(CE)
        n = len(pts) + 1

    factors = factorint(n)
    order = n
    for q, e in factors.items():
        for _ in range(e):
            if mult_point(P, order // q) == Infini(CE):
                order //= q
            else:
                break
    return order

# def ordre_courbe(CE):
#     a,b,c,p = CE.a,CE.b,CE.c,CE.o
#     F = GF(p)  # Corps fini à p éléments
#     E = EllipticCurve(F, [a, b, c])  # Courbe elliptique y^2 = x^3 + a x^2 + b x + c
#     return E.cardinality()  # Calcul du nombre de points sur E


# ============================================================
# --- Étude complète (avec export CSV + DICO) ---
# ============================================================
'''
def etude_ordre_rapide_et_export(CE, export_csv=True,verbose=True): # rajouter verbose=True comme argument si besoin
    points = find_points_fast(CE)
    if verbose: 
        print("points trouvés")
    try:
        print("Calcul du nombre de points par fichier executable")
        n = CE.nombre_points_subprocess() # appelle l'executable c
    except Exception as e:
        if verbose :
            print(f"erreur bon bah finalement on calcule en python mskn : {e}")
        n = CE.nombre_points() # appelle les fonctions python tant pis
    if verbose:
        print(f"Ordre estimé du groupe : {n}")

    distribution = Counter()
    dico = {}
    max_order = 0
    max_point = Infini(CE)
    l = []

    for i, P in enumerate(points, start=1):
        try:
            o = ordre_rapide(P, n)
        except Exception as e:
            if verbose:
                print(f"⚠️ Erreur sur {P} : {e} (calcul naïf de secours)")
            k = 1
            while mult_point(P, k) != Infini(CE):
                k += 1
            o = k

        distribution[o] += 1
        dico[(P.x, P.y)] = o
        l.append(o)
        
        if o > max_order:
            max_order = o
            max_point = P
            if verbose:
                print(f"➡️ Nouveau max : {max_order} pour {P}")

        if verbose and (i % 2000 == 0):
            print(f"Progression : {i}/{len(points)} points traités...")

    # Export CSV
    if export_csv:
        nom_csv = nom_fichier_ordre_CE(CE)
        with open(nom_csv, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Ordre max d'un point","ordre de la courbe"])
            writer.writerow([max_order,n])
        if verbose:
            print(f"📁 CSV créé : {nom_csv}")
            
    # Export CSV
    if export_csv:
        nom_csv = nom_fichier_ordre(CE)
        with open(nom_csv, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Ordre", "Frequence"])
            for ordre, freq in sorted(distribution.items(),reverse=True):
                writer.writerow([ordre, freq])
        if verbose:
            print(f"📁 CSV créé : {nom_csv}")


    # Export CSV with x, y, ordre
    if export_csv:
        nom_csv = nom_fichier_points(CE)
        with open(nom_csv, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y", "Ordre"])
            for P in points:
                writer.writerow([P.x, P.y, dico[(P.x, P.y)]])
        if verbose:
            print(f"📁 CSV créé : {nom_csv}")
            
    if export_csv:
        nom_csv = nom_fichier_points_ordre_max(CE)
        with open(nom_csv,"w",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x","y"])
            for x,y in dico:
                if dico[x,y] == max_order:
                    writer.writerow([x, y])
        if verbose:
            print(f"📁 CSV créé : {nom_csv}")

    if verbose:
        print("\n📊 Résumé :")
        # print(f"  - Ordre estimé du groupe : {n}")
        print(f"  - Ordre max trouvé       : {max_order}")
        print(f"  - Point correspondant    : {max_point}")

'''

def courbe_cyclique(CE,n=None):
    if n == None:
        print("Calcul du nombre de points par fichier executable")
        try:
            n = CE.nombre_points_subprocess() # appelle l'executable c
        except Exception as e:
            print(f"erreur bon bah finalement on calcule en python mskn : {e}")
            n = CE.nombre_points() # appelle les fonctions python tant pis
        print(f"Ordre estimé du groupe : {n}")        
    return sp.isprime(n)

def trouve_points(CE,verbose=True,n=None,nb_points=30000,cyclique=True):
    if n == None:
        print("Calcul du nombre de points par fichier executable")
        try:
            n = CE.nombre_points_subprocess() # appelle l'executable c
        except Exception as e:
            print(f"erreur bon bah finalement on calcule en python mskn : {e}")
            n = CE.nombre_points() # appelle les fonctions python tant pis
    print("tout va bien ici")
    points = find_points_fast(CE,nb_points)
    if verbose: 
        print("points trouvés")

    nom_csv = nom_fichier_points(CE)
    with open(nom_csv, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        for P in points:
            writer.writerow([P.x, P.y])
    if verbose:
        print(f"📁 CSV créé : {nom_csv}")
    
    nom_csv = nom_CEcsv()
    with open(nom_csv, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([CE.b,CE.c,CE.o,n,cyclique])
    if verbose:
        print(f"📁 CSV créé : {nom_csv}")
    return True

def file_points_to_list(CE,nom_fichier):
    points = []
    with open(nom_fichier, "r", newline='') as fichier:
        reader = csv.DictReader(fichier)  # On lit avec les noms de colonnes
        for row in reader:
            x = int(row['x'])  # convertir en entier
            y = int(row['y'])
            points.append(Point(x,y,CE))
    return points

def ordre(CE):
    with open(nom_CEcsv(), "r", newline='') as fichier:
        reader = csv.DictReader(fichier)  # On lit avec les noms de colonnes
        for line in reader:
            if (CE.b,CE.c,CE.o) == ((int(line["a"]),int(line["b"]),int(line["p"]))):
                return int(line["ordre"])
        return None
    
def liste_points(CE):
    nom_fichier = nom_fichier_points(CE)
    l = file_points_to_list(CE,nom_fichier)
    return l

def cyclique(CE):
    with open(nom_CEcsv(), "r", newline='') as fichier:
        reader = csv.DictReader(fichier)  # On lit avec les noms de colonnes
        for line in reader:
            if (CE.b,CE.c,CE.o) == ((int(line["a"]),int(line["b"]),int(line["p"]))):
                return int(line["cyclique"])
        return None
'''
def liste_points_ordre_max(CE):
    nom_fichier = nom_fichier_points_ordre_max(CE)
    l = file_points_to_list(CE,nom_fichier)
    return l'''

def point_random(CE):
    l = liste_points(CE)
    i = randint(0,len(l)-1)
    return l[i]

'''
def point_ordre_max_random(CE):
    l = liste_points_ordre_max(CE)
    i = randint(0,len(l)-1)
    return l[i]

def ordre(CE):
    nom_fichier = nom_fichier_ordre_CE(CE)
    with open(nom_fichier, "r", newline='') as fichier:
        reader = csv.DictReader(fichier)  # On lit avec les noms de colonnes
        for row in reader:
            ordre_max = int(row["Ordre max d'un point"])  # convertir en entier
            ordre_courbe = int(row['ordre de la courbe'])
    return ordre_max,ordre_courbe

def ordre_CE():
    a,b = ordre(CE)
    return b

def ordre_max(CE):
    a,b = ordre(CE)
    return a
'''

