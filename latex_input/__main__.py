import keyboard

from .listener import KeyListener
from .latex_converter import latex_to_unicode

listener = KeyListener()

def main():
    print("latex_input started")

    setup_hotkeys()
    keyboard.wait()

def setup_hotkeys():
    # We use CapsLock as a modifier key for the hotkey, so we should
    # disable capslock functionality
    # TODO: Disable capslock when the script starts
    keyboard.add_hotkey('capslock+s', activation_callback)
    keyboard.block_key('capslock')

    keyboard.add_hotkey('space', accept_callback)
    keyboard.add_hotkey('escape', cancel_callback)

def activation_callback():
    keyboard.send("backspace") # Delete the s character
    listener.start_listening()

def accept_callback():
    text = listener.stop_listening()

    if text.startswith('s'):
        text = text[1:] # Remove the activation character

    if not text:
        return

    translated_text = latex_to_unicode(text)

    num_backspace = len(text) + 1
    keyboard.send(",".join(["backspace"]*num_backspace))
    keyboard.write(translated_text)
    print(translated_text)

def cancel_callback():
    listener.stop_listening()

if __name__ == "__main__":
    main()
