from tkinter import *
from tkinter.scrolledtext import *
from tkinter.filedialog import *

win = Tk()

with open(askopenfile().name, "r") as file:
    text = ScrolledText(win, width=80, height=41, wrap=WORD)
    text.pack(expand=True, fill=BOTH)
    text.insert(1.0, file.read())

win.mainloop()
