import gettext
from array import array
from ast import literal_eval
from struct import pack
from platform import system
from os import path, remove
from locale import getlocale, getdefaultlocale, setlocale, LC_ALL
from email.parser import HeaderParser
from copy import copy

LANG_CODES = {
    'en_us': 'en',
    'en_gb': 'en',
    'zh_sg': 'zh_hans',
    'zh_my': 'zh_hans',
    'zh_cn': 'zh_hans',
    'zh_hk': 'zh_hant',
    'zh_mo': 'zh_hant',
    'zh_tw': 'zh_hant'
}

def lang_init(default_lang = 'en', lang_dir = 'langs', file_name = 'lang'):
    lfile = None
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

    langsys = path.join(lang_dir, loca, file_name + '.po')
    lange = path.join(lang_dir, 'en', file_name + '.po')

    if loca != default_lang:
        if path.exists(langsys):
            lfile = path.join(lang_dir, loca, file_name + '.mo')
            make(langsys, lfile)
            lang = translation(file_name, localedir=lang_dir, languages=loca)
            lang.install()
        else:
            if path.exists(lange):
                lfile = path.join(lang_dir, 'en', file_name + '.mo')
                make(lange, lfile)
                lang = translation(file_name, localedir=lang_dir, languages='en')
                lang.install()
            else:
                gettext.install('')
    else:
        gettext.install('')

    if lfile is not None:
        remove(lfile)
    return loc

#-----------------------------------------------------------------------------
# gettext.translation
# Modify by R-YaTian

_translations = {}

def translation(domain, localedir, languages,
                class_=None, fallback=False):
    if class_ is None:
        class_ = gettext.GNUTranslations
    mofile = path.join(localedir, languages, '%s.mo' % domain)
    if not path.exists(mofile):
        if fallback:
            return gettext.NullTranslations()
        from errno import ENOENT
        raise FileNotFoundError(ENOENT,
                                'No translation file found for domain', domain)
    key = (class_, path.abspath(mofile))
    t = _translations.get(key)
    if t is None:
        with open(mofile, 'rb') as fp:
            t = _translations.setdefault(key, class_(fp))
    t = copy(t)
    return t

#-----------------------------------------------------------------------------
# msgfmt
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>
# Modify by R-YaTian

"""Generate binary message catalog from textual translation description.

This program converts a textual Uniforum-style message catalog (.po file) into
a binary GNU catalog (.mo file).  This is essentially the same function as the
GNU msgfmt program, however, it is a simpler implementation.
"""

MESSAGES = {}

def add(id, str, fuzzy):
    "Add a non-fuzzy translation to the dictionary."
    global MESSAGES
    if not fuzzy and str:
        MESSAGES[id] = str

def generate():
    "Return the generated output."
    global MESSAGES
    # the keys are sorted in the .mo file
    keys = sorted(MESSAGES.keys())
    offsets = []
    ids = strs = b''
    for id in keys:
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        offsets.append((len(ids), len(id), len(strs), len(MESSAGES[id])))
        ids += id + b'\0'
        strs += MESSAGES[id] + b'\0'
    output = ''
    # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    # translated string.
    keystart = 7*4+16*len(keys)
    # and the values start after the keys
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1+keystart]
        voffsets += [l2, o2+valuestart]
    offsets = koffsets + voffsets
    output = pack("Iiiiiii",
                  0x950412de,       # Magic
                  0,                 # Version
                  len(keys),         # # of entries
                  7*4,               # start of key index
                  7*4+len(keys)*8,   # start of value index
                  0, 0)              # size and offset of hash table
    output += array("i", offsets).tobytes()
    output += ids
    output += strs
    return output

def make(filename, outfile):
    ID = 1
    STR = 2

    # Compute .mo name from .po name and arguments
    if filename.endswith('.po'):
        infile = filename
    else:
        infile = filename + '.po'
    if outfile is None:
        outfile = path.splitext(infile)[0] + '.mo'

    try:
        with open(infile, 'rb') as f:
            lines = f.readlines()
    except IOError as msg:
        print(msg)
        return

    section = None
    fuzzy = 0

    # Start off assuming Latin-1, so everything decodes without failure,
    # until we know the exact encoding
    encoding = 'latin-1'

    # Parse the catalog
    lno = 0
    for l in lines:
        l = l.decode(encoding)
        lno += 1
        # If we get a comment line after a msgstr, this is a new entry
        if l[0] == '#' and section == STR:
            add(msgid, msgstr, fuzzy)
            section = None
            fuzzy = 0
        # Record a fuzzy mark
        if l[:2] == '#,' and 'fuzzy' in l:
            fuzzy = 1
        # Skip comments
        if l[0] == '#':
            continue
        # Now we are in a msgid section, output previous section
        if l.startswith('msgid') and not l.startswith('msgid_plural'):
            if section == STR:
                add(msgid, msgstr, fuzzy)
                if not msgid:
                    # See whether there is an encoding declaration
                    p = HeaderParser()
                    charset = p.parsestr(msgstr.decode(encoding)).get_content_charset()
                    if charset:
                        encoding = charset
            section = ID
            l = l[5:]
            msgid = msgstr = b''
            is_plural = False
        # This is a message with plural forms
        elif l.startswith('msgid_plural'):
            if section != ID:
                print('msgid_plural not preceded by msgid on %s:%d' % (infile, lno))
                return
            l = l[12:]
            msgid += b'\0' # separator of singular and plural
            is_plural = True
        # Now we are in a msgstr section
        elif l.startswith('msgstr'):
            section = STR
            if l.startswith('msgstr['):
                if not is_plural:
                    print('plural without msgid_plural on %s:%d' % (infile, lno))
                    return
                l = l.split(']', 1)[1]
                if msgstr:
                    msgstr += b'\0' # Separator of the various plural forms
            else:
                if is_plural:
                    print('indexed msgstr required for plural on  %s:%d' % (infile, lno))
                    return
                l = l[6:]
        # Skip empty lines
        l = l.strip()
        if not l:
            continue
        l = literal_eval(l)
        if section == ID:
            msgid += l.encode(encoding)
        elif section == STR:
            msgstr += l.encode(encoding)
        else:
            print('Syntax error on %s:%d' % (infile, lno), \
                  'before:')
            print(l)
            return
    # Add last entry
    if section == STR:
        add(msgid, msgstr, fuzzy)

    # Compute output
    output = generate()

    try:
        with open(outfile, "wb") as f:
            f.write(output)
    except IOError as msg:
        print(msg)
