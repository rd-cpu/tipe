from module.crackEGEC import *
import csv
import time
import numpy as np


CEstand = CourbeElliptique(2,0,2,49993)

def duree_crack(CE,N):
    tab_sk = np.random.uniform(0,CE.o-1,N)
    tab_P = np.array([point_random(CE) for i in range(N)])
    tab_pk = generate_PK(tab_sk,P,)
    tab_temps_crack = numpy.array([0]*N)
    
