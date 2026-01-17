Messagerie : 
    Initialiser une courbe elliptique de la forme y² = x³ + ax² + bx + c mod o :
        CEstand = CourbeElliptique( a, b, c, o)  
        
    Récupérer une liste de points d'une courbe :
        l = find_points(CEstand)
    
    Initialiser un points d'une courbe elliptique : 
        P=Point(x,y,CEstand)

    Créer un clé publique :
        cle_publique = generate_PK(cle_secrete, P, CEstand)
    
    Encrypter un point : 
        P_crypté = cryptage(cle_publique,P)

    Décrypter un point : 
        P_décrypté = decryptage(P_crypté,cle_secrete)
    
    Crypté un message sous forme de str : 
        message_crypté = envoyeur(message,cle_publique,CE,sauvarder=True)
    
    Décrypté un message qui était un str : 
        message_decrypté = receveur(CE,cle_secrete, message_crypte=None)

