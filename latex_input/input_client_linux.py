from pynput import keyboard as pkeyboard  # Differentiate from keyboard module
from queue import Queue


class InputClient:
    def __init__(self):
        self.key_log = ""
        self.queue = Queue(1)

    def wait_for_hotkey(self):
        def on_activate():
            # Stop the listener thread once the hotkey is pressed
            l.stop()

        def for_canonical(f):
            return lambda k: f(l.canonical(k))

        hotkey = pkeyboard.HotKey(
            pkeyboard.HotKey.parse("<ctrl>+<shift>+l"),
            on_activate)
        with pkeyboard.Listener(
                on_press=for_canonical(hotkey.press),
                on_release=for_canonical(hotkey.release)) as l:
            l.join()

    def listen(self, starting_text: str) -> str | None:
        self.key_log = starting_text

        with pkeyboard.Events() as events:
            for e in events:
                if isinstance(e, pkeyboard.Events.Release):
                    continue

                if e.key == pkeyboard.Key.space:
                    self.queue.put(self.key_log)
                    break
                elif e.key == pkeyboard.Key.backspace:
                    if self.key_log:
                        self.key_log = self.key_log[:-1]
                elif e.key == pkeyboard.Key.esc:
                    self.queue.put(None)
                    break
                else:
                    try:
                        self.key_log += e.key.char
                    except AttributeError:
                        pass

        text = self.queue.get()
        self.key_log = ""

        return text

    def write(self, char: str):
        self._write_pynput(char)

    def _write_pynput(self, char: str):
        controller = pkeyboard.Controller()

        if char == "\b":
            controller.press(pkeyboard.Key.backspace)
            controller.release(pkeyboard.Key.backspace)
        else:
            controller.type(char)
