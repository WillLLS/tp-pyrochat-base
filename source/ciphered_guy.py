import cryptography
import dearpygui.dearpygui as dpg
from basic_gui import BasicGUI
import logging
import serpent

import os
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo"
}

salt = b"hello world"
kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=16,
            salt=salt,
            iterations=390000,
        )

class CypheredGUI(BasicGUI):
    def __init__(self) -> None:
        self._key = None 
        super().__init__()

    def _create_connection_window(self)->None:
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):
            for field in ["host", "port", "name"]:
                with dpg.group(horizontal=True):
                    dpg.add_text(field)
                    dpg.add_input_text(default_value=DEFAULT_VALUES[field], tag=f"connection_{field}")
                
            with dpg.group(horizontal=True):
                dpg.add_text("password")
                dpg.add_input_text(tag="connection_password",password=True)

            dpg.add_button(label="Connect", callback=self.run_chat)

    def run_chat(self,sender,app_data)->None:
        super().run_chat(sender, app_data)
        self._key = kdf.derive(bytes(dpg.get_value('connection_password'),"utf8"))
        
    def encrypt(self, message):
        iv = os.urandom(16)
        message_bin = bytes(message,"utf8")
        cipher = Cipher(algorithms.AES(self._key), modes.CTR(iv))
        encryptor = cipher.encryptor()
        
        padder = padding.PKCS7(128).padder()
        padder_data = padder.update(message_bin) + padder.finalize()

        ct = encryptor.update(padder_data) + encryptor.finalize()

        print(f'encrypted text = {ct}')
        return (iv, ct)


    def decrypt(self, data):
        iv = data[0]
        ct = data[1]
        cipher = Cipher(algorithms.AES(self._key), modes.CTR(iv))
        decryptor = cipher.decryptor()


        padded_text = decryptor.update(ct) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()

        text = unpadder.update(padded_text) + unpadder.finalize()

        return str(text,"utf8")
    
    def send(self, text)->None:
        print(f'Text : {text}')
        encrypted = self.encrypt(text)
        print(f'encrypted {encrypted}')
        super().send(encrypted)

    def recv(self)->None:
        if self._callback is not None:
            for user, message in self._callback.get():
                iv = serpent.tobytes(message[0])
                msg = serpent.tobytes(message[1])
                data = (iv,msg)

                self.update_text_screen(f"{user} : {self.decrypt(data)}")
            self._callback.clear()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # instanciate the class, create context and related stuff, run the main loop
    client = CypheredGUI()
    client.create()
    client.loop()