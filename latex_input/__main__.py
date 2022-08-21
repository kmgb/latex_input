import argparse
from typing import Final
from PyQt5 import QtGui, QtWidgets, QtCore
import keyboard
import sys
import time

from .listener import KeyListener
from .latex_converter import latex_to_unicode

APP_NAME: Final[str] = "LaTeX Input"
APP_ICON_FILE: Final[str] = "./icon.ico"

# Necessary, as some applications will process keystrokes out
# of order if they arrive too quickly, or they won't process
# them at all.
KEYPRESS_DELAY: Final[float] = 0.002

listener = KeyListener()
use_key_delay = True


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-gui", "--daemon",
        action="store_true",
        help="Launch without a visible GUI"
    )

    parser.add_argument(
        "--faster-keypresses",
        action="store_true"
    )

    return parser


def main():
    args = get_parser().parse_args()

    if args.faster_keypresses:
        global use_key_delay
        use_key_delay = False

    setup_hotkeys()
    print(f"{APP_NAME} started")

    if args.no_gui:
        keyboard.wait()
    else:
        run_gui()


def setup_hotkeys():
    # We use CapsLock as a modifier key for the hotkey, so we should
    # disable capslock functionality
    # TODO: Disable capslock when the script starts
    keyboard.add_hotkey("capslock+s", activation_callback, suppress=True)
    keyboard.block_key("capslock")

    keyboard.add_hotkey("space", accept_callback)
    keyboard.add_hotkey("escape", cancel_callback)


def activation_callback():
    listener.start_listening()


def accept_callback():
    text = listener.stop_listening()

    if text.startswith("s"):
        text = text[1:]  # Remove the activation character

    if not text:
        return

    translated_text = latex_to_unicode(text)

    # Press backspace to delete the entered LaTeX
    num_backspace = len(text) + 1  # +1 for space
    write_with_delay("\b" * num_backspace, delay=use_key_delay * KEYPRESS_DELAY)

    print(f"Writing: {translated_text}")
    write_with_delay(translated_text, delay=use_key_delay * KEYPRESS_DELAY)


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


def cancel_callback():
    listener.stop_listening()


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
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    window.setWindowIcon(QtGui.QIcon(APP_ICON_FILE))
    window.setWindowTitle(APP_NAME)
    layout = QtWidgets.QVBoxLayout(window)
    layout.addWidget(QtWidgets.QLabel(
        "Press <b>CapsLock+s</b> to enter input mode. Enter your desired LaTeX,"
        "then press <b>space</b> to translate the text and exit input mode."
        "<br>Try it in the text box below."))
    layout.addWidget(QtWidgets.QTextEdit(window))

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
