@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\py_langs py_langs\langs.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\py_langs py_langs\po2buf.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap appgen.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\tk_tooltip tk_tooltip\tooltip.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap TWLMagician.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap pyutils.py

cd bootstrap
call nuitka.bat --standalone --onefile --onefile-no-compression --msvc=14.3 --remove-output --enable-plugin=tk-inter --nofollow-import-to=dbm --nofollow-import-to=distutils --nofollow-import-to=py_compile --nofollow-import-to=argparse --windows-icon-from-ico=..\icon.ico TWLMagician_Container.py

rename .\TWLMagician_Container.exe TWLMagician.exe
rmdir /S /Q py_langs
rmdir /S /Q tk_tooltip
del *.pyd

cd .. && mkdir dist
move bootstrap\TWLMagician.exe dist
xcopy /Y /S /Q i18n dist\i18n\
xcopy /Y /S /Q Windows dist\Windows\
copy lib\x64\TaskbarLib.dll dist
copy lib\x64\api-ms-win-core-path-l1-1-0.dll dist
copy icon.ico dist
copy LICENSE dist
copy README.md dist

cd dist
python -m zipfile -c TWLMagician_Win_x64.zip Windows i18n TWLMagician.exe icon.ico LICENSE README.md TaskbarLib.dll api-ms-win-core-path-l1-1-0.dll

pause
