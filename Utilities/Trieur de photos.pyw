import os
import time
import glob
import shutil
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.ttk import *
from threading import Thread

tk = Tk()
tk.title("Trieur de photos")
tk.resizable(0, 0)

path = ""

def browse():
    global path, entry
    path = askdirectory()
    if path is None:
        return
    else:
        entry.delete(0, "end")
        entry.insert(0, path)

def getMonth(month):
    if month == "Jan":
        return "1 - Janvier"
    elif month == "Feb":
        return "2 - Février"
    elif month == "Mar":
        return "3 - Mars"
    elif month == "Apr":
        return "4 - Avril"
    elif month == "May":
        return "5 - Mai"
    elif month == "Jun":
        return "6 - Juin"
    elif month == "Jul":
        return "7 - Juillet"
    elif month == "Aug":
        return "8 - Août"
    elif month == "Sep":
        return "9 - Septembre"
    elif month == "Oct":
        return "10 - Octobre"
    elif month == "Nov":
        return "11 - Novembre"
    else:
        return "12 - Décembre"

def run():
    global path, btn
    if path == "":
        showwarning("Pas de chemin spécifié", "Vous devez choisir le dossier à lire.")
    else:
        try:
            label = Label(tk, text="")
            label.grid(column=1, row=4, columnspan=2, pady=5)
            btn["state"] = "disabled"
            btn["text"] = "Veuillez patienter"
            btn.grid(column=0, columnspan=2)
            fichiers = []
            if allowPhoto.state() != ():
                for f in glob.glob(path + "/*.JPG"):
                    fichiers.append(f)
                for f in glob.glob(path + "/*.PNG"):
                    fichiers.append(f)
            if allowVideo.state() != ():
                for f in glob.glob(path + "/*.MOV"):
                    fichiers.append(f)
                for f in glob.glob(path + "/*.MP4"):
                    fichiers.append(f)
                for f in glob.glob(path + "/*.AVI"):
                    fichiers.append(f)
            if allowSuppr.state() != ():
                label["text"] = "%s fichiers vont être déplacés" % len(fichiers)
                showinfo("Information", "%s fichiers vont être déplacés : ils vont être rangés par année et par mois dans des dossiers différents. " % len(fichiers))
            else:
                label["text"] = "%s fichiers vont être copiés" % len(fichiers)
                showinfo("Information", "%s fichiers vont être rangés, mais les originaux resteront dans le dossier %s sans être supprimés. " % (len(fichiers), path.split("\\")[len(path.split("\\")) - 1]))
            percent = 0
            prev = time.time()
            for f in fichiers:
                label["text"] = "Copie : " + f.split("\\")[-1]
                bar["value"] = fichiers.index(f) / (len(fichiers) - 1) * 100
                bar.update()
                with open(f, "rb") as f_:
                    date = time.ctime(os.path.getmtime(f)).split()
                    for d in date:
                        if d == "":
                            date.remove(date.index(d))
                    year = date[4]
                    month = getMonth(date[1])
                    try:
                        os.makedirs(path + "/" + year + "/" + month)
                    except:
                        pass
                    shutil.copy(f, path + "/" + year + "/" + month + "/" + f.split("\\")[-1])
                    shutil.copystat(f, path + "/" + year + "/" + month + "/" + f.split("\\")[-1])
            if allowSuppr.state() != ():
                for f in fichiers:
                   bar["value"] = fichiers.index(f) / (len(fichiers) - 1) * 100
                   label["text"] = "Suppression : " + f.split("\\")[-1]
                   os.remove(f)
                   bar.update()
            bar["value"] = 100
            label["text"] = "Terminé en %.3f secondes." % (time.time() - prev)
            label.grid(column=2)
            btn.grid(column=1, columnspan=1)
            tk.update()
        except:
            if askyesno("Erreur", "Erreur détectée.\nRéessayer ?"):
                run()
        bar["value"] = 0
        btn["state"] = "normal"
        btn["text"] = "Ranger les fichiers"
        btn.grid(column=1, columnspan=1)

entry = Entry(tk, width=35)
entry.grid(column=0, columnspan=2, row=0)
Button(tk, text="Choisir un dossier...", command=browse).grid(column=2, row=0, pady=(5, 0))

frame2 = LabelFrame(tk, text="Options").grid(column=0, row=1)
allowPhoto = Checkbutton(frame2, text="Copier les photos")
allowPhoto.grid(column=0, row=2, padx=5, pady=5)
allowVideo = Checkbutton(frame2, text="Copier les vidéos")
allowVideo.grid(column=1, row=2, padx= 5, pady=5)
allowSuppr = Checkbutton(frame2, text="Déplacer et non copier")
allowSuppr.grid(column=2, row=2, padx=5, pady=5)

bar = Progressbar(tk, orient="horizontal", length=390, mode="determinate")
bar.grid(column=0, row=3, columnspan=3, padx=5, pady=2)
bar["maximum"] = 100
bar["value"] = 0

btn = Button(tk, text="Ranger les fichiers", command=lambda: Thread(target=run).start())
btn.grid(column=1, row=4, pady=5)

tk.mainloop()
