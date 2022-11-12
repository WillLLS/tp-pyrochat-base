from ciphered_guy import CypheredGUI
import os
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from hashlib import sha256
import base64
import dearpygui.dearpygui as dpg
import serpent

DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo"
}

class FernetGUI(CypheredGUI):
    def __init__(self) -> None:
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
        password = bytes(dpg.get_value('connection_password'),"utf8")
        hashpass = sha256(password)
        print(f"sha256 = {hashpass}")
        #self._key = base64.b64encode(hashpass)
        #self._key = base64.urlsafe_b64decode(hashpass.hexdigest())
        self._key = base64.b64encode(hashpass.digest())
        print(f'self._key = {self._key}')

    def encrypt(self, message):
        message_bin = bytes(message,"utf8")
        f = Fernet(self._key)
        token = f.encrypt(message_bin)
        print(f'token = {token}')
        return (token)

    def decrypt(self, token):
        f = Fernet(self._key)
        message_bin = f.decrypt(token)
        return str(message_bin,"utf8")


    def recv(self)->None:
        if self._callback is not None:
            for user, message in self._callback.get():
                msg = serpent.tobytes(message)
                data = (msg)

                self.update_text_screen(f"{user} : {self.decrypt(data)}")
            self._callback.clear()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # instanciate the class, create context and related stuff, run the main loop
    client = FernetGUI()
    client.create()
    client.loop()