CALL "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

FOR /F "tokens=*" %%S IN ('dir /B "*.a"') DO (
  echo running %%S ...
  lib /SUBSYSTEM:POSIX /MACHINE:X64 %%S
)