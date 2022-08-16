import keyboard

class KeyListener:
    is_listening = False
    key_log = ""

    def _hook_callback(self, event:keyboard.KeyboardEvent):
        if event.event_type != keyboard.KEY_DOWN:
            return

        # FIXME: Bandaid for ignoring 'shift' and 'ctrl'
        if len(event.name) > 1:
            return

        self.key_log += event.name

    def start_listening(self):
        if self.is_listening:
            return

        keyboard.hook(self._hook_callback)
        self.is_listening = True

    def stop_listening(self) -> str:
        if not self.is_listening:
            return ""

        keyboard.unhook(self._hook_callback)

        self.is_listening = False

        key_log = self.key_log
        self.key_log = ""
        return key_log
