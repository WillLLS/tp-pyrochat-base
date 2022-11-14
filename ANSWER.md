# Prise en main

## 1. 
    Il s'agit d'une topologie Client / Server en étoile. Dans cette topologie, tout les clients sont reliés au serveur (la communication entre 2 clients transite donc par le serveur).
    
## 2. 
    Chaque log se localise sur le serveur et s'affiche dans le terminal.
    
## 3.
    Les log sont en clair.
    Le Debug est activé.
    Cela ne respect donc pas la principe de confidentialité.
    
## 4.
    L'utilisation d'un algorithme de chiffrement symétrique (tel que l'AES).
    Ces algorithmes de chiffrement se basent sur une même clé pour chiffrer et déchiffrer un message. 
    Ainsi, pour communiquer, 2 utilisateurs devront donc se partager une clé de manière confidentielle(clé privé).

# Chiffrement

## 1.
    Non, car cette fonction est pseudo-aléatoire. Une fonction pseudo-aléatoire suit une séquence définit et peut donc être prédictible. 

## 2.
    En cryptographie, il est nécessaire de connaitre parfaitement son code pour pouvoir détecter et 
    combler l'ensemble des vulnérabilités. En utilisant ces primitives nous ne sommes pas sur à 100 % de tout ce que nous implémentons.
    
## 3.
    Un serveur malveillant peut envoyé de faux messages et surcharger le serveur. 

## 4.
    Il manque une étape d'authentification en utilisant le HMAC.

# Authenticated Symetric Encryption

## 1.
    L'ensemble de l'algorithme est implémenter dans la class Fernet.
    Les vecteurs d'initialisation et le chiffrement des messages sont gérés automatiquement.
        Le vecteur d'initialisation est ici encodé.
        ( Voir fernet.py >> _encrypt_from_parts() )

    L'implémentation d'un HMAC.

    L'implémentation d'une méthode TTL.

## 2. 
    Il s'agit d'une attaque par dénis de service (DoS).

## 3.
    L'utilisation d'une durée de vie au message permet de contrer cela. (TTL)

# TTL

## 1.
    A première vu, il ne semble pas y avoir de changement

## 2. 
    En ajoutant 45 secondes au delay de réception, nous pouvons soulever une erreur InvalidToken.
    (Cf. la fonction _decrypt_data de la librairy Fernet)

## 3.
    Oui (on peut également réduire le TTL pour augmenter l'efficacité).
    Diminuer la valeur du TTL permet de désengorger plus rapidement le serveur et donc d'éléminer plus rapidement les requêtes parasites.

## 4.
    Certaines requête plus complexe (mais correct) peuvent se retrouver ignorées à cause du TTL, 
    si le temps d'analyse de cette dernière est trop élevé.
    
# Regard critique 

    Lors de la réalisation des différents codes, nous avons pu relever certaines vulnérabilités :
   
    - La taille des messages reçu constitue une autre vulnérabilité. La librairie Fernet est idéale pour chiffrer des données qui tiennent facilement 
    en mémoire mais est inadaptée pour les messages trop volumineux. En effet, Fernet ne permet pas de chiffrer les messages trop volumineux et d'afficher 
    les données non authentifiées. Une personne souhaitant envoyer un message de taille trop importante risque donc de voir son message tronquer à la reception. 
   
    - De plus, la librairie Fernet génère un IV en utilisant la fonction urandom du module os. Comme évoqué dans les questions précédentes, 
    cette fonction est pseudo-aléatoire et peut donc générer un IV prédictible. Pour combler cette faille, il faudrait générer des IV purement 
    aléatoure en utilisant le bruit.

    -Bien que les messages envoyés ne soient plus visibles depuis le serveur, le nom des destinataires des messages sont restés en clair. 
    Il est donc possible de voir qui envoi le message et à qui le message est destiné.
    

    
    
