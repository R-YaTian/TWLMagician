@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x86 --vcvars_ver=14.16
set CCFLAGS=/nologo /D _USING_V110_SDK71_ /D _WIN32_WINNT=0x0503
set LDFLAGS=/nologo /subsystem:console,"5.01"
call .venv\Scripts\activate.bat
call nuitka.cmd --standalone --msvc=14.3 --remove-output --enable-plugin=tk-inter --nowarn-mnemonic=old-python-windows-console --windows-icon-from-ico=icon.ico TWLMagician.py

::Clean and move
rmdir /S /Q TWLMagician.dist\tk\images
move TWLMagician.dist dist

::Copying files
xcopy /Y /S /Q i18n dist\i18n\
xcopy /Y /S /Q Windows dist\Windows\
copy lib\x86\TaskbarLib.dll dist
copy icon.ico dist
copy LICENSE dist
copy README.md dist

::Packing
cd dist
zip -r ../TWLMagician_Win_x86.zip .

pause
