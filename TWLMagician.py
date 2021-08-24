#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TWLMagician
# Version 0.6.6
# Author: R-YaTian
# Original "HiyaCFW-Helper" Author: mondul <mondul@huyzona.com>

from tkinter import (Tk, Frame, LabelFrame, PhotoImage, Button, Entry, Checkbutton, Radiobutton,
    Label, Toplevel, Scrollbar, Text, StringVar, IntVar, RIGHT, W, X, Y, DISABLED, NORMAL, SUNKEN,
    END)
from tkinter.messagebox import askokcancel, showerror, showinfo, WARNING
from tkinter.filedialog import askopenfilename, askdirectory
from os import path, remove, chmod, listdir, rename, environ, mkdir
from sys import exit, stdout
from threading import Thread
from queue import Queue, Empty
from hashlib import sha1
from urllib.request import urlopen
from urllib.error import URLError
from subprocess import Popen, PIPE
from struct import unpack_from
from shutil import rmtree, copyfile, copyfileobj
from distutils.dir_util import copy_tree, _path_created
from re import search
from appgen import agen
from tooltip import ToolTip
from inspect import isclass
from datetime import datetime
from time import sleep
from binascii import hexlify, unhexlify
from langs import lang_init
import ctypes, platform, ssl
ssl._create_default_https_context = ssl._create_unverified_context

#TimeLog-Print
ntime_tmp = None
def printl(*objects, sep=' ', end='\n', file=stdout, flush=False, fixn=False):
    global ntime_tmp
    clog = open('Console.log', 'a')
    try:
        ntime = datetime.now().strftime('%F %T')
    except:
        ntime = datetime.now().strftime('%c')
    if ntime_tmp != ntime or ntime_tmp == None:
        if fixn == False:
            print('[' + ntime + ']')
        else:
            print('\n[' + ntime + ']')
        clog.write('[' + ntime + ']\n')
    print(*objects, sep=' ', end='\n', file=stdout, flush=False)
    clog.write(*objects)
    clog.write('\n')
    ntime_tmp = ntime
    clog.close()
#Thread-Control
def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("Invalid Thread ID")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc Failed")
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


####################################################################################################
# Thread-safe text class

class ThreadSafeText(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.now_time_tmp = None
        self.queue = Queue()
        self.update_me()

    def write(self, line):
        self.wlog = open('Window.log', 'a')
        try:
            now_time = datetime.now().strftime('%F %T')
        except:
            now_time = datetime.now().strftime('%c')
        if self.now_time_tmp != now_time or self.now_time_tmp == None:
            self.queue.put('[' + now_time + ']')
            self.wlog.write('[' + now_time + ']\n')
        self.queue.put(line)
        self.wlog.write(line + '\n')
        self.now_time_tmp = now_time
        self.wlog.close()

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
        self.transfer_mode = False
        self.setup_select = False
        self.have_hiya = False
        self.is_tds = False
        self.have_menu = False
        self.finish = False

        self.image_file = StringVar()

        # First row
        f1 = Frame(self) 

        self.bak_frame=LabelFrame(f1, text=_('含有No$GBA footer的NAND备份文件'), padx=10, pady=10)

        self.nand_button = Button(self.bak_frame, image=nand_icon, command=self.change_mode, state=DISABLED)

        self.nand_button.pack(side='left')

        self.nand_file = StringVar()
        self.nandfile = Entry(self.bak_frame, textvariable=self.nand_file, state='readonly', width=40)
        self.nandfile.pack(side='left')

        self.chb = Button(self.bak_frame, text='...', command=self.choose_nand)
        self.chb.pack(side='left')

        self.bak_frame.pack(fill=X)

        self.adv_frame=LabelFrame(f1, text=_('存储卡根目录'), padx=10, pady=10)

        self.transfer_button = Button(self.adv_frame, image=nand_icon, command=self.change_mode2, state=DISABLED)

        self.transfer_button.pack(side='left')

        self.sdp = StringVar()
        self.sdpath = Entry(self.adv_frame, textvariable=self.sdp, state='readonly', width=40)
        self.sdpath.pack(side='left')

        self.chb1 = Button(self.adv_frame, text='...', command=self.choose_sdp)
        self.chb1.pack(side='left')

        f1.pack(padx=10, pady=10, fill=X)

        # Second row
        f2 = Frame(self)

        self.setup_frame = LabelFrame(f2, text=_('NAND解压选项'), padx=10, pady=10)

        self.setup_operation = IntVar()

        if fatcat is None:
            if _7z is not None:
                self.setup_operation.set(1)
            elif osfmount is not None:
                self.setup_operation.set(2)
        else:
            self.setup_operation.set(0)

        self.rb1 = Radiobutton(self.setup_frame, text=_('Fatcat(默认)'), variable=self.setup_operation, value=0)
        self.rb2 = Radiobutton(self.setup_frame, text='7-Zip', variable=self.setup_operation, value=1)
        self.rb3 = Radiobutton(self.setup_frame, text=_('OSFMount(需要管理员权限)'), variable=self.setup_operation, value=2)

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
            text=_('同时安装TWiLightMenu++'), variable=self.twilight)

        twl_chk.pack(padx=10, anchor=W)

        self.appgen = IntVar()
        self.appgen.set(0)

        ag_chk = Checkbutton(self.checks_frame, text=_('使用AppGen'), variable=self.appgen)

        ag_chk.pack(padx=10, anchor=W)
        ToolTip(ag_chk, msg=_('提取Nand备份中的DSiWare软件并复制到\nroms/dsiware'))

        self.devkp = IntVar()
        self.devkp.set(0)

        dkp_chk = Checkbutton(self.checks_frame, text=_('启用系统设置-数据管理功能'), variable=self.devkp)

        dkp_chk.pack(padx=10, anchor=W)
        ToolTip(dkp_chk, msg=_('勾选此选项将会在CFW中开启系统设置中的数据管理功能，如果已经在NAND中开启了此功能，则不需要勾选此选项'))

        self.photo = IntVar()
        self.photo.set(0)

        photo_chk = Checkbutton(self.checks_frame, text=_('提取相册分区'), variable=self.photo)

        photo_chk.pack(padx=10, anchor=W)
        ToolTip(photo_chk, msg=_('提取Nand备份中的相册分区文件到存储卡中，此操作会占用一定的存储卡空间(取决于相片数量，最多可达32MB左右)'))

        self.altdl = IntVar()
        self.altdl.set(0)

        if loc == 'zh_CN':
            adl_chk = Checkbutton(self.checks_frame, text='优先使用备用载点', variable=self.altdl)
            adl_chk.pack(padx=10, anchor=W)
            ToolTip(adl_chk, msg='使用备用载点可能可以提高下载必要文件的速度')

        self.checks_frame.pack(fill=X)

        self.checks_frame1 = Frame(f2)

        self.ag1_chk = Checkbutton(self.checks_frame1, text=_('使用AppGen'), variable=self.appgen, state=DISABLED)

        self.ag1_chk.pack(padx=10, anchor=W)
        ToolTip(self.ag1_chk, msg=_('提取SDNand中的DSiWare软件并复制到\nroms/dsiware'))

        self.updatehiya = IntVar()
        self.updatehiya.set(0)

        self.uh_chk = Checkbutton(self.checks_frame1, text=_('更新hiyaCFW'), variable=self.updatehiya, state=DISABLED)

        self.uh_chk.pack(padx=10, anchor=W)

        self.dkp1_chk = Checkbutton(self.checks_frame1, text=_('启用系统设置-数据管理功能'), variable=self.devkp, state=DISABLED)

        self.dkp1_chk.pack(padx=10, anchor=W)
        ToolTip(self.dkp1_chk, msg=_('勾选此选项将会在CFW中开启系统设置中的数据管理功能，如果已经在NAND中开启了此功能，则不需要勾选此选项'))

        self.tftt = IntVar()
        self.tftt.set(0)

        self.tftt_chk = Checkbutton(self.checks_frame1, text=_('同时安装TFTT'), variable=self.tftt, state=DISABLED)

        self.tftt_chk.pack(padx=10, anchor=W)
        ToolTip(self.tftt_chk, msg=_('在3DS系列机器上安装TWLFontTransferTool(基于GodMode9脚本)'))

        if loc == 'zh_CN':
            adl1_chk = Checkbutton(self.checks_frame1, text='优先使用备用载点', variable=self.altdl)
            adl1_chk.pack(padx=10, anchor=W)
            ToolTip(adl1_chk, msg='使用备用载点可能可以提高下载必要文件的速度')

        self.checks_frame2 = Frame(f2)

        self.dkp2_chk = Checkbutton(self.checks_frame2, text=_('启用系统设置-数据管理功能'), variable=self.devkp)

        self.dkp2_chk.pack(padx=10, anchor=W)
        ToolTip(self.dkp2_chk, msg=_('勾选此选项将会在CFW中开启系统设置中的数据管理功能，如果已经在NAND中开启了此功能，则不需要勾选此选项'))

        self.tmfh = IntVar()
        self.tmfh.set(0)

        self.tmfh_chk = Checkbutton(self.checks_frame2, text=_('同时安装TMFH'), variable=self.tmfh)

        self.tmfh_chk.pack(padx=10, anchor=W)

        self.updatemenu = IntVar()
        self.updatemenu.set(0)

        self.um_chk = Checkbutton(self.checks_frame2, text=_('安装或更新TWiLightMenu++'), variable=self.updatemenu, state=DISABLED)

        self.um_chk.pack(padx=10, anchor=W)

        if loc == 'zh_CN':
            adl2_chk = Checkbutton(self.checks_frame2, text='优先使用备用载点', variable=self.altdl, state=DISABLED)
            adl2_chk.pack(padx=10, anchor=W)
            ToolTip(adl2_chk, msg='使用备用载点可能可以提高下载必要文件的速度')

        # NAND operation frame
        self.nand_frame = LabelFrame(f2, text=_('NAND操作选项'), padx=10, pady=10)

        self.nand_operation = IntVar()
        self.nand_operation.set(0)

        rb0 = Radiobutton(self.nand_frame, text=_('安装或卸载最新版本的unlaunch'),
            variable=self.nand_operation, value=2,
            command=lambda: self.enable_entries(False))
        if osfmount is not None:
            rb0.pack(anchor=W)
        Radiobutton(self.nand_frame, text=_('移除 No$GBA footer'), variable=self.nand_operation,
            value=0, command=lambda: self.enable_entries(False)).pack(anchor=W)

        Radiobutton(self.nand_frame, text=_('添加 No$GBA footer'), variable=self.nand_operation,
            value=1, command=lambda: self.enable_entries(True)).pack(anchor=W)

        fl = Frame(self.nand_frame)

        self.cid_label = Label(fl, text='eMMC CID', state=DISABLED)
        self.cid_label.pack(anchor=W, padx=(24, 0))

        self.cid = StringVar()
        self.cid_entry = Entry(fl, textvariable=self.cid, width=35, state=DISABLED)
        self.cid_entry.pack(anchor=W, padx=(24, 0))

        fl.pack(anchor=W)

        fr = Frame(self.nand_frame)

        self.console_id_label = Label(fr, text='Console ID', state=DISABLED)
        self.console_id_label.pack(anchor=W, padx=(24, 0))

        self.console_id = StringVar()
        self.console_id_entry = Entry(fr, textvariable=self.console_id, width=35, state=DISABLED)
        self.console_id_entry.pack(anchor=W, padx=(24, 0))

        fr.pack(anchor=W)

        f2.pack(fill=X)

        # Third row
        f3 = Frame(self)

        self.start_button = Button(f3, text=_('开始'), width=13, command=self.start_point, state=DISABLED)
        self.start_button.pack(side='left', padx=(0, 5))

        self.adv_button = Button(f3, text=_('高级'), command=self.change_mode1, width=13)
        self.back_button = Button(f3, text=_('返回'), command=self.change_mode, width=13)
        self.back1_button = Button(f3, text=_('返回'), command=self.change_mode1, width=13)
        self.back2_button = Button(f3, text=_('返回'), command=self.change_mode2, width=13)
        self.adv_button.pack(side='left', padx=(0, 0))
        ToolTip(self.adv_button, msg=_('高级模式提供了单独安装TWiLightMenu++等功能'))

        self.exit_button = Button(f3, text=_('退出'), command=root.destroy, width=13)
        self.exit_button.pack(side='left', padx=(5, 0))

        f3.pack(pady=(10, 20))

        self.folders = []
        self.files = []


    ################################################################################################
    def change_mode(self):
        if (self.nand_mode):
            self.nand_operation.set(0)
            self.enable_entries(False)
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
            if askokcancel(_('警告'), (_('你正要进入NAND操作模式, 请确认你知道自己在做什么, 继续吗?')), icon=WARNING):
                self.have_hiya = False
                self.is_tds = False
                self.have_menu = False
                if (self.setup_select):
                    self.setup_frame.pack_forget()
                self.setup_operation.set(0)
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
            self.transfer_button['state'] = DISABLED
            self.have_menu = False
            self.is_tds = False
            self.have_hiya = False
            if self.tftt.get() == 1:
                self.tftt.set(0)
            if self.appgen.get() == 1:
                self.appgen.set(0)
            if self.devkp.get() == 1:
                self.devkp.set(0)
            if self.updatehiya.get() == 1:
                self.updatehiya.set(0)
            if self.sdp.get() != '':
                self.sdp.set('')
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
            self.start_button['state'] = DISABLED
            self.nand_button['state'] = DISABLED
            self.start_button.pack(side='left', padx=(0, 5))
            self.adv_button.pack(side='left', padx=(0, 0))
            self.exit_button.pack(side='left', padx=(5, 0))
            self.adv_mode = False
        else:
            self.have_menu = False
            self.is_tds = False
            self.have_hiya = False
            if self.tftt.get() == 1:
                self.tftt.set(0)
            if self.appgen.get() == 1:
                self.appgen.set(0)
            if self.devkp.get() == 1:
                self.devkp.set(0)
            if self.updatehiya.get() == 1:
                self.updatehiya.set(0)
            if self.nand_file.get() != '':
                self.nand_file.set('')
            self.bak_frame.pack_forget()
            if (self.setup_select):
                self.setup_frame.pack_forget()
            self.checks_frame.pack_forget()
            self.start_button.pack_forget()
            self.adv_button.pack_forget()
            self.exit_button.pack_forget()
            self.adv_frame.pack(fill=X)
            self.checks_frame1.pack(anchor=W)
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.tftt_chk['state'] = DISABLED
            self.start_button['state'] = DISABLED
            self.start_button.pack(side='left', padx=(0, 5))
            self.back1_button.pack(side='left', padx=(0, 0))
            self.exit_button.pack(side='left', padx=(5, 0))
            self.adv_mode = True
    def change_mode2(self):
        if (self.transfer_mode):
            if self.updatehiya.get() == 1:
                self.updatehiya.set(0)
            if self.updatemenu.get() == 1:
                self.updatemenu.set(0)
            if self.tmfh.get() == 1:
                self.tmfh.set(0)
            self.start_button.pack_forget()
            self.back2_button.pack_forget()
            self.exit_button.pack_forget()
            self.checks_frame2.pack_forget()
            self.checks_frame1.pack(anchor=W)
            self.start_button.pack(side='left', padx=(0, 5))
            self.back1_button.pack(side='left', padx=(0, 0))
            self.exit_button.pack(side='left', padx=(5, 0))
            self.chb1['state'] = NORMAL
            self.transfer_mode = False
            self.adv_mode = True
        else:
            self.chb1['state'] = DISABLED
            if self.updatehiya.get() == 1:
                self.updatehiya.set(0)
            if self.updatemenu.get() == 1:
                self.updatemenu.set(0)
            if self.tmfh.get() == 1:
                self.tmfh.set(0)
            self.start_button.pack_forget()
            self.back1_button.pack_forget()
            self.exit_button.pack_forget()
            self.checks_frame1.pack_forget()
            self.checks_frame2.pack(anchor=W)
            self.start_button.pack(side='left', padx=(0, 5))
            self.back2_button.pack(side='left', padx=(0, 0))
            self.exit_button.pack(side='left', padx=(5, 0))
            self.transfer_mode = True
            self.adv_mode = False


    ################################################################################################
    def enable_entries(self, status):
        self.cid_label['state'] = (NORMAL if status else DISABLED)
        self.cid_entry['state'] = (NORMAL if status else DISABLED)
        self.console_id_label['state'] = (NORMAL if status else DISABLED)
        self.console_id_entry['state'] = (NORMAL if status else DISABLED)
    def check_console(self, spath):
        tmenu = path.join(spath, '_nds', 'TWiLightMenu', 'main.srldr')
        if path.exists(tmenu):
            self.have_menu = True
        tds = path.join(spath, 'Nintendo 3DS')
        tds1 = path.join(spath, 'boot.firm')
        if path.exists(tds) or path.exists(tds1):
            self.is_tds = True
        else:
            hiyad = path.join(spath, 'hiya.dsi')
            hiyab = path.join(spath, 'hiya', 'bootloader.nds')
            hiyas = path.join(spath, 'sys', 'HWINFO_S.dat')
            if path.exists(hiyad) or path.exists(hiyab) or path.exists(hiyas):
                self.have_hiya = True
    def make_dekp(self, dpath):
        dekp = path.join(dpath, 'sys', 'dev.kp')
        if not path.exists(dekp):
            with open(dekp, 'wb+') as f:
                f.seek(0,0)
                f.write(b'DUMMY')
                f.close()
            self.log.write(_('"系统设置-数据管理"功能启用成功'))


    ################################################################################################
    def choose_sdp(self):
        self.have_hiya = False
        self.is_tds = False
        self.have_menu = False
        showinfo(_('提示'), _('请选择机器的存储卡根目录'))
        self.sd_path1 = askdirectory(title='')
        self.sdp.set(self.sd_path1)
        if self.tftt.get() == 1:
            self.tftt.set(0)
        if self.appgen.get() == 1:
            self.appgen.set(0)
        if self.devkp.get() == 1:
            self.devkp.set(0)
        if self.updatehiya.get() == 1:
            self.updatehiya.set(0)
        self.start_button['state'] = (NORMAL if self.sd_path1 != '' else DISABLED)
        if self.sd_path1 == '':
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.tftt_chk['state'] = DISABLED
            self.transfer_button['state'] = DISABLED
            return
        self.check_console(self.sd_path1)
        if self.is_tds == True:
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.tftt_chk['state'] = NORMAL
            self.transfer_button['state'] = DISABLED
        elif self.have_hiya == True:
            self.uh_chk['state'] = NORMAL
            self.dkp1_chk['state'] = NORMAL
            self.ag1_chk['state'] = (DISABLED if self.have_menu == True else NORMAL)
            self.tftt_chk['state'] = DISABLED
            self.transfer_button['state'] = NORMAL
        elif self.have_menu == True:
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.tftt_chk['state'] = DISABLED
            self.transfer_button['state'] = DISABLED
        else:
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.tftt_chk['state'] = DISABLED
            self.transfer_button['state'] = DISABLED
    def choose_nand(self):
        name = askopenfilename(filetypes=( ( 'nand.bin', '*.bin' ), ( 'DSi-1.mmc', '*.mmc' ) ))
        self.nand_file.set(name)
        self.nand_button['state'] = (NORMAL if name != '' else DISABLED)
        self.start_button['state'] = (NORMAL if name != '' else DISABLED)


    ################################################################################################
    def start_point(self):
        if not self.transfer_mode:
            self.TThread = Thread(target=self.hiya)
            self.TThread.start()
        else:
            self.TThread = Thread(target=self.transfer)
            self.TThread.start()
    def log_window(self):
        if sysname == 'Linux':
            self.dialog = Toplevel(class_ = 'Magician')
            self.dialog.tk.call('wm', 'iconphoto', self.dialog._w, nand_icon)
        else:
            self.dialog = Toplevel()
        # Open as dialog (parent disabled)
        self.dialog.grab_set()
        self.dialog.title(_('状态'))
        # Disable maximizing
        self.dialog.resizable(0, 0)
        self.dialog.protocol("WM_DELETE_WINDOW", self.closethread)

        frame = Frame(self.dialog, bd=2, relief=SUNKEN)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.log = ThreadSafeText(frame, bd=0, width=52, height=20,
            yscrollcommand=scrollbar.set)
        self.log.pack()

        scrollbar.config(command=self.log.yview)

        frame.pack()

        Button(self.dialog, text=_('关闭'), command=self.closethread, width=16).pack(pady=10)

        # Center in window
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        self.dialog.geometry('%dx%d+%d+%d' % (width, height, root.winfo_x() + (root.winfo_width() / 2) -
            (width / 2), root.winfo_y() + (root.winfo_height() / 2) - (height / 2)))

        self.finish = False
    def transfer(self):
        showinfo(_('提示'), _('接下来请选择TWLTransfer目标镜像文件\n请注意: TWLCFG会被重置'))
        name = askopenfilename(filetypes=[(_('镜像文件'), '*.bin')])
        self.image_file.set(name)
        if self.image_file.get() == '':
            return
        self.log_window()
        self.TThread = Thread(target=self.check_image)
        self.TThread.start()
    def hiya(self):
        if not self.adv_mode:
            if self.setup_operation.get() == 2 or self.nand_operation.get() == 2:
                if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                    root.withdraw()
                    showerror(_('错误'), _('此功能需要以管理员权限运行本工具'))
                    root.destroy()
                    exit(1)

        if not self.nand_mode:
            self.have_hiya = False
            self.is_tds = False
            self.have_menu = False
            if not self.adv_mode:
                showinfo(_('提示'), _('接下来请选择你用来安装自制系统的存储卡路径(或输出路径)\n为了避免 '
                    '启动错误 请确保目录下无任何文件'))
                self.sd_path = askdirectory(title='')
                # Exit if no path was selected
                if self.sd_path == '':
                    return
                self.check_console(self.sd_path)
                if self.is_tds or self.have_hiya:
                    showerror(_('错误'), _('目录检测未通过，若CFW已安装，请转到高级模式，或选择一个空目录以继续'))
                    return
            else:
                self.check_console(self.sd_path1)

        # If adding a No$GBA footer, check if CID and ConsoleID values are OK
        elif self.nand_operation.get() == 1:
            cid = self.cid.get()
            console_id = self.console_id.get()

            # Check lengths
            if len(cid) != 32:
                showerror(_('错误'), 'Bad eMMC CID')
                return

            elif len(console_id) != 16:
                showerror(_('错误'), 'Bad Console ID')
                return

            # Parse strings to hex
            try:
                cid = bytearray.fromhex(cid)

            except ValueError:
                showerror(_('错误'), 'Bad eMMC CID')
                return

            try:
                console_id = bytearray(reversed(bytearray.fromhex(console_id)))

            except ValueError:
                showerror(_('错误'), 'Bad Console ID')
                return

        self.log_window()

        # Check if we'll be adding a No$GBA footer
        if self.nand_mode and self.nand_operation.get() == 1:
            self.TThread = Thread(target=self.add_footer, args=(cid, console_id))
            self.TThread.start()
        elif self.adv_mode:
            if self.updatehiya.get() == 1:
                self.TThread = Thread(target=self.get_latest_hiyacfw)
                self.TThread.start()
            else:
                self.TThread = Thread(target=self.get_latest_twilight)
                self.TThread.start()
        else:
            self.TThread = Thread(target=self.check_nand)
            self.TThread.start()


    ################################################################################################
    def closethread(self):
        if self.adv_mode:
            self.sd_path1 = ''
            self.sdp.set(self.sd_path1)
            if self.tftt.get() == 1:
                self.tftt.set(0)
            if self.appgen.get() == 1:
                self.appgen.set(0)
            if self.devkp.get() == 1:
                self.devkp.set(0)
            if self.updatehiya.get() == 1:
                self.updatehiya.set(0)
            self.start_button['state'] = DISABLED
            self.transfer_button['state'] = DISABLED
            self.tftt_chk['state'] = DISABLED
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
        self.dialog.destroy()
        if self.finish == True:
            self.finish = False
            return
        try:
            stop_thread(self.TThread)
            self.proc.kill()
        except:
            pass
        Thread(target=self.after_close).start()
    def after_close(self):
        sleep(1)
        printl(_('操作过程发生错误或用户终止操作'))
        if self.setup_operation.get() == 2 or self.nand_operation.get() == 2:
            if not self.adv_mode:
                self.unmount_nand1()
        else:
            self.clean(True,)
    def check_nand(self):
        self.log.write(_('正在检查NAND文件...'))

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
                    self.cid.set(hexlify(bstr).upper().decode('ascii'))
                    self.log.write('- eMMC CID: ' + self.cid.get())

                    # Read the console ID
                    bstr = f.read(8)
                    self.console_id.set(hexlify(bytearray(reversed(bstr))).upper().decode('ascii'))
                    self.log.write('- Console ID: ' + self.console_id.get())

                    if self.nand_mode:
                        if self.nand_operation.get() == 2:
                            self.TThread = Thread(target=self.decrypt_nand)
                            self.TThread.start()
                        else:
                            self.TThread = Thread(target=self.remove_footer)
                            self.TThread.start()
                    else:
                        self.TThread = Thread(target=self.get_latest_hiyacfw)
                        self.TThread.start()

                else:
                    self.log.write(_('错误: 没有检测到No$GBA footer\n警告: 若确定Nand已完整dump, 则用于dump的存储卡极有可能是扩容卡或者已出现坏块'))

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法打开文件 ') +
                path.basename(self.nand_file.get()))
    def check_image(self):
        REGION_CODES_IMAGE = {
            '053A1C2ADB047AC28C4FB218244C4FA3BB315525': 'CHN',
            '627AEC8FDF778401958E96DB267CC628A72772F2': 'USA',
            '939190F0E6AC93B7F5833756BE2A251DA71125F9': 'JPN',
            '6B7BBC961C686C4382811D48BEF8A100CACE25E4': 'KOR',
            '12546984F820B681AC0B2E7485531F0818FC1DF3': 'EUR',
            '600F7E36E9F6966540B7F79F057942D3C2336F9E': 'AUS',
            '0FE96AAF374BA777FFEC30A2525409D0DE0E7EA1': 'JPN-kst'
        }
        REGION_HWINFO = {
            '00': 'JPN',
            '01': 'USA',
            '02': 'EUR',
            '03': 'AUS',
            '04': 'CHN',
            '05': 'KOR'
        }
        try:
            sha1_hash = sha1()

            with open(self.image_file.get(), 'rb') as f:
                sha1_hash.update(f.read())

            image_sha1 = hexlify(sha1_hash.digest()).upper().decode('ascii')
            image_filename = path.basename(self.image_file.get())

            try:
                self.dest_region = REGION_CODES_IMAGE[image_sha1]
            except SystemExit:
                return
            except:
                self.log.write(_('错误: 无效的镜像文件'))
                return

            self.log.write('- ' + image_filename + ' SHA1:\n' + image_sha1)
            self.log.write(_('目标系统: ') + self.dest_region)

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法打开文件 ') + image_filename)
            return

        hwinfo = path.join(self.sd_path1, 'sys', 'HWINFO_S.dat')
        hwinfo_o = path.join(self.sd_path1, 'sys', 'HWINFO_O.dat')

        if path.exists(hwinfo):
            with open(hwinfo, 'rb') as infotmp:
                infotmp.seek(0x90,0)
                self.cur_region = REGION_HWINFO[hexlify(infotmp.read(0x01)).decode('ascii')]
                self.log.write(_('当前区域: ') + self.cur_region)
        else:
            self.log.write(_('错误: 无法读取系统区域信息'))
            return

        if path.exists(hwinfo_o):
            with open(hwinfo_o, 'rb') as infotmp:
                infotmp.seek(0x90,0)
                self.origin_region = REGION_HWINFO[hexlify(infotmp.read(0x01)).decode('ascii')]
        else:
            self.origin_region = self.cur_region
        self.log.write(_('原始区域: ') + self.origin_region)
        self.check_serial(self.sd_path1)

        self.TThread = Thread(target=self.get_common_data)
        self.TThread.start()


    ################################################################################################
    def get_latest_hiyacfw(self):
        filename = 'hiyaCFW.7z'
        self.folders.append('for PC')
        self.folders.append('for SDNAND SD card')

        try:
            if not path.isfile(filename):
                self.log.write(_('正在下载最新版本的hiyaCFW...'))
                if self.altdl.get() == 1:
                    with urlopen('https://gitee.com/ryatian/twlmagician-resources/raw/master/' + filename) as src, open(filename, 'wb') as dst:
                        copyfileobj(src, dst)
                else:
                    try:
                        with urlopen('https://github.com/RocketRobz/hiyaCFW/releases/latest/download/' +
                            filename) as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        if loc == 'zh_CN':
                            with urlopen('https://gitee.com/ryatian/twlmagician-resources/raw/master/' + filename) as src, open(filename, 'wb') as dst:
                                copyfileobj(src, dst)
                        else:
                            raise IOError

            self.log.write(_('- 正在解压 hiyaCFW 压缩包...'))

            if self.adv_mode and self.updatehiya.get() == 1:
                self.proc = Popen([ _7za, 'x', '-bso0', '-y', filename, 'for SDNAND SD card' ])
            else:
                self.proc = Popen([ _7za, 'x', '-bso0', '-y', filename, 'for PC', 'for SDNAND SD card' ])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.adv_mode and self.updatehiya.get() == 1:
                    self.TThread = Thread(target=self.update_hiyacfw)
                    self.TThread.start()
                else:
                    self.TThread = Thread(target=self.decrypt_nand if path.isfile('bootloader.nds')
                        else self.extract_bios)
                    self.TThread.start()

            else:
                self.log.write(_('错误: 解压失败'))
                Thread(target=self.clean, args=(True,)).start()

        except (URLError, IOError) as e:
            printl(str(e))
            self.log.write(_('错误: 无法下载hiyaCFW'))

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + _7za)


    ################################################################################################
    def extract_bios(self):
        self.files.append('arm7.bin')
        self.files.append('arm9.bin')
        self.log.write(_('正在从NAND中解压 ARM7/ARM9 BIOS...'))

        try:
            printl(_('调用 twltool(解压 BIOS)'))
            self.proc = Popen([ twltool, 'boot2', '--in', self.nand_file.get() ])

            ret_val = self.proc.wait()

            if ret_val == 0:
                # Hash arm7.bin
                sha1_hash = sha1()

                with open('arm7.bin', 'rb') as f:
                    sha1_hash.update(f.read())
                self.log.write('- arm7.bin SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper().decode('ascii'))

                # Hash arm9.bin
                sha1_hash = sha1()

                with open('arm9.bin', 'rb') as f:
                    sha1_hash.update(f.read())
                self.log.write('- arm9.bin SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper().decode('ascii'))

                self.TThread = Thread(target=self.patch_bios)
                self.TThread.start()

            else:
                self.log.write(_('错误: 解压失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + twltool)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def patch_bios(self):
        self.log.write('Patching ARM7/ARM9 BIOS...')

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
                hexlify(sha1_hash.digest()).upper().decode('ascii'))

            # Hash arm9.bin
            sha1_hash = sha1()

            with open('arm9.bin', 'rb') as f:
                sha1_hash.update(f.read())
            self.log.write('- Patched arm9.bin SHA1:\n  ' +
                hexlify(sha1_hash.digest()).upper().decode('ascii'))

            self.TThread = Thread(target=self.arm9_prepend)
            self.TThread.start()

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法完成 patch BIOS'))
            Thread(target=self.clean, args=(True,)).start()

        except Exception as e:
            printl(str(e))
            self.log.write(_('错误: 无效的 patch header'))
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def arm9_prepend(self):
        self.log.write(_('正在预载数据到 ARM9 BIOS...'))

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
                hexlify(sha1_hash.digest()).upper().decode('ascii'))

            self.TThread = Thread(target=self.make_bootloader)
            self.TThread.start()

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法预载数据到 ARM9 BIOS'))
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def make_bootloader(self):
        self.log.write(_('正在生成 bootloader...'))

        exe = (path.join('for PC', 'bootloader files', 'ndstool.exe') if sysname == 'Windows' else
            path.join(sysname, 'ndsblc'))

        try:
            if sysname == 'Windows':
                printl(_('调用 ndstool(生成 bootloader)'))
            else:
                printl(_('调用 ndsblc(生成 bootloader)'))
            self.proc = Popen([ exe, '-c', 'bootloader.nds', '-9', 'arm9.bin', '-7', 'arm7.bin', '-t',
                path.join('for PC', 'bootloader files', 'banner.bin'), '-h',
                path.join('for PC', 'bootloader files', 'header.bin') ])

            ret_val = self.proc.wait()

            if ret_val == 0:

                # Hash bootloader.nds
                sha1_hash = sha1()

                with open('bootloader.nds', 'rb') as f:
                    sha1_hash.update(f.read())
                self.log.write('- bootloader.nds SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper().decode('ascii'))

                self.TThread = Thread(target=self.decrypt_nand)
                self.TThread.start()

            else:
                self.log.write(_('错误: 生成失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def decrypt_nand(self):
        if not self.nand_mode:
            self.files.append(self.console_id.get() + '.img')
        self.log.write(_('正在解密 NAND...'))

        try:
            printl(_('调用 twltool(解密 NAND)'))
            self.proc = Popen([ twltool, 'nandcrypt', '--in', self.nand_file.get(), '--out',
                self.console_id.get() + '.img' ])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.nand_operation.get() == 2 or self.setup_operation.get() == 2:
                    self.TThread = Thread(target=self.mount_nand)
                    self.TThread.start()
                else:
                    self.TThread = Thread(target=self.extract_nand1 if (sysname == 'Windows' and self.setup_operation.get() == 1)
                        else self.extract_nand)
                    self.TThread.start()
            else:
                self.log.write(_('错误: 解密失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + twltool)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def extract_nand1(self):
        self.files.append('0.fat')
        self.files.append('1.fat')
        self.log.write(_('正在从NAND中解压文件...'))

        try:
            printl(_('调用 7-Zip(解压 NAND)'), fixn=True)
            if self.photo.get() == 1:
                self.proc = Popen([ _7z, 'x', '-bso0', '-y', self.console_id.get() + '.img', '0.fat', '1.fat' ])
            else:
                self.proc = Popen([ _7z, 'x', '-bso0', '-y', self.console_id.get() + '.img', '0.fat' ])

            ret_val = self.proc.wait()

            if ret_val == 0:

                self.proc = Popen([ _7z, 'x', '-bso0', '-y', '-o' + self.sd_path, '0.fat' ])

                ret_val = self.proc.wait()

                if ret_val == 0:
                    if self.photo.get() == 1:
                        self.proc = Popen([ _7z, 'x', '-bso0', '-y', '-o' + self.sd_path, '1.fat' ])
                        ret_val = self.proc.wait()
                        if ret_val == 0:
                            self.TThread = Thread(target=self.get_launcher)
                            self.TThread.start()
                        else:
                            self.log.write(_('错误: 解压相册分区失败'))
                            Thread(target=self.clean, args=(True,)).start()
                    else:
                        self.TThread = Thread(target=self.get_launcher)
                        self.TThread.start()
                else:
                    self.log.write(_('错误: 解压失败'))

                    if path.exists(fatcat):
                        self.log.write(_('尝试使用fatcat...'))
                        self.TThread = Thread(target=self.extract_nand)
                        self.TThread.start()

                    else:
                        Thread(target=self.clean, args=(True,)).start()

            else:
                self.log.write(_('错误: 解压失败'))

                if path.exists(fatcat):
                    self.log.write(_('尝试使用fatcat...'))
                    self.TThread = Thread(target=self.extract_nand)
                    self.TThread.start()

                else:
                    Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + _7z)

            if path.exists(fatcat):
                self.log.write(_('尝试使用fatcat...'))
                self.TThread = Thread(target=self.extract_nand)
                self.TThread.start()

            else:
                Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def mount_nand(self):
        self.log.write(_('挂载解密的NAND镜像中...'))

        try:
            printl(_('调用 osfmount(挂载 twln)'), fixn=True)
            cmd = [ osfmount, '-a', '-t', 'file', '-f', self.console_id.get() + '.img', '-m',
                '#:', '-o', 'ro,rem' ]

            if self.nand_mode:
                cmd[-1] = 'rw,rem'

            self.proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            outs, errs = self.proc.communicate()
            print(outs.decode('utf-8').strip())

            if self.proc.returncode == 0:
                self.mounted = search(r'[a-zA-Z]:\s', outs.decode('utf-8')).group(0).strip()
                self.log.write(_('- 挂载到驱动器 ') + self.mounted)
                if self.nand_mode == False and self.photo.get() == 1:
                    printl(_('调用 osfmount(挂载 twlp)'))
                    cmd = [ osfmount, '-a', '-t', 'file', '-f', self.console_id.get() + '.img', '-m',
                        '#:', '-v', '2', '-o', 'ro,rem' ]
                    self.proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    outs, errs = self.proc.communicate()
                    print(outs.decode('utf-8').strip())

                    if self.proc.returncode == 0:
                        self.twlp = search(r'[a-zA-Z]:\s', outs.decode('utf-8')).group(0).strip()
                        self.log.write(_('- DSi相册分区挂载到驱动器 ') + self.twlp)
                    else:
                        self.log.write(_('错误: 挂载相册分区失败'))
                        Thread(target=self.clean, args=(True,)).start()
                        return
            else:
                self.log.write(_('错误: 挂载失败'))
                Thread(target=self.clean, args=(True,)).start()
                return

            if self.nand_mode:
                self.TThread = Thread(target=self.unlaunch_proc)
                self.TThread.start()
            else:
                self.TThread = Thread(target=self.extract_nand2)
                self.TThread.start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + osfmount)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def extract_nand(self):
        self.log.write(_('正在从NAND中解压文件...'))

        try:
            printl(_('调用 fatcat(解压 NAND)'), fixn=True)
            # DSi first partition offset: 0010EE00h
            self.proc = Popen([ fatcat, '-O', '1109504', '-x', self.sd_path,
                self.console_id.get() + '.img' ])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.photo.get() == 1:
                    # DSi photo partition offset: 0CF09A00h
                    self.proc = Popen([ fatcat, '-O', '217094656', '-x', self.sd_path,
                        self.console_id.get() + '.img' ])
                    ret_val = self.proc.wait()
                    if ret_val == 0:
                        self.TThread = Thread(target=self.get_launcher)
                        self.TThread.start()
                    else:
                        self.log.write(_('错误: 解压相册分区失败'))
                        Thread(target=self.clean, args=(True,)).start()
                else:
                    self.TThread = Thread(target=self.get_launcher)
                    self.TThread.start()
            else:
                self.log.write(_('错误: 解压失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + fatcat)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def extract_nand2(self):
        self.log.write(_('正在从NAND中复制文件...'))
        # Reset copied files cache
        _path_created.clear()
        try:
            copy_tree(self.mounted, self.sd_path, preserve_mode=0)
            if self.nand_mode == False and self.photo.get() == 1:
                copy_tree(self.twlp, self.sd_path, preserve_mode=0)
            self.TThread = Thread(target=self.unmount_nand)
            self.TThread.start()
        except SystemExit:
            return
        except:
            self.log.write(_('错误: 复制失败'))
            self.TThread = Thread(target=self.unmount_nand1)
            self.TThread.start()


    ################################################################################################
    def get_launcher(self):
        app = self.detect_region()

        # Stop if no supported region was found
        if not app:
            Thread(target=self.clean, args=(True,)).start()
            return

        # Delete contents of the launcher folder as it will be replaced by the one from hiyaCFW
        launcher_folder = path.join(self.sd_path, 'title', '00030017', app, 'content')

        # Walk through all files in the launcher content folder
        for file in listdir(launcher_folder):
            file = path.join(launcher_folder, file)

            if _7z is not None:
                if self.setup_operation.get() == 1:
                    chmod(file, 438)
            remove(file)

        try:
            if not path.isfile(self.launcher_region):
                self.log.write(_('正在下载 ') + self.launcher_region + ' Launcher...')
                if self.altdl.get() == 1:
                    with urlopen('https://gitee.com/ryatian/twlmagician-resources/raw/master/launchers/' + self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                        copyfileobj(src, dst)
                else:
                    try:
                        with urlopen('https://raw.githubusercontent.com'
                            '/R-YaTian/TWLMagician/main/launchers/' +
                            self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        if loc == 'zh_CN':
                            with urlopen('https://gitee.com/ryatian/twlmagician-resources/raw/master/launchers/' + self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                                copyfileobj(src, dst)
                        else:
                            raise IOError

            self.log.write(_('- 正在解压Launcher...'))

            if self.launcher_region in ('CHN', 'KOR'):
                launcher_app = '00000000.app'
            elif self.launcher_region == 'USA-dev':
                launcher_app = '7412e50d.app'
                self.files.append('title.tmd')
            else:
                launcher_app = '00000002.app'

            self.files.append(launcher_app)

            # Prepare decryption params
            params = [ _7za, 'x', '-bso0', '-y', '-p' + app.lower(), self.launcher_region,
                launcher_app ]

            if launcher_app == '7412e50d.app':
                params.append('title.tmd')

            self.proc = Popen(params)

            ret_val = self.proc.wait()

            if ret_val == 0:

                # Hash launcher app
                sha1_hash = sha1()

                with open(launcher_app, 'rb') as f:
                    sha1_hash.update(f.read())
                self.log.write('- Patched Launcher SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper().decode('ascii'))

                self.TThread = Thread(target=self.install_hiyacfw, args=(launcher_app, launcher_folder, app))
                self.TThread.start()

            else:
                self.log.write(_('错误: 解压失败'))
                Thread(target=self.clean, args=(True,)).start()

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法下载 ') + self.launcher_region + ' Launcher')
            Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + _7za)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def install_hiyacfw(self, launcher_app, launcher_folder, app):
        self.check_serial(self.sd_path)
        self.log.write(_('正在复制hiyaCFW相关文件...'))

        # Reset copied files cache
        _path_created.clear()

        copy_tree(path.join('for SDNAND SD card', 'hiya'), path.join(self.sd_path, 'hiya'))
        copy_tree(path.join('for SDNAND SD card', 'photo'), path.join(self.sd_path, 'photo'))
        copyfile(path.join('for SDNAND SD card', 'hiya.dsi'), path.join(self.sd_path, 'hiya.dsi'))
        copyfile('bootloader.nds', path.join(self.sd_path, 'hiya', 'bootloader.nds'))
        copyfile(launcher_app, path.join(launcher_folder, launcher_app))

        tmd_src = path.join('for SDNAND SD card', 'title', '00030017', app, 'content', 'title.tmd')
        if launcher_app == '7412e50d.app':
            copyfile('title.tmd', path.join(launcher_folder, 'title.tmd'))
        else:
            copyfile(tmd_src, path.join(launcher_folder, 'title.tmd'))

        if self.devkp.get() == 1:
            self.make_dekp(self.sd_path)

        self.TThread = Thread(target=self.get_latest_twilight if self.twilight.get() == 1 else self.clean)
        self.TThread.start()
    def update_hiyacfw(self):
        self.log.write(_('正在更新hiyaCFW...'))

        copyfile(path.join('for SDNAND SD card', 'hiya.dsi'), path.join(self.sd_path1, 'hiya.dsi'))

        self.TThread = Thread(target=self.get_latest_twilight)
        self.TThread.start()
    def check_serial(self, infopath):
        hwinfo = path.join(infopath, 'sys', 'HWINFO_S.dat')
        if path.exists(hwinfo):
            with open(hwinfo, 'rb') as infotmp:
                infotmp.seek(0x91,0)
                strtmp = infotmp.read(0xC).decode('ascii')
                self.log.write(_('机器序列号: ') + strtmp)


    ################################################################################################
    def get_latest_twilight(self):
        filename = 'TWiLightMenu-DSi.7z' if self.is_tds == False else 'TWiLightMenu-3DS.7z'
        self.files.append(filename)
        self.files.append('BOOT.NDS')
        self.files.append('snemul.cfg')
        self.files.append('TWiLight Menu - Game booter.cia')
        self.files.append('TWiLight Menu.cia')
        self.files.append('version.txt')
        self.files.append('Temp.fid')
        self.folders.append('_nds')
        self.folders.append('roms')
        self.folders.append('title')
        self.folders.append('hiya')

        try:
            if not path.isfile(filename):
                self.log.write(_('正在下载最新版本的TWiLightMenu++...'))
                if self.altdl.get() == 1:
                    try:
                        with urlopen('https://spinaround.tk/somefiles/' +
                            filename) as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        idfile = 'ID1.bin' if self.is_tds == False else 'ID2.bin'
                        with urlopen('https://gitee.com/ryatian/twlmagician-resources/raw/master/' + idfile) as src0, open('Temp.fid', 'wb') as dst0:
                            copyfileobj(src0, dst0)
                        with open('Temp.fid', 'r') as ftmp:
                            fileid = ftmp.read()
                        remove('Temp.fid')
                        with urlopen('https://gitee.com/ryatian/twlmagician-resources/attach_files/' + fileid + '/download/' + filename) as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                else:
                    try:
                        with urlopen('https://github.com/DS-Homebrew/TWiLightMenu/releases/latest/download/' +
                            filename) as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        if loc == 'zh_CN':
                            try:
                                with urlopen('https://spinaround.tk/somefiles/' +
                                    filename) as src, open(filename, 'wb') as dst:
                                    copyfileobj(src, dst)
                            except SystemExit:
                                return
                            except:
                                idfile = 'ID1.bin' if self.is_tds == False else 'ID2.bin'
                                with urlopen('https://gitee.com/ryatian/twlmagician-resources/raw/master/' + idfile) as src0, open('Temp.fid', 'wb') as dst0:
                                    copyfileobj(src0, dst0)
                                with open('Temp.fid', 'r') as ftmp:
                                    fileid = ftmp.read()
                                remove('Temp.fid')
                                with urlopen('https://gitee.com/ryatian/twlmagician-resources/attach_files/' + fileid + '/download/' + filename) as src, open(filename, 'wb') as dst:
                                    copyfileobj(src, dst)
                        else:
                            raise IOError

            self.log.write(_('- 正在解压 ') + filename[:-3] + _(' 压缩包...'))

            if self.is_tds == False:
                self.proc = Popen([ _7za, 'x', '-bso0', '-y', filename, '_nds', 'title',
                    'hiya', 'roms', 'BOOT.NDS', 'snemul.cfg', 'version.txt'])
            else:
                self.proc = Popen([ _7za, 'x', '-bso0', '-y', filename, '_nds', 'TWiLight Menu - Game booter.cia',
                    'TWiLight Menu.cia', 'roms', 'BOOT.NDS', 'snemul.cfg', 'version.txt'])

            ret_val = self.proc.wait()

            if ret_val == 0:
                self.TThread = Thread(target=self.install_twilight, args=(filename[:-3],))
                self.TThread.start()

            else:
                self.log.write(_('错误: 解压失败'))
                Thread(target=self.clean, args=(True,)).start()

        except (URLError, IOError) as e:
            printl(str(e))
            self.log.write(_('错误: 无法下载TWiLightMenu++'))
            Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + _7za)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def install_twilight(self, name):
        self.log.write(_('正在复制 ') + name + _(' 相关文件...'))

        # Reset copied files cache
        _path_created.clear()

        if not self.adv_mode:
            copy_tree('_nds', path.join(self.sd_path, '_nds'))
            copy_tree('title', path.join(self.sd_path, 'title'))
            copy_tree('hiya', path.join(self.sd_path, 'hiya'))
            copy_tree('roms', path.join(self.sd_path, 'roms'))
            copyfile('BOOT.NDS', path.join(self.sd_path, 'BOOT.NDS'))
            copyfile('snemul.cfg', path.join(self.sd_path, 'snemul.cfg'))
        else:
            if self.updatehiya.get() == 1:
                copy_tree('title', path.join(self.sd_path1, 'title'))
                copy_tree('hiya', path.join(self.sd_path1, 'hiya'))
            copy_tree('_nds', path.join(self.sd_path1, '_nds'))
            copy_tree('roms', path.join(self.sd_path1, 'roms'))
            copyfile('BOOT.NDS', path.join(self.sd_path1, 'BOOT.NDS'))
            copyfile('snemul.cfg', path.join(self.sd_path1, 'snemul.cfg'))
            if self.is_tds == True:
                cias = path.join(self.sd_path1, 'cias')
                if not path.exists(cias):
                    mkdir(cias)
                copyfile('TWiLight Menu.cia', path.join(self.sd_path1, 'cias', 'TWiLight Menu.cia'))
                copyfile('TWiLight Menu - Game booter.cia', path.join(self.sd_path1, 'cias', 'TWiLight Menu - Game booter.cia'))

        with open('version.txt', 'r') as ver:
            tmpstr = ver.readline()
            tmpstr1 = ver.readline()
            tmpstr1 = tmpstr1.replace('\n','')
            self.log.write(_('版本信息:\n') + tmpstr + tmpstr1)

        if self.appgen.get() == 1:
            printl(_('调用 appgen'))
            if not self.adv_mode:
                agen(path.join(self.sd_path, 'title' , '00030004'), path.join(self.sd_path, 'roms'))
            else:
                agen(path.join(self.sd_path1, 'title' , '00030004'), path.join(self.sd_path1, 'roms'))
        if self.adv_mode and self.devkp.get() == 1:
            self.make_dekp(self.sd_path1)
        if self.adv_mode and self.have_hiya == True:
            self.check_serial(self.sd_path1)
        if self.adv_mode and self.tftt.get() == 1:
            if path.exists('TFTT.dat'):
                self.log.write(_('- 正在安装TFTT'))
                self.folders.append('gm9')
                self.folders.append('luma')
                try:
                    self.proc = Popen([ _7za, 'x', '-bso0', '-y', '-pR-YaTian', 'TFTT.dat', 'gm9', 'luma'])
                    ret_val = self.proc.wait()
                    if ret_val == 0:
                        copy_tree('gm9', path.join(self.sd_path1, 'gm9'))
                        copy_tree('luma', path.join(self.sd_path1, 'luma'))
                    else:
                        self.log.write(_('错误: 安装TFTT失败'))
                except OSError as e:
                    printl(str(e))
                    self.log.write(_('错误: 无法运行 ') + _7za)
            else:
                self.log.write(_('警告: 找不到TFTT.dat文件, 未安装TFTT'))

        Thread(target=self.clean).start()


    ################################################################################################
    def clean(self, err=False):
        self.finish = True
        self.log.write(_('清理中...'))

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
            self.log.write(_('操作过程发生错误或用户终止操作\n'))
            return

        if self.nand_mode:
            file = self.console_id.get() + self.suffix + '.bin'
            try:
                rename(self.console_id.get() + '.img', file)
                self.log.write(_('完成!\n修改后的NAND已保存为') + file + '\n')
            except FileExistsError:
                remove(self.console_id.get() + '.img')
                self.log.write(_('操作终止!\n目标文件已存在于程序运行目录下, 无法覆盖原文件\n'))
            return

        if self.adv_mode and self.is_tds:
            self.log.write(_('完成!\n弹出你的存储卡并插回到机器中\n对于3DS设备, 你还需要在机器上使用FBI完成Title的安装\n'))
        else:
            self.log.write(_('完成!\n弹出你的存储卡并插回到机器中\n'))


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
            '484e414a': 'JPN',
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
                    if file.lower().endswith('.app'):
                        try:
                            if file.startswith("0000000"):
                                self.log.write(_('- 检测到 ') + REGION_CODES[app.lower()] +
                                     ' Launcher')
                                if not self.nand_mode:
                                    self.launcher_region = REGION_CODES[app.lower()]
                            else:
                                if self.nand_mode:
                                    self.log.write(_('- 检测到 ') + REGION_CODES[app.lower()] +
                                         '-dev Launcher')
                                else:
                                    self.log.write(_('- 检测到 ') + REGION_CODES_DEV[app.lower()] +
                                         ' Launcher')
                                    self.launcher_region = REGION_CODES_DEV[app.lower()]
                            return app

                        except KeyError:
                            self.log.write(_('错误: 在NAND中找不到受支持的Launcher'))
                            return False

            self.log.write(_('错误: 无法检测系统区域'))

        except OSError as e:
            self.log.write(_('错误: ') + e.strerror + ': ' + e.filename)

        return False


    ################################################################################################
    def unlaunch_proc(self):
        filename = 'unlaunch.zip'
        self.files.append('UNLAUNCH.DSI')
        self.log.write(_('检查unlaunch状态中...'))

        app = self.detect_region()

        if not app:
            self.TThread = Thread(target=self.unmount_nand1)
            self.TThread.start()
            return

        tmd = path.join(self.mounted, 'title', '00030017', app, 'content', 'title.tmd')

        tmd_size = path.getsize(tmd)

        if tmd_size == 520:
            self.log.write(_('- 未安装...'))

            try:
                if not path.exists('unlaunch.zip'):
                    self.log.write(_('正在下载最新版本的unlaunch...'))
                    try:
                        with urlopen('http://problemkaputt.de/unlaunch.zip') as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        if loc == 'zh_CN':
                            with urlopen('https://gitee.com/ryatian/twlmagician-resources/raw/master/unlaunch.zip') as src, open(filename, 'wb') as dst:
                                copyfileobj(src, dst)
                        else:
                            raise IOError

                self.proc = Popen([ _7za, 'x', '-bso0', '-y', filename, 'UNLAUNCH.DSI' ])

                ret_val = self.proc.wait()

                if ret_val == 0:

                    self.log.write(_('- 正在安装unlaunch...'))

                    self.suffix = '-unlaunch'

                    with open(tmd, 'ab') as f:
                        with open('UNLAUNCH.DSI', 'rb') as unl:
                            f.write(unl.read())

                    self.check_serial(self.mounted)
                    self.make_dekp(self.mounted)

                    # Set files as read-only
                    for file in listdir(path.join(self.mounted, 'title', '00030017', app,
                        'content')):
                        file = path.join(self.mounted, 'title', '00030017', app, 'content', file)
                        chmod(file, 292)

                else:
                    self.log.write(_('错误: 解压失败'))
                    self.TThread = Thread(target=self.unmount_nand1)
                    self.TThread.start()
                    return

            except IOError as e:
                printl(str(e))
                self.log.write(_('错误: 无法下载 unlaunch'))
                self.TThread = Thread(target=self.unmount_nand1)
                self.TThread.start()
                return

            except OSError as e:
                printl(str(e))
                self.log.write(_('错误: 无法运行 ') + _7za)
                self.TThread = Thread(target=self.unmount_nand1)
                self.TThread.start()
                return

        else:
            self.log.write(_('- 已安装, 卸载中...'))

            self.suffix = '-no-unlaunch'

            # Set files as read-write
            for file in listdir(path.join(self.mounted, 'title', '00030017', app, 'content')):
                file = path.join(self.mounted, 'title', '00030017', app, 'content', file)
                chmod(file, 438)

            with open(tmd, 'r+b') as f:
                f.truncate(520)

            self.check_serial(self.mounted)
            self.make_dekp(self.mounted)

        self.TThread = Thread(target=self.unmount_nand)
        self.TThread.start()


    ################################################################################################
    def unmount_nand(self):
        self.log.write(_('正在卸载NAND...'))

        try:
            printl(_('调用 osfmount(卸载 twln)'))
            self.proc = Popen([ osfmount, '-D', '-m', self.mounted ])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.nand_mode == False and self.photo.get() == 1:
                    printl(_('调用 osfmount(卸载 twlp)'))
                    self.proc = Popen([ osfmount, '-D', '-m', self.twlp ])
                    ret_val = self.proc.wait()
                    if ret_val == 0:
                        self.TThread = Thread(target=self.encrypt_nand if self.nand_mode else self.get_launcher)
                        self.TThread.start()
                    else:
                        self.log.write(_('错误: 卸载相册分区失败'))
                        Thread(target=self.clean, args=(True,)).start()
                else:
                    self.TThread = Thread(target=self.encrypt_nand if self.nand_mode else self.get_launcher)
                    self.TThread.start()
            else:
                self.log.write(_('错误: 卸载失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + osfmount)
            Thread(target=self.clean, args=(True,)).start()
    def unmount_nand1(self):
        self.log.write(_('正在强制卸载NAND...'))

        try:
            printl(_('调用 osfmount(强制卸载 twln)'))
            self.proc = Popen([ osfmount, '-D', '-m', self.mounted ])

            ret_val = self.proc.wait()

            if ret_val != 0:
                self.log.write(_('错误: 卸载失败或尚未挂载'))

            if self.nand_mode == False and self.photo.get() == 1:
                printl(_('调用 osfmount(强制卸载 twlp)'))
                self.proc = Popen([ osfmount, '-D', '-m', self.twlp ])
                ret_val = self.proc.wait()
                if ret_val != 0:
                    self.log.write(_('错误: 卸载相册分区失败或尚未挂载'))

            Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + osfmount)
            Thread(target=self.clean, args=(True,)).start()
        except SystemExit:
            return
        except:
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def encrypt_nand(self):
        self.log.write(_('正在重加密NAND...'))

        try:
            printl(_('调用 twltool(重加密 NAND)'))
            self.proc = Popen([ twltool, 'nandcrypt', '--in', self.console_id.get() + '.img' ])

            ret_val = self.proc.wait()

            if ret_val == 0:
                Thread(target=self.clean).start()

            else:
                self.log.write(_('错误: 加密失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + twltool)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def remove_footer(self):
        self.log.write(_('正在移除No$GBA footer...'))

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
            self.finish = True
            self.log.write(_('完成!\n修改后的NAND已保存为\n') + file +
                _('\nfooter信息已保存到 ') + self.console_id.get() + '-info.txt\n')

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法打开 ') +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def add_footer(self, cid, console_id):
        self.log.write(_('正在添加No$GBA footer...'))

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
                    self.log.write(_('错误: 文件中已存在 No$GBA footer'))
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
            self.finish = True
            self.log.write(_('完成!\n修改后的NAND已保存为\n') + file + '\n')

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法打开 ') +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def get_common_data(self):
        self.files.append('Common.dat')
        self.folders.append('hiya')
        self.folders.append('title')
        self.folders.append('ticket')

        try:
            if not path.isfile('Common.dat'):
                self.log.write(_('正在下载通用数据...'))
                with urlopen('https://gitee.com/ryatian/twlmagician-resources/raw/master/Common.dat') as src, open('Common.dat', 'wb') as dst:
                    copyfileobj(src, dst)

            self.log.write(_('- 正在解压通用数据...'))

            if self.tmfh.get() == 1:
                self.proc = Popen([ _7za, 'x', '-bso0', '-y', '-pR-YaTian', 'Common.dat', 'hiya', 'title', 'ticket', 'TMFH' ])
            else:
                self.proc = Popen([ _7za, 'x', '-bso0', '-y', '-pR-YaTian', 'Common.dat', 'hiya', 'title', 'ticket' ])

            ret_val = self.proc.wait()

            if ret_val == 0:
                self.TThread = Thread(target=self.decrypt_image)
                self.TThread.start()

            else:
                self.log.write(_('错误: 解压失败'))
                Thread(target=self.clean, args=(True,)).start()

        except (URLError, IOError) as e:
            printl(str(e))
            self.log.write(_('错误: 无法下载通用数据'))

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + _7za)


    ################################################################################################
    def decrypt_image(self):
        self.files.append(self.dest_region + '.app')
        self.folders.append('shared1')
        self.folders.append('sys')
        self.folders.append('title')
        self.folders.append('ticket')
        self.log.write(_('正在解密TWLTransfer镜像文件...'))

        try:
            self.proc = Popen([ _7za, 'x', '-bso0', '-y', '-pR-YaTian', self.image_file.get(),
                                self.dest_region + '.app', 'shared1', 'sys', 'title', 'ticket' ])

            ret_val = self.proc.wait()

            if ret_val == 0:
                self.TThread = Thread(target=self.transfer_main)
                self.TThread.start()

            else:
                self.log.write(_('错误: 解密失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + _7za)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def transfer_main(self):
        TITLE_ID = {
            'CHN': '484e4143',
            'USA': '484e4145',
            'JPN': '484e414a',
            'KOR': '484e414b',
            'EUR': '484e4150',
            'AUS': '484e4155'
        }
        REGION_BYTES = {
            'JPN'    : '00',
            'JPN-kst': '00',
            'USA'    : '01',
            'EUR'    : '02',
            'AUS'    : '03',
            'CHN'    : '04',
            'KOR'    : '05'
        }
        if self.origin_region in ('CHN', 'KOR'):
            launcher_name = '00000000.app'
        else:
            launcher_name = '00000002.app'
        launcher_id = TITLE_ID[self.origin_region]

        self.log.write(_('正在执行TWLTransfer...'))

        oldfolders = []
        oldfolders.append(path.join(self.sd_path1, 'title', '0003000f'))
        oldfolders.append(path.join(self.sd_path1, 'title', '00030004'))
        oldfolders.append(path.join(self.sd_path1, 'title', '00030005'))
        oldfolders.append(path.join(self.sd_path1, 'title', '00030015'))
        oldfolders.append(path.join(self.sd_path1, 'ticket', '0003000f'))
        oldfolders.append(path.join(self.sd_path1, 'ticket', '00030004'))
        oldfolders.append(path.join(self.sd_path1, 'ticket', '00030005'))
        oldfolders.append(path.join(self.sd_path1, 'ticket', '00030015'))
        while len(oldfolders) > 0:
            rmtree(oldfolders.pop(), ignore_errors=True)

        hwinfo = path.join(self.sd_path1, 'sys', 'HWINFO_S.dat')
        hwinfo_o = path.join(self.sd_path1, 'sys', 'HWINFO_O.dat')
        if not path.exists(hwinfo_o):
            copyfile(hwinfo, hwinfo_o)

        with open(hwinfo, 'rb+') as f:
            f.seek(0x90,0)
            f.write(unhexlify(REGION_BYTES[self.dest_region]))
            f.flush()
            f.close()

        _path_created.clear()
        copy_tree('title', path.join(self.sd_path1, 'title'))
        copy_tree('hiya', path.join(self.sd_path1, 'hiya'))
        copy_tree('ticket', path.join(self.sd_path1, 'ticket'))
        copy_tree('sys', path.join(self.sd_path1, 'sys'))
        copy_tree('shared1', path.join(self.sd_path1, 'shared1'))
        if self.tmfh.get() == 1:
            self.log.write(_('正在安装TMFH...'))
            copy_tree('TMFH/title', path.join(self.sd_path1, 'title'))
        #copy_tree('_nds', path.join(self.sd_path1, '_nds'))
        #copy_tree('roms', path.join(self.sd_path1, 'roms'))
        #copyfile('BOOT.NDS', path.join(self.sd_path1, 'BOOT.NDS'))
        #copyfile('snemul.cfg', path.join(self.sd_path1, 'snemul.cfg'))
        copyfile(self.dest_region + '.app', path.join(self.sd_path1, 'title', '00030017', launcher_id, 'content', launcher_name))

        if self.devkp.get() == 1:
            self.make_dekp(self.sd_path1)

        Thread(target=self.clean).start()


####################################################################################################
# Entry point

sysname = platform.system()
root = Tk(className="Magician") if sysname == 'Linux' else Tk()

loc = lang_init('zh_hans', 'i18n')

if path.isfile('console.log'):
    clog = open('Console.log', 'a')
    clog.write('\n')
    clog.close()
printl(_('TWLMagician启动中...'))

fatcat = path.join(sysname, 'fatcat')
_7za = path.join(sysname, '7za')
twltool = path.join(sysname, 'twltool')
osfmount  = None
_7z = None

if sysname == 'Windows':
    fatcat += '.exe'
    _7za += '.exe'
    twltool += '.exe'

    pybits = platform.architecture()[0]
    winver = platform.win32_ver()[0]
    if winver == 'Vista' or winver == 'XP' or winver == '2003Server':
        osfpath = 'elder'
    else:
        osfpath = 'extras'

    if pybits == '64bit':
        osfmount = path.join(sysname, osfpath, 'OSFMount.com')
        if path.exists(osfmount):
            printl(_('64位版本的OSFMount模块已加载'))
        else:
            osfmount  = None
    else:
        try:
            if environ['PROGRAMFILES(X86)']:
                osfmount = path.join(sysname, osfpath, 'OSFMount.com')
                if path.exists(osfmount):
                    printl(_('64位版本的OSFMount模块已加载'))
                else:
                    osfmount  = None
        except KeyError:
            osfmount = path.join(sysname, osfpath, 'x86', 'OSFMount.com')
            if path.exists(osfmount):
                printl(_('32位版本的OSFMount模块已加载'))
            else:
                osfmount  = None

    _7z = path.join(sysname, '7z.exe')
    if path.exists(_7z):
        printl(_('7-Zip模块已加载'))
    else:
         _7z = None

if not path.exists(fatcat):
    if osfmount or _7z is not None:
        fatcat = None
    else:
        root.withdraw()
        showerror(_('错误'), _('找不到Fatcat, 请确认此程序位于本工具目录的"{}"文件夹中').format(sysname))
        root.destroy()
        exit(1)

printl(_('GUI初始化中...'))

root.title('TWLMagician Beta6 BY R-YaTian')
# Disable maximizing
root.resizable(0, 0)
# Center in window
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
nand_icon = PhotoImage(data=('R0lGODlhEAAQAIMAAAAAADMzM2ZmZpmZmczMzP///wAAAAAAAAA'
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAAYALAAAAAAQAB'
            'AAAARG0MhJaxU4Y2sECAEgikE1CAFRhGMwSMJwBsU6frIgnR/bv'
            'hTPrWUSDnGw3JGU2xmHrsvyU5xGO8ql6+S0AifPW8kCKpcpEQA7'))
if sysname == 'Linux':
    root.tk.call('wm', 'iconphoto', root._w, nand_icon)
app = Application(master=root)
app.mainloop()
