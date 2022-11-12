from cryptography.fernet import Fernet
from ciphered_gui import *
from base64 import b64encode, b64decode

from hashlib import sha256

class fernetGui(CipheredGUI):

    """
    Fonction d'initialisation : 
        Nous ajoutons un membre _fernet
    """
    def __init__(self) -> None:
        super().__init__()
        self._fernet = None

    """
    Fonction démarrage du chat :
        Récupération du mot de passe renseigné par l'utilisateur
        Création d'un clef
    """
    def run_chat(self, sender, app_data) -> None:
        super().run_chat(sender, app_data)

        passwd = dpg.get_value("connection_password")   # Récupréation du mot de passe

        m = sha256()                                    # Initialisation objet sha256
        m.update(bytes(passwd, "utf8"))                 # Update de l'objet sha256 avec le mot de passe
        key = m.digest()                                # Chiffrement SHA256 du mot de passe dans la variable key
        self._key = b64encode(key)                      # Chiffrement en base64
        self._fernet = Fernet(self._key)                # Initialisation de l'objet Fernet
    
    """
    Fonction de chiffrement :
        Chiffrement basé sur l'objet Fernet
    """
    def encrypt(self, plaintext):
        cipher = self._fernet.encrypt(bytes(plaintext, "utf8"))
        return (cipher)

    """
    Fonction de déchiffrement :
        Après récéption des données, cette fonction décrypt le message.
    """
    def decrypt(self, data):
        encrypted_data = b64decode(data)                 # Déchiffrement en base64
        plaintext = self._fernet.decrypt(encrypted_data) # Déchiffrement du message
        return str(plaintext, "utf8")

    """
    Fonction de réception du message :
        Déchiffrement du message grâce à la fonction decrypt
    """
    def recv(self) -> None:
        if self._callback is not None:
            for user, message in self._callback.get():

                msg = bytes(message['data'], "utf8")
                
                self.update_text_screen(f"{user} : {self.decrypt(msg)}")
            self._callback.clear()
        
if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG)

    client = fernetGui()
    client.create()
    client.loop()