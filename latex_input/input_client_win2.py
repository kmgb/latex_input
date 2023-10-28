from pynput import keyboard as pkeyboard
from pynput.keyboard import KeyCode
from queue import Queue
from subprocess import Popen, PIPE
import time


class InputClient:
    def __init__(self):
        self.key_log = ""
        self.queue = Queue(1)
        self.controller = pkeyboard.Controller()

    def wait_for_hotkey(self):
        def on_release(key):
            if isinstance(key, KeyCode) and key.char == "\\":
                # Stop the listener thread once the hotkey is pressed
                listener.stop()

        with pkeyboard.Listener(on_release) as listener:
            listener.join()

        self.send_backspace(1)  # Delete the backslash from the hotkey

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
                elif isinstance(e.key, KeyCode):
                    self.key_log += e.key.char

        text = self.queue.get()
        self.key_log = ""

        return text

    def write(self, text: str, delay: float = 0.0):
        self._write_pynput(text)

    def send_backspace(self, num_backspace: int, delay: float = 0.0):
        for _ in range(num_backspace):
            self.controller.press(pkeyboard.Key.backspace)
            self.controller.release(pkeyboard.Key.backspace)

            # self._accurate_delay(delay)

    def _accurate_delay(self, delay):
        """
        Function to provide accurate time delay
        From https://stackoverflow.com/a/50899124
        """
        target_time = time.perf_counter() + delay
        while time.perf_counter() < target_time:
            pass

    def _write_pynput(self, text: str):
        """
        Write a character to the active window using pynput
        Note: This doesn't always work, for example \\bigodot
        - See https://github.com/moses-palmer/pynput/issues/465
        """
        self.controller.type(text)
