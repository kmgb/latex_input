#SingleInstance, Force
#NoEnv
#Include .\socket.ahk
SendMode Input
SetWorkingDir, %A_ScriptDir%

StringCaseSense, On

socket := new SocketTCP()
socket.Connect(["127.0.0.1", 14739])

SendActivation()
{
    socket.SendText(Chr(16)Chr(2))
}

SendDectivation()
{
    socket.SendText(Chr(16)Chr(3))
}

CapsLock & s::
    SendActivation()
    Input, value, V, {Space}{Tab}{Esc}{LControl}{RControl}{LAlt}{RAlt}{LWin}{RWin}{AppsKey}{F1}{F2}{F3}{F4}{F5}{F6}{F7}{F8}{F9}{F10}{F11}{F12}{Left}{Right}{Up}{Down}{Home}{End}{PgUp}{PgDn}{Del}{Ins}{NumLock}{PrintScreen}{Pause}

    ; New Input has been started, cancel this one
    if (ErrorLevel = "NewInput")
    {
        SendDectivation()
        return
    }

    ; If any end key was pressed other than space or tab, cancel the operation
    if (ErrorLevel != "EndKey:Space" and ErrorLevel != "EndKey:Tab")
    {
        SendDectivation()
        return
    }

    socket.SendText(value)
    SendDectivation()
return
