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
call nuitka.cmd --standalone --msvc=14.3 --remove-output --enable-plugin=tk-inter --nofollow-import-to=PIL --nofollow-import-to=dbm --nofollow-import-to=distutils --nofollow-import-to=py_compile --nofollow-import-to=argparse --nowarn-mnemonic=old-python-windows-console --windows-icon-from-ico=..\icon.ico TWLMagician_Container.py

::Copy
rmdir /S /Q TWLMagician_Container.dist\tk\images
xcopy /Y /S /Q TWLMagician_Container.dist C:\Users\Public\TWLMagician_Container.dist\
mkdir dist
copy /Y TWLMagician_Container.dist\vcruntime140.dll .\dist\vcruntime140.dll

::Clean
rmdir /S /Q TWLMagician_Container.dist py_langs tk_tooltip
del *.pyd

@REM rename appgen.*.pyd appgen.pyd
@REM move /Y appgen.pyd TWLMagician_Container.dist\
@REM move TWLMagician_Container.dist ..\dist
@REM rmdir /S /Q py_langs
@REM rmdir /S /Q tk_tooltip
@REM del *.pyd

@REM cd ..
@REM xcopy /Y /S /Q i18n dist\i18n\
@REM xcopy /Y /S /Q Windows dist\Windows\
@REM copy lib\x86\TaskbarLib.dll dist
@REM copy icon.ico dist
@REM copy LICENSE dist
@REM copy README.md dist

@REM cd dist
@REM rmdir /S /Q tk\images
@REM rename .\TWLMagician_Container.exe TWLMagician.exe
@REM zip -r ../TWLMagician_Win_x86.zip .

pause
