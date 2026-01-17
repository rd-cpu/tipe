# Cryptographie sur les courbes elliptiques

# Messagerie 

## Utilisation rapide : 
Executer le fichier "messagerie\interface.py"

## Mise en place "à la main" :

Etape facultative car des dictionnaires sont déjà présents pour certaines courbes dans les dossier en question.

* Calcul d'un nombre suffisants de points d'une courbe elliptique (ne fonctionne plus)
* Création des dictionnaire dans le sens direct et réciproque 

```
creation_dicos(CE)
```

## Utilisation "à la main" :

Initialiser une courbe elliptique de la forme y² = x³ + ax² + bx + c mod o :
```
CE = CourbeElliptique( a, b, c, o)  
```
 Récupérer une liste de points d'une courbe :
```
l = find_points(CE)
```    
Initialiser un points d'une courbe elliptique : 
```
P = Point(x,y,CE)
```
Créer un clé publique :
```
cle_publique = generate_PK(cle_secrete, P, CE)
```    
Encrypter un point : 
```
P_crypté = cryptage(cle_publique,P)
```
Décrypter un point : 
```
P_décrypté = decryptage(P_crypté,cle_secrete)
```
Crypté un message sous forme de str : 
```
message_crypté = envoyeur(message,cle_publique,CE,sauvarder=True)
```    
Décrypté un message qui était un str : 
```
message_decrypté = receveur(CE,cle_secrete, message_crypte=None)
```    


# Attaque du système d'encryption 

## Attaque d'un message :

Algorithme de force brute 
``` 
P_décrypté = crack_point_force_brute(P_crypté,cle_publique)
``` 
Algorithme rho de Pollard  
``` 
P_décrypté = crack_point_rho_de_pollard(P_crypté,cle_publique)
``` 
## Etude comparative des algorithmes :

### Mise en place de nouvelles courbes :

Calcul des points d'une nouvelle courbe elliptique ( o doit être premier)
~~~
creationCE(b,c,o,ordre=None,nb_points=30000,cyclique=True, a = 0)
~~~

Calcul des point d'une courbe elliptique d'ordre premier dans les bornes données
~~~
trouve_CE_viable(a,b,min,max,nb_points=30000,cyclique=True)
~~~ 
### Utilisation rapide :

Lancer "crack\gui_cracker.py" dans un terminal 

### Utilisation "à la main" : 

Mise en place de calculs de plusieurs attaques sur plusieurs thread. 

Les calculs ne sont pas réellement parallélisés mais une attaque différente tourne sur chaque thread aloué.
``` 
temps_moyen, u_temps = duree_crack_monte_carlo(CE, algo, N, progress_callback=None, workers=None):
``` 

Même calcul mais on enregistre les résultats sous forme dans un fichier csv au nom de la courbe et de l'algo utilisé et on update le graphique qui résume les calculs fait précédement.
~~~
temps_moyen, u_temps = crack_perfCE_csv(CE, algo, N, progress_callback=None, workers=None, update_plot=True)
~~~

### Analyse des données 

Mise à jour du graphique résumant les calculs 
~~~
chemin_graph = generate_perf_graph(show=False, output_path=None, verbose=True):
~~~

Calcul de la loi d'évolutio du temps de calcul de la forme y = a * x^b 
~~~
fit_log_power_law(x, y) 
~~~

Prédiction du temps de calcul
~~~
predict_time_for_order(order, method='brute', script_dir=script_dir)
~~~