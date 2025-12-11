from concurrent.futures import ProcessPoolExecutor
import time
import numpy as np
import csv

# IMPORTS DU MODULE (garder dans le main script)
from module.algo_crack.crackEGEC import *
from module.algo_crack.rho_de_pollard import *


# --- Worker: doit contenir uniquement DES ARGUMENTS PICKLABLES ---

def worker_temps_crack(args):
    pk_data, CE_params, algo_name = args

    # --- RECONSTRUCTION DES OBJETS DANS LE WORKER ---
    CE = CourbeElliptique(*CE_params)

    # reconstruction de pk (pk_data = (px,py,bx,by))
    px, py, bx, by = pk_data
    P = Point(px, py, CE)
    B = Point(bx, by, CE)
    pk = (CE, P, B)

    # reconstruction de l'algorithme
    if algo_name == "rho":
        algo = crack_rho_de_pollard
    elif algo_name == "force":
        algo = crack_force_brute
    else:
        raise ValueError("algorithme inconnu")

    # --- timer ---
    start = time.perf_counter()
    _ = algo(pk)
    end = time.perf_counter()

    return end - start


# --- VERSION PARALLÈLE ---

def duree_crack_monte_carlo(CE, algo_crack, N=20, progress_callback=None, workers=None):

    # identifie l'algo
    algo_name = "rho" if algo_crack == crack_rho_de_pollard else "force"

    o = ordre(CE)
    tab_sk = np.random.randint(1, o, size=N)

    # génère P
    tab_P = [point_random(CE) for _ in range(N)]
    tab_pk = []
    for i in range(len(tab_sk)):
        pk = generate_PK(tab_sk[i], tab_P[i], CE)
        # store coordinates of P and B so they are picklable
        P_point = pk[1]
        B_point = pk[2]
        tab_pk.append((P_point.x, P_point.y, B_point.x, B_point.y))
        
    # paramètre de la courbe, picklable !
    CE_params = (CE.a, CE.b, CE.c, CE.o)

    # prépare les arguments pour chaque worker
    args = [
        (pk_tuple, CE_params, algo_name)
        for pk_tuple in tab_pk
    ]

    if progress_callback:
        progress_callback(f"Génération des données : OK\n")

    # ---- PARALLÉLISATION ----
    tab_temps = []
    # permet au caller de contrôler le nombre de processus workers (None = défaut)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for i, elapsed_time in enumerate(pool.map(worker_temps_crack, args), 1):
            tab_temps.append(elapsed_time)
            if progress_callback:
                progress_callback(f"Cracked: {i}/{N} ({elapsed_time:.4f}s)\n")

    if progress_callback:
        progress_callback("Calcul parallèle terminé\n")

    temps_moyen = float(np.mean(tab_temps))
    u_temps = float(np.std(tab_temps, ddof=1))

    return temps_moyen, u_temps


def crack_perfCE_csv(CE, algo, N=1000, progress_callback=None, workers=None):
    temps_moyen, u_temps = duree_crack_monte_carlo(CE, algo, N, progress_callback=progress_callback, workers=workers)

    with open(nom_perfcsv(algo), "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([repr(CE), str(CE.o), str(N), str(temps_moyen), str(u_temps)])
    
    return temps_moyen, u_temps


if __name__ == "__main__":
    # nécessaire sous Windows
    import multiprocessing
    multiprocessing.freeze_support()

    CE1 = CourbeElliptique(0, 2, 2, 40423)

    crack_perfCE_csv(CE1, crack_rho_de_pollard, 10)
