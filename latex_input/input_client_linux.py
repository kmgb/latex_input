from pynput import keyboard as pkeyboard  # Differentiate from keyboard module
from queue import Queue
from subprocess import Popen, PIPE
import time


class InputClient:
    def __init__(self):
        self.key_log = ""
        self.queue = Queue(1)
        self.controller = pkeyboard.Controller()

    def wait_for_hotkey(self):
        def on_activate():
            # Stop the listener thread once the hotkey is pressed
            l.stop()

        def for_canonical(f):
            return lambda k: f(l.canonical(k))

        hotkey = pkeyboard.HotKey(
            pkeyboard.HotKey.parse("<ctrl>+<shift>+i"),
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

    def write(self, text: str, delay: float = 0.0):
        # self._write_pynput(char)
        # self._write_ctrlshiftu(char)
        self._write_clipboard(text)

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

    def _write_pynput(self, char: str):
        """
        Write a character to the active window using pynput
        Note: This doesn't always work, for example \\bigodot
        - See https://github.com/moses-palmer/pynput/issues/465
        """
        self.controller.type(char)

    def _write_ctrlshiftu(self, char: str):
        """
        Write a character to the active window using Ctrl+Shift+U
        This is a workaround for the pynput method, which doesn't
        work for some unicode characters

        FIXME: Excessively slow, requires 0.05 delay between characters or else
        it will fail to type the characters
        """
        codepoint = "{:x}".format(ord(char))

        # Press Ctrl+Shift+U to start the unicode input process
        self.controller.press(pkeyboard.Key.ctrl)
        self.controller.press(pkeyboard.Key.shift)
        self.controller.press("u")
        self.controller.release("u")
        self.controller.release(pkeyboard.Key.shift)
        self.controller.release(pkeyboard.Key.ctrl)

        # Type the codepoint
        for c in codepoint:
            self.controller.press(c)
            self.controller.release(c)

        # Press Enter to finish the unicode input process
        self.controller.press(pkeyboard.Key.enter)
        self.controller.release(pkeyboard.Key.enter)

    def _write_clipboard(self, text: str):
        """
        Writes the character to the clipboard and pastes it. This seems to work in most cases
        unlike the other methods.
        Disadvantages:
        - Requires xclip to be installed
        - Overwrites the clipboard contents
        - Only works if Ctrl-v is the paste shortcut (not true for terminals)
        """
        def copy_to_clipboard(text: str):
            # TODO: Wayland support with wclip
            p = Popen(['xclip', '-selection', 'clipboard'], stdin=PIPE)
            p.communicate(input=text.encode('utf-8'))
            p.wait()

        copy_to_clipboard(text)
        self.controller.press(pkeyboard.Key.ctrl)
        self.controller.press("v")
        self.controller.release("v")
        self.controller.release(pkeyboard.Key.ctrl)
