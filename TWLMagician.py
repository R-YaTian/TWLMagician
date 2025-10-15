#!/usr/bin/env python3
# coding=utf-8

# TWLMagician
# Version 1.5.6
# Author: R-YaTian
# Original "HiyaCFW-Helper" Author: mondul <mondul@huyzona.com>

import ttkbootstrap as ttk
from ttkbootstrap import (Frame, LabelFrame, PhotoImage, Button, Entry, Checkbutton, Radiobutton, OptionMenu,
                     Label, Toplevel, Scrollbar, Text, StringVar, IntVar, RIGHT, W, X, Y, DISABLED, NORMAL, SUNKEN,
                     END,
                     toast, tableview, scrolled)
import ttkbootstrap.utility
from ttkbootstrap.tooltip import ToolTip
from tkinter.messagebox import askokcancel, showerror, showinfo, WARNING
from tkinter.filedialog import askopenfilename, askdirectory
from os import path, remove, chmod, listdir, environ, mkdir
from sys import exit, stdout, argv
from threading import Thread
from queue import Queue, Empty
from hashlib import sha1
from urllib.request import urlopen
from urllib.error import URLError
from subprocess import Popen, PIPE
from struct import unpack_from
from shutil import rmtree, copyfile
from re import search
from inspect import isclass
from datetime import datetime
from time import sleep
from binascii import hexlify, unhexlify
from appgen import agen
from py_langs.langs import lang_init
from pyutils import copyfileobj, copytree
import ctypes
import platform
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
ntime_tmp = None
downloadfile = False
version_number = 155


# Check Update
def get_version():
    if path.isfile('version.meta'):
        remove('version.meta')
    if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
        version_url = 'https://gitee.com/ryatian/mirrors/raw/master/'
    else:
        version_url = 'https://raw.githubusercontent.com/R-YaTian/TWLMagician/main/Res/'
    try:
        with urlopen(version_url + 'version.meta') as src0, open('version.meta', 'wb') as dst0:
            copyfileobj(src0, dst0, show_progress=False)
        with open('version.meta', 'rb') as ftmp:
            data = ftmp.read()
            number = unpack_from('<I', data, offset=0)[0]
        remove('version.meta')
        return number
    except:
        if path.isfile('version.meta'):
            remove('version.meta')
        return -1


def check_update():
    printl(_('检查更新中...'))
    new_version = get_version()
    if new_version == -1:
        printl(_('检查更新失败'))
    elif new_version > version_number:
        import webbrowser
        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
            release_url = 'https://gitee.com/ryatian/mirrors/releases/tag/TWLMagician'
        else:
            release_url = 'https://github.com/R-YaTian/TWLMagician/releases/latest'
        printl(_('检测到新版本, 由于本程序新版本包含重要更新\n暂不支持跳过更新, 即将前往发布页'))
        webbrowser.open(release_url, 2, autoraise=True)
        exit(1)
    else:
        printl(_('当前为最新版本!'))


# TimeLog-Print
def printl(*objects, sep=' ', end='\n', file=stdout, flush=False, fixn=False):
    global ntime_tmp, downloadfile
    clog = open('Console.log', 'a', encoding="UTF-8")
    ntime = datetime.now().strftime('%F %T')
    if downloadfile:
        fixn = True
        downloadfile = False
    if ntime_tmp != ntime or ntime_tmp is None:
        if fixn is False:
            print('[' + ntime + ']')
        else:
            print('\n[' + ntime + ']')
        clog.write('[' + ntime + ']\n')
    print(*objects, sep=sep, end=end, file=file, flush=flush)
    clog.write(*objects)
    clog.write('\n')
    ntime_tmp = ntime
    clog.close()


# Thread-Control
def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
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
        self.wlog = None
        self.now_time_tmp = None
        self.queue = Queue()
        self.update_me()

    def write(self, line):
        self.wlog = open('Window.log', 'a', encoding="UTF-8")
        now_time = datetime.now().strftime('%F %T')
        if self.now_time_tmp != now_time or self.now_time_tmp is None:
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
# Main application class

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.log = None
        self.out_path = None
        self.dialog = None
        self.dest_region = None
        self.cur_region = None
        self.origin_region = None
        self.twlp = None
        self.loop_dev = None
        self.raw_disk = None
        self.mounted = None
        self.launcher_region = None
        self.suffix = None
        self.proc = None
        self.TThread = None
        self.sd_path = None
        self.sd_path1 = None
        self.pack()
        self.adv_mode = False
        self.nand_mode = False
        self.transfer_mode = False
        self.setup_select = False
        self.have_hiya = False
        self.is_tds = False
        self.have_menu = False
        self.finish = False

        adl_chk = None
        adl1_chk = None
        adl2_chk = None

        self.image_file = StringVar()

        self.nand_icon = PhotoImage(data=('R0lGODlhEAAQAIMAAAAAADMzM2ZmZpmZmczMzP///wAAAAAAAAA'
                                     'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAAYALAAAAAAQAB'
                                     'AAAARG0MhJaxU4Y2sECAEgikE1CAFRhGMwSMJwBsU6frIgnR/bv'
                                     'hTPrWUSDnGw3JGU2xmHrsvyU5xGO8ql6+S0AifPW8kCKpcpEQA7'))

        # First row
        f1 = Frame(self)

        self.bak_frame = LabelFrame(f1, text=_(
            '含有No$GBA footer的NAND备份文件'), padding=(10, 10))

        self.nand_button = Button(
            self.bak_frame, image=self.nand_icon, command=self.change_mode, state=DISABLED)

        self.nand_button.pack(side='left')

        self.nand_file = StringVar()
        self.nandfile = Entry(
            self.bak_frame, textvariable=self.nand_file, state='readonly', width=40)
        self.nandfile.pack(side='left')

        self.chb = Button(self.bak_frame, text='...', command=self.choose_nand)
        self.chb.pack(side='left')

        self.bak_frame.pack(fill=X)

        self.adv_frame = LabelFrame(f1, text=_('存储卡根目录'), padding=(10, 10))

        self.transfer_button = Button(
            self.adv_frame, image=self.nand_icon, command=self.change_mode2, state=DISABLED)

        self.transfer_button.pack(side='left')

        self.sdp = StringVar()
        self.sdpath = Entry(
            self.adv_frame, textvariable=self.sdp, state='readonly', width=40)
        self.sdpath.pack(side='left')

        self.chb1 = Button(self.adv_frame, text='...', command=self.choose_sdp)
        self.chb1.pack(side='left')

        f1.pack(padx=10, pady=10, fill=X)

        # Second row
        f2 = Frame(self)

        self.setup_frame = LabelFrame(f2, text=_('NAND解压选项'), padding=(10, 10))

        self.setup_operation = IntVar()

        if fatcat is None:
            if _7z is not None:
                self.setup_operation.set(1)
            elif osfmount is not None:
                self.setup_operation.set(2)
        else:
            self.setup_operation.set(0)

        self.rb1 = Radiobutton(self.setup_frame, text=_(
            'Fatcat(默认)'), variable=self.setup_operation, value=0)
        self.rb2 = Radiobutton(
            self.setup_frame, text='7-Zip', variable=self.setup_operation, value=1)
        self.rb3 = Radiobutton(self.setup_frame, text=_(
            'OSFMount(需要管理员权限)'), variable=self.setup_operation, value=2)

        self.common_pack(True)

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

        ag_chk = Checkbutton(self.checks_frame, text=_(
            '使用AppGen'), variable=self.appgen)

        ag_chk.pack(padx=10, anchor=W)

        self.devkp = IntVar()
        self.devkp.set(0)

        dkp_chk = Checkbutton(self.checks_frame, text=_(
            '启用系统设置-数据管理功能'), variable=self.devkp)

        dkp_chk.pack(padx=10, anchor=W)

        self.photo = IntVar()
        self.photo.set(0)

        photo_chk = Checkbutton(self.checks_frame, text=_(
            '提取相册分区'), variable=self.photo)

        photo_chk.pack(padx=10, anchor=W)

        self.altdl = IntVar()
        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
            self.altdl.set(1)
        else:
            self.altdl.set(0)

        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
            adl_chk = Checkbutton(
                self.checks_frame, text='优先使用备用载点', variable=self.altdl)
            adl_chk.pack(padx=10, anchor=W)

        self.checks_frame.pack(fill=X)

        self.checks_frame1 = Frame(f2)

        self.ag1_chk = Checkbutton(self.checks_frame1, text=_(
            '使用AppGen'), variable=self.appgen, state=DISABLED)

        self.ag1_chk.pack(padx=10, anchor=W)

        self.updatehiya = IntVar()
        self.updatehiya.set(0)

        self.uh_chk = Checkbutton(self.checks_frame1, text=_(
            '更新hiyaCFW'), variable=self.updatehiya, state=DISABLED)

        self.uh_chk.pack(padx=10, anchor=W)

        self.dkp1_chk = Checkbutton(self.checks_frame1, text=_(
            '启用系统设置-数据管理功能'), variable=self.devkp, state=DISABLED)

        self.dkp1_chk.pack(padx=10, anchor=W)

        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
            adl1_chk = Checkbutton(
                self.checks_frame1, text='优先使用备用载点', variable=self.altdl)
            adl1_chk.pack(padx=10, anchor=W)

        self.checks_frame2 = Frame(f2)

        label = Label(self.checks_frame2, text=_("选择目标系统区域:"))
        label.grid(row=0, column=0, padx=10, sticky="w")
        region_items = ["JPN", "JPN-kst", "USA", "EUR", "AUS", "CHN", "KOR"]
        self.selected_option = StringVar(value="JPN")
        self.dropdown = OptionMenu(self.checks_frame2, self.selected_option, *region_items)
        self.dropdown.grid(row=0, column=1, padx=0, pady=0, sticky="w")

        self.dkp2_chk = Checkbutton(self.checks_frame2, text=_(
            '启用系统设置-数据管理功能'), variable=self.devkp)

        self.dkp2_chk.grid(row=1, column=0, padx=10, sticky="w")

        self.ntm = IntVar()
        self.ntm.set(0)

        self.ntm_chk = Checkbutton(
            self.checks_frame2, text=_('同时安装NTM'), variable=self.ntm)

        self.ntm_chk.grid(row=2, column=0, padx=10, sticky="w")

        self.updatemenu = IntVar()
        self.updatemenu.set(0)

        self.um_chk = Checkbutton(self.checks_frame2, text=_(
            '安装或更新TWiLightMenu++'), variable=self.updatemenu)

        self.um_chk.grid(row=3, column=0, padx=10, sticky="w")

        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
            adl2_chk = Checkbutton(
                self.checks_frame2, text='优先使用备用载点', variable=self.altdl)
            adl2_chk.grid(row=4, column=0, padx=10, sticky="w")

        # NAND operation frame
        self.nand_frame = LabelFrame(f2, text=_('NAND操作选项'), padding=(10, 10))

        self.nand_operation = IntVar()
        self.nand_operation.set(0)

        rb0 = Radiobutton(self.nand_frame, text=_('安装或卸载最新版本的unlaunch'),
                          variable=self.nand_operation, value=2,
                          command=lambda: self.enable_entries(False))
        if osfmount is not None or (sysname == 'Linux' and su is True) or sysname == 'Darwin':
            rb0.pack(anchor=W)
        Radiobutton(self.nand_frame, text=_('移除 No$GBA footer'), variable=self.nand_operation,
                    value=0, command=lambda: self.enable_entries(False)).pack(anchor=W)

        Radiobutton(self.nand_frame, text=_('添加 No$GBA footer'), variable=self.nand_operation,
                    value=1, command=lambda: self.enable_entries(True)).pack(anchor=W)

        fl = Frame(self.nand_frame)

        self.cid_label = Label(fl, text='eMMC CID', state=DISABLED)
        self.cid_label.pack(anchor=W, padx=(24, 0))

        self.cid = StringVar()
        self.cid_entry = Entry(fl, textvariable=self.cid,
                               width=35, state=DISABLED)
        self.cid_entry.pack(anchor=W, padx=(24, 0))

        fl.pack(anchor=W)

        fr = Frame(self.nand_frame)

        self.console_id_label = Label(fr, text='Console ID', state=DISABLED)
        self.console_id_label.pack(anchor=W, padx=(24, 0))

        self.console_id = StringVar()
        self.console_id_entry = Entry(
            fr, textvariable=self.console_id, width=35, state=DISABLED)
        self.console_id_entry.pack(anchor=W, padx=(24, 0))

        fr.pack(anchor=W)

        f2.pack(fill=X)

        # Third row
        f3 = Frame(self)

        self.start_button = Button(f3, text=_(
            '开始'), width=13, command=self.start_point, state=DISABLED)
        self.start_button.pack(side='left', padx=(0, 5))

        self.adv_button = Button(f3, text=_(
            '高级'), command=self.change_mode_adv, width=13)
        self.back_button = Button(f3, text=_(
            '返回'), command=self.change_mode, width=13)
        self.back1_button = Button(f3, text=_(
            '返回'), command=self.change_mode_adv, width=13)
        self.back2_button = Button(f3, text=_(
            '返回'), command=self.change_mode2, width=13)
        self.adv_button.pack(side='left', padx=(0, 0))

        self.exit_button = Button(f3, text=_(
            '退出'), command=root.destroy, width=13)
        self.exit_button.pack(side='left', padx=(5, 0))

        f3.pack(pady=(10, 20))

        self.folders = []
        self.files = []

        # General ToolTip
        ToolTip(ag_chk, text=_('提取Nand备份中的DSiWare软件并复制到\nroms/dsiware'))
        ToolTip(dkp_chk, text=_(
            '勾选此选项将会在CFW中开启系统设置中的数据管理功能，如果已经在NAND中开启了此功能，则不需要勾选此选项'))
        ToolTip(photo_chk, text=_(
            '提取Nand备份中的相册分区文件到存储卡中，此操作会占用一定的存储卡空间(取决于相片数量，最多可达32MB左右)'))
        ToolTip(self.ag1_chk, text=_(
            '提取SDNand中的DSiWare软件并复制到\nroms/dsiware'))
        ToolTip(self.dkp1_chk, text=_(
            '勾选此选项将会在CFW中开启系统设置中的数据管理功能，如果已经在NAND中开启了此功能，则不需要勾选此选项'))
        ToolTip(self.dkp2_chk, text=_(
            '勾选此选项将会在CFW中开启系统设置中的数据管理功能，如果已经在NAND中开启了此功能，则不需要勾选此选项'))
        ToolTip(self.adv_button, text=_('高级模式提供了单独安装TWiLightMenu++等功能'))
        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
            ToolTip(adl_chk, text='使用备用载点可能可以提高下载必要文件的速度')
            ToolTip(adl1_chk, text='使用备用载点可能可以提高下载必要文件的速度')
            ToolTip(adl2_chk, text='使用备用载点可能可以提高下载必要文件的速度')

    ################################################################################################
    def common_pack(self, init):
        if osfmount or _7z is not None:
            if fatcat is not None:
                self.rb1.pack(anchor=W)
            if _7z is not None:
                self.rb2.pack(anchor=W)
            if osfmount is not None:
                self.rb3.pack(anchor=W)
            if (fatcat is not None) or (osfmount and _7z is not None):
                self.setup_frame.pack(padx=10, pady=(0, 10), fill=X)
                if init is True:
                    self.setup_select = True
        if init is not True:
            self.checks_frame.pack(anchor=W)

    def change_mode(self):
        if self.nand_mode:
            self.nand_operation.set(0)
            self.enable_entries(False)
            self.nand_frame.pack_forget()
            self.start_button.pack_forget()
            self.back_button.pack_forget()
            self.exit_button.pack_forget()
            self.common_pack(False)
            self.start_button.pack(side='left', padx=(0, 5))
            self.adv_button.pack(side='left', padx=(0, 0))
            self.exit_button.pack(side='left', padx=(5, 0))
            self.nand_mode = False
        else:
            if askokcancel(_('警告'), (_('你正要进入NAND操作模式, 请确认你知道自己在做什么, 继续吗?')), icon=WARNING):
                self.have_hiya = False
                self.is_tds = False
                self.have_menu = False
                if self.setup_select:
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

    def change_mode_adv(self):
        if self.adv_mode:
            self.transfer_button['state'] = DISABLED
            self.have_menu = False
            self.is_tds = False
            self.have_hiya = False
            self.common_set()
            if self.sdp.get() != '':
                self.sdp.set('')
            self.adv_frame.pack_forget()
            self.checks_frame1.pack_forget()
            self.start_button.pack_forget()
            self.back1_button.pack_forget()
            self.exit_button.pack_forget()
            self.bak_frame.pack(fill=X)
            self.common_pack(False)
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
            self.common_set()
            if self.nand_file.get() != '':
                self.nand_file.set('')
            self.bak_frame.pack_forget()
            if self.setup_select:
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
            self.start_button['state'] = DISABLED
            self.start_button.pack(side='left', padx=(0, 5))
            self.back1_button.pack(side='left', padx=(0, 0))
            self.exit_button.pack(side='left', padx=(5, 0))
            self.adv_mode = True

    def change_mode2(self):
        if self.updatehiya.get() == 1:
            self.updatehiya.set(0)
        if self.updatemenu.get() == 1:
            self.updatemenu.set(0)
        if self.ntm.get() == 1:
            self.ntm.set(0)
        self.start_button.pack_forget()
        self.exit_button.pack_forget()
        if self.transfer_mode:
            self.back2_button.pack_forget()
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
            self.back1_button.pack_forget()
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
                f.seek(0, 0)
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
        self.common_set()
        self.start_button['state'] = (
            NORMAL if self.sd_path1 != '' else DISABLED)
        if self.sd_path1 == '':
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.transfer_button['state'] = DISABLED
            return
        self.check_console(self.sd_path1)
        if self.is_tds:
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.transfer_button['state'] = DISABLED
        elif self.have_hiya:
            self.uh_chk['state'] = NORMAL
            self.dkp1_chk['state'] = NORMAL
            self.ag1_chk['state'] = (
                DISABLED if self.have_menu is True else NORMAL)
            self.transfer_button['state'] = NORMAL
        elif self.have_menu:
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.transfer_button['state'] = DISABLED
        else:
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
            self.transfer_button['state'] = DISABLED

    def choose_nand(self):
        typefilters = [
            ('nand.bin', '*.bin'),
            ('DSi-1.mmc', '*.mmc')
        ]
        if sysname == 'Linux':
            typefilters.append(('*.*', '*.*'))
        name = askopenfilename(filetypes=typefilters)

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
        self.dialog = Toplevel()
        if sysname == 'Windows':
            self.dialog.iconbitmap("icon.ico")
        # Open as dialog (parent disabled)
        self.dialog.grab_set()
        self.dialog.title(_('状态'))
        # Disable maximizing
        self.dialog.resizable(False, False)
        self.dialog.protocol("WM_DELETE_WINDOW", self.closethread)

        frame = Frame(self.dialog, borderwidth=2, relief=SUNKEN)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.log = ThreadSafeText(frame, bd=0, width=52, height=20,
                                  yscrollcommand=scrollbar.set)
        self.log.bind("<Key>", lambda a: "break")
        self.log.pack()

        scrollbar.config(command=self.log.yview)

        frame.pack()

        Button(self.dialog, text=_('关闭'),
               command=self.closethread, width=16).pack(pady=10)

        # Center in window
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        self.dialog.geometry('%dx%d+%d+%d' % (width, height, root.winfo_x() + (root.winfo_width() / 2) -
                                              (width / 2), root.winfo_y() + (root.winfo_height() / 2) - (height / 2)))

        self.finish = False

    def transfer(self):
        showinfo(_('提示'), _('接下来将自动下载目标区域的TWLTransfer镜像文件\n请注意: TWLCFG会被重置'))
        if taskbar is not None:
            taskbar.set_mode(0x1)
        root.after(0, self.log_window)
        while self.dialog is None or self.log is None:
            root.update()
        self.TThread = Thread(target=self.get_transfer_image)
        self.TThread.start()

    def hiya(self):
        if not self.adv_mode:
            if self.setup_operation.get() == 2 or self.nand_operation.get() == 2:
                if sysname == 'Windows' and ctypes.windll.shell32.IsUserAnAdmin() == 0:
                    showerror(_('错误'), _('此功能需要以管理员权限运行本工具'))
                    return

        cid = ""
        console_id = ""
        if not self.nand_mode:
            self.have_hiya = False
            self.is_tds = False
            self.have_menu = False
            if not self.adv_mode:
                showinfo(_('提示'), _('接下来请选择你用来安装自制系统的存储卡路径(或输出路径)\n为了避免 启动错误 请确保目录下无任何文件'))
                self.sd_path = askdirectory(title='')
                # Exit if no path was selected
                if not self.sd_path or self.sd_path == '':
                    return
                self.check_console(self.sd_path)
                if self.is_tds or self.have_hiya:
                    showerror(_('错误'), _('目录检测未通过，若CFW已安装，请转到高级模式，或选择一个空目录以继续'))
                    return
            else:
                self.check_console(self.sd_path1)
        else:
            showinfo(_('提示'), _('接下来请选择一个输出路径'))
            self.out_path = askdirectory(title='')
            if not self.out_path or self.out_path == '':
                return

            # If adding a No$GBA footer, check if CID and ConsoleID values are OK
            if self.nand_operation.get() == 1:
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

        if taskbar is not None:
            taskbar.set_mode(0x1)

        root.after(0, self.log_window)
        while self.dialog is None or self.log is None:
            root.update()

        # Check if we'll be adding a No$GBA footer
        if self.nand_mode and self.nand_operation.get() == 1:
            self.TThread = Thread(target=self.add_footer,
                                  args=(cid, console_id))
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
    def common_set(self):
        if self.appgen.get() == 1:
            self.appgen.set(0)
        if self.devkp.get() == 1:
            self.devkp.set(0)
        if self.updatehiya.get() == 1:
            self.updatehiya.set(0)

    def closethread(self):
        if self.adv_mode:
            self.sd_path1 = ''
            self.sdp.set(self.sd_path1)
            self.common_set()
            self.start_button['state'] = DISABLED
            self.transfer_button['state'] = DISABLED
            self.uh_chk['state'] = DISABLED
            self.dkp1_chk['state'] = DISABLED
            self.ag1_chk['state'] = DISABLED
        if self.dialog is not None:
            self.dialog.destroy()
            self.dialog = None
        if self.finish:
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
                self.unmount_nand_alt()
        else:
            self.clean(True, )

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
                    f.close()
                    self.console_id.set(
                        hexlify(bytearray(reversed(bstr))).upper().decode('ascii'))
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
                    self.log.write(
                        _('错误: 没有检测到No$GBA footer\n警告: 若确定Nand已完整dump, 则用于dump的存储卡极有可能是扩容卡或者已出现坏块'))

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法打开文件 ') +
                           path.basename(self.nand_file.get()))

    def get_transfer_image(self):
        global downloadfile
        if downloadfile is False:
            downloadfile = True

        REGION_CODES_IMAGE = {
            '0F586C0E66BE003A6AB07DB5049B0DD7394FD865': 'CHN',
            'EB2CEEB17490D008B311447AFB1387C70B6A109F': 'USA',
            '7BEC0FAC573FBB1C3A2409ECE1BAEDFF0B0360FF': 'JPN',
            'EB5DE62ECA3A61555752A6D4BB7840AF7E669F30': 'KOR',
            'F30A1E5C8868A027B94553227F86E7F0A36FC2E4': 'EUR',
            'BA21D4BB03ECAEE236EFD6C741E57E1202671B72': 'AUS',
            'BE881A6FC3829424849DD53550086BF012AA1667': 'JPN-kst'
        }
        REGION_HWINFO = {
            '00': 'JPN',
            '01': 'USA',
            '02': 'EUR',
            '03': 'AUS',
            '04': 'CHN',
            '05': 'KOR'
        }

        filename = self.selected_option.get() + '.bin'
        try:
            if not path.isfile(filename):
                self.log.write(_('正在下载 TWLTransfer 镜像文件: ') + filename)
                with urlopen('https://gitee.com/ryatian/mirrors/releases/download/TWLTransfer/' +
                                filename) as src, open(filename, 'wb') as dst:
                    copyfileobj(src, dst)

        except SystemExit:
            return

        except (URLError, IOError) as e:
            printl(str(e))
            self.log.write(_('错误: 无法下载 TWLTransfer 镜像文件'))
            return

        self.image_file.set(filename)
        image_filename = path.basename(filename)
        try:
            sha1_hash = sha1()

            with open(self.image_file.get(), 'rb') as f:
                sha1_hash.update(f.read())
                f.close()

            image_sha1 = hexlify(sha1_hash.digest()).upper().decode('ascii')

            try:
                self.dest_region = REGION_CODES_IMAGE[image_sha1]
            except SystemExit:
                return
            except:
                self.log.write(_('错误: 无效的镜像文件'))
                remove(self.image_file.get())
                return

            self.log.write('- ' + image_filename + ' SHA1:\n' + image_sha1)
            self.log.write(_('目标系统: ') + self.dest_region)

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法打开文件 ') + image_filename)
            return

        hwinfo = path.join(self.sd_path1, 'sys', 'HWINFO_S.dat')
        if path.exists(hwinfo):
            with open(hwinfo, 'rb') as infotmp:
                infotmp.seek(0x90, 0)
                self.cur_region = REGION_HWINFO[hexlify(
                    infotmp.read(0x01)).decode('ascii')]
                infotmp.close()
                self.log.write(_('当前区域: ') + self.cur_region)
        else:
            self.log.write(_('错误: 无法检测系统区域'))
            return

        self.origin_region = self.check_serial(self.sd_path1)
        self.log.write(_('原始区域: ') + self.origin_region)

        self.TThread = Thread(target=self.get_common_data)
        self.TThread.start()

    ################################################################################################
    def get_latest_hiyacfw(self):
        global downloadfile
        if downloadfile is False:
            downloadfile = True
        filename = 'hiyaCFW.7z'
        self.files.append(filename)
        self.folders.append('for PC')
        self.folders.append('for SDNAND SD card')

        try:
            if not path.isfile(filename):
                self.log.write(_('正在下载最新版本的hiyaCFW...'))
                if self.altdl.get() == 1:
                    with urlopen('https://gitee.com/ryatian/mirrors/releases/download/Res/' +
                                 filename) as src, open(filename, 'wb') as dst:
                        copyfileobj(src, dst)
                else:
                    try:
                        with urlopen('https://github.com/DS-Homebrew/hiyaCFW/releases/latest/download/' +
                                     filename) as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
                            with urlopen('https://gitee.com/ryatian/mirrors/releases/download/Res/' +
                                         filename) as src, open(filename, 'wb') as dst:
                                copyfileobj(src, dst)
                        else:
                            raise IOError

            self.log.write(_('- 正在解压 hiyaCFW 压缩包...'))

            if self.adv_mode and self.updatehiya.get() == 1:
                self.proc = Popen(
                    [_7za, 'x', '-bso0', '-y', filename, 'for SDNAND SD card'])
            else:
                self.proc = Popen(
                    [_7za, 'x', '-bso0', '-y', filename, 'for PC', 'for SDNAND SD card'])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.adv_mode and self.updatehiya.get() == 1:
                    self.TThread = Thread(target=self.get_launcher)
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
            self.proc = Popen([twltool, 'boot2', '--in', self.nand_file.get()])

            ret_val = self.proc.wait()

            if ret_val == 0:
                # Hash arm7.bin
                sha1_hash = sha1()

                with open('arm7.bin', 'rb') as f:
                    sha1_hash.update(f.read())
                    f.close()
                self.log.write('- arm7.bin SHA1:\n  ' +
                               hexlify(sha1_hash.digest()).upper().decode('ascii'))

                # Hash arm9.bin
                sha1_hash = sha1()

                with open('arm9.bin', 'rb') as f:
                    sha1_hash.update(f.read())
                    f.close()
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
                f.close()
            self.log.write('- Patched arm7.bin SHA1:\n  ' +
                           hexlify(sha1_hash.digest()).upper().decode('ascii'))

            # Hash arm9.bin
            sha1_hash = sha1()

            with open('arm9.bin', 'rb') as f:
                sha1_hash.update(f.read())
                f.close()
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
                f.close()

            with open('arm9.bin', 'wb') as f:
                with open(path.join('for PC', 'bootloader files',
                                    'bootloader arm9 append to start.bin'), 'rb') as pre:
                    f.write(pre.read())
                    pre.close()
                f.write(data)
                f.close()

            # Hash arm9.bin
            sha1_hash = sha1()

            with open('arm9.bin', 'rb') as f:
                sha1_hash.update(f.read())
                f.close()
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
               ndsblc)

        try:
            if sysname == 'Windows':
                printl(_('调用 ndstool(生成 bootloader)'))
            else:
                printl(_('调用 ndsblc(生成 bootloader)'))
            self.proc = Popen([exe, '-c', 'bootloader.nds', '-9', 'arm9.bin', '-7', 'arm7.bin', '-t',
                               path.join('for PC', 'bootloader files',
                                         'banner.bin'), '-h',
                               path.join('for PC', 'bootloader files', 'header.bin')])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if sysname == 'Linux' and ug is not None and su is True:  # chown on Linux if with sudo
                    Popen(['chown', '-R', ug + ':' + ug, 'bootloader.nds']).wait()
                # Hash bootloader.nds
                sha1_hash = sha1()

                with open('bootloader.nds', 'rb') as f:
                    sha1_hash.update(f.read())
                    f.close()
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
            self.proc = Popen([twltool, 'nandcrypt', '--in', self.nand_file.get(), '--out',
                               self.console_id.get() + '.img'])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.nand_operation.get() == 2 or self.setup_operation.get() == 2:
                    self.TThread = Thread(target=self.mount_nand)
                    self.TThread.start()
                else:
                    self.TThread = Thread(target=self.extract_nand_alt if (
                            sysname == 'Windows' and self.setup_operation.get() == 1) else self.extract_nand)
                    self.TThread.start()
            else:
                self.log.write(_('错误: 解密失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + twltool)
            Thread(target=self.clean, args=(True,)).start()

    ################################################################################################
    def extract_nand_alt(self):
        self.files.append('0.fat')
        self.files.append('1.fat')
        self.log.write(_('正在从NAND中解压文件...'))

        try:
            printl(_('调用 7-Zip(解压 NAND)'), fixn=True)
            if self.photo.get() == 1:
                self.proc = Popen(
                    [_7z, 'x', '-bso0', '-y', self.console_id.get() + '.img', '0.fat', '1.fat'])
            else:
                self.proc = Popen(
                    [_7z, 'x', '-bso0', '-y', self.console_id.get() + '.img', '0.fat'])

            ret_val = self.proc.wait()

            if ret_val == 0:

                self.proc = Popen(
                    [_7z, 'x', '-bso0', '-y', '-o' + self.sd_path, '0.fat'])

                ret_val = self.proc.wait()

                if ret_val == 0:
                    if self.photo.get() == 1:
                        self.proc = Popen(
                            [_7z, 'x', '-bso0', '-y', '-o' + self.sd_path, '1.fat'])
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
        exe = ""

        try:
            if sysname == 'Windows':
                printl(_('调用 osfmount(挂载 twln)'), fixn=True)
                exe = osfmount
                cmd = [exe, '-a', '-t', 'file', '-f', self.console_id.get() + '.img', '-m',
                       '#:', '-o', 'ro,rem']

                if self.nand_mode:
                    cmd[-1] = 'rw,rem'

                self.proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                outs, errs = self.proc.communicate()
                print(outs.decode('utf-8').strip())

                if self.proc.returncode == 0:
                    self.mounted = search(
                        r'[a-zA-Z]:\s', outs.decode('utf-8')).group(0).strip()
                    self.log.write(_('- 挂载到驱动器 ') + self.mounted)
                    if self.nand_mode is False and self.photo.get() == 1:
                        printl(_('调用 osfmount(挂载 twlp)'))
                        cmd = [exe, '-a', '-t', 'file', '-f', self.console_id.get() + '.img', '-m',
                               '#:', '-v', '2', '-o', 'ro,rem']
                        self.proc = Popen(
                            cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        outs, errs = self.proc.communicate()
                        print(outs.decode('utf-8').strip())

                        if self.proc.returncode == 0:
                            self.twlp = search(
                                r'[a-zA-Z]:\s', outs.decode('utf-8')).group(0).strip()
                            self.log.write(_('- DSi相册分区挂载到驱动器 ') + self.twlp)
                        else:
                            self.log.write(_('错误: 挂载相册分区失败'))
                            Thread(target=self.clean, args=(True,)).start()
                            return
                else:
                    self.log.write(_('错误: 挂载失败'))
                    Thread(target=self.clean, args=(True,)).start()
                    return
            elif sysname == 'Linux':
                printl(_('调用 losetup(挂载 loop device)'), fixn=True)
                exe = 'losetup'
                cmd = [exe, '-P', '-f', '--show',
                       self.console_id.get() + '.img']

                self.proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                outs, errs = self.proc.communicate()

                if self.proc.returncode == 0:
                    self.loop_dev = search(
                        r'\/dev\/loop\d+', outs.decode('utf-8')).group(0).strip()
                    self.log.write(_('- 挂载loop device到 ') + self.loop_dev)
                    printl(_('调用 mount(挂载分区)'))
                    exe = 'mount'
                    self.mounted = '/mnt'
                    cmd = [exe, '-t', 'vfat',
                           self.loop_dev + 'p1', self.mounted]

                    self.proc = Popen(cmd)
                    ret_val = self.proc.wait()

                    if ret_val == 0:
                        self.log.write(_('- 挂载分区到 ') + self.mounted)
                    else:
                        self.log.write(_('错误: 挂载失败'))
                        Thread(target=self.clean, args=(True,)).start()
                        return
                else:
                    self.log.write(_('错误: 挂载失败'))
                    Thread(target=self.clean, args=(True,)).start()
                    return
            elif sysname == 'Darwin':
                exe = 'hdiutil'
                cmd = [exe, 'attach', '-imagekey', 'diskimage-class=CRawDiskImage', '-nomount',
                       self.console_id.get() + '.img']

                self.proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                outs, errs = self.proc.communicate()
                print(outs.decode('utf-8').strip())

                if self.proc.returncode == 0:
                    self.raw_disk = search(
                        r'^\/dev\/disk\d+', outs.decode('utf-8')).group(0).strip()
                    self.log.write(_('- 挂载raw disk到 ') + self.raw_disk)

                    cmd = [exe, 'mount', self.raw_disk + 's1']

                    self.proc = Popen(
                        cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    outs, errs = self.proc.communicate()

                    if self.proc.returncode == 0:
                        self.mounted = search(
                            r'\/Volumes\/.+', outs.decode('utf-8')).group(0).strip()
                        self.log.write(_('- 挂载卷到 ') + self.mounted)
                    else:
                        self.log.write(_('错误: 挂载失败'))
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
            self.log.write(_('错误: 无法运行 ') + exe)
            Thread(target=self.clean, args=(True,)).start()

    ################################################################################################
    def extract_nand(self):
        self.log.write(_('正在从NAND中解压文件...'))

        try:
            printl(_('调用 fatcat(解压 NAND)'), fixn=True)
            # DSi first partition offset: 0010EE00h
            self.proc = Popen([fatcat, '-O', '1109504', '-x', self.sd_path,
                               self.console_id.get() + '.img'])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.photo.get() == 1:
                    # DSi photo partition offset: 0CF09A00h
                    self.proc = Popen([fatcat, '-O', '217094656', '-x', self.sd_path,
                                       self.console_id.get() + '.img'])
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
        try:
            copytree(self.mounted, self.sd_path, dirs_exist_ok=True)
            if self.nand_mode is False and self.photo.get() == 1:
                copytree(self.twlp, self.sd_path, dirs_exist_ok=True)
            self.TThread = Thread(target=self.unmount_nand)
            self.TThread.start()
        except SystemExit:
            return
        except:
            self.log.write(_('错误: 复制失败'))
            self.TThread = Thread(target=self.unmount_nand_alt)
            self.TThread.start()

    ################################################################################################
    def get_launcher(self):
        app = self.detect_region()

        # Stop if no supported region was found
        if not app:
            Thread(target=self.clean, args=(True,)).start()
            return

        global downloadfile
        if downloadfile is False:
            downloadfile = True

        # Delete contents of the launcher folder as it will be replaced by the one from hiyaCFW
        launcher_folder = path.join(
            self.sd_path, 'title', '00030017', app, 'content')

        # Walk through all files in the launcher content folder
        for file in listdir(launcher_folder):
            file = path.join(launcher_folder, file)

            if ((_7z is not None and self.setup_operation.get() == 1) or
                    (osfmount is not None and self.setup_operation.get() == 2)):
                chmod(file, 438)
            # Workaround for issue #10
            try:
                remove(file)
            except FileNotFoundError:
                pass

        # noinspection PyExceptClausesOrder
        try:
            if not path.isfile(self.launcher_region):
                self.log.write(_('正在下载 ') + self.launcher_region + ' Launcher...')
                if self.altdl.get() == 1:
                    with urlopen('https://gitee.com/ryatian/mirrors/releases/download/Res/' +
                                 self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                        copyfileobj(src, dst)
                else:
                    try:
                        with urlopen('https://raw.githubusercontent.com/R-YaTian/TWLMagician/main/launchers/' +
                                     self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
                            with urlopen('https://gitee.com/ryatian/mirrors/releases/download/Res/' +
                                         self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                                copyfileobj(src, dst)
                        else:
                            with urlopen('https://gitlab.com/R-YaTian/twlmagician/-/raw/main/launchers/' +
                                         self.launcher_region) as src, open(self.launcher_region, 'wb') as dst:
                                copyfileobj(src, dst)

            if sysname == 'Linux' and ug is not None and su is True:  # chown on Linux if with sudo
                Popen(['chown', '-R', ug + ':' + ug, self.launcher_region]).wait()

            self.log.write(_('- 正在解压Launcher...'))

            if self.launcher_region in ('CHN', 'KOR'):
                launcher_app = '00000000.app'
            elif self.launcher_region == 'USA-dev':
                launcher_app = '7412e50d.app'
            elif self.launcher_region == 'JPN-dev':
                launcher_app = '3ed2df76.app'
            elif self.launcher_region == 'EUR-dev':
                launcher_app = '0ac9cea3.app'
            else:
                launcher_app = '00000002.app'
            self.files.append(launcher_app)

            # Prepare decryption params
            params = [_7za, 'x', '-bso0', '-y', '-p' + app.lower(), self.launcher_region,
                      launcher_app]

            if self.launcher_region in ('USA-dev', 'JPN-dev', 'EUR-dev'):
                params.append('title.tmd')
                self.files.append('title.tmd')

            self.proc = Popen(params)

            ret_val = self.proc.wait()

            if ret_val == 0:

                # Hash launcher app
                sha1_hash = sha1()

                with open(launcher_app, 'rb') as f:
                    sha1_hash.update(f.read())
                    f.close()
                self.log.write('- Patched Launcher SHA1:\n  ' +
                               hexlify(sha1_hash.digest()).upper().decode('ascii'))

                if self.adv_mode and self.updatehiya.get() == 1:
                    self.TThread = Thread(target=self.update_hiyacfw)
                    self.TThread.start()
                else:
                    self.TThread = Thread(target=self.install_hiyacfw, args=(
                        launcher_app, launcher_folder, app))
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

        copytree(path.join('for SDNAND SD card', 'hiya'),
                 path.join(self.sd_path, 'hiya'), dirs_exist_ok=True)
        copytree(path.join('for SDNAND SD card', 'photo'),
                 path.join(self.sd_path, 'photo'), dirs_exist_ok=True)
        copyfile(path.join('for SDNAND SD card', 'hiya.dsi'),
                 path.join(self.sd_path, 'hiya.dsi'))
        copyfile('bootloader.nds', path.join(
            self.sd_path, 'hiya', 'bootloader.nds'))
        copyfile(launcher_app, path.join(launcher_folder, launcher_app))

        tmd_src = path.join('for SDNAND SD card', 'title',
                            '00030017', app, 'content', 'title.tmd')
        if launcher_app == '7412e50d.app':
            copyfile('title.tmd', path.join(launcher_folder, 'title.tmd'))
        else:
            copyfile(tmd_src, path.join(launcher_folder, 'title.tmd'))

        if self.devkp.get() == 1:
            self.make_dekp(self.sd_path)

        self.TThread = Thread(
            target=self.get_latest_twilight if self.twilight.get() == 1 else self.clean)
        self.TThread.start()

    def update_hiyacfw(self):
        self.log.write(_('正在更新hiyaCFW...'))

        copyfile(path.join('for SDNAND SD card', 'hiya.dsi'),
                 path.join(self.sd_path1, 'hiya.dsi'))

        self.TThread = Thread(target=self.get_latest_twilight)
        self.TThread.start()

    def check_serial(self, infopath):
        REGION_SERIAL = {
            'J': 'JPN',
            'W': 'USA',
            'B': 'USA',
            'S': 'USA',
            'E': 'EUR',
            'A': 'AUS',
            'C': 'CHN',
            'K': 'KOR'
        }
        hwinfo = path.join(infopath, 'sys', 'HWINFO_S.dat')
        if path.exists(hwinfo):
            with open(hwinfo, 'rb') as infotmp:
                infotmp.seek(0x91, 0)
                strtmp = infotmp.read(0xB).decode('ascii')
                infotmp.close()
                self.log.write(_('机器序列号: ') + strtmp)
                return REGION_SERIAL[strtmp[1:2]]

    ################################################################################################
    def get_latest_twilight(self):
        global downloadfile
        if downloadfile is False:
            downloadfile = True
        filename = 'TWiLightMenu-DSi.7z' if self.is_tds is False else 'TWiLightMenu-3DS.7z'
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
                        with urlopen('https://spin.noidea.top/somefiles/' +
                                     filename) as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        with urlopen('https://gitee.com/ryatian/mirrors/releases/download/latest/' +
                                     filename) as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                else:
                    try:
                        with urlopen('https://github.com/DS-Homebrew/TWiLightMenu/releases/latest/download/' +
                                     filename) as src, open(filename, 'wb') as dst:
                            copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
                            try:
                                with urlopen('https://spin.noidea.top/somefiles/' +
                                             filename) as src, open(filename, 'wb') as dst:
                                    copyfileobj(src, dst)
                            except SystemExit:
                                return
                            except:
                                with urlopen('https://gitee.com/ryatian/mirrors/releases/download/latest/'
                                             + filename) as src, open(filename, 'wb') as dst:
                                    copyfileobj(src, dst)
                        else:
                            raise IOError

            self.log.write(_('- 正在解压 ') + filename[:-3] + _(' 压缩包...'))

            if self.is_tds is False:
                self.proc = Popen([_7za, 'x', '-bso0', '-y', filename, '_nds', 'title',
                                   'hiya', 'roms', 'BOOT.NDS', 'snemul.cfg', 'version.txt'])
            else:
                self.proc = Popen([_7za, 'x', '-bso0', '-y', filename, '_nds', 'TWiLight Menu - Game booter.cia',
                                   'TWiLight Menu.cia', 'roms', 'BOOT.NDS', 'snemul.cfg', 'version.txt'])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.transfer_mode and self.updatemenu.get() == 1:
                    self.TThread = Thread(target=self.decrypt_image)
                    self.TThread.start()
                else:
                    self.TThread = Thread(
                        target=self.install_twilight, args=(filename[:-3],))
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

        if not self.adv_mode:
            copytree('_nds', path.join(self.sd_path, '_nds'), dirs_exist_ok=True)
            copytree('title', path.join(self.sd_path, 'title'), dirs_exist_ok=True)
            try:
                copytree('hiya', path.join(self.sd_path, 'hiya'), dirs_exist_ok=True)
            except FileNotFoundError:
                pass
            copytree('roms', path.join(self.sd_path, 'roms'), dirs_exist_ok=True)
            copyfile('BOOT.NDS', path.join(self.sd_path, 'BOOT.NDS'))
            copyfile('snemul.cfg', path.join(self.sd_path, 'snemul.cfg'))
        else:
            if self.updatehiya.get() == 1:
                copytree('title', path.join(self.sd_path1, 'title'), dirs_exist_ok=True)
            copytree('_nds', path.join(self.sd_path1, '_nds'), dirs_exist_ok=True)
            copytree('roms', path.join(self.sd_path1, 'roms'), dirs_exist_ok=True)
            copyfile('BOOT.NDS', path.join(self.sd_path1, 'BOOT.NDS'))
            copyfile('snemul.cfg', path.join(self.sd_path1, 'snemul.cfg'))
            if self.is_tds is True:
                cias = path.join(self.sd_path1, 'cias')
                if not path.exists(cias):
                    mkdir(cias)
                copyfile('TWiLight Menu.cia', path.join(
                    self.sd_path1, 'cias', 'TWiLight Menu.cia'))
                copyfile('TWiLight Menu - Game booter.cia',
                         path.join(self.sd_path1, 'cias', 'TWiLight Menu - Game booter.cia'))

        self.read_ver()

        if self.appgen.get() == 1:
            printl(_('调用 appgen'))
            if not self.adv_mode:
                agen(path.join(self.sd_path, 'title', '00030004'),
                     path.join(self.sd_path, 'roms'))
            else:
                agen(path.join(self.sd_path1, 'title', '00030004'),
                     path.join(self.sd_path1, 'roms'))
        if self.adv_mode and self.devkp.get() == 1:
            self.make_dekp(self.sd_path1)
        if self.adv_mode and self.have_hiya is True:
            self.check_serial(self.sd_path1)

        Thread(target=self.clean).start()

    def read_ver(self):
        with open('version.txt', 'r') as ver:
            tmpstr = ver.readline()
            tmpstr1 = ver.readline()
            ver.close()
            tmpstr1 = tmpstr1.replace('\n', '')
            self.log.write(_('版本信息:\n') + tmpstr + tmpstr1)

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
            if taskbar is not None:
                taskbar.set_value(100, 100)
                taskbar.set_mode(0x4)
                sleep(0.5)
                taskbar.set_mode(0)
            return

        if self.nand_mode:
            ofilename = self.console_id.get() + self.suffix + '.bin'
            file = path.join(self.out_path, ofilename)
            copyfile(self.console_id.get() + '.img', file)
            if sysname == 'Linux' and ug is not None and su is True:  # chown on Linux if with sudo
                Popen(['chown', '-R', ug + ':' + ug, file]).wait()
            remove(self.console_id.get() + '.img')
            self.log.write(_('完成!\n修改后的NAND已保存为') + ofilename + '\n')
            if taskbar is not None:
                taskbar.set_mode(0)
            return

        if sysname == 'Linux' and ug is not None and su is True:  # chown on Linux if with sudo
            if self.adv_mode or self.transfer_mode:
                Popen(['chown', '-R', ug + ':' + ug, self.sd_path1]).wait()
            else:
                Popen(['chown', '-R', ug + ':' + ug, self.sd_path]).wait()

        if sysname == 'Darwin':
            from rmdot_files.rmdot_files import rmdot_
            if self.adv_mode or self.transfer_mode:
                out = rmdot_(self.sd_path1)
            else:
                out = rmdot_(self.sd_path)
            if out == 1:
                self.log.write(_("'._' 文件清理完毕"))

        if self.adv_mode and self.is_tds:
            self.log.write(
                _('完成!\n弹出你的存储卡并插回到机器中\n对于3DS设备, 你还需要在机器上使用FBI完成Title的安装\n'))
        else:
            self.log.write(_('完成!\n弹出你的存储卡并插回到机器中\n'))
        if taskbar is not None:
            taskbar.set_mode(0)

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

        while patchfile.tell() not in [patch_size, patch_size - 3]:
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
    @staticmethod
    def unpack_int(bstr):
        # Read an n-byte big-endian integer from a byte string
        (ret_val,) = unpack_from('>I', b'\x00' * (4 - len(bstr)) + bstr)
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
            '484e414a': 'JPN-dev',
            '484e4150': 'EUR-dev'
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
                                    self.launcher_region = REGION_CODES[app.lower(
                                    )]
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
            self.TThread = Thread(target=self.unmount_nand_alt)
            self.TThread.start()
            return

        global downloadfile
        if downloadfile is False:
            downloadfile = True

        tmd = path.join(self.mounted, 'title', '00030017',
                        app, 'content', 'title.tmd')

        tmd_size = path.getsize(tmd)

        if tmd_size == 520:
            self.log.write(_('- 未安装...'))

            # noinspection PyExceptClausesOrder
            try:
                if not path.exists(filename):
                    self.log.write(_('正在下载最新版本的unlaunch...'))
                    try:
                        if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
                            with urlopen('https://gitee.com/ryatian/mirrors/releases/download/Res/unlaunch.zip'
                                         ) as src, open(filename, 'wb') as dst:
                                copyfileobj(src, dst)
                        else:
                            with urlopen('https://raw.githubusercontent.com/R-YaTian/TWLMagician/main/Res/unlaunch.zip'
                                         ) as src, open(filename, 'wb') as dst:
                                copyfileobj(src, dst)
                    except SystemExit:
                        return
                    except:
                        raise IOError

                if sysname == 'Linux' and ug is not None and su is True:  # chown on Linux if with sudo
                    Popen(['chown', '-R', ug + ':' + ug, filename]).wait()

                self.proc = Popen(
                    [_7za, 'x', '-bso0', '-y', filename, 'UNLAUNCH.DSI'])

                ret_val = self.proc.wait()

                if ret_val == 0:
                    self.log.write(_('- 正在安装unlaunch...'))

                    self.suffix = '-unlaunch'

                    with open(tmd, 'ab') as f:
                        with open('UNLAUNCH.DSI', 'rb') as unl:
                            f.write(unl.read())
                            unl.close()
                        f.close()

                    self.check_serial(self.mounted)
                    self.make_dekp(self.mounted)

                    # Set files as read-only
                    for file in listdir(path.join(self.mounted, 'title', '00030017', app,
                                                  'content')):
                        file = path.join(self.mounted, 'title',
                                         '00030017', app, 'content', file)
                        if sysname == 'Darwin':
                            Popen(['chflags', 'uchg', file]).wait()
                        elif sysname == 'Linux':
                            Popen(
                                [path.join('Linux', 'fatattr'), '+R', file]).wait()
                        else:
                            chmod(file, 292)

                else:
                    self.log.write(_('错误: 解压失败'))
                    self.TThread = Thread(target=self.unmount_nand_alt)
                    self.TThread.start()
                    return

            except IOError as e:
                printl(str(e))
                self.log.write(_('错误: 无法下载 unlaunch'))
                self.TThread = Thread(target=self.unmount_nand_alt)
                self.TThread.start()
                return

            except OSError as e:
                printl(str(e))
                self.log.write(_('错误: 无法运行 ') + _7za)
                self.TThread = Thread(target=self.unmount_nand_alt)
                self.TThread.start()
                return

        else:
            self.log.write(_('- 已安装, 卸载中...'))

            self.suffix = '-no-unlaunch'

            # Set files as read-write
            for file in listdir(path.join(self.mounted, 'title', '00030017', app, 'content')):
                file = path.join(self.mounted, 'title',
                                 '00030017', app, 'content', file)
                if sysname == 'Darwin':
                    Popen(['chflags', 'nouchg', file]).wait()
                elif sysname == 'Linux':
                    Popen([path.join('Linux', 'fatattr'), '-R', file]).wait()
                else:
                    chmod(file, 438)

            with open(tmd, 'r+b') as f:
                f.truncate(520)
                f.close()

            self.check_serial(self.mounted)
            self.make_dekp(self.mounted)

        self.TThread = Thread(target=self.unmount_nand)
        self.TThread.start()

    ################################################################################################
    def unmount_nand(self):
        self.log.write(_('正在卸载NAND...'))
        exe = ""

        try:
            if sysname == 'Windows':
                printl(_('调用 osfmount(卸载 twln)'))
                exe = osfmount
                self.proc = Popen([exe, '-D', '-m', self.mounted])
            elif sysname == 'Darwin':
                printl(_('调用 hdiutil(卸载 raw disk)'))
                exe = 'hdiutil'
                self.proc = Popen([exe, 'detach', self.raw_disk])
            elif sysname == 'Linux':
                printl(_('调用 umount(卸载分区)'))
                exe = 'umount'
                self.proc = Popen([exe, self.mounted])
                ret_val = self.proc.wait()
                if ret_val == 0:
                    printl(_('调用 losetup(卸载 loop device)'))
                    exe = 'losetup'
                    self.proc = Popen([exe, '-d', self.loop_dev])
                else:
                    self.log.write(_('错误: 卸载失败'))
                    Thread(target=self.clean, args=(True,)).start()
                    return

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.nand_mode is False and self.photo.get() == 1:
                    printl(_('调用 osfmount(卸载 twlp)'))
                    self.proc = Popen([osfmount, '-D', '-m', self.twlp])
                    ret_val = self.proc.wait()
                    if ret_val == 0:
                        self.TThread = Thread(
                            target=self.encrypt_nand if self.nand_mode else self.get_launcher)
                        self.TThread.start()
                    else:
                        self.log.write(_('错误: 卸载相册分区失败'))
                        Thread(target=self.clean, args=(True,)).start()
                else:
                    self.TThread = Thread(
                        target=self.encrypt_nand if self.nand_mode else self.get_launcher)
                    self.TThread.start()
            else:
                self.log.write(_('错误: 卸载失败'))
                Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + exe)
            Thread(target=self.clean, args=(True,)).start()

    def unmount_nand_alt(self):
        self.log.write(_('正在强制卸载NAND...'))
        exe = ""

        try:
            if sysname == 'Windows':
                printl(_('调用 osfmount(强制卸载 twln)'))
                exe = osfmount
                self.proc = Popen([exe, '-D', '-m', self.mounted])
            elif sysname == 'Darwin':
                printl(_('调用 hdiutil(强制卸载 raw disk)'))
                exe = 'hdiutil'
                self.proc = Popen([exe, 'detach', self.raw_disk])
            elif sysname == 'Linux':
                printl(_('调用 umount(强制卸载分区)'))
                exe = 'umount'
                self.proc = Popen([exe, self.mounted])
                ret_val = self.proc.wait()
                if ret_val == 0:
                    printl(_('调用 losetup(强制卸载 loop device)'))
                    exe = 'losetup'
                    self.proc = Popen([exe, '-d', self.loop_dev])
                else:
                    self.log.write(_('错误: 卸载失败或尚未挂载'))
                    Thread(target=self.clean, args=(True,)).start()
                    return

            ret_val = self.proc.wait()

            if ret_val != 0:
                self.log.write(_('错误: 卸载失败或尚未挂载'))

            if self.nand_mode is False and self.photo.get() == 1:
                printl(_('调用 osfmount(强制卸载 twlp)'))
                self.proc = Popen([osfmount, '-D', '-m', self.twlp])
                ret_val = self.proc.wait()
                if ret_val != 0:
                    self.log.write(_('错误: 卸载相册分区失败或尚未挂载'))

            Thread(target=self.clean, args=(True,)).start()

        except OSError as e:
            printl(str(e))
            self.log.write(_('错误: 无法运行 ') + exe)
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
            self.proc = Popen([twltool, 'nandcrypt', '--in',
                               self.console_id.get() + '.img'])

            ret_val = self.proc.wait()

            if ret_val == 0:
                printl(_('操作成功完成'), fixn=True)
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

        ofilename = self.console_id.get() + '-no-footer.bin'
        file = path.join(self.out_path, ofilename)

        try:
            copyfile(self.nand_file.get(), file)

            # Back-up footer info
            info_file = path.join(self.out_path, self.console_id.get() + '-info.txt')
            with open(info_file, 'w', encoding="UTF-8") as f:
                f.write('eMMC CID: ' + self.cid.get() + '\n')
                f.write('Console ID: ' + self.console_id.get() + '\n')
                f.close()

            with open(file, 'r+b') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Remove footer
                f.truncate()
                f.close()
            self.finish = True
            if sysname == 'Linux' and ug is not None and su is True:  # chown on Linux if with sudo
                Popen(['chown', '-R', ug + ':' + ug, file]).wait()
                Popen(['chown', '-R', ug + ':' + ug, info_file]).wait()
            self.log.write(_('完成!\n修改后的NAND已保存为\n') + ofilename +
                           _('\nfooter信息已保存为 ') + self.console_id.get() + '-info.txt\n')

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法打开 ') +
                           path.basename(self.nand_file.get()))

    ################################################################################################
    def add_footer(self, cid, console_id):
        self.log.write(_('正在添加No$GBA footer...'))

        ofilename = self.console_id.get() + '-footer.bin'
        file = path.join(self.out_path, ofilename)

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
                f.close()
            self.finish = True
            if sysname == 'Linux' and ug is not None and su is True:  # chown on Linux if with sudo
                Popen(['chown', '-R', ug + ':' + ug, file]).wait()
            self.log.write(_('完成!\n修改后的NAND已保存为\n') + ofilename + '\n')

        except IOError as e:
            printl(str(e))
            self.log.write(_('错误: 无法打开 ') +
                           path.basename(self.nand_file.get()))

    ################################################################################################
    def get_common_data(self):
        global downloadfile
        if downloadfile is False:
            downloadfile = True
        self.folders.append('hiya')
        self.folders.append('title')
        self.folders.append('ticket')
        self.folders.append('NTM')

        try:
            if not path.isfile('Common.dat'):
                self.log.write(_('正在下载通用数据...'))
                if loc == 'zh_cn' or (loca == 'zh_hans' and region == 'cn'):
                    with urlopen('https://gitee.com/ryatian/mirrors/releases/download/Res/Common.dat'
                                ) as src, open('Common.dat', 'wb') as dst:
                        copyfileobj(src, dst)
                else:
                    with urlopen('https://raw.githubusercontent.com/R-YaTian/TWLMagician/main/Res/Common.dat'
                                ) as src, open('Common.dat', 'wb') as dst:
                        copyfileobj(src, dst)

            if sysname == 'Linux' and ug is not None and su is True:  # chown on Linux if with sudo
                Popen(['chown', '-R', ug + ':' + ug, 'Common.dat']).wait()

            self.log.write(_('- 正在解压通用数据...'))

            if self.ntm.get() == 1:
                self.proc = Popen([_7za, 'x', '-bso0', '-y', '-pR-YaTian',
                                   'Common.dat', 'hiya', 'title', 'ticket', 'NTM'])
            else:
                self.proc = Popen(
                    [_7za, 'x', '-bso0', '-y', '-pR-YaTian', 'Common.dat', 'hiya', 'title', 'ticket'])

            ret_val = self.proc.wait()

            if ret_val == 0:
                if self.updatemenu.get() == 1:
                    self.TThread = Thread(target=self.get_latest_twilight)
                    self.TThread.start()
                else:
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
        self.folders.append('shared1')
        self.folders.append('sys')
        self.folders.append('title')
        self.folders.append('ticket')
        self.log.write(_('正在解密TWLTransfer镜像文件...'))

        try:
            self.proc = Popen([_7za, 'x', '-bso0', '-y', '-pR-YaTian', self.image_file.get(),
                               'shared1', 'sys', 'title', 'ticket'])

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
        TITLE_ID_BYTE = {
            'CHN': '43',
            'USA': '45',
            'JPN': '4a',
            'JPN-kst': '4a',
            'KOR': '4b',
            'EUR': '50',
            'AUS': '55'
        }
        REGION_BYTES = {
            'JPN': '00',
            'JPN-kst': '00',
            'USA': '01',
            'EUR': '02',
            'AUS': '03',
            'CHN': '04',
            'KOR': '05'
        }

        self.log.write(_('正在执行TWLTransfer...'))

        oldfolders = [path.join(self.sd_path1, 'title', '0003000f'), path.join(self.sd_path1, 'title', '00030004'),
                      path.join(self.sd_path1, 'title', '00030005'), path.join(self.sd_path1, 'title', '00030015'),
                      path.join(self.sd_path1, 'title', '00030017'), path.join(self.sd_path1, 'ticket', '00030017'),
                      path.join(self.sd_path1, 'ticket', '0003000f'), path.join(self.sd_path1, 'ticket', '00030004'),
                      path.join(self.sd_path1, 'ticket', '00030005'), path.join(self.sd_path1, 'ticket', '00030015')]
        while len(oldfolders) > 0:
            rmtree(oldfolders.pop(), ignore_errors=True)

        hwinfo = path.join(self.sd_path1, 'sys', 'HWINFO_S.dat')
        with open(hwinfo, 'rb+') as f:
            f.seek(0x90, 0)
            f.write(unhexlify(REGION_BYTES[self.dest_region])) # Console Region
            f.seek(0x88, 0)
            f.write(unhexlify('ff')) # Bitmask for Supported Languages (0xFF for all languages)
            f.seek(0xA0, 0)
            f.write(unhexlify(TITLE_ID_BYTE[self.dest_region])) # Title ID First Byte for Launcher
            f.flush()
            f.close()

        copytree('title', path.join(self.sd_path1, 'title'), dirs_exist_ok=True)
        copytree('hiya', path.join(self.sd_path1, 'hiya'), dirs_exist_ok=True)
        copytree('ticket', path.join(self.sd_path1, 'ticket'), dirs_exist_ok=True)
        copytree('sys', path.join(self.sd_path1, 'sys'), dirs_exist_ok=True)
        copytree('shared1', path.join(self.sd_path1, 'shared1'), dirs_exist_ok=True)

        if self.ntm.get() == 1:
            self.log.write(_('正在安装NTM...'))
            copytree('NTM/title', path.join(self.sd_path1, 'title'), dirs_exist_ok=True)
        if self.updatemenu.get() == 1:
            if self.have_menu is True:
                self.log.write(_('正在更新TWiLightMenu++...'))
            else:
                self.log.write(_('正在安装TWiLightMenu++...'))
            copytree('_nds', path.join(self.sd_path1, '_nds'), dirs_exist_ok=True)
            copytree('roms', path.join(self.sd_path1, 'roms'), dirs_exist_ok=True)
            copyfile('BOOT.NDS', path.join(self.sd_path1, 'BOOT.NDS'))
            copyfile('snemul.cfg', path.join(self.sd_path1, 'snemul.cfg'))
            self.read_ver()

        if self.devkp.get() == 1:
            self.make_dekp(self.sd_path1)

        Thread(target=self.clean).start()


####################################################################################################
# Entry point

sysname = platform.system()

langs = lang_init('zh_hans', 'i18n')
loc = langs[0]
loca = langs[1]
region = langs[2]

selfPath = path.dirname(path.abspath(argv[0]))
if sysname == 'Windows':
    from os import getcwd, chdir
    if getcwd() != selfPath:
        chdir(path.dirname(path.abspath(argv[0])))

if path.isfile('Console.log'):
    clog = open('Console.log', 'a', encoding="UTF-8")
    clog.write('\n')
    clog.close()

if sysname == 'Linux':
    from os import getuid, getlogin
    try:
        ug = getlogin()
    except OSError:
        ug = None
    su = False if getuid() != 0 else True

    if ug is not None and su is True:
        if not path.isfile('Console.log'):
            open('Console.log', 'a', encoding="UTF-8")
            Popen(['chown', '-R', ug + ':' + ug, 'Console.log']).wait()
        if not path.isfile('Window.log'):
            open('Window.log', 'a', encoding="UTF-8")
            Popen(['chown', '-R', ug + ':' + ug, 'Window.log']).wait()
        try:
            Popen(['chown', '-R', ug + ':' + ug, '__pycache__']).wait()
            Popen(['chown', '-R', ug + ':' + ug, 'py_langs']).wait()
        except:
            pass

check_update()

if sysname == 'Darwin':
    import sys
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
        selfPath = bundle_dir

fatcat = path.join(selfPath, sysname, 'fatcat')
_7za = path.join(selfPath, sysname, '7za')
twltool = path.join(selfPath, sysname, 'twltool')
ndsblc = path.join(selfPath, sysname, 'ndsblc')
osfmount = None
_7z = None
taskbar = None

if sysname == 'Windows':
    fatcat += '.exe'
    _7za += '.exe'
    twltool += '.exe'

    pybits = platform.architecture()[0]
    winver = platform.win32_ver()[0]
    if winver == 'Vista' or winver == 'XP' or winver == '2003Server':
        osfpath = 'elder'
    else:
        try:
            taskbar = ctypes.CDLL('./TaskbarLib.dll')
        except (UnicodeEncodeError, AttributeError, OSError):
            pass
        osfpath = 'extras'

    if pybits == '64bit':
        osfmount = path.join(sysname, osfpath, 'OSFMount.com')
        if path.exists(osfmount):
            printl(_('64位版本的OSFMount模块已加载'))
        else:
            osfmount = None
    else:
        try:
            if environ['PROGRAMFILES(X86)']:
                osfmount = path.join(sysname, osfpath, 'OSFMount.com')
                if path.exists(osfmount):
                    printl(_('64位版本的OSFMount模块已加载'))
                else:
                    osfmount = None
        except KeyError:
            osfmount = path.join(sysname, osfpath, 'x86', 'OSFMount.com')
            if path.exists(osfmount):
                printl(_('32位版本的OSFMount模块已加载'))
            else:
                osfmount = None

    _7z = path.join(sysname, '7z.exe')
    if path.exists(_7z):
        _7za = _7z
        printl(_('7-Zip模块已加载'))
    else:
        _7z = None

if not path.exists(fatcat):
    if osfmount or _7z is not None:
        fatcat = None
    else:
        printl(_('错误') + ': ' + _('找不到Fatcat, 请确认此程序位于本工具目录的"{}"文件夹中').format(sysname))
        exit(1)

printl(_('TWLMagician启动中...'))
# Create window
root = ttk.Window(themename="cosmo", iconphoto=None)
root.title('TWLMagician V1.5.6 BY R-YaTian')
# Disable maximizing
root.resizable(False, False)
# Center in window
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
if sysname == 'Windows':
    root.iconbitmap("icon.ico")
    if taskbar is not None:
        hwnd = int(root.wm_frame(), 16)
        taskbar.init_with_hwnd(hwnd)

printl(_('GUI初始化中...'))
app = Application(master=root)
app.mainloop()
