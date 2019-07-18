#!/usr/bin/python
#coding:utf8

from Tkinter import (Tk, Frame, LabelFrame, PhotoImage, Button, Entry, Checkbutton, Radiobutton,
    Label, Toplevel, Scrollbar, Text, StringVar, IntVar, RIGHT, W, X, Y, DISABLED, NORMAL, SUNKEN,
    END)
from tkMessageBox import askokcancel, showerror, showinfo, WARNING
from tkFileDialog import askopenfilename, askdirectory
from platform import system
from os import path, remove, chmod, listdir, rename
from sys import exit
from locale import getpreferredencoding
from threading import Thread
from Queue import Queue, Empty
from binascii import hexlify
from hashlib import sha1
from urllib2 import urlopen, URLError
from urllib import urlretrieve
from json import load as jsonify
from subprocess import Popen, PIPE
from struct import unpack_from
from re import search
from shutil import move, rmtree, copyfile
from distutils.dir_util import copy_tree, _path_created


####################################################################################################
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

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.pack()

        # First row
        f1 = LabelFrame(self, text='NAND备份文件路径:', padx=10, pady=10)

        # NAND Button
        self.nand_mode = False

        nand_icon = PhotoImage(data=('R0lGODlhEAAQAIMAAAAAADMzM2ZmZpmZmczMzP///wAAAAAAAAA'
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAAYALAAAAAAQAB'
            'AAAARG0MhJaxU4Y2sECAEgikE1CAFRhGMwSMJwBsU6frIgnR/bv'
            'hTPrWUSDnGw3JGU2xmHrsvyU5xGO8ql6+S0AifPW8kCKpcpEQA7'))

        self.nand_button = Button(f1, image=nand_icon, command=self.change_mode, state=DISABLED)
        self.nand_button.image = nand_icon

        self.nand_button.pack(side='left')

        self.nand_file = StringVar()
        Entry(f1, textvariable=self.nand_file, state='readonly', width=40).pack(side='left')

        Button(f1, text='...', command=self.choose_nand).pack(side='left')

        f1.pack(padx=10, pady=10, fill=X)

        # Second row
        f2 = Frame(self)

        # Check box
        self.twilight = IntVar()
        self.twilight.set(1)

        self.chk = Checkbutton(f2, text='同时安装TWiLightMenu++',
            variable=self.twilight)

        self.chk.pack(padx=10, anchor=W)

        # NAND operation frame
        self.nand_frame = LabelFrame(f2, text='NAND操作', padx=10, pady=10)

        self.nand_operation = IntVar()
        self.nand_operation.set(0)

        Radiobutton(self.nand_frame, text='卸载unlaunch或安装unlaunch V1.9 stable',
            variable=self.nand_operation, value=0,
            command=lambda: self.enable_entries(False)).pack(anchor=W)

        Radiobutton(self.nand_frame, text='移除 No$GBA footer', variable=self.nand_operation,
            value=1, command=lambda: self.enable_entries(False)).pack(anchor=W)

        Radiobutton(self.nand_frame, text='添加 No$GBA footer', variable=self.nand_operation,
            value=2, command=lambda: self.enable_entries(True)).pack(anchor=W)

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

        self.start_button = Button(f3, text='开始', width=16, command=self.hiya, state=DISABLED)
        self.start_button.pack(side='left', padx=(0, 5))

        Button(f3, text='退出', command=root.destroy, width=16).pack(side='left', padx=(5, 0))

        f3.pack(pady=(10, 20))

        self.folders = []
        self.files = []


    ################################################################################################
    def change_mode(self):
        if (self.nand_mode):
            self.nand_frame.pack_forget()
            self.chk.pack(padx=10, anchor=W)
            self.nand_mode = False

        else:
            if askokcancel('警告', ('你正在进入NAND模式,请明确你知道自己在做什么!继续?'),
                           icon=WARNING):
                self.chk.pack_forget()
                self.nand_frame.pack(padx=10, pady=(0, 10), fill=X)
                self.nand_mode = True


    ################################################################################################
    def enable_entries(self, status):
        self.cid_label['state'] = (NORMAL if status else DISABLED)
        self.cid_entry['state'] = (NORMAL if status else DISABLED)
        self.console_id_label['state'] = (NORMAL if status else DISABLED)
        self.console_id_entry['state'] = (NORMAL if status else DISABLED)


    ################################################################################################
    def choose_nand(self):
        name = askopenfilename(filetypes=( ( 'nand.bin', '*.bin' ), ( 'DSi-1.mmc', '*.mmc' ) ))
        self.nand_file.set(name.encode(getpreferredencoding()))

        self.nand_button['state'] = (NORMAL if self.nand_file.get() != '' else DISABLED)
        self.start_button['state'] = (NORMAL if self.nand_file.get() != '' else DISABLED)


    ################################################################################################
    def hiya(self):
        if not self.nand_mode:
            showinfo('提示', '接下来请选择你用来安装自制系统的SD卡路径(或输出路径)\n为了避免 '
                '启动错误 请确保目录下无任何文件')
            self.sd_path = askdirectory()

            # Exit if no path was selected
            if self.sd_path == '':
                return

        # If adding a No$GBA footer, check if CID and ConsoleID values are OK
        elif self.nand_operation.get() == 2:
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
                cid = cid.decode('hex')

            except TypeError:
                showerror('错误', 'Bad eMMC CID')
                return

            try:
                console_id = bytearray(reversed(console_id.decode('hex')))

            except TypeError:
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
        if self.nand_mode and self.nand_operation.get() == 2:
            Thread(target=self.add_footer, args=(cid, console_id)).start()

        else:
            Thread(target=self.check_nand).start()


    ################################################################################################
    def check_nand(self):
        self.log.write('校验 NAND 文件...')

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
                    self.cid.set(hexlify(bstr).upper())
                    self.log.write('- eMMC CID: ' + self.cid.get())

                    # Read the console ID
                    bstr = f.read(8)
                    self.console_id.set(hexlify(bytearray(reversed(bstr))).upper())
                    self.log.write('- Console ID: ' + self.console_id.get())

                    # Check we are making an unlaunch operation or removing the No$GBA footer
                    if self.nand_mode:
                        if self.nand_operation.get() == 0:
                            Thread(target=self.decrypt_nand).start()

                        else:
                            Thread(target=self.remove_footer).start()
                            pass

                    else:
                        Thread(target=self.get_latest_hiyacfw).start()

                else:
                    self.log.write('错误: 找不到 No$GBA footer')

        except IOError:
            self.log.write('错误: 无法打开文件: ' +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def get_latest_hiyacfw(self):
        filename = 'HiyaCFW.7z'

        try:
            self.log.write('\n下载最新版的HiyaCFW...')

            conn = urlopen('https://api.github.com/repos/RocketRobz/hiyaCFW/releases/latest')
            latest = jsonify(conn)
            conn.close()

            urlretrieve(latest['assets'][0]['browser_download_url'], filename)

            self.log.write('- 解压缩 HiyaCFW 档案...')

            exe = path.join(sysname, '7za')

            proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'for PC', 'for SDNAND SD card' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(filename)
                self.folders.append('for PC')
                self.folders.append('for SDNAND SD card')
                # Got to decrypt NAND if bootloader.nds is present
                Thread(target=self.decrypt_nand if path.isfile('bootloader.nds')
                    else self.extract_bios).start()

            else:
                self.log.write('错误: 解压失败')

        except (URLError, IOError) as e:
            self.log.write('错误: 无法下载 HiyaCFW')
            self.log.write('- 尝试从本地磁盘解压文件...')

            exe = path.join(sysname, '7za')

            proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'for PC', 'for SDNAND SD card' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(filename)
                self.folders.append('for PC')
                self.folders.append('for SDNAND SD card')
                # Got to decrypt NAND if bootloader.nds is present
                Thread(target=self.decrypt_nand if path.isfile('bootloader.nds')
                    else self.extract_bios).start()

            else:
                self.log.write('错误: 解压失败')

        except OSError:
            self.log.write('错误: 无法运行 ' + exe)


    ################################################################################################
    def extract_bios(self):
        self.log.write('\n从NAND解压 ARM7/ARM9 BIOS...')

        exe = path.join(sysname, 'twltool')

        try:
            proc = Popen([ exe, 'boot2', '--in', self.nand_file.get() ])

            ret_val = proc.wait()

            if ret_val == 0:
                # Hash arm7.bin
                sha1_hash = sha1()

                with open('arm7.bin', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- arm7.bin SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper())

                # Hash arm9.bin
                sha1_hash = sha1()

                with open('arm9.bin', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- arm9.bin SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper())

                self.files.append('arm7.bin')
                self.files.append('arm9.bin')

                Thread(target=self.patch_bios).start()

            else:
                self.log.write('错误: 解压失败')
                Thread(target=self.clean, args=(True,)).start()

        except OSError:
            self.log.write('错误: 无法运行 ' + exe)
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
                hexlify(sha1_hash.digest()).upper())

            # Hash arm9.bin
            sha1_hash = sha1()

            with open('arm9.bin', 'rb') as f:
                sha1_hash.update(f.read())

            self.log.write('- Patched arm9.bin SHA1:\n  ' +
                hexlify(sha1_hash.digest()).upper())

            Thread(target=self.arm9_prepend).start()

        except IOError:
            self.log.write('错误: 无法执行 patch BIOS')
            Thread(target=self.clean, args=(True,)).start()

        except Exception:
            self.log.write('错误: Invalid patch header')
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
                hexlify(sha1_hash.digest()).upper())

            Thread(target=self.make_bootloader).start()

        except IOError:
            self.log.write('错误: 无法执行 prepend data to ARM9 BIOS')
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def make_bootloader(self):
        self.log.write('\n重新生成 bootloader...')

        exe = (path.join('for PC', 'bootloader files', 'ndstool') if sysname == 'Windows' else
            path.join(sysname, 'ndsblc'))

        try:
            proc = Popen([ exe, '-c', 'bootloader.nds', '-9', 'arm9.bin', '-7', 'arm7.bin', '-t',
                path.join('for PC', 'bootloader files', 'banner.bin'), '-h',
                path.join('for PC', 'bootloader files', 'header.bin') ])

            ret_val = proc.wait()

            if ret_val == 0:
                # Hash bootloader.nds
                sha1_hash = sha1()

                with open('bootloader.nds', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- bootloader.nds SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper())

                Thread(target=self.decrypt_nand).start()

            else:
                self.log.write('错误: 生成失败')
                Thread(target=self.clean, args=(True,)).start()

        except OSError:
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def decrypt_nand(self):
        self.log.write('\n解密NAND...')

        exe = path.join(sysname, 'twltool')

        try:
            proc = Popen([ exe, 'nandcrypt', '--in', self.nand_file.get(), '--out',
                self.console_id.get() + '.img' ])

            ret_val = proc.wait()

            if ret_val == 0:
                if not self.nand_mode:
                    self.files.append(self.console_id.get() + '.img')

                Thread(target=self.mount_nand).start()

            else:
                self.log.write('错误: 解密失败')
                Thread(target=self.clean, args=(True,)).start()

        except OSError:
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def mount_nand(self):
        self.log.write('\n挂载解密的NAND镜像...')

        try:
            if sysname == 'Windows':
                exe = osfmount

                cmd = [ osfmount, '-a', '-t', 'file', '-f', self.console_id.get() + '.img', '-m',
                    '#:', '-o', 'ro,rem' ]

                if self.nand_mode:
                    cmd[-1] = 'rw,rem'

                proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

                outs, errs = proc.communicate()

                if proc.returncode == 0:
                    self.mounted = search(r'[a-zA-Z]:\s', outs).group(0).strip()
                    self.log.write('- 挂载到虚拟驱动器 ' + self.mounted)

                else:
                    self.log.write('错误: 挂载失败')
                    Thread(target=self.clean, args=(True,)).start()
                    return

            elif sysname == 'Darwin':
                exe = 'hdiutil'

                cmd = [ exe, 'attach', '-imagekey', 'diskimage-class=CRawDiskImage', '-nomount',
                    self.console_id.get() + '.img' ]

                if not self.nand_mode:
                    cmd.insert(2, '-readonly')

                proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

                outs, errs = proc.communicate()

                if proc.returncode == 0:
                    self.raw_disk = search(r'^\/dev\/disk\d+', outs).group(0)
                    self.log.write('- Mounted raw disk on ' + self.raw_disk)

                    cmd = [ exe, 'mount', self.raw_disk + 's1' ]

                    if not self.nand_mode:
                        cmd.insert(2, '-readonly')

                    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

                    outs, errs = proc.communicate()

                    if proc.returncode == 0:
                        self.mounted = search(r'\/Volumes\/.+', outs).group(0)
                        self.log.write('- Mounted volume on ' + self.mounted)

                    else:
                        self.log.write('ERROR: Mounter failed')
                        Thread(target=self.clean, args=(True,)).start()
                        return

                else:
                    self.log.write('ERROR: Mounter failed')
                    Thread(target=self.clean, args=(True,)).start()
                    return

            else:  # Linux
                exe = 'losetup'

                cmd = [ exe, '-P', '-f', '--show', self.console_id.get() + '.img' ]

                if not self.nand_mode:
                    cmd.insert(2, '-r')

                proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                outs, errs = proc.communicate()

                if proc.returncode == 0:
                    self.loop_dev = search(r'\/dev\/loop\d+', outs).group(0)
                    self.log.write('- Mounted loop device on ' + self.loop_dev)

                    exe = 'mount'

                    self.mounted = '/mnt'

                    cmd = [ exe, '-t', 'vfat', self.loop_dev + 'p1', self.mounted ]

                    if not self.nand_mode:
                        cmd.insert(1, '-r')

                    proc = Popen(cmd)

                    ret_val = proc.wait()

                    if ret_val == 0:
                        self.log.write('- Mounted partition on ' + self.mounted)

                    else:
                        self.log.write('ERROR: Mounter failed')
                        Thread(target=self.clean, args=(True,)).start()
                        return

                else:
                    self.log.write('ERROR: Mounter failed')
                    Thread(target=self.clean, args=(True,)).start()
                    return

            # Check we are making an unlaunch operation
            Thread(target=self.unlaunch_proc if self.nand_mode else self.extract_nand).start()

        except OSError:
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def extract_nand(self):
        self.log.write('\n从NAND解压文件...')

        err = False

        # Reset copied files cache
        _path_created.clear()
        try:
            copy_tree(self.mounted, self.sd_path, preserve_mode=0, update=1)

        except:
            self.log.write('错误: 解压失败')
            err = True

        Thread(target=self.unmount_nand, args=(err,)).start()


    ################################################################################################
    def unmount_nand(self, err=False):
        self.log.write('\n卸载NAND镜像...')

        try:
            if sysname == 'Windows':
                exe = osfmount

                proc = Popen([ osfmount, '-D', '-m', self.mounted ])

            elif sysname == 'Darwin':
                exe = 'hdiutil'

                proc = Popen([ exe, 'detach', self.raw_disk ])

            else:  # Linux
                exe = 'umount'

                proc = Popen([ exe, self.mounted ])

                ret_val = proc.wait()

                if ret_val == 0:
                    exe = 'losetup'

                    proc = Popen([ exe, '-d', self.loop_dev ])

                else:
                    self.log.write('ERROR: Unmounter failed')
                    Thread(target=self.clean, args=(True,)).start()
                    return

            ret_val = proc.wait()

            if ret_val == 0:
                if err:
                    Thread(target=self.clean, args=(True,)).start()

                else:
                    Thread(target=self.encrypt_nand if self.nand_mode
                        else self.get_launcher).start()

            else:
                self.log.write('错误: 卸载失败')
                Thread(target=self.clean, args=(True,)).start()

        except OSError:
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def get_launcher(self):
        app = self.detect_region()

        # Stop if no supported region was found
        if not app:
            self.files.append('bootloader.nds')
            Thread(target=self.clean, args=(True,)).start()
            return

        # Check if unlaunch was installed on the NAND dump
        tmd = path.join(self.sd_path, 'title', '00030017', app, 'content', 'title.tmd')

        if path.getsize(tmd) > 520:
            self.log.write('- 警告: Unlaunch已经安装在此NAND dump中')

        # Delete title.tmd in case it does not get overwritten
        remove(tmd)

        try:
            self.log.write('\n下载 ' + self.launcher_region + ' launcher...')

            urlretrieve('https://raw.githubusercontent.com/mondul/HiyaCFW-Helper/master/'
                'launchers/' + self.launcher_region, self.launcher_region)

            self.log.write('- 解密launcher...')

            exe = path.join(sysname, '7za')

            proc = Popen([ exe, 'x', '-bso0', '-y', '-p' + app, self.launcher_region,
                '00000002.app' ])

            ret_val = proc.wait()

            if ret_val == 0:
                #self.files.append(self.launcher_region)

                # Hash 00000002.app
                sha1_hash = sha1()

                with open('00000002.app', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- Patched launcher SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper())

                Thread(target=self.install_hiyacfw, args=(path.join(self.sd_path, 'title',
                    '00030017', app, 'content', '00000002.app'),)).start()

            else:
                self.log.write('错误: 解压失败')
                Thread(target=self.clean, args=(True,)).start()

        except IOError:
            self.log.write('错误: 无法下载 ' + self.launcher_region + ' launcher')
            self.log.write('- 从本地磁盘解密launcher...')

            exe = path.join(sysname, '7za')

            proc = Popen([ exe, 'x', '-bso0', '-y', '-p' + app, self.launcher_region,
                '00000002.app' ])

            ret_val = proc.wait()

            if ret_val == 0:
                #self.files.append(self.launcher_region)

                # Hash 00000002.app
                sha1_hash = sha1()

                with open('00000002.app', 'rb') as f:
                    sha1_hash.update(f.read())

                self.log.write('- Patched launcher SHA1:\n  ' +
                    hexlify(sha1_hash.digest()).upper())

                Thread(target=self.install_hiyacfw, args=(path.join(self.sd_path, 'title',
                    '00030017', app, 'content', '00000002.app'),)).start()

            else:
                self.log.write('错误: 解压失败')
                Thread(target=self.clean, args=(True,)).start()

        except OSError:
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def install_hiyacfw(self, launcher_path):
        self.log.write('\n复制 HiyaCFW 相关文件...')

        copy_tree('for SDNAND SD card', self.sd_path, update=1)
        move('bootloader.nds', path.join(self.sd_path, 'hiya', 'bootloader.nds'))
        move('00000002.app', launcher_path)

        Thread(target=self.get_latest_twilight if self.twilight.get() == 1 else self.clean).start()


    ################################################################################################
    def get_latest_twilight(self):
        filename = 'TWiLightMenu.7z'

        try:
            self.log.write('\n下载最新版的TWiLightMenu++...')

            conn = urlopen('https://api.github.com/repos/RocketRobz/TWiLightMenu/releases/'
                'latest')
            latest = jsonify(conn)
            conn.close()

            urlretrieve(latest['assets'][0]['browser_download_url'], filename)

            self.log.write('- 解压缩 ' + filename[:-3] + ' 档案...')

            exe = path.join(sysname, '7za')

            proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'DSi - CFW users', '_nds', 'roms',
                'DSi&3DS - SD card users' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(filename)
                self.folders.append('DSi - CFW users')
                self.folders.append('DSi&3DS - SD card users')
                Thread(target=self.install_twilight, args=(filename[:-3],)).start()

            else:
                self.log.write('错误: 解压失败')
                Thread(target=self.clean, args=(True,)).start()

        except (URLError, IOError) as e:
            self.log.write('错误: 无法下载 TWiLightMenu++')
            self.log.write('- 从本地磁盘解压文件...')

            exe = path.join(sysname, '7za')

            proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'DSi - CFW users', '_nds', 'roms',
                'DSi&3DS - SD card users' ])

            ret_val = proc.wait()

            if ret_val == 0:
                self.files.append(filename)
                self.folders.append('DSi - CFW users')
                self.folders.append('DSi&3DS - SD card users')
                Thread(target=self.install_twilight, args=(filename[:-3],)).start()

            else:
                self.log.write('错误: 解压失败')
                Thread(target=self.clean, args=(True,)).start()


        except OSError:
            self.log.write('错误: 无法运行 ' + exe)
            Thread(target=self.clean, args=(True,)).start()


    ################################################################################################
    def install_twilight(self, name):
        self.log.write('\n复制 ' + name + ' 相关文件...')

        copy_tree(path.join('DSi - CFW users', 'SDNAND root'), self.sd_path, update=1)
        move('_nds'.decode('utf-8'), path.join(self.sd_path, '_nds'))
        move('roms', path.join(self.sd_path, 'roms'))
        copy_tree(path.join('DSi&3DS - SD card users'), self.sd_path, update=1)
        #copy_tree(path.join('DSi - CFW users', 'DSiWare (' + self.launcher_region + ')'),
             #path.join(self.sd_path, 'roms', 'dsiware'), update=1)

        # Set files as read-only
        twlcfg0 = path.join(self.sd_path, 'shared1', 'TWLCFG0.dat')
        twlcfg1 = path.join(self.sd_path, 'shared1', 'TWLCFG1.dat')

        if sysname == 'Darwin':
            Popen([ 'chflags', 'uchg', twlcfg0, twlcfg1 ]).wait()

        elif sysname == 'Linux':
            Popen([ path.join('Linux', 'fatattr'), '+R', twlcfg0, twlcfg1 ]).wait()

        else:
            #chmod(twlcfg0, 292)
            #chmod(twlcfg1, 292)

        # Generate Apps
        import os
        import shutil
        for app in listdir(path.join(self.sd_path, 'title', '00030004')):
            try:
                for title in listdir(path.join(self.sd_path, 'title', '00030004', app,
                                               'data')):
                    if title.endswith(".sav"):
                        if title.startswith("pri"):
                            shutil.copy(self.sd_path +
                                        "/title/00030004/{}/data/{}".format(app, title),
                                        self.sd_path + "/roms/dsiware")
                            os.rename(self.sd_path + "/roms/dsiware/{}".format(title),
                                      self.sd_path + "/roms/dsiware/{}.prv".format(app))

                        if title.startswith("pub"):
                            shutil.copy(self.sd_path +
                                        "/title/00030004/{}/data/{}".format(app, title),
                                        self.sd_path + "/roms/dsiware")
                            os.rename(self.sd_path + "/roms/dsiware/{}".format(title),
                                      self.sd_path + "/roms/dsiware/{}.pub".format(app))

                for title in listdir(path.join(self.sd_path, 'title', '00030004', app,
                    'content')):
                    if title.endswith('.app'):
                        shutil.copy(self.sd_path +
                                    "/title/00030004/{}/content/{}".format(app, title),
                                    self.sd_path + "/roms/dsiware")
                        os.rename(self.sd_path + "/roms/dsiware/{}".format(title),
                                  self.sd_path + "/roms/dsiware/{}.nds".format(app))

                        os.remove(self.sd_path + "/roms/dsiware/484e474a.prv")
                        os.remove(self.sd_path + "/roms/dsiware/484e474a.nds")
                        os.remove(self.sd_path + "/roms/dsiware/53524c41.nds")

            except:
                pass

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
            self.log.write('终止')
            return

        # Get logged user in Linux
        if sysname == 'Linux':
            from os import getlogin

            # Workaround for some Linux systems where this function does not work
            try:
                ug = getlogin()

            except OSError:
                ug = 'root'

        if (self.nand_mode):
            file = self.console_id.get() + self.suffix + '.bin'

            rename(self.console_id.get() + '.img', file)

            # Change owner of the file in Linux
            if sysname == 'Linux':
                Popen([ 'chown', '-R', ug + ':' + ug, file ]).wait()

            self.log.write('\nDone!\nModified NAND stored as\n' + file)
            return

        # Change owner of the out folder in Linux
        if sysname == 'Linux':
            Popen([ 'chown', '-R', ug + ':' + ug, self.sd_path ]).wait()

        self.log.write('完成!\n弹出SD卡并装回你的DSi')


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
            '484e4145': 'USA',
            '484e414a': 'JAP',
            '484e4150': 'EUR',
            '484e4155': 'AUS'
        }

        # Autodetect console region
        base = self.mounted if self.nand_mode else self.sd_path

        try:
            for app in listdir(path.join(base, 'title', '00030017')):
                for file in listdir(path.join(base, 'title', '00030017', app, 'content')):
                    if file.endswith('.app'):
                        try:
                            self.log.write('- 校验 ' + REGION_CODES[app] + ' console NAND dump')
                            self.launcher_region = REGION_CODES[app]
                            return app

                        except KeyError:
                            self.log.write('错误: 不支持的 console 区域')
                            return False

            self.log.write('错误: 无法校验 console 区域')

        except OSError as e:
            self.log.write('错误: ' + e.strerror + ': ' + e.filename)

        return False


    ################################################################################################
    def unlaunch_proc(self):
        self.log.write('\n检查unlaunch状态...')

        app = self.detect_region()

        # Stop if no supported region was found
        if not app:
            # TODO: Unmount NAND
            return

        tmd = path.join(self.mounted, 'title', '00030017', app, 'content', 'title.tmd')

        tmd_size = path.getsize(tmd)

        if tmd_size == 520:
            self.log.write('- 未安装,下载 V1.9...')

            try:
                filename = urlretrieve('http://problemkaputt.de/unlau19.zip')[0]

                exe = path.join(sysname, '7za')

                proc = Popen([ exe, 'x', '-bso0', '-y', filename, 'UNLAUNCH.DSI' ])

                ret_val = proc.wait()

                if ret_val == 0:
                    self.files.append(filename)
                    self.files.append('UNLAUNCH.DSI')

                    self.log.write('- 安装unlaunch...')

                    self.suffix = '-unlaunch'

                    with open(tmd, 'ab') as f:
                        with open('UNLAUNCH.DSI', 'rb') as unl:
                            f.write(unl.read())

                    # Set files as read-only
                    for file in listdir(path.join(self.mounted, 'title', '00030017', app,
                        'content')):
                        file = path.join(self.mounted, 'title', '00030017', app, 'content', file)

                        if sysname == 'Darwin':
                            Popen([ 'chflags', 'uchg', file ]).wait()

                        elif sysname == 'Linux':
                            Popen([ path.join('Linux', 'fatattr'), '+R', file ]).wait()
   
                        else:
                            chmod(file, 292)

                else:
                    self.log.write('错误: 解压失败')
                    # TODO: Unmount NAND


            except IOError:
                self.log.write('错误: 无法下载 unlaunch')
                # TODO: Unmount NAND

            except OSError:
                self.log.write('错误: 无法运行 ' + exe)
                # TODO: Unmount NAND

        else:
            self.log.write('- 已安装,卸载中...')

            self.suffix = '-no-unlaunch'

            # Set files as read-write
            for file in listdir(path.join(self.mounted, 'title', '00030017', app, 'content')):
                file = path.join(self.mounted, 'title', '00030017', app, 'content', file)

                if sysname == 'Darwin':
                    Popen([ 'chflags', 'nouchg', file ]).wait()

                elif sysname == 'Linux':
                    Popen([ path.join('Linux', 'fatattr'), '-R', file ]).wait()
   
                else:
                    chmod(file, 438)

            with open(tmd, 'r+b') as f:
                f.truncate(520)

        Thread(target=self.unmount_nand).start()


    ################################################################################################
    def encrypt_nand(self):
        self.log.write('\n加密NAND备份文件...')

        exe = path.join(sysname, 'twltool')

        try:
            proc = Popen([ exe, 'nandcrypt', '--in', self.console_id.get() + '.img' ])

            ret_val = proc.wait()

            if ret_val == 0:
                Thread(target=self.clean).start()

            else:
                self.log.write('错误: 加密失败')

        except OSError:
            self.log.write('错误: 无法运行 ' + exe)


    ################################################################################################
    def remove_footer(self):
        self.log.write('\n移除 No$GBA footer...')

        file = self.console_id.get() + '-no-footer.bin'

        try:
            copyfile(self.nand_file.get(), file)

            # Back-up footer info
            with open(self.console_id.get() + '-info.txt', 'wb') as f:
                f.write('eMMC CID: ' + self.cid.get() + '\r\n')
                f.write('Console ID: ' + self.console_id.get() + '\r\n')

            with open(file, 'r+b') as f:
                # Go to the No$GBA footer offset
                f.seek(-64, 2)
                # Remove footer
                f.truncate()

            # Change owner of the file in Linux
            if sysname == 'Linux':
                from os import getlogin

                ug = getlogin()

                Popen([ 'chown', '-R', ug + ':' + ug, file ]).wait()

            self.log.write('\n完成!\n修改后的NAND文件存储到\n' + file +
                '\nfooter信息保存在 ' + self.console_id.get() + '-info.txt')

        except IOError:
            self.log.write('错误: 无法打开文件 ' +
                path.basename(self.nand_file.get()))


    ################################################################################################
    def add_footer(self, cid, console_id):
        self.log.write('添加 No$GBA footer...')

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
                    return;

                # Go to the end of file
                f.seek(0, 2)
                # Write footer
                f.write(b'DSi eMMC CID/CPU')
                f.write(cid)
                f.write(console_id)
                f.write('\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

            self.log.write('\n完成!\n修改后的NAND文件存储到\n' + file)

        except IOError:
            self.log.write('错误: 无法打开文件 ' +
                path.basename(self.nand_file.get()))


####################################################################################################

sysname = system()

root = Tk()

if sysname == 'Windows':
    from ctypes import windll
    from _winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE

    if windll.shell32.IsUserAnAdmin() == 0:
        root.withdraw()
        showerror('错误', '请以管理员权限运行本工具')
        root.destroy()
        exit(1)

    # Search for OSFMount in the Windows registry
    try:
        with OpenKey(HKEY_LOCAL_MACHINE,
            'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\OSFMount_is1') as hkey:

            osfmount = path.join(QueryValueEx(hkey, 'InstallLocation')[0], 'OSFMount.com')

            if not path.exists(osfmount):
                raise WindowsError

    except WindowsError:
        root.withdraw()
        showerror('错误', '对应体系结构的OSFMount未安装')
        root.destroy()
        exit(1)

elif sysname == 'Linux':
    from os import getuid

    if getuid() != 0:
        root.withdraw()
        showerror('Error', 'This script needs to be run with sudo.')
        root.destroy()
        exit(1)

root.title('HiyaCFW Helper V2.9.9.9R BY天涯')
# Disable maximizing
root.resizable(0, 0)
# Center in window
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
app = Application(master=root)
app.mainloop()
