from module.crackEGEC import *
import csv
import time
import numpy as np


CEstand = CourbeElliptique(2,0,2,49993)

def duree_crack(CE,N=10000):
    tab_sk = np.random.randint(0, CE.o-1, size=N)
    tab_P = np.array([point_random(CE) for i in range(N)])
    tab_pk = generate_PK(tab_sk,tab_P,CE)
    tab_temps_crack = np.array([0]*N)
    print("tab_sk :", tab_sk)
    print('tab_pk :', tab_pk)
    