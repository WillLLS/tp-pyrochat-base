from basic_gui import *

# Derivation de la clef
import os
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Cipher block (chiffrage)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import serpent

# Default value : Ne pas laisser dans ce fichier
DEFAULT_VALUES["password"] = "password"
salt = b"Hello World"

# Configuration du kdf
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=16,
    salt=salt,
    iterations=390000,
)

class CipheredGUI(BasicGUI):

    """
    Fonction d'initialisation : 
        Nous ajoutons un membre _key
    """
    def __init__(self) -> None:
        super().__init__()
        self._key = None

    """
    Fonction de création de fenêtre :
        Ajout d'un champ pour le mot de passe
    """
    def _create_connection_window(self) -> None:
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):
            
            for field in [("host", False), ("port", False), ("name", False), ("password", True)]:
                with dpg.group(horizontal=True):
                    dpg.add_text(field[0])
                    dpg.add_input_text(default_value=DEFAULT_VALUES[field[0]], tag=f"connection_{field[0]}", password=field[1])

            dpg.add_button(label="Connect", callback=self.run_chat)

    """
    Fonction démarrage du chat :
        Récupération du mot de passe renseigné par l'utilisateur
        Création d'un clé de dérivation basé 
    """
    def run_chat(self, sender, app_data) -> None:
        super().run_chat(sender, app_data)
        passwd = dpg.get_value("connection_password")   # Récupération du mot de passe renseigné par l'utilisateur

        self._key = kdf.derive(bytes(passwd, "utf8"))   # dérivation du mot de passe pour la création de la clef de chiffrement
    
    """
    Fonction de chiffrement :
        Chiffrement basé l'algorithme AES afin de chiffré le message du client avant l'envoie.
    """
    def encrypt(self, plaintext):

        iv  = os.urandom(16)                                        # Vecteur d'initialisation pseudo-aléatoire
        cipher = Cipher(algorithms.AES(self._key), modes.CTR(iv))   # Initialisation du cipher
        encryptor = cipher.encryptor()                              # Initialisation de l'objet de chiffrement
        

        padder = padding.PKCS7(128).padder()                        # Ajout d'un padding pour obtenir la taille souhaitée.
        padded_text = padder.update(bytes(plaintext, "utf8")) + padder.finalize()

        ct = encryptor.update(padded_text) + encryptor.finalize()   # Cipher final à envoyer


        return (iv, ct)

    """
    Fonction de déchiffrement :
        Après récéption des données, cette fonction décrypt le message.
    """
    def decrypt(self, data):

        iv = data[0]                                                # Récupération du vecteur d'initialisation (en clair)
        encrypted = data[1]                                         # Récupération du message chiffré

        cipher = Cipher(algorithms.AES(self._key), modes.CTR(iv))   # Initialisation du cipher
        decryptor = cipher.decryptor()                              # Initialisation de l'objet de déchiffrement

        padded_text = decryptor.update(encrypted) + decryptor.finalize() 

        unpadder = padding.PKCS7(128).unpadder()                    # Création de l'objet unpadder

        plaintext = unpadder.update(padded_text) + unpadder.finalize()

        return str(plaintext, "utf8")
    
    """
    Fonction d'envoie du message :
        Ajout de l'étape de chiffrement
    """
    def send(self, text) -> None:
        encrypted_msg = self.encrypt(text)
        super().send(encrypted_msg)


    """
    Fonction de réception du message :
        Déchiffrement du message
    """
    def recv(self) -> None:
        if self._callback is not None:
            for user, message in self._callback.get():

                iv = serpent.tobytes(message[0])        # Récupération du vecteur d'initialisation
                encrypted = serpent.tobytes(message[1]) # Récupération du message encrypté
                
                data = (iv, encrypted)

                self.update_text_screen(f"{user} : {self.decrypt(data)}")
            self._callback.clear()


if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG)

    client = CipheredGUI()
    client.create()
    client.loop()