@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x86 10.0.10240.0 --vcvars_ver=14.16
call nuitka35.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap\py_langs py_langs\langs.py
call nuitka35.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap\py_langs py_langs\po2buf.py
call nuitka35.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap appgen.py
call nuitka35.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap tooltip.py
call nuitka35.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap TWLMagician.py
call nuitka35.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap pyutils.py

cd bootstrap
call nuitka35.bat --standalone --onefile --msvc=14.1 --remove-output --enable-plugin=tk-inter --nofollow-import-to=dbm --nofollow-import-to=distutils --nofollow-import-to=py_compile --nofollow-import-to=argparse --nowarn-mnemonic=old-python-windows-console --windows-icon-from-ico=..\icon.ico Run_TWLMagician.py

rename .\Run_TWLMagician.exe TWLMagician.exe
rmdir /S /Q py_langs
del *.pyd

pause
