import gettext
from platform import system
from os import path
from locale import getlocale, getdefaultlocale, setlocale, LC_ALL

LANG_CODES = {
    'zh_sg': 'zh_hans',
    'zh_my': 'zh_hans',
    'zh_cn': 'zh_hans',
    'zh_hk': 'zh_hant',
    'zh_mo': 'zh_hant',
    'zh_tw': 'zh_hant'
}

def lang_init(default_lang = 'en_US'):
    if system() == 'Darwin':
        if getlocale()[0] is None:
            setlocale(LC_ALL, 'en_US.UTF-8')
        loc = getlocale()[0]
    else:
        loc = getdefaultlocale()[0]

    try:
        loca = LANG_CODES[loc.lower()]
    except:
        loca = loc

    langsys = path.join('i18n', loca, 'LC_MESSAGES', 'lang.mo')
    lange = path.join('i18n', 'en_US', 'LC_MESSAGES', 'lang.mo')

    if loca != default_lang:
        if path.exists(langsys):
            lang = gettext.translation('lang', localedir='i18n', languages=[loca])
            lang.install()
        else:
            if path.exists(lange):
                lang = gettext.translation('lang', localedir='i18n', languages=['en_US'])
                lang.install()
            else:
                gettext.install('')
    else:
        gettext.install('')
    return loca
