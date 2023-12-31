import os
import shutil
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *

tk = Tk()
tk.title('Convert')
tk.wm_attributes('-alpha', 0)
path = askopenfile()
tk.destroy()

if path is None:
    exit()
path = path.name
file_name = os.path.splitext(os.path.basename(path))[0]
file_name_subfolder = '%s\\dist\\%s.exe' %(os.path.abspath(os.getcwd()), file_name)

os.system('py -m PyInstaller --onefile "%s"' %path)
if os.path.exists(file_name + '.exe'):
    os.remove(file_name + '.exe')
shutil.move(file_name_subfolder, file_name + '.exe')
shutil.rmtree('dist')
shutil.rmtree('build')
shutil.rmtree('__pycache__')
os.remove('%s.spec' %file_name)

tk = Tk()
tk.title('Success')
tk.wm_attributes('-alpha', 0)
showinfo('Success', 'Operation successful')
tk.destroy()
