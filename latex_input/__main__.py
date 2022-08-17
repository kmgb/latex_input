import argparse
from PyQt5 import QtGui, QtWidgets, QtCore
import keyboard
import sys

from .listener import KeyListener
from .latex_converter import latex_to_unicode

app_name = "LaTeX Input"
app_icon_file = "./icon.ico"
listener = KeyListener()


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Launch without a visible GUI"
    )

    return parser


def main():
    args = get_parser().parse_args()

    print(f"{app_name} started")

    setup_hotkeys()

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

    num_backspace = len(text) + 1  # +1 for space
    keyboard.send(",".join(["backspace"]*num_backspace))
    print(f"Writing: {translated_text}")
    keyboard.write(translated_text)


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
    window.setWindowIcon(QtGui.QIcon(app_icon_file))
    window.setWindowTitle(app_name)
    layout = QtWidgets.QVBoxLayout(window)
    layout.addWidget(QtWidgets.QLabel(
        "Press <b>CapsLock+s</b> to enter input mode. Enter your desired LaTeX,"
        "then press <b>space</b> to translate the text and exit input mode."
        "<br>Try it in the text box below."))
    layout.addWidget(QtWidgets.QTextEdit(window))

    tray_icon = SystemTrayIcon(QtGui.QIcon(app_icon_file))
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
