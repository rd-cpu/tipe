from module.courbe_el_final import *
from module.trouve_points_ordres import *
import matplotlib.pyplot as plt
import numpy as np


CE = CourbeElliptique(0,-2,2,47189)
CE2 = CourbeElliptique(0,-2,-1,47189)

def plot_ce_mod(CE,n=10000,save = True):
    point = find_points_fast(CE,n)
    print("Points trouvés :", len(point))
    x_vals = [p.x for p in point]
    y_vals = [p.y for p in point]
    plt.figure(figsize=(8, 6))
    plt.scatter(x_vals, y_vals, s=1, color='blue')
    plt.title(CE)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.axis('equal')
    if save:
        plt.savefig(f"plots_ce/{CE}mod.png")

    plt.show()

def plot_ce(CE, n=10000,min_x=-2,max_x=2,save = True):
    tab_x = np.linspace(min_x, max_x, n)
    y_squared = np.array([CE.f(x) for x in tab_x])

    valid_indices = y_squared >= 0
    tab_x_valid = tab_x[valid_indices]
    y_squared_valid = y_squared[valid_indices]

    tab_y_pos = np.sqrt(y_squared_valid)
    tab_y_neg = -np.sqrt(y_squared_valid)

    plt.figure(figsize=(8, 6))

    plt.scatter(tab_x_valid, tab_y_pos, s=1, color='blue')
    plt.scatter(tab_x_valid, tab_y_neg, s=1, color='blue')

    #plt.title(CE)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.axhline(0, color='k', linewidth=0.5)
    plt.axvline(0, color='k', linewidth=0.5)
    plt.axis('equal')
    if save:
        plt.savefig(f"plots_ce/{CE}.png")
    plt.show()
   