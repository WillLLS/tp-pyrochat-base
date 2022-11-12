# Prise en main

## 1. 
    Topology : Client / Server - Star topology
## 2. 
    Chaque log se localise sur le serveur et s'affiche dans le terminal.
## 3.
    Les log sont en clair.
    Le Debug est activé.
    Ne respect pas la règle de confidentialité.
## 4.
    L'utilisation d'un algorithme de chiffrement symétrique.
    Chaque utilisateur possède 1 clef.

# Chiffrement

## 1.
    Non, car cette fonction est pseudo-aléatoire, donc prédictible.

## 2.
    Le vecteur d'initialisation est envoyé en clair.

## 3.
    Le serveur malveillant peut envoyé de faux messages et surcharger le serveur.

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
    Il s'agit d'une attaque par dénis de service.

## 3.
    L'utilisation d'une durée de vie au message permet de contrer cela. (TTL)

# TTL

## 1.
    A première vu, il ne semble pas y avoir de changement

## 2. 
    En ajoutant 45 secondes au delay de réception, nous pouvons soulever une erreur InvalidToken.
    (Cf. la fonction _decrypt_data de la librairy Fernet)

## 3.
    Oui (on peut également réduire le TTL pour augmenter l'efficacité)

## 4.
    Certaines requête plus complexe (mais correct) peuvent se retrouver ignorées à cause du TTL, 
    si le temps d'analyse de cette dernière est trop élevé.

