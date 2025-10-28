from module.courbe_el_final import CourbeElliptique, Point, Infini
from collections import Counter
import csv
import math
from messagerie_final import *
from creer_dico import *
from random import randint


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

def find_points_fast(CE):
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
    n = 30000
    x_dejavus = []
    m = min(n,CE.o)
    while i < n:
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


# ============================================================
# --- Étude complète (avec export CSV + DICO) ---
# ============================================================

def etude_ordre_rapide_et_export(CE, export_csv=True, export_dico=True, verbose=True):
    points = find_points_fast(CE)
    if verbose:
        print(f"✅ {len(points)} points trouvés sur la courbe (hors point à l'infini)")
    n = len(points) + 1
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
        nom_csv = nom_fichier_ordre(CE)
        with open(nom_csv, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Ordre", "Frequence"])
            for ordre, freq in sorted(distribution.items()):
                writer.writerow([ordre, freq])
        if verbose:
            print(f"📁 CSV créé : {nom_csv}")

    # Export CSV with x, y, ordre
    if export_csv:
        nom_csv = nom_fichier_liste_ordre(CE)
        with open(nom_csv, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y", "Ordre"])
            for P in points:
                writer.writerow([P.x, P.y, dico[(P.x, P.y)]])
        if verbose:
            print(f"📁 CSV créé : {nom_csv}")
            
    # Export DICO
    if export_dico:
        nom_dico = nom_fichier_dico_ordre(CE)
        sauvegarder_dictionnaire(dico, nom_dico)

    if verbose:
        print("\n📊 Résumé :")
        print(f"  - Ordre estimé du groupe : {n}")
        print(f"  - Ordre max trouvé       : {max_order}")
        print(f"  - Point correspondant    : {max_point}")


