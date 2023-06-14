@echo off
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\py_langs py_langs\langs.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\py_langs py_langs\po2buf.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap appgen.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap tooltip.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap TWLMagician.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap pyutils.py

cd bootstrap
call nuitka.bat --standalone --msvc=14.3 --remove-output --enable-plugin=tk-inter --nofollow-import-to=dbm --nofollow-import-to=distutils --nofollow-import-to=py_compile --nofollow-import-to=argparse --windows-icon-from-ico=..\icon.ico Run_TWLMagician.py
rmdir /S /Q Run_TWLMagician.dist\tk\images

xcopy /Y /S /Q Run_TWLMagician.dist C:\Users\Public\Run_TWLMagician.dist\
mkdir dist
copy /Y Run_TWLMagician.dist\vcruntime140.dll .\dist\vcruntime140.dll
rmdir /S /Q Run_TWLMagician.dist py_langs
del *.pyd

..\pack\enigmavbconsole.exe ..\pack\main.evb ..\pack\lib.evb.template  .\dist\lib.dat
..\pack\enigmavbconsole.exe ..\pack\main.evb ..\pack\tkinter.evb.template .\dist\tkinter.dat
..\pack\enigmavbconsole.exe ..\pack\main.evb ..\pack\pyd.evb.template .\dist\pyd.dat
..\pack\enigmavbconsole.exe ..\pack\main.evb -output ..\bootstrap\dist\TWLMagician.exe

rmdir /S /Q C:\Users\Public\Run_TWLMagician.dist
copy /Y ..\pack\x64\TaskbarLib.dll .\dist\TaskbarLib.dll
copy /Y ..\pack\x64\tk86t.dll .\dist\tk86t.dll
copy /Y ..\pack\x64\api-ms-win-core-path-l1-1-0.dll .\dist\api-ms-win-core-path-l1-1-0.dll
pause
