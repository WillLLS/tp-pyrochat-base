from basic_gui import *

DEFAULT_VALUES["password"] = "password"

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
        #passwd = dpg.get_value("connection_password")

if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG)

    client = CipheredGUI()
    client.create()
    client.loop()