import keyboard
from queue import Queue


class InputClient:
    def __init__(self):
        self.key_log = ""
        self.queue = Queue(1)

    def wait_for_hotkey(self):
        # Generic disadvantage: Completely disables capslock
        keyboard.block_key("capslock")
        keyboard.wait('capslock+s', suppress=True, trigger_on_release=True)

    def listen(self, starting_text: str) -> str | None:
        self.key_log = starting_text

        keyboard.hook(self._hook_callback)

        text = self.queue.get()

        keyboard.unhook(self._hook_callback)
        self.key_log = ""

        return text

    def _hook_callback(self, event: keyboard.KeyboardEvent):
        if event.event_type != keyboard.KEY_DOWN:
            return

        assert event.name
        # Cancel characters
        if any(substring in event.name
                for substring in ["alt", "ctrl", "shift", "esc", "enter",
                                  "left", "right", "up", "down"]):
            self.queue.put(None)
            self.key_log = ""

        # Activation character
        elif event.name == "space":
            self.queue.put(self.key_log)
            self.key_log = ""

        elif event.name == "backspace":
            if self.key_log:
                self.key_log = self.key_log[:-1]
        else:
            self.key_log += event.name
