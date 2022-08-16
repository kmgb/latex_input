import keyboard

class KeyListener:
    is_listening = False
    key_log = ""

    def _hook_callback(self, event:keyboard.KeyboardEvent):
        if event.event_type != keyboard.KEY_DOWN:
            return

        if any(substring in event.name
            for substring in ["alt", "ctrl", "shift", "esc", "left", "right", "up", "down"]):
                return

        if event.name == "backspace":
            if self.key_log:
                self.key_log = self.key_log[:-1]
        else:
            self.key_log += event.name

    def start_listening(self):
        if self.is_listening:
            self._clear()

        keyboard.hook(self._hook_callback)
        self.is_listening = True

    def stop_listening(self) -> str:
        if not self.is_listening:
            return ""

        key_log = self.key_log
        self._clear()

        return key_log

    def _clear(self):
        if self.is_listening:
            keyboard.unhook(self._hook_callback)

        self.key_log = ""
        self.is_listening = False
