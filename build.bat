call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\py_langs py_langs\langs.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap\py_langs py_langs\po2buf.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap appgen.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap tooltip.py
call nuitka.bat --msvc=14.3 --module --no-pyi-file --remove-output --output-dir=bootstrap TWLMagician.py
cd bootstrap
call nuitka.bat --standalone --msvc=14.3 --remove-output --enable-plugin=tk-inter --nofollow-import-to=dbm --nofollow-import-to=distutils --nofollow-import-to=py_compile --nofollow-import-to=argparse Run_TWLMagician.py
rm -rf bootstrap\Run_TWLMagician.dist\tk\images
cp -r Run_TWLMagician.dist C:\Users\Public\Run_TWLMagician.dist
mkdir dist
cp -r Run_TWLMagician.dist\py_langs .\dist\py_langs
cp Run_TWLMagician.dist\api-ms-win-core-path-l1-1-0.dll .\dist\api-ms-win-core-path-l1-1-0.dll
cp Run_TWLMagician.dist\vcruntime140.dll .\dist\vcruntime140.dll
cp Run_TWLMagician.dist\appgen.pyd .\dist\appgen.pyd
cp Run_TWLMagician.dist\TWLMagician.pyd .\dist\TWLMagician.pyd
cp Run_TWLMagician.dist\tooltip.pyd .\dist\tooltip.pyd
rm -rf Run_TWLMagician.dist py_langs *.pyd
.\pack\enigmavbconsole.exe .\pack\main.evb .\pack\lib.evb.template .\dist\lib.dat
.\pack\enigmavbconsole.exe .\pack\main.evb .\pack\tkinter.evb.template .\dist\tkinter.dat
.\pack\enigmavbconsole.exe .\pack\main.evb .\pack\pyd.evb.template .\dist\pyd.dat
.\pack\enigmavbconsole.exe .\pack\main.evb -output ..\dist\TWLMagician.exe
rm -rf C:\Users\Public\Run_TWLMagician.dist
cp pack\x64\TaskbarLib.dll .\dist\TaskbarLib.dll
pause
