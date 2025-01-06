@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\py_langs py_langs\langs.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\py_langs py_langs\po2buf.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap appgen.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\tk_tooltip tk_tooltip\tooltip.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap TWLMagician.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap pyutils.py

cd bootstrap
call nuitka.bat --standalone --msvc=14.3 --remove-output --enable-plugin=tk-inter --nofollow-import-to=dbm --nofollow-import-to=distutils --nofollow-import-to=py_compile --nofollow-import-to=argparse --windows-icon-from-ico=..\icon.ico TWLMagician_Container.py

::Copy
rmdir /S /Q TWLMagician_Container.dist\tk\images
xcopy /Y /S /Q TWLMagician_Container.dist C:\Users\Public\TWLMagician_Container.dist\
mkdir dist
copy /Y TWLMagician_Container.dist\vcruntime140.dll .\dist\vcruntime140.dll
copy /Y TWLMagician_Container.dist\vcruntime140_1.dll .\dist\vcruntime140_1.dll
copy /Y TWLMagician_Container.dist\pyutils.pyd .\dist\pyutils.pyd

::Clean
rmdir /S /Q TWLMagician_Container.dist py_langs tk_tooltip
del *.pyd

::enigmavb pack
..\pack\enigmavbconsole.exe ..\pack\main.evb ..\pack\x64\lib.evb.template  .\dist\lib.dat
..\pack\enigmavbconsole.exe ..\pack\main.evb ..\pack\x64\tkinter.evb.template .\dist\tkinter.dat
..\pack\enigmavbconsole.exe ..\pack\main.evb ..\pack\x64\pyd.evb.template .\dist\pyd.dat
..\pack\enigmavbconsole.exe ..\pack\main.evb -output ..\bootstrap\dist\TWLMagician.exe

::Clean and copy to dist
rmdir /S /Q C:\Users\Public\TWLMagician_Container.dist
copy /Y ..\pack\x64\TaskbarLib.dll .\dist\TaskbarLib.dll
xcopy /Y /S /Q ..\i18n .\dist\i18n\
xcopy /Y /S /Q ..\Windows .\dist\Windows\
copy ..\icon.ico .\dist
copy ..\LICENSE .\dist
copy ..\README.md .\dist

::Zipped it
cd dist
zip -r ../TWLMagician_Win_x64.zip .

pause
