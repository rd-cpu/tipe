from module.crackEGEC import *
import csv
import time
import numpy as np


CEstand = CourbeElliptique(2,0,2,6482753)

def duree_crack(CE,N=10000):
    o = ordre_max(CE)
    tab_sk = np.random.randint(1,o, size=N)
    tab_P = np.array([point_random(CE) for i in range(N)])
    tab_pk = generate_PK(tab_sk,tab_P,CE)
    tab_temps = np.array([0]*N)
    print("tab_sk :", tab_sk)
    print("tab_pk :", tab_pk)
    tab_temps = np.array([0]*N)
    for i in range(N):
        start = time.perf_counter()
        sk_cracké = crack_force_brute(tab_pk[i])
        end = time.perf_counter()
        tab_temps[i] = end - start # en s
        print(i)
    temps_moyen = np.mean(tab_temps)
    u_temps = np.std(tab_temps,ddof=1)
    print("le temps nécessaire pour cracker la CE est", temps_moyen,"s +-",u_temps)
