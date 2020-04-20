#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# HiyaCFW Helper R
# Version 3.6.0R
# Author: R-YaTian
# Original Author: mondul <mondul@huyzona.com>

from tkinter import (Tk, Frame, LabelFrame, PhotoImage, Button, Entry, Checkbutton, Radiobutton,
    Label, Toplevel, Scrollbar, Text, StringVar, IntVar, RIGHT, W, X, Y, DISABLED, NORMAL, SUNKEN,
    END)
from tkinter.messagebox import askokcancel, showerror, showinfo, WARNING
from tkinter.filedialog import askopenfilename, askdirectory
from platform import system
from os import path, remove, chmod, listdir, rename
from sys import exit
from threading import Thread
from queue import Queue, Empty
from hashlib import sha1
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError
from subprocess import Popen, PIPE
from struct import unpack_from
from shutil import rmtree, copyfile, copyfileobj
from distutils.dir_util import copy_tree, _path_created
from re import search
from ctypes import windll
from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY


####################################################################################################
# Thread-safe text class

class ThreadSafeText(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.queue = Queue()
        self.update_me()

    def write(self, line):
        self.queue.put(line)

    def update_me(self):
        try:
            while 1:
                self.insert(END, str(self.queue.get_nowait()) + '\n')
                self.see(END)
                self.update_idletasks()

        except Empty:
            pass

        self.after(500, self.update_me)


####################################################################################################
# Main application class

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.pack()
        self.adv_mode = False
        self.nand_mode = False
        self.setup_select = False
 
        # First row
        f1 = Frame(self) 

        self.bak_frame=LabelFrame(f1, text='含有No$GBA footer的NAND备份文件', padx=10, pady=10)

        nand_icon = PhotoImage(data=('R0lGODlhEAAQAIMAAAAAADMzM2ZmZpmZmczMzP///wAAAAAAAAA'
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAAYALAAAAAAQAB'
            'AAAARG0MhJaxU4Y2sECAEgikE1CAFRhGMwSMJwBsU6frIgnR/bv'
            'hTPrWUSDnGw3JGU2xmHrsvyU5xGO8ql6+S0AifPW8kCKpcpEQA7'))

        self.nand_button = Button(self.bak_frame, image=nand_icon, command=self.change_mode, state=DISABLED)
        self.nand_button.image = nand_icon

        self.nand_button.pack(side='left')

        self.nand_file = StringVar()
        self.nandfile = Entry(self.bak_frame, textvariable=self.nand_file, state='readonly', width=40)
        self.nandfile.pack(side='left')

        self.chb = Button(self.bak_frame, text='...', command=self.choose_nand)
        self.chb.pack(side='left')

        self.bak_frame.pack(fill=X)

        self.adv_frame=LabelFrame(f1, text='存储卡根目录', padx=10, pady=10)

        self.sd_path1 = StringVar()
        self.sdpath = Entry(self.adv_frame, textvariable=self.sd_path1, state='readonly', width=41)
        self.sdpath.pack(side='left')

        self.chb1 = Button(self.adv_frame, text='浏览', command=self.choose_nand)
        self.chb1.pack(side='left')

        f1.pack(padx=10, pady=10, fill=X)

        # Second row
        f2 = Frame(self)

        self.setup_frame = LabelFrame(f2, text='NAND解压选项', padx=10, pady=10)

        self.setup_operation = IntVar()

        if fatcat is None:
            if _7z is not None:
                self.setup_operation.set(1)
            elif osfmount is not None:
                self.setup_operation.set(2)
        else:
            self.setup_operation.set(0)

        self.rb1 = Radiobutton(self.setup_frame, text='Fatcat(默认)', variable=self.setup_operation, value=0)
        self.rb2 = Radiobutton(self.setup_frame, text='7-Zip', variable=self.setup_operation, value=1)
        self.rb3 = Radiobutton(self.setup_frame, text='OSFMount2(需要管理员权限)', variable=self.setup_operation, value=2)

        if osfmount or _7z is not None:
            if fatcat is not None:
                self.rb1.pack(anchor=W)
            if _7z is not None:
                self.rb2.pack(anchor=W)
            if osfmount is not None:
                self.rb3.pack(anchor=W)
            if (fatcat is not None) or (osfmount and _7z is not None):
                self.setup_frame.pack(padx=10, pady=(0, 10), fill=X)
                self.setup_select = True

        # Check boxes
        self.checks_frame = Frame(f2)

        # Install TWiLight check
        self.twilight = IntVar()
        self.twilight.set(1)

        twl_chk = Checkbutton(self.checks_frame,
            text='同时安装TWiLightMenu++', variable=self.twilight)

        twl_chk.pack(padx=10, anchor=W)

        self.appgen = IntVar()
        self.appgen.set(0)

        ag_chk = Checkbutton(self.checks_frame, text='使用AppGen', variable=self.appgen)

        ag_chk.pack(padx=10, anchor=W)

        self.devkp = IntVar()
        self.devkp.set(0)

        dkp_chk = Checkbutton(self.checks_frame, text='开启系统设置-数据管理功能', variable=self.devkp, command=self.usedevkp)

        dkp_chk.pack(padx=10, anchor=W)

        self.altdl = IntVar()
        self.altdl.set(0)

        adl_chk = Checkbutton(self.checks_frame, text='使用备用载点', variable=self.altdl, command=self.usealtdl)

        adl_chk.pack(padx=10, anchor=W)

        self.checks_frame.pack(fill=X)

        self.checks_frame1 = Frame(f2)

        self.ag1_chk = Checkbutton(self.checks_frame1, text='使用AppGen(需装有HiyaCFW)', variable=self.appgen, state=DISABLED)

        self.ag1_chk.pack(padx=10, anchor=W)

        self.updatemode = IntVar()
        self.updatemode.set(0)

        self.um_chk = Checkbutton(self.checks_frame1,
            text='更新模式', variable=self.updatemode, command=lambda: self.updatehiya.set(0) if (self.updatehiya.get() == 1) else '', state=DISABLED)

        self.um_chk.pack(padx=10, anchor=W)

        self.updatehiya = IntVar()
        self.updatehiya.set(0)

        self.uh_chk = Checkbutton(self.checks_frame1,
            text='同时更新HiyaCFW', variable=self.updatehiya, command=lambda: self.updatemode.set(1) if (self.updatemode.get() == 0) else '', state=DISABLED)

        self.uh_chk.pack(padx=10, anchor=W)

        # NAND operation frame
        self.nand_frame = LabelFrame(f2, text='NAND操作选项', padx=10, pady=10)

        self.nand_operation = IntVar()
        self.nand_operation.set(0)

        rb0 = Radiobutton(self.nand_frame, text='安装或卸载最新版本的unlaunch(需要管理员权限)',
            variable=self.nand_operation, value=2,
            command=lambda: self.enable_entries(False))
        if osfmount is not None:
            rb0.pack(anchor=W)
        Radiobutton(self.nand_frame, text='移除 No$GBA footer', variable=self.nand_operation,
            value=0, command=lambda: self.enable_entries(False)).pack(anchor=W)

        Radiobutton(self.nand_frame, text='添加 No$GBA footer', variable=self.nand_operation,
            value=1, command=lambda: self.enable_entries(True)).pack(anchor=W)

        fl = Frame(self.nand_frame)

        self.cid_label = Label(fl, text='eMMC CID', state=DISABLED)
        self.cid_label.pack(anchor=W, padx=(24, 0))

        self.cid = StringVar()
        self.cid_entry = Entry(fl, textvariable=self.cid, width=20, state=DISABLED)
        self.cid_entry.pack(anchor=W, padx=(24, 0))

        fl.pack(side='left')

        fr = Frame(self.nand_frame)

        self.console_id_label = Label(fr, text='Console ID', state=DISABLED)
        self.console_id_label.pack(anchor=W)

        self.console_id = StringVar()
        self.console_id_entry = Entry(fr, textvariable=self.console_id, width=20, state=DISABLED)
        self.console_id_entry.pack(anchor=W)

        fr.pack(side='right')

        f2.pack(fill=X)

        # Third row
        f3 = Frame(self)

        self.start_button = Button(f3, text='开始', width=13, command=self.hiya, state=DISABLED)
        self.start_button.pack(side='left', padx=(0, 5))

        self.adv_button = Button(f3, text='高级', command=self.change_mode1, width=13)
        self.back_button = Button(f3, text='返回', command=self.change_mode, width=13)
        self.back1_button = Button(f3, text='返回', command=self.change_mode1, width=13)
        self.adv_button.pack(side='left', padx=(0, 0))

        self.exit_button = Button(f3, text='退出', command=root.destroy, width=13)
        self.exit_button.pack(side='left', padx=(5, 0))

        f3.pack(pady=(10, 20))

        self.folders = []
        self.files = []


    ################################################################################################
    def usealtdl(self):
        if self.altdl.get() == 1:
            if not askokcancel('警告', ('使用备用载点可能可以提高下载必要文件的速度，但这会给备用载点带来流量负担，确定选择吗？\n(提示: 如果默认载点下载失败，会自动切换备用载点重试，不太需要优先勾选此选项!)'), icon=WARNING):
                self.altdl.set(0)
    def usedevkp(self):
        if self.devkp.get() == 1:
            if not askokcancel('提示', ('勾选此选项将会在CFW中开启系统设置中的数据管理功能，如果你已经在NAND中开启了此功能，则不需要勾选此选项')):
                self.devkp.set(0)
    def change_mode(self):
        if (self.nand_mode):
            self.nand_frame.pack_forget()
            self.start_button.pack_forget()
            self.back_button.pack_forget()
            self.exit_button.pack_forget()
            if osfmount or _7z is not None:
                if fatcat is not None:
                    self.rb1.pack(anchor=W)
                if _7z is not None:
                    self.rb2.pack(anchor=W)
                if osfmount is not None:
                    self.rb3.pack(anchor=W)
                if (fatcat is not None) or (osfmount and _7z is not None):
                    self.setup_frame.pack(padx=10, pady=(0, 10), fill=X)
            self.checks_frame.pack(anchor=W)
            self.start_button.pack(side='left', padx=(0, 5))
            self.adv_button.pack(side='left', padx=(0, 0))
            self.exit_button.pack(side='left', padx=(5, 0))
            self.nand_mode = False
        else:
            if askokcancel('警告', ('你正要进入NAND操作模式, 请确认你知道自己在做什么, 继续吗?'), icon=WARNING):
                if (self.setup_select):
                    self.setup_frame.pack_forget()
                self.checks_frame.pack_forget()
                self.start_button.pack_forget()
                self.adv_button.pack_forget()
                self.exit_button.pack_forget()
                self.nand_frame.pack(padx=10, pady=(0, 10), fill=X)
                self.start_button.pack(side='left', padx=(0, 5))
                self.back_button.pack(side='left', padx=(0, 0))
                self.exit_button.pack(side='left', padx=(5, 0))
                self.nand_mode = True
    def change_mode1(self):
        if (self.adv_mode):
            if self.appgen.get() == 1:
                self.appgen.set(0)
            self.adv_frame.pack_forget()
            self.checks_frame1.pack_forget()
            self.start_button.pack_forget()
            self.back1_button.pack_forget()
            self.exit_button.pack_forget()
            self.bak_frame.pack(fill=X)
            if osfmount or _7z is not None:
                if fatcat is not None:
                    self.rb1.pack(anchor=W)
                if _7z is not None:
                    self.rb2.pack(anchor=W)
                if osfmount is not None:
                    self.rb3.pack(anchor=W)
                if (fatcat is not None) or (osfmount and _7z is not None):
                    self.setup_frame.pack(padx=10, pady=(0, 10), fill=X)
            self.checks_frame.pack(anchor=W)
            self.start_button.pack(side='left', padx=(0, 5))
            self.adv_button.pack(side='left', padx=(0, 0))
            self.exit_button.pack(side='left', padx=(5, 0))
            self.adv_mode = False
        else:
            if askokcancel('提示', ('高级模式提供了单独安装TWiLightMenu++等功能, 点击"确定"以进入')):
                if self.appgen.get() == 1:
                    self.appgen.set(0)
                self.bak_frame.pack_forget()
                if (self.setup_select):
                    self.setup_frame.pack_forget()
                self.checks_frame.pack_forget()
                self.start_button.pack_forget()
                self.adv_button.pack_forget()
                self.exit_button.pack_forget()
                self.adv_frame.pack(fill=X)
                self.checks_frame1.pack(anchor=W)
                self.start_button.pack(side='left', padx=(0, 5))
                self.back1_button.pack(side='left', padx=(0, 0))
                self.exit_button.pack(side='left', padx=(5, 0))
                self.adv_mode = True


    ################################################################################################
    def enable_entries(self, status):
        self.cid_label['state'] = (NORMAL if status else DISABLED)
        self.cid_entry['state'] = (NORMAL if status else DISABLED)
        self.console_id_label['state'] = (NORMAL if status else DISABLED)
        self.console_id_entry['state'] = (NORMAL if status else DISABLED)


    ################################################################################################
    def choose_nand(self):
        name = askopenfilename(filetypes=( ( 'nand.bin', '*.bin' ), ( 'DSi-1.mmc', '*.mmc' ) ))
        self.nand_file.set(name)

        self.nand_button['state'] = (NORMAL if name != '' else DISABLED)
        self.start_button['state'] = (NORMAL if name != '' else DISABLED)


    ################################################################################################
    def hiya(self):
        if self.setup_operation.get() == 2 or self.nand_operation.get() == 2:
            if windll.shell32.IsUserAnAdmin() == 0:
                root.withdraw()
                if self.nand_operation.get()  == 2:
                    showerror('错误', '此功能需要以管理员权限运行本工具')
                else:
                    showerror('错误', '使用OSFMount需要以管理员权限运行本工具')
                root.destroy()
                exit(1)

        if not self.nand_mode:
            if not self.adv_mode:
                showinfo('提示', '接下来请选择你用来安装自制系统的存储卡路径(或输出路径)\n为了避免 '
                    '启动错误 请确保目录下无任何文件')
                self.sd_path = askdirectory()

                # Exit if no path was selected
                if self.sd_path == '':
                    return

        # If adding a No$GBA footer, check if CID and ConsoleID values are OK
        elif self.nand_operation.get() == 1:
            cid = self.cid.get()
            console_id = self.console_id.get()

            # Check lengths
            if len(cid) != 32:
                showerror('错误', 'Bad eMMC CID')
                return

            elif len(console_id) != 16:
                showerror('错误', 'Bad Console ID')
                return

            # Parse strings to hex
            try:
                cid = bytearray.fromhex(cid)

            except ValueError:
                showerror('错误', 'Bad eMMC CID')
                return

            try:
                console_id = bytearray(reversed(bytearray.fromhex(console_id)))

            except ValueError:
                showerror('错误', 'Bad Console ID')
                return

        dialog = Toplevel(self)
        # Open as dialog (parent disabled)
        dialog.grab_set()
        dialog.title('状态')
        # Disable maximizing
        dialog.resizable(0, 0)

        frame = Frame(dialog, bd=2, relief=SUNKEN)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.log = ThreadSafeText(frame, bd=0, width=52, height=20,
            yscrollcommand=scrollbar.set)
        self.log.pack()

        scrollbar.config(command=self.log.yview)

        frame.pack()

        Button(dialog, text='关闭', command=dialog.destroy, width=16).pack(pady=10)

        # Center in window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        dialog.geometry('%dx%d+%d+%d' % (width, height, root.winfo_x() + (root.winfo_width() / 2) -
            (width / 2), root.winfo_y() + (root.winfo_height() / 2) - (height / 2)))

        # Check if we'll be adding a No$GBA footer
        if self.nand_mode and self.nand_operation.get() == 1:
            Thread(target=self.add_footer, args=(cid, console_id)).start()
        else:
            Thread(target=self.check_nand).start()


    ################################################################################################
    def check_nand(self):
        self.log.write('Checking NAND file...')

        # Read the NAND file
        try:
            with open(self.nand_file.get(), 'rb') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Read the footer's header :-)
                bstr = f.read(0x10)

                if bstr == b'DSi eMMC CID/CPU':
                    # Read the CID
                    bstr = f.read(0x10)
                    self.cid.set(bstr.hex().upper())
                    self.log.write('- eMMC CID: ' + self.cid.get())

                    # Read the console ID
                    bstr = f.read(8)
                    self.console_id.set(bytearray(reversed(bstr)).hex().upper())
                    self.log.write('- Console ID: ' + self.console_id.get())

                    # Check we are removing the No$GBA footer
                    if self.nand_mode:
                        if self.nand_operation.get() == 2:
                            Thread(target=self.decrypt_nand).start()
                        else:
                            Thread(target=self.remove_footer).start()
                            pass
                    else:
                        Thread(target=self.get_latest_hiyacfw).start()

                else:
                    self.log.write('ERROR: No$GBA footer not found')

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not open the file ' +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def get_latest_hiyacfw(self):
        # Try to use already downloaded HiyaCFW archive
        filename = 'HiyaCFW.7z'

        try:
            if path.isfile(filename):
                self.log.write('\nPreparing HiyaCFW...')

            else:
                self.log.write('\nDownloading latest HiyaCFW release...')

                with urlopen('https://github.com/RocketRobz/hiyaCFW/releases/latest/download/' +
                    filename) as src, open(filename, 'wb') as dst:
                    copyfileobj(src, dst)

            self.log.write('- Extracting HiyaCFW archive...')

            proc = Popen([ _7za, 'x', '-bso0', '-y', filename, 'for PC', 'for SDNAND SD card' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(filename)
                self.folders.append('for PC')
                self.folders.append('for SDNAND SD card')
                # Got to decrypt NAND if bootloader.nds is present
                Thread(target=self.decrypt_nand if path.isfile('bootloader.nds')
                    else self.extract_bios).start()

            else:
                self.log.write('ERROR: Extractor failed')

        except (URLError, IOError) as e:
            print(e)
            self.log.write('ERROR: Could not get HiyaCFW')

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)


    ################################################################################################
    def extract_bios(self):
        self.log.write('\nExtracting ARM7/ARM9 BIOS from NAND...')

        try:
            proc = Popen([ twltool, 'boot2', '--in', self.nand_file.get() ])

            ret_val = proc.wait()

            if ret_val == 0:
                # Hash arm7.bin
                sha1_hash = sha1()

                with open('arm7.bin', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- arm7.bin SHA1:\n  ' +
                    sha1_hash.digest().hex().upper())

                # Hash arm9.bin
                sha1_hash = sha1()

                with open('arm9.bin', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- arm9.bin SHA1:\n  ' +
                    sha1_hash.digest().hex().upper())

                self.files.append('arm7.bin')
                self.files.append('arm9.bin')

                Thread(target=self.patch_bios).start()

            else:
                self.log.write('ERROR: Extractor failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def patch_bios(self):
        self.log.write('\nPatching ARM7/ARM9 BIOS...')

        try:
            self.patcher(path.join('for PC', 'bootloader files', 'bootloader arm7 patch.ips'),
                'arm7.bin')

            self.patcher(path.join('for PC', 'bootloader files', 'bootloader arm9 patch.ips'),
                'arm9.bin')

            # Hash arm7.bin
            sha1_hash = sha1()

            with open('arm7.bin', 'rb') as f:
                sha1_hash.update(f.read())

            self.log.write('- Patched arm7.bin SHA1:\n  ' +
                sha1_hash.digest().hex().upper())

            # Hash arm9.bin
            sha1_hash = sha1()

            with open('arm9.bin', 'rb') as f:
                sha1_hash.update(f.read())

            self.log.write('- Patched arm9.bin SHA1:\n  ' +
                sha1_hash.digest().hex().upper())

            Thread(target=self.arm9_prepend).start()

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not patch BIOS')
            Thread(target=self.clean, args=(True,)).start()

        except Exception as e:
            print(e)
            self.log.write('ERROR: Invalid patch header')
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def arm9_prepend(self):
        self.log.write('\nPrepending data to ARM9 BIOS...')

        try:
            with open('arm9.bin', 'rb') as f:
                data = f.read()

            with open('arm9.bin', 'wb') as f:
                with open(path.join('for PC', 'bootloader files',
                    'bootloader arm9 append to start.bin'), 'rb') as pre:
                    f.write(pre.read())

                f.write(data)

            # Hash arm9.bin
            sha1_hash = sha1()

            with open('arm9.bin', 'rb') as f:
                sha1_hash.update(f.read())

            self.log.write('- Prepended arm9.bin SHA1:\n  ' +
                sha1_hash.digest().hex().upper())

            Thread(target=self.make_bootloader).start()

        except IOError as e:
            print(e)
            self.log.write('ERROR: Could not prepend data to ARM9 BIOS')
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def make_bootloader(self):
        self.log.write('\nGenerating new bootloader...')

        exe = (path.join('for PC', 'bootloader files', 'ndstool.exe') if sysname == 'Windows' else
            path.join(sysname, 'ndsblc'))

        try:
            proc = Popen([ exe, '-c', 'bootloader.nds', '-9', 'arm9.bin', '-7', 'arm7.bin', '-t',
                path.join('for PC', 'bootloader files', 'banner.bin'), '-h',
                path.join('for PC', 'bootloader files', 'header.bin') ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append('bootloader.nds')

                # Hash bootloader.nds
                sha1_hash = sha1()

                with open('bootloader.nds', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- bootloader.nds SHA1:\n  ' +
                    sha1_hash.digest().hex().upper())

                Thread(target=self.decrypt_nand).start()

            else:
                self.log.write('ERROR: Generator failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def decrypt_nand(self):
        self.log.write('\nDecrypting NAND...')

        try:
            proc = Popen([ twltool, 'nandcrypt', '--in', self.nand_file.get(), '--out',
                self.console_id.get() + '.img' ])

            ret_val = proc.wait()
            print("\n")

            if ret_val == 0:
                if not self.nand_mode:
                    self.files.append(self.console_id.get() + '.img')
                if not self.nand_operation.get() == 2:
                    Thread(target=self.extract_nand1 if (sysname == 'Windows' and _7z is not None)
                        else self.extract_nand).start()
                else:
                    Thread(target=self.mount_nand).start()
            else:
                self.log.write('ERROR: Decryptor failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def extract_nand1(self):
        self.log.write('\nExtracting files from NAND...')

        try:
            proc = Popen([ _7z, 'x', '-bso0', '-y', self.console_id.get() + '.img', '0.fat' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append('0.fat')

                proc = Popen([ _7z, 'x', '-bso0', '-y', '-o' + self.sd_path, '0.fat' ])

                ret_val = proc.wait()

                if ret_val == 0:
                    Thread(target=self.get_launcher).start()

                else:
                    self.log.write('ERROR: Extractor failed, please update 7-Zip')

                    if path.exists(fatcat):
                        self.log.write('\nTrying with fatcat...')
                        Thread(target=self.extract_nand).start()

                    else:
                        Thread(target=self.clean, args=(True,)).start()

            else:
                self.log.write('ERROR: Extractor failed')

                if path.exists(fatcat):
                    self.log.write('\nTrying with fatcat...')
                    Thread(target=self.extract_nand).start()

                else:
                    Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)

            if path.exists(fatcat):
                self.log.write('\nTrying with fatcat...')
                Thread(target=self.extract_nand).start()

            else:
                Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def mount_nand(self):
        self.log.write('\n挂载解密的NAND镜像中...')

        try:
            exe = osfmount

            cmd = [ osfmount, '-a', '-t', 'file', '-f', self.console_id.get() + '.img', '-m',
                '#:', '-o', 'ro,rem' ]

            if self.nand_mode:
                cmd[-1] = 'rw,rem'

            proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

            outs, errs = proc.communicate()

            if proc.returncode == 0:
                self.mounted = search(r'[a-zA-Z]:\s', outs.decode('utf-8')).group(0).strip()
                self.log.write('- 挂载到驱动器 ' + self.mounted)

            else:
                self.log.write('错误: 挂载失败')
                Thread(target=self.clean, args=(True,)).start()
                return

            Thread(target=self.unlaunch_proc).start()

        except OSError as e:
            print(e)
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def extract_nand(self):
        self.log.write('\nExtracting files from NAND...')

        try:
            # DSi first partition offset: 0010EE00h
            proc = Popen([ fatcat, '-O', '1109504', '-x', self.sd_path,
                self.console_id.get() + '.img' ])

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.get_launcher).start()

            else:
                self.log.write('ERROR: Extractor failed')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def get_launcher(self):
        app = self.detect_region()

        # Stop if no supported region was found
        if not app:
            Thread(target=self.clean, args=(True,)).start()
            return

        # Delete contents of the launcher folder as it will be replaced by the one from HiyaCFW
        launcher_folder = path.join(self.sd_path, 'title', '00030017', app, 'content')

        # Walk through all files in the launcher content folder
        for file in listdir(launcher_folder):
            file = path.join(launcher_folder, file)

            if _7z is not None:
                chmod(file, 438)
            remove(file)

        # Try to use already downloaded launcher
        try:
            if not path.isfile(self.launcher_region):
                self.log.write('\n正在下载 ' + self.launcher_region + ' Launcher...')

                with urlopen('https://raw.githubusercontent.com'
                    '/R-YaTian/HHF-Toolkit/HiyaCFW-Helper-R3/launchers/' +
                    self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                    copyfileobj(src, dst)

            self.log.write('- 正在解压Launcher...')

            # Set launcher filename according to the region
            if self.launcher_region in ('CHN', 'KOR'):
                launcher_app = '00000000.app'
            elif self.launcher_region in ('USA-dev'):
                launcher_app = '7412e50d.app'
            else:
                launcher_app = '00000002.app'

            # Prepare decryption params
            params = [ _7za, 'x', '-bso0', '-y', '-p' + app.lower(), self.launcher_region,
                launcher_app ]

            if launcher_app == '7412e50d.app':
                params.append('title.tmd')

            proc = Popen(params)

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(launcher_app)

                if launcher_app == '7412e50d.app':
                    self.files.append('title.tmd')

                # Hash launcher app
                sha1_hash = sha1()

                with open(launcher_app, 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- Patched Launcher SHA1:\n  ' +
                    sha1_hash.digest().hex().upper())

                Thread(target=self.install_hiyacfw, args=(launcher_app, launcher_folder)).start()

            else:
                self.log.write('错误: 解压失败')
                Thread(target=self.clean, args=(True,)).start()

        except IOError as e:
            print(e)
            self.log.write('错误: 无法下载 ' + self.launcher_region + ' Launcher')
            Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def install_hiyacfw(self, launcher_app, launcher_folder):
        self.log.write('\nCopying HiyaCFW files...')

        # Reset copied files cache
        _path_created.clear()

        copy_tree('for SDNAND SD card', self.sd_path, update=1)
        copyfile('bootloader.nds', path.join(self.sd_path, 'hiya', 'bootloader.nds'))
        copyfile(launcher_app, path.join(launcher_folder, launcher_app))

        if launcher_app == '00000000.app':
            copyfile('title.tmd', path.join(launcher_folder, 'title.tmd'))

        Thread(target=self.get_latest_twilight if self.twilight.get() == 1 else self.clean).start()


    ################################################################################################
    def get_latest_twilight(self):
        # Try to use already downloaded TWiLight Menu++ archive
        filename = 'TWiLightMenu.7z'

        try:
            if not path.isfile(filename):
                self.log.write('\nDownloading latest TWiLight Menu++ release...')

                with urlopen('https://github.com/DS-Homebrew/TWiLightMenu/releases/latest/download/' +
                    filename) as src, open(filename, 'wb') as dst:
                    copyfileobj(src, dst)

            self.log.write('- Extracting ' + filename[:-3] + ' archive...')

            proc = Popen([ _7za, 'x', '-bso0', '-y', filename, '_nds', 'DSi - CFW users',
                'DSi&3DS - SD card users', 'roms' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(filename)
                self.folders.append('DSi - CFW users')
                self.folders.append('_nds')
                self.folders.append('DSi&3DS - SD card users')
                self.folders.append('roms')
                Thread(target=self.install_twilight, args=(filename[:-3],)).start()

            else:
                self.log.write('ERROR: Extractor failed')
                Thread(target=self.clean, args=(True,)).start()

        except (URLError, IOError) as e:
            print(e)
            self.log.write('ERROR: Could not get TWiLight Menu++')
            Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('ERROR: Could not execute ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def install_twilight(self, name):
        self.log.write('\nCopying ' + name + ' files...')

        copy_tree(path.join('DSi - CFW users', 'SDNAND root'), self.sd_path, update=1)
        copy_tree('_nds', path.join(self.sd_path, '_nds'))
        copy_tree('DSi&3DS - SD card users', self.sd_path, update=1)
        copy_tree('roms', path.join(self.sd_path, 'roms'))

        Thread(target=self.clean).start()


    ################################################################################################
    def clean(self, err=False):
        self.log.write('\n清理中...')

        while len(self.folders) > 0:
            rmtree(self.folders.pop(), ignore_errors=True)

        while len(self.files) > 0:
            try:
                remove(self.files.pop())

            except:
                pass

        if err:
            if self.nand_mode:
                try:
                    remove(self.console_id.get() + '.img')
                except:
                    pass
            self.log.write('操作过程发生错误, 已终止')
            return

        if self.nand_mode:
            file = self.console_id.get() + self.suffix + '.bin'
            try:
                rename(self.console_id.get() + '.img', file)
                self.log.write('\n完成!\n修改后的NAND保存为\n' + file)
            except FileExistsError:
                remove(self.console_id.get() + '.img')
                self.log.write('\n操作终止!\n目标文件已存在于程序运行目录下, 未覆盖')
            return

        self.log.write('完成!\n弹出你的存储卡并插回到机器中')


    ################################################################################################
    def patcher(self, patchpath, filepath):
        patch_size = path.getsize(patchpath)

        patchfile = open(patchpath, 'rb')

        if patchfile.read(5) != b'PATCH':
            patchfile.close()
            raise Exception()

        target = open(filepath, 'r+b')

        # Read First Record
        r = patchfile.read(3)

        while patchfile.tell() not in [ patch_size, patch_size - 3 ]:
            # Unpack 3-byte pointers.
            offset = self.unpack_int(r)
            # Read size of data chunk
            r = patchfile.read(2)
            size = self.unpack_int(r)

            if size == 0:  # RLE Record
                r = patchfile.read(2)
                rle_size = self.unpack_int(r)
                data = patchfile.read(1) * rle_size

            else:
                data = patchfile.read(size)

            # Write to file
            target.seek(offset)
            target.write(data)
            # Read Next Record
            r = patchfile.read(3)

        if patch_size - 3 == patchfile.tell():
            trim_size = self.unpack_int(patchfile.read(3))
            target.truncate(trim_size)

        # Cleanup
        target.close()
        patchfile.close()


    ################################################################################################
    def unpack_int(self, bstr):
        # Read an n-byte big-endian integer from a byte string
        ( ret_val, ) = unpack_from('>I', b'\x00' * (4 - len(bstr)) + bstr)
        return ret_val


    ################################################################################################
    def detect_region(self):
        REGION_CODES = {
            '484e4143': 'CHN',
            '484e4145': 'USA',
            '484e414a': 'JAP',
            '484e414b': 'KOR',
            '484e4150': 'EUR',
            '484e4155': 'AUS'
        }
        REGION_CODES_DEV = {
            '484e4145': 'USA-dev',
        }
        base = self.mounted if self.nand_mode else self.sd_path
        # Autodetect console region
        try:
            for app in listdir(path.join(base, 'title', '00030017')):
                for file in listdir(path.join(base, 'title', '00030017', app, 'content')):
                    if file.endswith('.app'):
                        try:
                            if file.startswith("0000000"):
                                self.log.write('- 检测到 ' + REGION_CODES[app.lower()] +
                                     ' Launcher')
                                if not self.nand_mode:
                                    self.launcher_region = REGION_CODES[app.lower()]
                            else:
                                if self.nand_mode:
                                    self.log.write('- 检测到 ' + REGION_CODES[app.lower()] +
                                         '-dev Launcher')
                                else:
                                    self.log.write('- 检测到 ' + REGION_CODES_DEV[app.lower()] +
                                         ' Launcher')
                                    self.launcher_region = REGION_CODES_DEV[app.lower()]
                            return app

                        except KeyError:
                            self.log.write('错误: 在NAND中找不到受支持的Launcher')
                            return False

            self.log.write('错误: 无法检测系统区域')

        except OSError as e:
            self.log.write('错误: ' + e.strerror + ': ' + e.filename)

        return False


    ################################################################################################
    def unlaunch_proc(self):
        self.log.write('\n检查unlaunch状态中...')

        app = self.detect_region()

        if not app:
            Thread(target=self.unmount_nand1).start()
            return

        tmd = path.join(self.mounted, 'title', '00030017', app, 'content', 'title.tmd')

        tmd_size = path.getsize(tmd)

        if tmd_size == 520:
            self.log.write('- 未安装,下载中...')

            try:
                if not path.exists('unlaunch.zip'):
                    try:
                        filename = urlretrieve('http://problemkaputt.de/unlaunch.zip')[0]
                    except:
                        filename = urlretrieve('http://spblog.tk/somefiles/unlaunch.zip')[0]
                else:
                    filename = 'unlaunch.zip'

                exe = path.join(sysname, '7za')

                proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'UNLAUNCH.DSI' ])

                ret_val = proc.wait()

                if ret_val == 0:
                    self.files.append(filename)
                    self.files.append('UNLAUNCH.DSI')

                    self.log.write('- 正在安装unlaunch...')

                    self.suffix = '-unlaunch'

                    with open(tmd, 'ab') as f:
                        with open('UNLAUNCH.DSI', 'rb') as unl:
                            f.write(unl.read())

                    dekp = path.join(self.mounted, 'sys', 'dev.kp')
                    if not path.exists(dekp):
                        with open(dekp, 'wb+') as f:
                            f.seek(0,0)
                            f.read(0x04)
                            f.write(b'DUMMY')
                            f.close()

                    # Set files as read-only
                    for file in listdir(path.join(self.mounted, 'title', '00030017', app,
                        'content')):
                        file = path.join(self.mounted, 'title', '00030017', app, 'content', file)
                        chmod(file, 292)

                else:
                    self.log.write('错误: 解压失败')
                    Thread(target=self.unmount_nand1).start()
                    return

            except IOError as e:
                print(e)
                self.log.write('错误: 无法下载 unlaunch')
                Thread(target=self.unmount_nand1).start()
                return

            except OSError as e:
                print(e)
                self.log.write('错误: 无法运行 ' + exe)
                Thread(target=self.unmount_nand1).start()
                return

        else:
            self.log.write('- 已安装, 卸载中...')

            self.suffix = '-no-unlaunch'

            # Set files as read-write
            for file in listdir(path.join(self.mounted, 'title', '00030017', app, 'content')):
                file = path.join(self.mounted, 'title', '00030017', app, 'content', file)
                chmod(file, 438)

            with open(tmd, 'r+b') as f:
                f.truncate(520)

            dekp = path.join(self.mounted, 'sys', 'dev.kp')
            if not path.exists(dekp):
                with open(dekp, 'wb+') as f:
                    f.seek(0,0)
                    f.read(0x04)
                    f.write(b'DUMMY')
                    f.close()

        Thread(target=self.unmount_nand).start()


    ################################################################################################
    def unmount_nand(self):
        self.log.write('\n正在卸载NAND...')

        try:
            exe = osfmount
            proc = Popen([ osfmount, '-D', '-m', self.mounted ])

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.encrypt_nand).start()

            else:
                self.log.write('错误: 卸载失败')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()
    def unmount_nand1(self):
        self.log.write('\n正在卸载NAND...')

        try:
            exe = osfmount
            proc = Popen([ osfmount, '-D', '-m', self.mounted ])

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.clean, args=(True,)).start()

            else:
                self.log.write('错误: 卸载失败')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def encrypt_nand(self):
        self.log.write('\n正在重加密NAND...')

        try:
            proc = Popen([ twltool, 'nandcrypt', '--in', self.console_id.get() + '.img' ])

            ret_val = proc.wait()
            print("\n")

            if ret_val == 0:
                Thread(target=self.clean).start()

            else:
                self.log.write('错误: 加密失败')
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            print(e)
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def remove_footer(self):
        self.log.write('\n正在移除No$GBA footer...')

        file = self.console_id.get() + '-no-footer.bin'

        try:
            copyfile(self.nand_file.get(), file)

            # Back-up footer info
            with open(self.console_id.get() + '-info.txt', 'w') as f:
                f.write('eMMC CID: ' + self.cid.get() + '\r\n')
                f.write('Console ID: ' + self.console_id.get() + '\r\n')

            with open(file, 'r+b') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Remove footer
                f.truncate()

            self.log.write('\n完成!\n修改后的NAND已保存为\n' + file +
                '\nfooter信息已保存到 ' + self.console_id.get() + '-info.txt')

        except IOError as e:
            print(e)
            self.log.write('错误: 无法打开 ' +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def add_footer(self, cid, console_id):
        self.log.write('正在添加No$GBA footer...')

        file = self.console_id.get() + '-footer.bin'

        try:
            copyfile(self.nand_file.get(), file)

            with open(file, 'r+b') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Read the footer's header :-)
                bstr = f.read(0x10)

                # Check if it already has a footer
                if bstr == b'DSi eMMC CID/CPU':
                    self.log.write('错误: 文件中已存在 No$GBA footer')
                    f.close()
                    remove(file)
                    return

                # Go to the end of file
                f.seek(0, 2)
                # Write footer
                f.write(b'DSi eMMC CID/CPU')
                f.write(cid)
                f.write(console_id)
                f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

            self.log.write('\n完成!\n修改后的NAND已保存为\n' + file)

        except IOError as e:
            print(e)
            self.log.write('错误: 无法打开 ' +
                path.basename(self.nand_file.get()))


####################################################################################################
# Entry point

print('HiyaCFW Helper启动中...')

sysname = system()

print('GUI初始化中...')

root = Tk()

fatcat = path.join(sysname, 'fatcat')
_7za = path.join(sysname, '7za')
twltool = path.join(sysname, 'twltool')
osfmount  = None
_7z = None

if sysname == 'Windows':
    fatcat += '.exe'
    _7za += '.exe'
    twltool += '.exe'
    try:
        with OpenKey(HKEY_LOCAL_MACHINE,
            'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\OSFMount_is1') as hkey:
            osfmount = path.join(QueryValueEx(hkey, 'InstallLocation')[0], 'OSFMount.com')
            if path.exists(osfmount):
                print('对应版本、体系结构的OSFMount已安装')
    except:
        osfmount  = None

    try:
        with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip', 0, KEY_READ | KEY_WOW64_64KEY) as hkey:
            _7z = path.join(QueryValueEx(hkey, 'Path')[0], '7z.exe')
            if not path.exists(_7z):
                raise WindowsError
            print('7-Zip已安装')
    except WindowsError:
        try:
            with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip') as hkey:
                _7z = path.join(QueryValueEx(hkey, 'Path')[0], '7z.exe')
                if not path.exists(_7z):
                    raise WindowsError
                print('7-Zip已安装')
        except WindowsError:
            _7z = None

if not path.exists(fatcat):
    if osfmount or _7z is not None:
        fatcat = None
    else:
        root.withdraw()
        showerror('错误', '找不到Fatcat, 请确认此程序位于本工具目录的"' + sysname + '"文件夹中')
        root.destroy()
        exit(1)

root.title('HiyaCFW Helper V3.6.0R(BY天涯)')
# Disable maximizing
root.resizable(0, 0)
# Center in window
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
app = Application(master=root)
app.mainloop()
