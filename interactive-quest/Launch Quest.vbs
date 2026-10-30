Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
shell.Run """C:\Python314\pythonw.exe"" """ & shell.CurrentDirectory & "\main.py""", 1, False
