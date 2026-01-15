import random
from sympy import isprime, primerange
from math import log, exp

def index_calculus(g, h, p, factor_base_size=None):
    """
    Résout g^x ≡ h (mod p) en utilisant l'algorithme Index Calculus.
    
    Args:
        g: générateur
        h: cible
        p: module premier
        factor_base_size: taille de la base de factorisation (None = auto)
    
    Returns:
        x tel que g^x ≡ h (mod p), ou None si échec
    """
    
    # Vérifications
    if not isprime(p):
        raise ValueError("p doit être premier")
    
    # Construction de la base de factorisation optimisée
    if factor_base_size is None:
        # Heuristique : L_p(1/2) où L_p(α) = exp((log p)^α * (log log p)^(1-α))
        factor_base_size = max(100, int(exp(0.5 * log(p)**0.5 * log(log(p))**0.5)))
    
    factor_base = list(primerange(2, factor_base_size))
    B = len(factor_base)
    
    print(f"Module p = {p}")
    print(f"Base de factorisation : {factor_base[:10]}... ({B} premiers jusqu'à {factor_base[-1]})")
    print(f"Smoothness bound : {factor_base[-1]}")
    
    # Phase 1 : Construction du système d'équations
    print("\nPhase 1 : Collecte des relations...")
    relations = []
    
    # Calcul de la probabilité théorique qu'un nombre soit B-smooth
    prob = 1.0 / log(p) ** (log(p) / log(factor_base[-1]))
    expected_trials = int((B + 20) / prob) if prob > 0 else B * 1000
    max_attempts = min(expected_trials * 5, 100000)
    
    print(f"Tentatives estimées : ~{expected_trials}")
    
    attempts = 0
    
    while len(relations) < B + 20:  # On en veut un peu plus que B pour la redondance
        if attempts >= max_attempts:
            print(f"\n⚠ Échec après {attempts} tentatives.")
            print(f"Seulement {len(relations)}/{B + 20} relations trouvées.")
            print(f"Conseil : Augmenter la taille de la base de factorisation.")
            return None
        
        attempts += 1
        k = random.randint(1, p - 2)
        gk = pow(g, k, p)
        
        # Essayer de factoriser g^k mod p avec la base de factorisation
        factors = try_factor_with_base(gk, factor_base)
        
        if factors is not None:
            relations.append((k, factors))
            if len(relations) % 5 == 0 or len(relations) <= 5:
                print(f"  Relations : {len(relations)}/{B + 20} (tentatives: {attempts})")
    
    print(f"\n✓ {len(relations)} relations collectées en {attempts} tentatives")
    
    # Phase 2 : Résolution du système linéaire (mod p-1)
    print("\nPhase 2 : Résolution du système...")
    logs = solve_system_mod(relations, factor_base, p - 1)
    
    if logs is None:
        print("⚠ Échec de la résolution du système")
        return None
    
    print(f"✓ Logarithmes de la base calculés")
    
    # Phase 3 : Calcul du logarithme de h
    print("\nPhase 3 : Calcul du logarithme de la cible...")
    max_attempts_h = min(expected_trials * 2, 5000000000)
    
    for attempt in range(max_attempts_h):
        s = random.randint(0, p - 2)
        hs = (h * pow(g, s, p)) % p
        
        factors_h = try_factor_with_base(hs, factor_base)
        
        if factors_h is not None:
            # h * g^s = produit(pi^ei) mod p
            # log_g(h) + s = somme(ei * log_g(pi)) mod (p-1)
            sum_logs = sum(factors_h[i] * logs[i] for i in range(len(factor_base)))
            x = (sum_logs - s) % (p - 1)
            
            # Vérification
            if pow(g, x, p) == h:
                print(f"✓ Logarithme trouvé après {attempt + 1} tentatives")
                return x
        
        if (attempt + 1) % 100000000 == 0:
            print(f"  Tentatives phase 3 : {attempt + 1}/{max_attempts_h}")
    
    print(f"⚠ Échec phase 3 : impossible de factoriser h*g^s après {max_attempts_h} tentatives")
    return None

def try_factor_with_base(n, factor_base):
    """
    Essaie de factoriser n en utilisant uniquement les premiers de factor_base.
    Retourne un vecteur d'exposants ou None si échec.
    """
    if n <= 1:
        return None
    
    original_n = n
    exponents = [0] * len(factor_base)
    
    for i, prime in enumerate(factor_base):
        while n % prime == 0:
            n //= prime
            exponents[i] += 1
        
        # Optimisation : arrêt précoce
        if n == 1:
            return exponents
    
    # n doit être égal à 1 pour être B-smooth
    if n == 1:
        return exponents
    return None

def solve_system_mod(relations, factor_base, modulus):
    """
    Résout le système linéaire pour trouver les logarithmes des éléments
    de la base de factorisation avec élimination gaussienne mod modulus.
    """
    B = len(factor_base)
    
    # Construction de la matrice augmentée
    matrix = []
    for k, factors in relations[:B + 10]:  # On prend plus d'équations que d'inconnues
        row = factors + [k]
        matrix.append(row)
    
    n_rows = len(matrix)
    
    # Élimination gaussienne mod (modulus)
    pivot_row = 0
    for col in range(B):
        # Trouver un pivot non nul
        found_pivot = False
        for row in range(pivot_row, n_rows):
            if matrix[row][col] % modulus != 0:
                # Échanger les lignes
                matrix[pivot_row], matrix[row] = matrix[row], matrix[pivot_row]
                found_pivot = True
                break
        
        if not found_pivot:
            continue
        
        # Normalisation et élimination
        pivot = matrix[pivot_row][col]
        try:
            pivot_inv = pow(pivot, -1, modulus)
        except:
            continue
        
        # Éliminer les autres lignes
        for row in range(n_rows):
            if row != pivot_row and matrix[row][col] != 0:
                factor = (matrix[row][col] * pivot_inv) % modulus
                for c in range(B + 1):
                    matrix[row][c] = (matrix[row][c] - factor * matrix[pivot_row][c]) % modulus
        
        pivot_row += 1
    
    # Extraction des solutions
    logs = [0] * B
    for i in range(min(pivot_row, B)):
        # Trouver la colonne pivot
        pivot_col = -1
        for c in range(B):
            if matrix[i][c] % modulus != 0:
                pivot_col = c
                break
        
        if pivot_col != -1:
            try:
                inv = pow(matrix[i][pivot_col], -1, modulus)
                logs[pivot_col] = (matrix[i][B] * inv) % modulus
            except:
                pass
    
    return logs

# Exemples d'utilisation
if __name__ == "__main__":
    print("="*60)
    print("Test 1 : Exemple avec un petit module")
    print("="*60)
    
    # Exemple avec des nombres petits (marche bien)
    p1 = 1019
    g1 = 2
    secret_x1 = 123
    h1 = pow(g1, secret_x1, p1)
    
    print(f"\nProblème : trouver x tel que {g1}^x ≡ {h1} (mod {p1})")
    print(f"(Solution attendue : x = {secret_x1})\n")
    
    result1 = index_calculus(g1, h1, p1, factor_base_size=50)
    
    if result1 is not None:
        print(f"\n✓ SUCCÈS : x = {result1}")
        print(f"Vérification : {g1}^{result1} mod {p1} = {pow(g1, result1, p1)}")
    else:
        print("\n✗ ÉCHEC")
    
    print("\n" + "="*60)
    print("Test 2 : Exemple avec un module moyen")
    print("="*60)
    
    # Exemple avec un module plus grand mais raisonnable
    p2 = 1000000363
    g2 = 5
    secret_x2 = 123456
    h2 = pow(g2, secret_x2, p2)
    
    print(f"\nProblème : trouver x tel que {g2}^x ≡ {h2} (mod {p2})")
    print(f"(Solution attendue : x = {secret_x2})\n")
    
    result2 = index_calculus(g2, h2, p2, factor_base_size=150)
    
    if result2 is not None:
        print(f"\n✓ SUCCÈS : x = {result2}")
        print(f"Vérification : {g2}^{result2} mod {p2} = {pow(g2, result2, p2)}")
    else:
        print("\n✗ ÉCHEC")
    
    print("\n" + "="*60)
    print("NOTE SUR LES GRANDS MODULES")
    print("="*60)
    print("""
Pour p = 1000000363 (grand module), Index Calculus nécessite :
- Une base de factorisation beaucoup plus grande (milliers de premiers)
- Des millions de tentatives pour trouver des relations
- Beaucoup de temps de calcul (plusieurs minutes à heures)

C'est normal : c'est précisément pourquoi le logarithme discret
est difficile et utilisé en cryptographie !

Pour tester avec de grands modules, utilisez des implémentations
optimisées (en C/C++) et des techniques avancées (crible, etc.)
    """)