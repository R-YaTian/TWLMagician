@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x86 10.0.10240.0 --vcvars_ver=14.16
set CCFLAGS=/nologo /D _USING_V110_SDK71_ /D _WIN32_WINNT=0x0503
set LDFLAGS=/nologo /subsystem:console,"5.01"
call nuitka37.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap\py_langs py_langs\langs.py
call nuitka37.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap\py_langs py_langs\po2buf.py
call nuitka37.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap appgen.py
call nuitka37.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap tooltip.py
call nuitka37.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap TWLMagician.py
call nuitka37.bat --msvc=14.1 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap pyutils.py

cd bootstrap
call nuitka37.bat --standalone --onefile --onefile-no-compression --include-data-files=../pack/x86/TaskbarLib.dll=TaskbarLib.dll --msvc=14.1 --remove-output --enable-plugin=tk-inter --nofollow-import-to=dbm --nofollow-import-to=distutils --nofollow-import-to=py_compile --nofollow-import-to=argparse --nowarn-mnemonic=old-python-windows-console --windows-icon-from-ico=..\icon.ico Run_TWLMagician.py

rename .\Run_TWLMagician.exe TWLMagician.exe
rmdir /S /Q py_langs
del *.pyd

pause
