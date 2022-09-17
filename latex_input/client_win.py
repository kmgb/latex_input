from typing import NoReturn
import ahk
import atexit

ahk_wait_activation = r"""
#NoTrayIcon
CapsLock & s::
    ; Wait for CapsLock to be released
    ; Otherwise this script exits before it can toggle CapsLock back off
    KeyWait, CapsLock
    ExitApp
return
"""

ahk_listen_script = r"""
#NoTrayIcon
SendDeactivation()
{
    var := Chr(16)Chr(3)
    FileAppend, %var%, *, UTF-8  ; Send a special code to indicate the input was cancelled
}

Input, value, V, {Space}{Tab}{Esc}{LControl}{RControl}{LAlt}{RAlt}{LWin}{RWin}{AppsKey}{F1}{F2}{F3}{F4}{F5}{F6}{F7}{F8}{F9}{F10}{F11}{F12}{Left}{Right}{Up}{Down}{Home}{End}{PgUp}{PgDn}{Del}{Ins}{NumLock}{PrintScreen}{Pause}

; New Input has been started, cancel this one
if (ErrorLevel = "NewInput")
{
    SendDeactivation()
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


class Client():
    def __init__(self, on_accept=None, on_activate=None, on_deactivate=None):
        self.ahk = ahk.AHK()
        self.on_accept = on_accept
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.proc = None

    def listen(self) -> NoReturn:
        """
        Listens for key activation and records written text.
        Sends any written text to `on_accept`.
        """
        # Special handling to kill any dangling AutoHotKey process when this
        # thread gets killed
        def kill_proc():
            if self.proc:
                self.proc.kill()

        atexit.register(kill_proc)

        while True:
            self._do_script(ahk_wait_activation)

            if self.on_activate:
                self.on_activate()

            result = self._do_script(ahk_listen_script)

            # Data Link Escape + End of Text
            if result == "\x10\x03":
                if self.on_deactivate:
                    self.on_deactivate()
            else:
                self.on_accept(result)
                if self.on_deactivate:
                    self.on_deactivate()

    def _do_script(self, script: str) -> str:
        # We choose blocking=False to get a Popen instance, then block
        # on it exiting anyways.
        self.proc = self.ahk.run_script(script, blocking=False)
        out, err = self.proc.communicate()

        return out.decode('utf-8')
