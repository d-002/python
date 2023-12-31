from os.path import *
from winreg import *

def get_icon_path(ext):
    if ext in icons:
        return icons[ext]

    try:
        ext_key = OpenKeyEx(reg, ext)
    except:
        icons[ext] = ''
        return ''

    type_name = QueryValueEx(ext_key, '')[0]
    icon_key = OpenKey(reg, join(type_name, 'DefaultIcon'))
    path = QueryValueEx(icon_key, '')[0]

    CloseKey(ext_key)
    CloseKey(icon_key)

    icons[ext] = path
    return path

reg = ConnectRegistry(None, HKEY_CLASSES_ROOT)
icons = {}

print(get_icon_path(input('Enter extension with dot: ')))
