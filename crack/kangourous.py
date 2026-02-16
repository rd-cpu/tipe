from module.courbe_el_final import *
from module.el_gamal import *
from random import randint
from module.trouve_points_ordres import *
import numpy as np


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
        


'''
#----------------Test--------------------
CEstand = CourbeElliptique(2,0,2,49993)
P=Point(28,31632,CEstand)
s = 35804
pk = generate_PK(s,P,CEstand)
CE, P, B = pk
r = kangourous(P,B,30000,40000,CEstand.o)
print("s = ",s ,"r = ",r)
print(s%CEstand.o==r)
'''

'''
#----------------Test--------------------
CEstand = CourbeElliptique(2,0,2,6482753)
s = randint(0,CEstand.o - 1)
P=point_random(CEstand)
pk = generate_PK(s,P,CEstand)
CE, P, B = pk
r = kangourous(P,B,max(0,s-100000),s+100000,CEstand.o)
print("s = ",s ,"r = ",r)
print(s%CEstand.o==r)
'''


#def kangourous_meute(alpha: Point ,beta: Point):