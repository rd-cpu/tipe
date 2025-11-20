from module.crackEGEC import *
from module.algo_crack.rho_de_pollard import *
import csv
import time
import numpy as np



CE1 = CourbeElliptique(0,2,2,40423)
def duree_crack_monte_carlo(CE,algo_crack,N=1000):
    o = ordre(CE)
    tab_sk = np.random.randint(1,o, size=N)
    tab_P = np.array([point_random(CE) for i in range(N)])
    tab_pk = generate_PK(tab_sk,tab_P,CE)
    tab_temps = np.array([0.]*N)
    for i in range(N):
        start = time.perf_counter()
        sk_cracké = algo_crack(tab_pk[i])
        end = time.perf_counter()
        tab_temps[i] = end - start # en s
    temps_moyen = np.mean(tab_temps)
    u_temps = np.std(tab_temps,ddof=1)
    print("le temps nécessaire pour cracker la CE est", temps_moyen,"s +-",u_temps)
    return tab_sk,tab_P,tab_temps,temps_moyen,u_temps

def crack_perfCE_csv(CE,algo,N=1000): # prendre en compte l'ordre
    tab_sk,tab_P,tab_temps,temps_moyen,u_temps = duree_crack_monte_carlo(CE,algo,N)
    with open(nom_perfcsv(algo), "a", newline='') as f: # 'w' si pas écrit
        writer = csv.writer(f)
        # writer.writerow(["Courbe Elliptique", "Échantillon","Temps Moyen","Incertitude"])
        writer.writerow([repr(CE),str(N),str(temps_moyen),str(u_temps)])

# faire crack_perf_ZnZ

CEstand = CE1

s = randint(0,CEstand.o - 1)
print("clé secrète :",s)
P = point_random(CEstand)
pk = generate_PK(s,P,CEstand)
Q = point_random(CEstand)
M = cryptage(pk,Q)
Md = crack_point_rho_de_pollard(M,pk)
