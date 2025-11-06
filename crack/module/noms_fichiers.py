from module.courbe_el_final import CourbeElliptique

def extension(CE):
    return str(CE.a) + '_' + str(CE.b) + '_' + str(CE.c) + '_' + str(CE.o) 

def nom_fichier_ordre(CE):
    return "ordreptsCEs/ordrepts_" + extension(CE) + ".csv"

def nom_fichier_ordre_CE(CE):
    return "ordreCEs/ordre_" + extension(CE) + ".csv"

def nom_fichier_points(CE):
    return "pointsCEs/points_" + extension(CE) + ".csv"

def nom_fichier_points_ordre_max(CE):
    return "points_ordre_max/pt_om_" + extension(CE) + ".csv"

def nom_CEcsv(): return "CE.csv"