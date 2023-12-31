from shutil import move
from os import listdir, walk, rmdir
from os.path import join, isdir, isfile
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askdirectory

def run():
    path = askdirectory()
    if not path:
        return
    
    dirs = [x for x in listdir(path) if not '.' in x]
    while dirs != []:
        for dir in dirs:
            files = listdir(join(path, dir))
            for file in files:
                add('  |  Copie de %s...  --' %file)
                if isdir(join(path, file)):
                    move(join(path, dir, file), join(path, file + '-'))
                else:
                    move(join(path, dir, file), join(path, file))
                add(' OK\n')
            if listdir(join(path, dir)) == []:
                add('  |  Suppression de %s... --' %dir)
                rmdir(join(path, dir))
                add(' OK\n')
            add('\n\n')
        dirs = [x for x in listdir(path) if not '.' in x]
        
    add('--- TERMINE ---\n\n\n')

def add(text):
    textbox.insert(1.0, text)
    tk.update()

tk = Tk()
tk.title('Regroupement de fichiers')
Button(tk, text='Choisir un dossier et regrouper', command=run, width=55).grid(padx=2, pady=2)
textbox = ScrolledText(tk, width=40, height=10, wrap=WORD)
textbox.grid(row=1, padx=5, pady=5)
tk.mainloop()
