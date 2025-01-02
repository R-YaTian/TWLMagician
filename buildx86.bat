@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x86 --vcvars_ver=14.16
set CCFLAGS=/nologo /D _USING_V110_SDK71_ /D _WIN32_WINNT=0x0503
set LDFLAGS=/nologo /subsystem:console,"5.01"
call nuitka.cmd --msvc=14.3 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap\py_langs py_langs\langs.py
call nuitka.cmd --msvc=14.3 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap\py_langs py_langs\po2buf.py
call nuitka.cmd --msvc=14.3 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap appgen.py
call nuitka.cmd --msvc=14.3 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap\tk_tooltip tk_tooltip\tooltip.py
call nuitka.cmd --msvc=14.3 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap TWLMagician.py
call nuitka.cmd --msvc=14.3 --module --no-pyi-file --remove-output --nowarn-mnemonic=old-python-windows-console --output-dir=bootstrap pyutils.py

cd bootstrap
call nuitka.cmd --standalone --onefile --onefile-no-compression --include-data-files=../icon.ico=icon.ico --msvc=14.3 --remove-output --enable-plugin=tk-inter --nofollow-import-to=PIL --nofollow-import-to=dbm --nofollow-import-to=distutils --nofollow-import-to=py_compile --nofollow-import-to=argparse --nowarn-mnemonic=old-python-windows-console --windows-icon-from-ico=..\icon.ico TWLMagician_Container.py

rename .\TWLMagician_Container.exe TWLMagician.exe
rmdir /S /Q py_langs
rmdir /S /Q tk_tooltip
del *.pyd

cd ..
mkdir dist
move bootstrap\TWLMagician.exe dist
xcopy /Y /S /Q i18n dist\i18n\
xcopy /Y /S /Q Windows dist\Windows\
copy pack\x86\TaskbarLib.dll dist
copy LICENSE dist
copy README.md dist

cd dist
python -m zipfile -c TWLMagician.zip Windows i18n TWLMagician.exe LICENSE README.md TaskbarLib.dll

pause
