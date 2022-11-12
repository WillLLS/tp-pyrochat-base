from cryptography.fernet import Fernet
from ciphered_gui import *
from base64 import b64encode, b64decode

from hashlib import sha256

class fernetGui(CipheredGUI):

    def __init__(self) -> None:
        super().__init__()
        self.f = None

    def run_chat(self, sender, app_data) -> None:
        super().run_chat(sender, app_data)

        passwd = dpg.get_value("connection_password")

        m = sha256()
        m.update(bytes(passwd, "utf8"))
        key = m.digest()
        self._key = b64encode(key)
        self.f = Fernet(self._key)
    
    def encrypt(self, plaintext):
        cipher = self.f.encrypt(bytes(plaintext, "utf8"))
        print("Cipher : ", cipher)
        return (cipher)

    def decrypt(self, data):
        print("Data :", data)
        encrypted_data = b64decode(data)
        plaintext = self.f.decrypt(encrypted_data)
        return str(plaintext, "utf8")

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