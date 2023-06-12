import os
from shutil import copy2, copystat, Error
from time import time


def copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2,
             ignore_dangling_symlinks=False, dirs_exist_ok=False):
    os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []

    for srcentry in os.scandir(src):
        if ignore is not None:
            ignored_names = ignore(src, srcentry.name)
        else:
            ignored_names = set()
        if srcentry.name in ignored_names:
            continue
        srcname = os.path.join(src, srcentry.name)
        dstname = os.path.join(dst, srcentry.name)
        try:
            if os.path.islink(srcname):
                linkto = os.readlink(srcname)
                if symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    copystat(srcname, dstname, follow_symlinks=not symlinks)
                else:
                    # ignore dangling symlink if the flag is on
                    if not os.path.exists(linkto) and ignore_dangling_symlinks:
                        continue
                    # otherwise let the copy occur. copy2 will raise an error
                    if srcentry.is_dir():
                        copytree(srcname, dstname, symlinks, ignore,
                                 copy_function, dirs_exist_ok=dirs_exist_ok)
                    else:
                        copy_function(srcname, dstname)
            elif srcentry.is_dir():
                copytree(srcname, dstname, symlinks, ignore, copy_function,
                         dirs_exist_ok=dirs_exist_ok)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy_function(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        # Copying file access times may fail on Windows
        if getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)
    return dst


def print_progress(filename, size, res, download_speed):
    sp = res / size
    sp = 1 if (sp > 1) else sp
    done_block = '▊' * int(10 * sp)
    print('\r{0}: [{1:10}] '.format(filename, done_block), format(sp * 100, '.2f'),
          '% ', format_bytes_num(download_speed), '/s ', format_bytes_num(res),
          '/', format_bytes_num(size) + '        ', sep='', end='')


def copyfileobj(fsrc, fdst, length=0, show_progress=True):
    """copy data from file-like object fsrc to file-like object fdst"""
    if not length:
        length = 32 * 1024
    # Localize variable access to minimize overhead.
    fsrc_read = fsrc.read
    fdst_write = fdst.write
    filename = fdst.name
    size = fsrc.length
    show_progress = False if size is None else show_progress
    if show_progress is True:
        last_time = start_time = time()
        last_res = res = 0
        download_speed = 0.0
    while True:
        buf = fsrc_read(length)
        if not buf:
            break
        fdst_write(buf)
        if show_progress is True:
            res += length
            rt_time = time()
            if rt_time - last_time >= 1:
                download_time = rt_time - last_time
                last_time = time()
                download_speed = (res - last_res) / download_time
                last_res = res
            print_progress(filename, size, res, download_speed)
    if show_progress is True:
        rt_time = time()
        if rt_time - start_time < 1:
            download_time = rt_time - start_time
            download_speed = size / download_time
            print_progress(filename, size, size, download_speed)
        print('\r', sep='', flush=True)


def format_bytes_num(bytes_num):
    i = 0
    while bytes_num > 1024 and i < 9 - 1:
        bytes_num /= 1024
        i += 1
    unit = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')[i]
    return "%.2f" % bytes_num + unit
