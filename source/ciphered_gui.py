import logging
import os
import serpent
import base64

import dearpygui.dearpygui as dpg

from basic_gui import BasicGUI, DEFAULT_VALUES
from chat_client import ChatClient
from generic_callback import GenericCallback

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


DEFAULT_VALUES["password"]=""

class CipheredGUI(BasicGUI):
    """
    GUI for a chat client. Securied
    """
    def __init__(self)-> None:
        # constructor
        BasicGUI.__init__(self)
        self._key= None


    def _create_chat_window(self)->None:
            # chat windows
            # known bug : the add_input_text do not display message in a user friendly way
            with dpg.window(label="Chat", pos=(0, 0), width=800, height=600, show=False, tag="chat_windows", on_close=self.on_close):
                dpg.add_input_text(default_value="Readonly\n\n\n\n\n\n\n\nfff", multiline=True, readonly=True, tag="screen", width=790, height=525)
                dpg.add_input_text(default_value="some text", tag="input", on_enter=True, callback=self.text_callback, width=790)

    def _create_connection_window(self)->None:
        # windows about connexion
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):
            
            for field in ["host", "port", "name"]:
                with dpg.group(horizontal=True):
                    dpg.add_text(field)
                    dpg.add_input_text(default_value=DEFAULT_VALUES[field], tag=f"connection_{field}")
            
            with dpg.group(horizontal=True):
                dpg.add_text("password")
                dpg.add_input_text(password=True,tag="connection_password")
        
            dpg.add_button(label="Connect", callback=self.run_chat)

    def _create_menu(self)->None:
        # menu (file->connect)
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Connect", callback=self.connect)

    def create(self):
        # create the context and all windows
        dpg.create_context()

        self._create_chat_window()
        self._create_connection_window()
        self._create_menu()        
            
        dpg.create_viewport(title='Secure chat - or not', width=800, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def update_text_screen(self, new_text:str)->None:
        # from a nex_text, add a line to the dedicated screen text widget
        text_screen = dpg.get_value("screen")
        text_screen = text_screen + "\n" + new_text
        dpg.set_value("screen", text_screen)

    def text_callback(self, sender, app_data)->None:
        # every time a enter is pressed, the message is gattered from the input line
        text = dpg.get_value("input")
        self.update_text_screen(f"Me: {text}")
        self.send(text)
        dpg.set_value("input", "")

    def connect(self, sender, app_data)->None:
        # callback used by the menu to display connection windows
        dpg.show_item("connection_windows")

    def encrypt(self, text):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self._key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        bin_text=bytes(text, "utf8")

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(bin_text) + padder.finalize()

        ct = encryptor.update(padded_data) + encryptor.finalize()
        return ((iv, ct))

    def decrypt(self, message: tuple):
        cipher = Cipher(algorithms.AES(self._key), modes.CBC(message[0]))
        decryptor = cipher.decryptor()
        padded_message=decryptor.update(message[1]) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        message_decr = unpadder.update(padded_message)+unpadder.finalize()
        return (message_decr)


    def run_chat(self, sender, app_data)->None:
        # callback used by the connection windows to start a chat session
        host = dpg.get_value("connection_host")
        port = int(dpg.get_value("connection_port"))
        name = dpg.get_value("connection_name")
        password=dpg.get_value("connection_password")
        salt = b"ala"
        # derive
        kdf = PBKDF2HMAC(
             algorithm=hashes.SHA256(),
             length=32,
             salt=salt,
             iterations=100000,
             )
        password=bytes(password, "utf8")
        self._key = kdf.derive(password)


        self._log.info(f"Connecting {name}@{host}:{port}")

        self._callback = GenericCallback()

        self._client = ChatClient(host, port)
        self._client.start(self._callback)
        self._client.register(name)

        dpg.hide_item("connection_windows")
        dpg.show_item("chat_windows")
        dpg.set_value("screen", "Connecting")

    def on_close(self):
        # called when the chat windows is closed
        self._client.stop()
        self._client = None
        self._callback = None

    def recv(self)->None:
        # function called to get incoming messages and display them
        
        if self._callback is not None:
            for user, message in self._callback.get():
                print(message)
                message_bytes_iv=serpent.tobytes(message[0])
                #print(message_bytes_iv)
                message_bytes_ct=serpent.tobytes(message[1])
                #print(message_bytes_ct)
                message_decr=self.decrypt((message_bytes_iv, message_bytes_ct))
                self.update_text_screen(f"{user} : {message_decr}")
                print(message_decr)
            self._callback.clear()

    def send(self, text)->None:
        # function called to send a message to all (broadcasting)
        message= self.encrypt(text)
        self._client.send_message(message)

    def loop(self):
        # main loop
        while dpg.is_dearpygui_running():
            self.recv()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # instanciate the class, create context and related stuff, run the main loop
    client = CipheredGUI()
    client.create()
    client.loop()