import ahk
import atexit

ahk_wait_activation = r"""
#NoEnv
#NoTrayIcon
CapsLock & s::
    ; This script exits before it can toggle CapsLock back
    ; So we manually toggle it to its original state
    SetCapsLockState % !GetKeyState("CapsLock", "T")
    ExitApp
return
"""

ahk_listen_script = r"""
#NoEnv
#NoTrayIcon
SendDeactivation()
{
    var := Chr(16)Chr(3)
    FileAppend, %var%, *, UTF-8  ; Send a special code to indicate the input was cancelled
}

SendBackspace(value)
{
    bs := Chr(8)
    FileAppend, %value%, *, UTF-8
    FileAppend, %bs%, *, UTF-8  ; Send a special code at the end to indicate backspace was pressed
}

Input, value, V, {Space}{Tab}{BS}{Esc}{LControl}{RControl}{LAlt}{RAlt}{LWin}{RWin}{AppsKey}{F1}{F2}{F3}{F4}{F5}{F6}{F7}{F8}{F9}{F10}{F11}{F12}{Left}{Right}{Up}{Down}{Home}{End}{PgUp}{PgDn}{Del}{Ins}{NumLock}{PrintScreen}{Pause}

; New Input has been started, cancel this one
if (ErrorLevel = "NewInput")
{
    SendDeactivation()
    ExitApp
}

; Send notification on backspace
if (ErrorLevel == "EndKey:Backspace")
{
    SendBackspace(value)
    ExitApp
}

; If any end key was pressed other than space or tab, cancel the operation
if (ErrorLevel != "EndKey:Space" and ErrorLevel != "EndKey:Tab")
{
    SendDeactivation()
    ExitApp
}

FileAppend, %value%, *, UTF-8  ; Print to stdout for Python to read

ExitApp
"""


class InputClient:
    def __init__(self):
        self.ahk = ahk.AHK()
        self.proc = None

        atexit.register(self._kill_proc)

    def _kill_proc(self):
        if self.proc:
            self.proc.kill()

    def wait_for_hotkey(self):
        self._do_script(ahk_wait_activation)

    def listen(self, starting_text: str) -> str | None:
        result = starting_text

        while True:
            data = self._do_script(ahk_listen_script)

            if data == "\x10\x03":  # Cancellation sequence
                return None

            # Concatenate the data from the script, handling backspace
            result = self._add_characters(result, data)

            if data.endswith("\b"):
                continue

            break

        return result

    def _do_script(self, script: str) -> str:
        # We choose blocking=False to get a Popen instance, then block
        # on it exiting anyways.
        self.proc = self.ahk.run_script(script, blocking=False)
        out, err = self.proc.communicate()
        self.proc = None

        return out.decode('utf-8')

    def _add_characters(self, base: str, add: str) -> str:
        result = base

        # If the string contains backspace, handle that by deleting the previous character
        for c in add:
            if c == "\b":
                if result:
                    result = result[:-1]
            else:
                result += c

        return result
