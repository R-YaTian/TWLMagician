from cx_Freeze import setup, Executable

build_options = {
    "packages": [],
    "excludes": ["tkinter_tooltips", "rmdot_files", "logging"],
    "include_files": [
        ("i18n", "i18n"),
        ("Windows", "Windows"),
        ("icon.ico", "icon.ico"),
        ("LICENSE", "LICENSE"),
        ("README.md", "README.md"),
        ("pack/x86/TaskbarLib.dll", "TaskbarLib.dll")
    ]
}

executables = [
    Executable('TWLMagician.py',
               target_name='TWLMagician',
               icon='icon.ico')
]

setup(
    name='TWLMagician',
    version='1.4.1',
    description='TWLMagician is a multipurpose tool for TWL Console (aka Nintendo DSi)',
    options={"build_exe": build_options},
    executables=executables
)
