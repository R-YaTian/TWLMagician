import sys
from cx_Freeze import setup, Executable

if sys.maxsize > 2**32:  # 64-bit Python
    upgrade_code = "{ea5bd479-d197-4593-9a93-68fe2fda1afc}"
    build_options = {
        "packages": [],
        "excludes": ["rmdot_files",
                     "zipfile",
                     "xml",
                     "packaging",
                     "_bz2",
                     "elementtree",
                     "pyexpat",
                     "lzma",
                     "_wmi",
                     "decimal"],
        "include_files": [
            ("i18n", "i18n"),
            ("Windows", "Windows"),
            ("icon.ico", "icon.ico"),
            ("LICENSE", "LICENSE"),
            ("README.md", "README.md"),
            ("Res/TaskbarLib/x64/TaskbarLib.dll", "TaskbarLib.dll")
        ]
    }
else:  # 32-bit Python
    upgrade_code = "{4afdac91-38fe-4006-af19-e513982bdc68}"
    build_options = {
        "packages": [],
        "excludes": ["rmdot_files",
                     "xmlrpc",
                     "xml",
                     "packaging",
                     "_bz2",
                     "elementtree",
                     "pyexpat",
                     "lzma",
                     "decimal",
                     "_overlapped",
                     "_multiprocessing",
                     "_asyncio",
                     "concurrent",
                     "asyncio",
                     "multiprocessing"],
        "include_files": [
            ("i18n", "i18n"),
            ("Windows", "Windows"),
            ("icon.ico", "icon.ico"),
            ("LICENSE", "LICENSE"),
            ("README.md", "README.md"),
            ("Res/TaskbarLib/x86/TaskbarLib.dll", "TaskbarLib.dll")
        ]
    }

executables = [
    Executable('TWLMagician.py',
               target_name='TWLMagician',
               icon='icon.ico')
]

setup(
    name='TWLMagician',
    author="R-YaTian",
    version='1.5.4',
    description='TWLMagician is a multipurpose tool for TWL Console (aka Nintendo DSi)',
    options={"build_exe": build_options,
             "bdist_msi": {
                "upgrade_code": upgrade_code,
                "add_to_path": False,
                "all_users": True,
                "install_icon": "icon.ico",
                "initial_target_dir": r"[ProgramFilesFolder]\\TWLMagician"
            }},
    executables=executables
)
