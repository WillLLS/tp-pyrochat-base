from basic_gui import *

# Derivation de la clef
import os
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Cipher block (chiffrage)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import serpent

DEFAULT_VALUES["password"] = "password"


salt = b"Hello World"
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=16,
    salt=salt,
    iterations=390000,
)

class CipheredGUI(BasicGUI):

    def __init__(self) -> None:
        super().__init__()
        self._key = None

    def _create_connection_window(self) -> None:
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):
            
            for field in [("host", False), ("port", False), ("name", False), ("password", True)]:
                with dpg.group(horizontal=True):
                    dpg.add_text(field[0])
                    dpg.add_input_text(default_value=DEFAULT_VALUES[field[0]], tag=f"connection_{field[0]}", password=field[1])

            dpg.add_button(label="Connect", callback=self.run_chat)



    def run_chat(self, sender, app_data) -> None:
        super().run_chat(sender, app_data)
        passwd = dpg.get_value("connection_password")

        # https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#pbkdf2
        self._key = kdf.derive(bytes(passwd, "utf8"))
    
    def encrypt(self, plaintext):
        iv  = os.urandom(16)
        cipher = Cipher(algorithms.AES(self._key), modes.CTR(iv)) 
        encryptor = cipher.encryptor()
        

        padder = padding.PKCS7(128).padder()
        padded_text = padder.update(bytes(plaintext, "utf8")) + padder.finalize()

        ct = encryptor.update(padded_text) + encryptor.finalize()

        print("Encryptor : ", plaintext, self._key, iv, ct)

        return (iv, ct)

    def decrypt(self, data):
        iv = data[0]
        encrypted = data[1]

        cipher = Cipher(algorithms.AES(self._key), modes.CTR(iv))
        decryptor = cipher.decryptor()

        
        padded_text = decryptor.update(encrypted) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()

        print("Decryptor : ", padded_text, self._key, iv)

        plaintext = unpadder.update(padded_text) + unpadder.finalize()


        

        return str(plaintext, "utf8")
    
    def send(self, text) -> None:
        super().send(self.encrypt(text))



    def recv(self) -> None:
        if self._callback is not None:
            for user, message in self._callback.get():

                iv = serpent.tobytes(message[0])
                encrypted = serpent.tobytes(message[1])
                
                data = (iv, encrypted)


                self.update_text_screen(f"{user} : {self.decrypt(data)}")
            self._callback.clear()




if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG)

    client = CipheredGUI()
    client.create()
    client.loop()