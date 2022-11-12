from fernet_gui import *
import time

from cryptography.fernet import InvalidToken

class TimeFernetGUI(fernetGui):

    def __init__(self) -> None:
        super().__init__()

    """
    Fonction de chiffrement :
        Chiffrement basé sur l'objet Fernet avec l'utilisation d'un TTL attribué au message.
    """
    def encrypt(self, plaintext):
        current_time = int(time.time())
        cipher = self._fernet.encrypt_at_time(bytes(plaintext, "utf8"), current_time)
        return (cipher)
    
    """
    Fonction de déchiffrement :
        Après récéption des données, cette fonction décrypt le message.
        L'objet Fernet va vérifier le TTL.
    """
    def decrypt(self, data):
        encrypted_data = b64decode(data)    # Déchiffrement base64 du message
        current_time = int(time.time())     # Récupération du temps actuel pour le TTL
        try:
            plaintext = self._fernet.decrypt_at_time(
                        encrypted_data,
                        30,
                        current_time)       # Déchiffrement avec vérification TTL
            return str(plaintext, "utf8")
        except InvalidToken:
            self._log.warning(InvalidToken.__name__)

if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG)

    client = TimeFernetGUI()
    client.create()
    client.loop()