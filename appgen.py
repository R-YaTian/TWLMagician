from os import path, getcwd, mkdir, listdir
from shutil import rmtree, copyfile


def agen(apath, dst):
    print('AppGen V1.8 - BY R-YaTian')

    files = ['dsiware', 'appgen.py', '53524c41', '484e474a', '534c524e']

    dware = path.join(dst, 'dsiware')

    if dst == getcwd():
        if path.exists(dware):
            rmtree(dware)
        mkdir(dware)

    num = 0

    for app in listdir(apath):
        if app in files or app.endswith('.exe'):
            continue
        apps = path.join(apath, app)
        try:
            for title in listdir(path.join(apps, 'content')):
                if title.endswith('.app'):
                    print('{}/content/{}'.format(app, title))
                    copyfile(path.join(apath, app, 'content', title), path.join(dware, app + '.nds'))
                    num += 1
        except:
            pass

        try:
            for titleid in listdir(path.join(apps, 'data')):
                if titleid.endswith('.sav'):
                    if titleid.startswith('pri'):
                        print('{}/data/{}'.format(app, titleid))
                        copyfile(path.join(apath, app, 'data', titleid), path.join(dware, app + '.prv'))
                    if titleid.startswith('pub'):
                        print('{}/data/{}'.format(app, titleid))
                        copyfile(path.join(apath, app, 'data', titleid), path.join(dware, app + '.pub'))
        except:
            pass

    if num == 0 and dst == getcwd():
        rmtree(dware)


if __name__ == '__main__':
    agen(getcwd(), getcwd())
