import argparse
import threading
from typing import Final
from PyQt5 import QtGui, QtWidgets, QtCore
import keyboard
import sys
import time
from latex_input.client_win import Client

from latex_input.listener import KeyListener
from latex_input.latex_converter import latex_to_unicode, FontContext
from latex_input.parse_unicode_data import FontVariantType

APP_NAME: Final[str] = "LaTeX Input"
APP_ICON_FILE: Final[str] = "./icon.ico"
APP_ACTIVATED_ICON_FILE: Final[str] = "./icon_activated.ico"
TEXT_EDIT_FONTSIZE: Final[int] = 12

# Necessary, as some applications will process keystrokes out
# of order if they arrive too quickly, or they won't process
# them at all.
KEYPRESS_DELAY: Final[float] = 0.002

listener = KeyListener()
tray_icon: QtWidgets.QSystemTrayIcon
use_key_delay = True
is_math_mode = False


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-gui", "--daemon",
        action="store_true",
        help="Launch without a visible GUI"
    )

    parser.add_argument(
        "--faster-keypresses",
        action="store_true",
        help="Barely faster keypresses, can cause applications to misbehave"
    )

    # --math-mode and --no-math-mode
    parser.add_argument(
        "--math-mode",
        action=argparse.BooleanOptionalAction
    )

    return parser


def main():
    args = get_parser().parse_args()

    if args.faster_keypresses:
        global use_key_delay
        use_key_delay = False

    if args.math_mode is None:
        # TODO: Load from preferences file
        pass

    elif args.math_mode:
        global is_math_mode
        is_math_mode = True

    client = Client(
        on_accept=accept_callback,
        on_activate=lambda: set_icon_state(True),
        on_deactivate=lambda: set_icon_state(False)
    )
    client_thread = threading.Thread(target=client.run, daemon=True)
    client_thread.start()

    print(f"{APP_NAME} started")

    if args.no_gui:
        client_thread.join()
    else:
        run_gui()

    print(f"{APP_NAME} stopped")


def set_icon_state(activated: bool):
    if tray_icon:
        tray_icon.setIcon(QtGui.QIcon(
            APP_ACTIVATED_ICON_FILE if activated else APP_ICON_FILE
        ))


def activate_listener(text=""):
    """
    Start listening to global keystrokes, adds `text` to the
    beginning of the listening buffer.
    """
    print("Starting listening")
    listener.start_listening(text)

    if tray_icon:
        tray_icon.setIcon(QtGui.QIcon(APP_ACTIVATED_ICON_FILE))


def accept_callback():
    if not listener.is_listening:
        return

    listened_text = listener.stop_listening()
    print(f"Listened text: '{listened_text}'")
    text = listened_text

    # Continue listening, there was no data to translate
    if len(listened_text) == 0 or listened_text == " ":
        activate_listener()
        return

    translated_text = latex_to_unicode(
        text,
        FontContext(formatting=FontVariantType.ITALIC if is_math_mode else 0)
    )

    # Restart the listener with the original text if the translation failed
    # Could be the user is still entering text that would make the translation work
    # ie. `\mathbb{e asy}' fails at `\mathbb{e' but succeeds when complete.
    if not translated_text:
        print(f"Failed conversion, re-listening with text '{listened_text}'")
        activate_listener(listened_text)
        return

    # Press backspace to delete the entered LaTeX
    num_backspace = len(listened_text) + 1  # +1 for space character
    write_with_delay("\b" * num_backspace, delay=use_key_delay * KEYPRESS_DELAY)

    print(f"Writing: '{translated_text}'")
    write_with_delay(translated_text, delay=use_key_delay * KEYPRESS_DELAY)

    # Continue listening
    # HACK: The call_later is to fix consecutive `accept_callback`s from picking up
    # the <space> from the previous call.
    keyboard.call_later(activate_listener)


def cancel_listener():
    listener.stop_listening()

    if tray_icon:
        tray_icon.setIcon(QtGui.QIcon(APP_ICON_FILE))


def write_with_delay(text: str, delay: float):
    def accurate_delay(delay):
        """
        Function to provide accurate time delay
        From https://stackoverflow.com/a/50899124
        """
        target_time = time.perf_counter() + delay
        while time.perf_counter() < target_time:
            pass

    # FIXME: Can use keyboard.write(text, delay=...) after Python 3.11
    for c in text:
        # Don't use built-in delay parameter as it uses time.sleep
        # which doesn't have good time accurancy until Python 3.11
        keyboard.write(c)
        accurate_delay(delay)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    show_clicked = QtCore.pyqtSignal()
    clicked = QtCore.pyqtSignal()

    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)
        showAction = menu.addAction("Show")
        exitAction = menu.addAction("Exit")
        self.setContextMenu(menu)

        exitAction.triggered.connect(self.exit)
        showAction.triggered.connect(self.show_clicked)
        self.activated.connect(self._handle_activated)

    def exit(self):
        QtCore.QCoreApplication.exit()

    def _handle_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.clicked.emit()


def run_gui():
    global tray_icon

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    window.setWindowIcon(QtGui.QIcon(APP_ICON_FILE))
    window.setWindowTitle(APP_NAME)
    layout = QtWidgets.QVBoxLayout(window)
    layout.addWidget(QtWidgets.QLabel(
        "How to use:"
        "<ol>"
        "<li>Press <b>CapsLock+S</b> to enter input mode</li>"
        "<li>Enter your desired LaTeX</li>"
        "<li>Press <b>Space</b> to translate the text</li>"
        "<li>Press <b>Esc</b> to exit input mode</li>"
        "</ol>"
        "Try it in the text box below:"))
    text_edit = QtWidgets.QTextEdit(window)
    text_edit_font = text_edit.font()
    text_edit_font.setPointSize(TEXT_EDIT_FONTSIZE)
    text_edit.setFont(text_edit_font)
    layout.addWidget(text_edit)

    math_mode_checkbox = QtWidgets.QCheckBox(
        "Math mode — italic text by default"
    )
    math_mode_checkbox.setChecked(is_math_mode)

    def on_mathmode_checked(state: bool):
        global is_math_mode
        is_math_mode = state

    math_mode_checkbox.clicked.connect(on_mathmode_checked)
    layout.addWidget(math_mode_checkbox)

    key_delay_checkbox = QtWidgets.QCheckBox(
        "Slower key presses (some applications need this to work properly — including this window)"
    )
    key_delay_checkbox.setChecked(use_key_delay)

    def on_keydelay_checked(state: bool):
        global use_key_delay
        use_key_delay = state

    key_delay_checkbox.clicked.connect(on_keydelay_checked)
    layout.addWidget(key_delay_checkbox)

    tray_icon = SystemTrayIcon(QtGui.QIcon(APP_ICON_FILE))
    tray_icon.show()

    def trigger_window(show: bool):
        if show:
            window.show()
            window.raise_()
            window.activateWindow()
        else:
            window.hide()

    tray_icon.clicked.connect(lambda: trigger_window(not window.isVisible()))
    tray_icon.show_clicked.connect(lambda: trigger_window(True))

    # Don't close application if the configuration window is closed
    app.setQuitOnLastWindowClosed(False)
    app.exec()


if __name__ == "__main__":
    main()
