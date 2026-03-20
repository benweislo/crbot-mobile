Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\User\WORK\MEETINGS"
WshShell.Run """C:\Python314\pythonw.exe"" -m app.main", 0, False
