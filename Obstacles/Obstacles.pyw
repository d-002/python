import time
import glob
import pickle
import _thread
import math
import simpleaudio as sa

from tkinter import *

animations = True

# Initialisation
class Jeu:
    def __init__(self):
        global animations
        self.maxVies = 0
        self.vies = 0
        self.checkPoint = 100000
        self.charge = 0
        self.vitesse = 300
        self.mort = False
        self.lutins = []
        self.tk = Tk()
        self.tk.title("Obstacles")
        #self.tk.wm_attributes("-topmost", 1)
        self.tk.resizable(0, 0)
        self.canvas = Canvas(self.tk, width = 500, height = 300, background="#000000", highlightthickness=0)
        self.canvas.pack()
        self.tk.update()
        self.imageCoeurPlein = PhotoImage(file=r"fichiers\coeur plein.gif")
        self.imageCoeurMoitie = PhotoImage(file=r"fichiers\coeur moitié.gif")
        self.imageCoeurVide = PhotoImage(file=r"fichiers\coeur vide.gif")
        self.ap = PhotoImage(file=r"fichiers\background.gif")
        self.pleinAir = PhotoImage(file=r"fichiers\plein air.gif")
        self.grotte = PhotoImage(file=r"fichiers\grotte.gif")
        self.glace = PhotoImage(file=r"fichiers\glace.gif")
        self.ap2 = self.pleinAir
        if animations:
            self.logo = PhotoImage(file=r"fichiers\logo.gif")
            time.sleep(0.5)
            self.intro = sa.WaveObject.from_wave_file(r"fichiers\intro.wav")
            self.intro = self.intro.play()
            self.canvas.create_image(0, 0, image=self.logo, anchor="nw")
            self.tk.update()
            time.sleep(3)
        self.canvas.delete("all")
        self.setImages()

    def setImages(self):
        global petitBas
        global petitHaut
        global grandBas
        global grandHaut
        if self.ap2 == self.pleinAir:
            petitBas = PhotoImage(file=r"fichiers\petit bas.gif")
            petitHaut = PhotoImage(file=r"fichiers\petit haut.gif")
            grandBas = PhotoImage(file=r"fichiers\grand bas.gif")
            grandHaut = PhotoImage(file=r"fichiers\grand haut.gif")
            self.theme = "plein air"
        elif self.ap2 == self.grotte:
            petitBas = PhotoImage(file=r"fichiers\petit bas_.gif")
            petitHaut = PhotoImage(file=r"fichiers\petit haut_.gif")
            grandBas = PhotoImage(file=r"fichiers\grand bas_.gif")
            grandHaut = PhotoImage(file=r"fichiers\grand haut_.gif")
            self.theme = "grotte"
        elif self.ap2 == self.glace:
            petitBas = PhotoImage(file=r"fichiers\petit bas__.gif")
            petitHaut = PhotoImage(file=r"fichiers\petit haut__.gif")
            grandBas = PhotoImage(file=r"fichiers\grand bas__.gif")
            grandHaut = PhotoImage(file=r"fichiers\grand haut__.gif")
            self.theme = "glace"

    def stop(self, evt):
        self.STOP = True
        
    def animationFin(self):
        if self.xScroll > fin[menu.niveau] and menu.niveau == 7:
            self.co = menu.personnage.coords()
            self.canvas.move(menu.personnage.image, 0, 220 - self.co.y1)
            while self.xScroll - fin[menu.niveau] < 300:
                self.prev = time.time()
                menu.personnage.x += 1
                self.xScroll += 9
                for lutin in self.lutins:
                    lutin.deplacer()
                self.tk.update()
                self.tk.update_idletasks()
                time.sleep(10 / self.vitesse - time.time() + self.prev)
            menu.personnage.y = 15
            while menu.personnage.x > 0.1 and self.co.x2 != 150:
                self.prev = time.time()
                for lutin in self.lutins:
                    lutin.deplacer()
                self.tk.update()
                self.tk.update_idletasks()
                time.sleep(10 / self.vitesse - time.time() + self.prev)
                self.co = menu.personnage.coords()
            self.canvas.itemconfig(menu.personnage.image, image=menu.personnage.imagesAvance[2])
            self.tk.update()
            self.tk.update_idletasks()
            time.sleep(1)
            self.canvas.create_text(250, 100, text="Bravo ! Vous avez terminé le jeu !", font=("Helvetica", 20))
            self.canvas.create_text(250, 170, text="Essayez de battre votre score", font=("Helvetica", 22))
            self.canvas.create_text(250, 190, text="au High Score challenge !", font=("Helvetica", 22))
            self.canvas.create_text(250, 170, text="Essayez de battre votre score", fill="#ff0000", font=("Helvetica", 21))
            self.canvas.create_text(250, 190, text="au High Score challenge !", fill="#ff0000", font=("Helvetica", 21))
            self.canvas.create_text(250, 170, text="Essayez de battre votre score", fill="#ffffff", font=("Helvetica", 20))
            self.canvas.create_text(250, 190, text="au High Score challenge !", fill="#ffffff", font=("Helvetica", 20))
            self.tk.update()
            self.tk.update_idletasks()
            time.sleep(5)
            self.canvas.itemconfig(menu.personnage.image, image=menu.personnage.retourne)
            self.tk.update()
            self.tk.update_idletasks()
            time.sleep(1)
            menu.personnage.x = 0
            self.co = menu.personnage.coords()
            while self.co.x1 < 500:
                self.co = menu.personnage.coords()
                menu.personnage.x += 2
                for lutin in self.lutins:
                    lutin.deplacer()
                self.tk.update()
                self.tk.update_idletasks()
                try:
                    time.sleep(10 / self.vitesse - time.time() + self.prev)
                except:
                    pass
            time.sleep(1)
            self.highScore = True
            self.TERMINE = True
        elif self.xScroll - fin[menu.niveau] > 600:
            self.co = menu.personnage.coords()
            self.canvas.move(menu.personnage.image, 0, 220 - self.co.y1)
            self.x = 0
            self.y = 0
            while self.co.x1 < 500:
                self.prev = time.time()
                self.x += 2
                menu.personnage.x = self.x
                menu.personnage.y = self.y
                menu.personnage.deplacer()
                self.x = self.x * 0.8
                self.tk.update()
                self.tk.update_idletasks()
                time.sleep(10 / self.vitesse - time.time() + self.prev)
                self.co = menu.personnage.coords()
                if self.co.x1 > 399 and self.co.x1 < 401 + self.x:
                    self.y = 15
                if self.y > 0:
                    self.y -= 1
            time.sleep(1)
            self.TERMINE = True

    # Boucle principale : mise à jour des lutins et game over
    def bouclePrincipale(self):
        self.canvas.bind_all("<Escape>", self.stop)
        self.xScroll = self.checkPoint
        self.donnees = menu.donnees
        self.TERMINE = False
        self.STOP = False
        self.mort = False
        self.tk.update_idletasks()
        self.tk.update()
        self.coeurs = []
        self.canvas.create_image(0, 0, image=self.ap, anchor='nw')
        for lutin in self.lutins:
            lutin.setImage()
            if jeu.xScroll != 0:
                lutin.deplacer()
        if menu.niveau < 8:
            for coeur in range(self.maxVies):
                if coeur < self.vies:
                    self.coeurs.append(self.canvas.create_image(10 + 14 * coeur, 10, image=self.imageCoeurPlein, anchor="nw"))
                else:
                    self.coeurs.append(self.canvas.create_image(10 + 14 * coeur, 10, image=self.imageCoeurVide, anchor="nw"))
        for lutin in self.lutins:
            if lutin != menu.personnage:
                lutin.deplacer()
        self.tk.update_idletasks()
        self.tk.update()
        time.sleep(1)
        if menu.niveau == 8:
            self.vies = self.maxVies
            for x in range(2 * self.maxVies):
                for coeur in range(self.maxVies):
                    if coeur < self.vies:
                        if coeur + 0.5 == self.vies:
                            self.coeurs.append(self.canvas.create_image(10 + 14 * coeur, 10, image=self.imageCoeurMoitie, anchor="nw"))
                        else:
                            self.coeurs.append(self.canvas.create_image(10 + 14 * coeur, 10, image=self.imageCoeurPlein, anchor="nw"))
                    else:
                        self.coeurs.append(self.canvas.create_image(10 + 14 * coeur, 10, image=self.imageCoeurVide, anchor="nw"))
                self.tk.update_idletasks()
                self.tk.update()
                self.vies -= 0.5
                time.sleep(0.1 / (self.vies + 0.5))
            time.sleep(1)
            self.vies = 0.5
        while True:
            self.prev = time.time()
            self.sol = False
            for lutin in self.lutins:
                lutin.deplacer()
            self.animationFin()
            self.tk.update_idletasks()
            self.tk.update()
            self.xScroll += 9
            if self.mort and self.vies == int(self.vies):
                self.vies -= 0.5
                jeu.canvas.itemconfig(self.coeurs[int(self.vies)], image=self.imageCoeurMoitie)
                while self.mort:
                    self.mort = False
                    for lutin in self.lutins:
                        lutin.deplacer()
                    self.tk.update_idletasks()
                    self.tk.update()
                    self.xScroll += 5
                self.mort = False
                for lutin in self.lutins:
                    lutin.deplacer()
                self.tk.update_idletasks()
                self.tk.update()
                self.xScroll += 5
            elif self.mort:
                self.vies -= 0.5
                jeu.canvas.itemconfig(self.coeurs[int(self.vies)], image=self.imageCoeurVide)
                break
            elif self.STOP or self.TERMINE:
                self.tk.update_idletasks()
                self.tk.update()
                break
            try:
                time.sleep(10 / self.vitesse - time.time() + self.prev)
            except:
                pass
        
        if self.STOP:
            self.canvas.delete("all")
            menu.resetCanvas(True)
        elif not self.TERMINE:
        # Animation Game Over
            self.prevGameOver = time.time()
            if menu.niveau < 8: 
                self.canvas.create_text(250, 100, text = "GAME OVER...", fill = '#000000', font=('Helvetica', 50))
            while time.time() - self.prevGameOver < 3 and not self.STOP:
                self.prev = time.time()
                for lutin in self.lutins:
                    if lutin == menu.personnage:
                        lutin.mort()
                    else:
                        lutin.deplacer()
                self.xScroll += 9
                self.tk.update_idletasks()
                self.tk.update()
                try:
                    time.sleep(10 / self.vitesse - time.time() + self.prev)
                except:
                    pass
            if self.vies == 0:
                self.STOP = True
            else:
                menu.personnage.reset()

    # Affichage de l'écran de chargement
    def chargement(self):
        if self.charge == -1:
            self.canvas.create_text(250, 190, text = "Veuillez patienter...", fill='#000000')
        else:
            self.canvas.create_rectangle(16, 176, 484, 204, fill='#ffffff')
            self.canvas.create_rectangle(20, 180, 20+int(self.charge), 200, fill='#000000')
            self.canvas.create_text(250, 190, text = str(int(self.charge / 4.6)) + " %", fill='#888888')
        self.tk.update_idletasks()
        self.tk.update()

# Initialisation des coordonnées
class Coords:
    def __init__(self, x1 = 0, y1 = 0, x2 = 0, y2 = 0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


# Base de classe lutins
class Lutin:
    def __init__(self, jeu):
        self.jeu = jeu
        coordonnees = None

    def deplacer(self):
        pass

    def coords(self):
        return self.coordonnees



#Affichage de l'arrière-plan
class ArrierePlan(Lutin):
    def __init__(self):
        Lutin.__init__(self, jeu)
        jeu.lutins.insert(0, self)
        self.costume = jeu.ap2

    def setImage(self):
        self.image = jeu.canvas.create_image(500, 0, image=self.costume, anchor='nw')

    def deplacer(self):
        self.jeu.canvas.move(self.image, -jeu.xScroll * 2000 / (fin[menu.niveau] + 5000) - self.jeu.canvas.coords(self.image)[0], 0)


# Personnage (classe fille de Lutins)
class LutinPersonnage(Lutin):
    
    # Initialisation
    def __init__(self, jeu):
        self.coordonnees = Coords()
        Lutin.__init__(self, jeu)
        self.jeu.lutins.append(self)
        self.numero = len(jeu.lutins)
        if menu.menuCourant == "edit":
            self.numero -= 1
        self.x = 0
        self.y = 0
        self.prevTombeVite = 0
        self.prevCourt = 0
        self.indexImage = 0
        self.retourne = PhotoImage(file=r"fichiers\retourne.gif")
        self.imageSaute = PhotoImage(file=r"fichiers\saut.gif")
        self.imageTombe = PhotoImage(file=r"fichiers\tombe.gif")
        self.imageAssis = PhotoImage(file=r"fichiers\assis.gif")
        self.imagesAvance = [\
            PhotoImage(file=r"fichiers\R1.gif"), \
            PhotoImage(file=r"fichiers\R2.gif"), \
            PhotoImage(file=r"fichiers\R3.gif"), \
            PhotoImage(file=r"fichiers\R4.gif")]
        self.imagesCourt = [\
            PhotoImage(file=r"fichiers\RR1.gif"), \
            PhotoImage(file=r"fichiers\RR2.gif"), \
            PhotoImage(file=r"fichiers\RR3.gif"), \
            PhotoImage(file=r"fichiers\RR4.gif")]
        self.imagesRecule = [\
            PhotoImage(file=r"fichiers\G1.gif"), \
            PhotoImage(file=r"fichiers\G2.gif"), \
            PhotoImage(file=r"fichiers\G3.gif"), \
            PhotoImage(file=r"fichiers\G4.gif")]
        jeu.canvas.bind_all("<Button-1>", self.saut)
        jeu.canvas.bind_all("<Button-3>", self.tombeVite)
        jeu.canvas.bind_all("<KeyPress-Left>", self.gauche)
        jeu.canvas.bind_all("<KeyPress-Right>", self.droite)
        jeu.canvas.bind_all("<KeyPress-Up>", self.saut)
        jeu.canvas.bind_all("<KeyPress-Down>", self.tombeVite)

    def setImage(self):
        self.image = jeu.canvas.create_image(80, 220, image=self.imagesAvance[2], anchor="nw")

    def setPos(self, x, y):
        co = self.coords()
        self.jeu.canvas.move(self.image, x - co.x1, y - co.y1)

    # Récupération des coordonnées
    def coords(self):
        xy = self.jeu.canvas.coords(self.image)
        self.coordonnees.x1 = xy[0]
        self.coordonnees.y1 = xy[1]
        self.coordonnees.x2 = xy[0] + 27
        self.coordonnees.y2 = xy[1] + 30
        return self.coordonnees

    # Sauter si le sol est touché
    def saut(self, evt):
        co = self.coords()
        if jeu.xScroll < fin[menu.niveau]:
            if self.y == 0 or (self.y == -2 and co.y2 == 150):
                self.y = 15

    # Animation de saut groupé
    def tombeVite(self, evt):
        if not jeu.mort and jeu.xScroll < fin[menu.niveau]:
            co = self.coords()
            if co.y1 == 120:
                self.y = -10
            else:
                self.jeu.canvas.itemconfig(self.image, image=self.imageAssis)
                self.jeu.canvas.move(self.image, 0, 0)
                self.jeu.tk.update()
                time.sleep(0.3)
                self.setPos(co.x1, 110 + co.y2 / 2)
                time.sleep(0.01)
                self.jeu.tk.update()
                co = self.coords()
                time.sleep(0.1)
                self.setPos(co.x1, 220)
                self.jeu.tk.update()
                self.prevTombeVite = time.time()
                self.y = 0
                self.x = 0

    # Aller à gauche
    def gauche(self, evt):
        if self.y == 0 and jeu.xScroll < fin[menu.niveau]:
            self.x -= 2

    # Aller à droite
    def droite(self, evt):
        if self.y == 0 and jeu.xScroll < fin[menu.niveau]:
            self.x += 1

    # Couleur du sol pour impact + animations :
    # avance, accélère, ralentit, saute, tombe, saut groupé
    def costumage(self):
        if time.time() - self.prevTombeVite < 0.3:
            self.jeu.canvas.move(jeu.arriereplan.image, 0, (50 * (time.time() - self.prevTombeVite)) % 2 * 10 + 6 * (time.time() - self.prevTombeVite)- self.jeu.canvas.coords(jeu.arriereplan.image)[1])
        elif time.time() - self.prevTombeVite < 0.4 or jeu.mort:
            self.jeu.canvas.move(jeu.arriereplan.image, 0, -self.jeu.canvas.coords(jeu.arriereplan.image)[1])
        if self.y > 0:
            self.jeu.canvas.itemconfig(self.image, image=self.imageSaute)
        elif self.y < 0:
            self.jeu.canvas.itemconfig(self.image, image=self.imageTombe)
        elif self.y == 0 or (co.y2 < 155 and co.y2 > 145 and jeu.sol):
            if self.x < -0.1 and time.time() - self.prevCourt > 0.05:
                self.prevCourt = time.time()
                self.indexImage = 4 * ((1 + self.indexImage) / 4 - int((1 + self.indexImage) / 4))
                self.jeu.canvas.itemconfig(self.image, image=self.imagesRecule[int(self.indexImage)])
            elif self.x > 0.1 and time.time() - self.prevCourt > 0.05:
                self.prevCourt = time.time()
                self.indexImage = 4 * ((1 + self.indexImage) / 4 - int((1 + self.indexImage) / 4))
                self.jeu.canvas.itemconfig(self.image, image=self.imagesCourt[int(self.indexImage)])
            elif time.time() - self.prevCourt > 0.1:
                self.prevCourt = time.time()
                self.indexImage = 4 * ((1 + self.indexImage) / 4 - int((1 + self.indexImage) / 4))
                self.jeu.canvas.itemconfig(self.image, image=self.imagesAvance[int(self.indexImage)])

    def reset(self):
        self.jeu.canvas.itemconfig(self.image, image=self.imagesAvance[0])
        co = self.coords()
        self.setPos(80, 220)
        self.x = 0
        self.y = 0

    # Déplacement du personnage en fonction des modifications des variables
    def deplacer(self):
        # Si touche une plateforme
        self.jeu.canvas.move(self.image, self.x, -self.y)
        co = self.coords()
        if not jeu.xScroll > fin[menu.niveau]:
            if co.x1 < 0:
                self.setPos(0, co.y1)
            if co.x2 > 500:
                self.setPos(500, co.y1)
        # Si touche le sol
        co = self.coords()
        if int(co.y1) > 220:
            self.setPos(co.x1, 220)
            self.y = 0
        co = self.coords()
        # Sur une plateforme
        if co.y2 < 155 and co.y2 > 145 and jeu.sol:
            self.y = 0
            self.setPos(co.x1, 120)
            jeu.sol = False
            co = self.coords()
        self.costumage()
        # Modification des variables
        if self.y == 0:
            self.x = self.x * 0.8
            if co.y2 == 150:
                self.y -= 2
        else:
            self.x = self.x * 1.01
            if self.y > 1:
                self.y = self.y - 1
            else:
                self.y = self.y - 2
        co = self.coords()

    def mort(self):
        co = self.coords()
        if co.y1 > 180:
            self.jeu.canvas.itemconfig(self.image, image=self.imageSaute)
            self.jeu.canvas.move(self.image, 0, 220 - co.y1)
        elif co.y1 > 120:
            self.jeu.canvas.itemconfig(self.image, image=self.imageSaute)
            self.jeu.canvas.move(self.image, 0, 150 - co.y1)
        elif co.y1 > 50:
            self.jeu.canvas.itemconfig(self.image, image=self.imageTombe)
            self.jeu.canvas.move(self.image, 0, 80 - co.y1)
        else:
            self.jeu.canvas.itemconfig(self.image, image=self.imageTombe)
            self.jeu.canvas.move(self.image, 0, 20 - co.y1)
        self.x = -9
        self.jeu.canvas.move(self.image, self.x, 0)


# Pics (classe fille de Lutins)
class LutinPic(Lutin):
    
    # Initialisation
    def __init__(self, jeu, costume, x):
        self.coordonnees = Coords()
        Lutin.__init__(self, jeu)
        self.jeu.lutins.append(self)
        self.numero = len(jeu.lutins)
        if menu.menuCourant == "edit":
            self.numero -= 1
        self.x = x
        self.costume = costume
        if self.costume == petitBas:
            self.y = 200
            self.hauteur = 50
        elif self.costume == petitHaut:
            self.y = 0
            self.hauteur = 50
        elif self.costume == grandBas:
            self.y = 150
            self.hauteur = 100
        else:
            self.y = 0
            self.hauteur = 121

    def setImage(self):
        self.image = self.jeu.canvas.create_image(500, self.y, image=self.costume, anchor ='nw')

    def setPos(self, x, y):
        co = self.coords()
        self.jeu.canvas.move(self.image, x - co.x1, y - co.y1)

    # Récupération des coordonnées
    def coords(self):
        xy = self.jeu.canvas.coords(self.image)
        self.coordonnees.x1 = xy[0]
        self.coordonnees.y1 = xy[1]
        self.coordonnees.x2 = xy[0] + 50
        self.coordonnees.y2 = xy[1] + self.hauteur
        return self.coordonnees

    # Déplacement si visible
    def deplacer(self):
        if self.x - jeu.xScroll < 501 and self.x - jeu.xScroll > -100:
            coSelf = self.coords()
            self.jeu.canvas.move(self.image, self.x - coSelf.x1 - jeu.xScroll, 0)
            coPers = menu.personnage.coords()
            coSelf = self.coords()
            #Tue le joueur s'il a touché un pic
            if abs(coPers.x2 - coSelf.x1 - 25) < 10 and coPers.y2 > coSelf.y1 + 5 and coPers.y1 < coSelf.y2:
                jeu.mort = True
            if self.y < 150:
                if coPers.x2 > coSelf.x1 and coPers.x1 < coSelf.x2 and coPers.y1 == coSelf.y1:
                    jeu.mort = True
            else:
                if coPers.x2 > coSelf.x1 and coPers.x1 < coSelf.x2 and coPers.y2 == coSelf.y2:
                    jeu.mort = True


# Plateformes (classe fille de Lutins)
class LutinPlateforme(Lutin):

    # Initialisation
    def __init__(self, jeu, costume, x):
        self.coordonnees = Coords()
        Lutin.__init__(self, jeu)
        self.jeu.lutins.append(self)
        self.numero = len(jeu.lutins)
        if menu.menuCourant == "edit":
            self.numero -= 1
        self.x = x
        self.y = 150
        self.costume = costume
        if self.costume == imagePlateforme:
            self.hauteur = 110
        else:
            self.hauteur = 100
            self.checkPointOK = PhotoImage(file=r"fichiers\checkPoint2.gif")

    def setImage(self):
        self.image = self.jeu.canvas.create_image(500, self.y, image=self.costume, anchor = 'nw')

    def setPos(self, x, y):
        co = self.coords()
        self.jeu.canvas.move(self.image, x - co.x1, y - co.y1)

    # Récupération des coordonnées
    def coords(self):
        xy = self.jeu.canvas.coords(self.image)
        self.coordonnees.x1 = xy[0]
        self.coordonnees.y1 = xy[1]
        self.coordonnees.x2 = xy[0] + 100
        self.coordonnees.y2 = xy[1] + self.hauteur
        return self.coordonnees
        
    # Déplacement si visible
    def deplacer(self):
        if self.x - jeu.xScroll < 501 and self.x - jeu.xScroll > -150:
            coSelf = self.coords()
            self.setPos(self.x - jeu.xScroll, coSelf.y1)
            coPers = menu.personnage.coords()
            coSelf = self.coords()
            # Change d'image
            if self.costume == imageCheckPoint:
                if jeu.checkPoint < self.x - 75:
                    self.jeu.canvas.itemconfig(self.image, image=self.costume)
                elif menu.donnees[2] != 2:
                    self.jeu.canvas.itemconfig(self.image, image=self.checkPointOK)
            # Vérifie si le joueur est posé dessus
            if coSelf.x2 > coPers.x1 and coSelf.x1 < coPers.x2 and coPers.y2 < coSelf.y1 + 10 and self.costume == imagePlateforme:
                jeu.sol = True
            elif coSelf.x2 > coPers.x1 and coSelf.x1 < coPers.x2 and self.costume != imagePlateforme and menu.donnees[2] != 2:
                jeu.checkPoint = self.x - coPers.x1 + 25


class Musique():
    def __init__(self):
        self.sonPleinAir = sa.WaveObject.from_wave_file(r"fichiers\plein air.wav")
        self.sonGrotte = sa.WaveObject.from_wave_file(r"fichiers\grotte.wav")
        self.sonGlace = sa.WaveObject.from_wave_file(r"fichiers\glace.wav")
        self.sonChateau = sa.WaveObject.from_wave_file(r"fichiers\chateau.wav")
        self.sonMenu = sa.WaveObject.from_wave_file(r"fichiers\menu.wav")
        self.sonEditeur = sa.WaveObject.from_wave_file(r"fichiers\editeur.wav")
        self.sonRate = sa.WaveObject.from_wave_file(r"fichiers\raté.wav")
        self.sonStop = sa.WaveObject.from_wave_file(r"fichiers\stop.wav")
        self.sonGagne = sa.WaveObject.from_wave_file(r"fichiers\gagné.wav")
        self.tempsPleinAir = 67
        self.tempsGrotte = 60
        self.tempsGlace = 60
        self.tempsChateau = 120.8
        self.tempsMenu = 50
        self.tempsEditeur = 67
        self.tempsDebut = 0
        self.temps = 0
        while menu.donnees[3]:
            if menu.menuCourant == "jouer":
                sa.stop_all()
                time.sleep(1)
                if menu.niveau == 7:
                    if menu.menuCourant == "jouer":
                        self.sonChateau.play()
                    else:
                        break
                    while not (jeu.mort and jeu.vies == int(jeu.vies) or jeu.STOP) and menu.menuCourant == "jouer" or not menu.donnees[3]:
                        time.sleep(0.1)
                    time.sleep(0.1)
                    if jeu.mort:
                        sa.stop_all()
                        self.sonRate.play()
                        time.sleep(3)
                    elif jeu.STOP or jeu.TERMINE:
                        sa.stop_all()
                        self.sonStop.play()
                        time.sleep(1)
                else:
                    if menu.menuCourant == "jouer":
                        if jeu.theme == "plein air":
                            self.sonPleinAir.play()
                            self.temps = self.tempsPleinAir
                        elif jeu.theme == "grotte":
                            self.sonGrotte.play()
                            self.temps = self.tempsGrotte
                        elif jeu.theme == "glace":
                            self.sonGlace.play()
                            self.temps = self.tempsGlace
                        self.tempsDebut = time.time()
                    else:
                        break
                    while not (jeu.mort or jeu.STOP) and menu.menuCourant == "jouer" or not menu.donnees[3]:
                        if time.time() - self.tempsDebut >= self.temps:
                            if jeu.theme == "plein air":
                                self.sonPleinAir.play()
                                self.temps = self.tempsPleinAir
                            elif jeu.theme == "grotte":
                                self.sonGrotte.play()
                                self.temps = self.tempsGrotte
                            elif jeu.theme == "glace":
                                self.sonGlace.play()
                                self.temps = self.tempsGlace
                            self.tempsDebut = time.time()
                        time.sleep(0.3)
                    if jeu.mort:
                        sa.stop_all()
                        self.sonRate.play()
                        while jeu.mort:
                            time.sleep(0.75)
                    elif jeu.STOP:
                        sa.stop_all()
                        self.sonStop.play()
                        time.sleep(1)
                    elif jeu.TERMINE:
                        sa.stop_all()
                        self.sonGagne.play()
                        time.sleep(2)
            elif menu.menuCourant == "edit":
                sa.stop_all()
                self.sonEditeur.play()
                self.temps = self.tempsEditeur
                self.tempsDebut = time.time()
                self.attendre()
            elif menu.menuCourant == "test":
                sa.stop_all()
                self.sonNiveau.play()
                self.attendre()
            else:
                sa.stop_all()
                self.sonMenu.play()
                self.temps = self.tempsMenu
                self.tempsDebut = time.time()
                self.attendre(True)
        sa.stop_all()
        while not menu.donnees[3]:
            time.sleep(0.3)
        self.__init__()

    def attendre(self,  multiple=False):
        if multiple:
            while menu.menuCourant != "jouer" and menu.menuCourant != "edit" and menu.menuCourant != "test" and menu.donnees[3]:
                if time.time() - self.tempsDebut >= self.temps:
                    self.sonMenu.play()
                    self.temps = self.tempsMenu
                    self.tempsDebut = time.time()
                time.sleep(0.1)
        else:
            self.menu = menu.menuCourant
            while menu.menuCourant == self.menu and menu.donnees[3]:
                if time.time() - self.tempsDebut >= self.temps:
                    self.sonEditeur.play()
                    self.temps = self.tempsEditeur
                    self.tempsDebut = time.time()
                time.sleep(0.1)


class Menu:
    def __init__(self):
        self.fichiers = []
        self.donnees = []
        self.donneesEdit1 = []
        self.donneesEdit2 = []
        self.donneesEdit3 = []
        self.donneesEdit4 = []
        self.OK = True
        self.animations = True
        self.highScore = False
        self.editeur = False
        self.thread = False
        self.menuCourant = ""
        self.nomUtil = ""
        jeu.canvas.bind_all("<Button-1>", self.clic)
        self.reglage = PhotoImage(file=r"fichiers\reglage.gif")
        self.etoile = PhotoImage(file=r"fichiers\étoile pleine.gif")
        self.etoile_ = PhotoImage(file=r"fichiers\étoile vide.gif")

    def affectation(self, typePics, distancePics, typePlateformes, distancePlateformes):
        self.menuCourant = ""
        jeu.maxVies = 15 - 5 * self.donnees[2]
        jeu.checkPoint = 0
        jeu.STOP = False
        jeu.TERMINE = False
        jeu.lutins = []
        if self.niveau == 8:
            jeu.vies = 0.5
        if jeu.vies == 0:
            jeu.vies = jeu.maxVies

        jeu.canvas.delete(all)

        # Initialisation de toutes les plateformes
        jeu.canvas.create_image(0, 0, image=jeu.ap, anchor='nw')
        jeu.canvas.create_text(250, 100, text = "Chargement...", font=('Helvetica', 50))
        jeu.canvas.create_text(250, 160, text = "Plateformes et points de sauvegarde")
        for plateforme in range(len(typePlateformes)):
            listePlateformes.append(plateforme)
            if typePlateformes[plateforme] == 1:
                LutinPlateforme(jeu, imagePlateforme, int(distancePlateformes[plateforme] * 100))
            else:
                LutinPlateforme(jeu, imageCheckPoint, int(distancePlateformes[plateforme] * 100))
            jeu.charge = plateforme / len(typePlateformes) * 460
            jeu.chargement()
        jeu.charge = 460
        jeu.chargement()
        time.sleep(0.1)

        # Initialisation de tous les pics
        jeu.canvas.create_image(0, 0, image=jeu.ap, anchor='nw')
        jeu.canvas.create_text(250, 100, text = "Chargement...", font=('Helvetica', 50))
        jeu.canvas.create_text(250, 160, text = "Pics")
        time.sleep(0.5)
        for pic in range(len(typePics)):
            listePics.append(pic)
            if typePics[pic] == 1:
                LutinPic(jeu, petitBas, int(100 * distancePics[pic]))
            elif typePics[pic] == 2:
                LutinPic(jeu, petitHaut, int(100 * distancePics[pic]))
            elif typePics[pic] == 3:
                LutinPic(jeu, grandBas, int(100 * distancePics[pic]))
            else:
                LutinPic(jeu, grandHaut, int(100 * distancePics[pic]))
            jeu.charge = pic / len(typePics) * 460
            jeu.chargement()
        jeu.charge = 460
        jeu.chargement()
        time.sleep(0.3)

        jeu.arriereplan = ArrierePlan()
        self.personnage = LutinPersonnage(jeu)

        self.menuCourant = "jouer"

        while jeu.vies > 0 and not jeu.STOP and not jeu.TERMINE:
            jeu.bouclePrincipale()
        self.menuCourant = ""
        if jeu.TERMINE:
            if self.niveau < 7:
                jeu.canvas.create_text(250, 100, text="Niveau terminé !", font=("Helvetica", 20))
                jeu.tk.update()
                jeu.tk.update_idletasks()
                time.sleep(2)
            if not self.donnees[self.niveau + 15] == 2:
                self.donnees[self.niveau + 15] = self.donnees[2]
            self.sauvegarder()
        if self.niveau == 8:
            if self.donnees[1] < jeu.xScroll:
                jeu.canvas.create_text(250, 100, text="Points : %s - Nouveau record !" % jeu.xScroll, font=("Helvetica", 20))
                if jeu.xScroll >= 7000:
                    jeu.tk.update()
                    jeu.tk.update_idletasks()
                    time.sleep(1)
                    jeu.canvas.create_text(250, 150, text="Vous avez débloqué un nouveau bonus !", fill="#ff0000", font=("Helvetica", 20))
                    self.editeur = True
                self.donnees[1] = jeu.xScroll
            else:
                jeu.canvas.create_text(250, 100, text="Points : %s - Record : %s" % (jeu.xScroll, self.donnees[1]), font=("Helvetica", 20))
            jeu.tk.update()
            jeu.tk.update_idletasks()
            time.sleep(2)
        jeu.canvas.bind_all("<Button-1>", self.clic)
        self.sauvegarder()
        self.demanderNiveau()

    def valider(self):
        if self.OK == False:
            self.OK = True

    def clic(self, evt):
        time.sleep(0.2)
        if self.menuCourant == "demanderCompte":
            for x in range(0, 10):
                if evt.x >= 10 + 235 * (x % 2) and evt.y >= 50 * int(2 + x / 2) - 50 and evt.x <= 240 + 250 * (x % 2) and evt.y <= 50 * int(2 + x / 2) - 5:
                    if x < len(glob.glob("*.dat")):
                        self.fichier = glob.glob("*.dat")[x]
                        self.donnees = []
                        f = open(str(self.fichier), "rb")
                        self.donnees = pickle.load(f)
                        self.nombreReussi = 0
                        self.highScore = False
                        self.editeur = False
                        for z in range(0, 8):
                            if self.donnees[z + 15] > 0:
                                self.nombreReussi += 1
                        if self.nombreReussi == 8:
                            self.highScore = True
                        if self.donnees[1] >= 7000:
                            self.editeur = True
                        f.close()
                        self.menuCourant = None
                        self.nomUtil = ''
                        if not self.thread:
                            global musique
                            musique = _thread.start_new_thread(Musique, ())
                            self.thread = True
                        jeu.theme = self.donnees[0]
                        if jeu.theme == "plein air":
                            jeu.ap2 = jeu.pleinAir
                        elif jeu.theme == "grotte":
                            jeu.ap2 = jeu.grotte
                        elif jeu.theme == "glace":
                            jeu.ap2 = jeu.glace
                        jeu.setImages()
                        self.demanderNiveau()
                    elif x == len(glob.glob("*.dat")):
                        self.tk2 = Tk()
                        self.tk2.wm_attributes("-topmost")
                        self.tk2.resizable(0, 0)
                        entree = Entry(self.tk2, width = 15, justify = CENTER)
                        entree.grid(padx=5, pady=5)
                        entree.focus()
                        btn = Button(self.tk2, text= 'Valider', command = self.valider, state='disable')
                        btn.grid(row=0, column=1)
                        self.OK = False
                        while self.OK == False:
                            if entree.get() == "":
                                btn['state'] = 'disable'
                            else:
                                btn['state'] = 'normal'
                            jeu.tk.update()
                            self.tk2.update()
                        self.nomUtil = entree.get()
                        self.tk2.destroy()
                        try:
                            self.donnees = []
                            self.donnees.append("plein air")
                            self.donnees.append(0)
                            self.donnees.append(1)
                            self.donnees.append(True)
                            self.donnees.append(1)
                            for y in range(0, 10):
                                self.donnees.append([0, 0, 0, 0])
                            for y in range(0, 8):
                                self.donnees.append(-1)
                            f = open("%s.dat" % self.nomUtil, "wb")
                            pickle.dump(self.donnees, f)
                            f.close()
                            self.fichier = None
                            self.nomUtil = ""
                            self.resetCanvas()
                            fichiers = glob.glob("*.dat")
                            jeu.canvas.create_text(250, 25, text = "Choisissez un compte ou sélectionnez un nouvel emplacement.")
                            for x in range(0, 10):
                                jeu.canvas.create_rectangle(10 + 235 * (x % 2), 50 * int(2 + x / 2) - 50, 240 + 250 * (x % 2), 50 * int(2 + x / 2) - 5, fill = "#ffffff")
                            for x in range(0, 10):
                                if x < len(fichiers):
                                    nomUtilProvisoire = ""
                                    self.nomUtil = fichiers[x]
                                    for y in self.nomUtil:
                                        if y == ".":
                                            break
                                        nomUtilProvisoire = nomUtilProvisoire + y
                                    self.nomUtil = nomUtilProvisoire
                                    jeu.canvas.create_text(125 + 250 * (x % 2), 50 * int(2 + x / 2) - 30, text = "%s" % self.nomUtil)
                                elif x == len(fichiers):
                                    jeu.canvas.create_text(125 + 250 * (x % 2), 50 * int(2 + x / 2) - 30, text = "-- Libre --")
                            jeu.tk.update()
                            jeu.tk.update_idletasks()
                        except self.entree.get() == "":
                            pass
                        except:
                            pass

        elif self.menuCourant == "demanderNiveau":
            for x in range(0, 10):
                if evt.x >= 10 + 235 * (x % 2) and evt.y >= 50 * int(2 + x / 2) - 50 and evt.x <= 240 + 250 * (x % 2) and evt.y <= 50 * int(2 + x / 2) - 5:
                    self.niveau = x
                    self.jouer()

        elif self.menuCourant == "demanderEditer":
            for x in range(0, 10):
                if evt.x >= 10 + 235 * (x % 2) and evt.y >= 50 * int(2 + x / 2) - 50 and evt.x <= 240 + 250 * (x % 2) and evt.y <= 50 * int(2 + x / 2) - 5:
                    self.niveau = -x - 1
                    edit.getNiveau(self.niveau)
                    edit.modifier()

        if self.menuCourant == "demanderNiveau" or self.menuCourant == "demanderEditer":
            if evt.x > 455 and evt.y > 5 and evt.x < 495 and evt.y < 45:
                self.reglages()
        elif self.menuCourant == "reglages":
            if evt.x > 455 and evt.y > 5 and evt.x < 495 and evt.y < 45:
                self.demanderNiveau()
            elif evt.x > 10 and evt.y > 50 and evt.x < 240 and evt.y < 95:
                jeu.canvas.create_rectangle(10, 50, 240, 95, fill = "#ffffff")
                if self.donnees[2] == 1:
                    jeu.canvas.create_text(125, 70, text = "Difficulté : difficile", fill="#ff0000")
                    self.donnees[2] = 2
                    jeu.vitesse = 400
                elif self.donnees[2] == 0:
                    jeu.canvas.create_text(125, 70, text = "Difficulté : moyen", fill="#ff7700")
                    self.donnees[2] = 1
                    jeu.vitesse = 300
                else:
                    jeu.canvas.create_text(125, 70, text = "Difficulté : facile", fill="#00aa00")
                    self.donnees[2] = 0
                    jeu.vitesse = 200
                jeu.maxVies = 15 - 5 * self.donnees[2]
                jeu.vies = jeu.maxVies
                jeu.tk.update()
                jeu.tk.update_idletasks()
            elif evt.x > 245 and evt.y > 50 and evt.x < 490 and evt.y < 95:
                self.menuCourant = ""
                self.demanderCompte()
            elif evt.x > 10 and evt.y > 100 and evt.x < 240 and evt.y < 145:
                if self.donnees[3]:
                    self.donnees[3] = 0
                else:
                    self.donnees[3] = 1
                jeu.canvas.create_rectangle(10, 100, 240, 145, fill = "#ffffff")
                if self.donnees[3]:
                    jeu.canvas.create_text(125, 120, text = "Musique : oui")
                else:
                    jeu.canvas.create_text(125, 120, text = "Musique : non")
                jeu.tk.update()
                jeu.tk.update_idletasks()
            elif evt.x > 245 and evt.y > 100 and evt.x < 490 and evt.y < 145:
                jeu.canvas.create_rectangle(245, 100, 490, 145, fill="#ffffff")
                jeu.canvas.create_text(375, 120, text = "Sauvegarde...", fill="#ff0000")
                jeu.tk.update()
                self.sauvegarder()
                time.sleep(0.2)
                jeu.canvas.create_rectangle(245, 100, 490, 145, fill="#ffffff")
                jeu.canvas.create_text(375, 120, text = "Sauvegardé", fill="#00aa00")
                jeu.tk.update()
            elif evt.x > 10 and evt.y > 150 and evt.x < 240 and evt.y < 195:
                global animations
                jeu.canvas.create_rectangle(10, 150, 240, 195, fill = "#ffffff")
                if animations:
                    animations = False
                    jeu.canvas.create_text(125, 170, text = "Animations : non")
                else:
                    animations = True
                    jeu.canvas.create_text(125, 170, text = "Animations : oui")
                jeu.tk.update()
                jeu.tk.update_idletasks()
            elif evt.x > 245 and evt.y > 150 and evt.x < 490 and evt.y < 195:
                jeu.canvas.create_rectangle(245, 150, 490, 195, fill = "#ffffff")
                if jeu.theme == "plein air":
                    jeu.ap2 = jeu.grotte
                elif jeu.theme == "grotte":
                    jeu.ap2 = jeu.glace
                elif jeu.theme == "glace":
                    jeu.ap2 = jeu.pleinAir
                jeu.setImages()
                jeu.canvas.create_text(375, 170, text = "Thème : %s" % jeu.theme)
                self.donnees[0] = jeu.theme
                jeu.tk.update()
                jeu.tk.update_idletasks()
            elif evt.x > 10 and evt.y > 200 and evt.x < 240 and evt.y < 245:
                self.demanderNiveau()
            elif evt.x > 245 and evt.y > 200 and evt.x < 490 and evt.y < 245:
                self.menuCourant = ""
                exit()

    def preparerMenu(self, texte, reglages=False, nombre=10, nombre_=10):
        global animations
        self.menuCourant = ""
        for x in range(nombre_):
            jeu.canvas.create_rectangle(10 + 235 * (x % 2), 50 * int(2 + x / 2) - 50, 240 + 250 * (x % 2), 50 * int(2 + x / 2) - 5, fill = "#ffffff")
            if animations:
                time.sleep(0.05)
            jeu.tk.update()
            jeu.tk.update_idletasks()
        self.resetCanvas(reglages)
        jeu.canvas.create_text(250, 25, text = texte)
        for x in range(nombre):
            jeu.canvas.create_rectangle(10 + 235 * (x % 2), 50 * int(2 + x / 2) - 50, 240 + 250 * (x % 2), 50 * int(2 + x / 2) - 5, fill = "#ffffff")
            if animations:
                time.sleep(0.05)
            jeu.tk.update()
            jeu.tk.update_idletasks()

    def sauvegarder(self):
        f = open(str(self.fichier), "wb")
        pickle.dump(self.donnees, f)
        f.close()

    def resetCanvas(self, icone=False):
        jeu.canvas.bind_all("<Button-1>", self.clic)
        jeu.canvas.delete('all')
        jeu.canvas.create_image(0, 0, image=jeu.ap, anchor='nw')
        if icone:
            jeu.canvas.create_image(455, 5, image=self.reglage, anchor='nw')
        jeu.tk.update()
        jeu.tk.update_idletasks()

    def demanderCompte(self):
        self.resetCanvas()
        self.preparerMenu("Choisissez un compte ou sélectionnez un nouvel emplacement.")
        fichiers = glob.glob("*.dat")
        for x in range(0, 10):
            if x < len(fichiers):
                nomUtilProvisoire = ""
                self.nomUtil = fichiers[x]
                for y in self.nomUtil:
                    if y == ".":
                        break
                    nomUtilProvisoire = nomUtilProvisoire + y
                self.nomUtil = nomUtilProvisoire
                nomUtilProvisoire = None
                jeu.canvas.create_text(125 + 250 * (x % 2), 50 * int(2 + x / 2) - 30, text = "%s" % self.nomUtil)
            elif x == len(fichiers):
                jeu.canvas.create_text(125 + 250 * (x % 2), 50 * int(2 + x / 2) - 30, text = "-- Libre --")
            if animations:
                time.sleep(0.05)
            jeu.tk.update()
            jeu.tk.update_idletasks()
        self.menuCourant = "demanderCompte"
        while self.menuCourant == "demanderCompte":
            jeu.tk.update()

    def demanderNiveau(self):
        if menu.menuCourant == "reglages":
            n = 6
        else:
            n = 10
        if self.highScore:
            self.preparerMenu("Choisissez un niveau ou un bonus.", True, nombre_=n)
        else:
            self.preparerMenu("Choisissez un niveau.", True, nombre_=n)
        for x in range(0, 8):
            jeu.canvas.create_text(55 + 250 * (x % 2), 50 * int(2 + x / 2) - 30, text = "Niveau %d" % (x + 1))
            if animations:
                time.sleep(0.05)
            for y in range(3):
                if self.donnees[15 + x] < y:
                    jeu.canvas.create_image(y * 25 + 160 + 250 * (x % 2), 50 * int(2 + x / 2) - 25, image=self.etoile_)
                else:
                    jeu.canvas.create_image(y * 25 + 160 + 250 * (x % 2), 50 * int(2 + x / 2) - 25, image=self.etoile)
            jeu.tk.update()
            jeu.tk.update_idletasks()
        if self.highScore:
            jeu.canvas.create_text(125, 272, fill="#dd0000", text = "High Score Challenge (%d)" % self.donnees[1])
        else:
            jeu.canvas.create_text(125, 272, fill="#999999", text = "Bonus")
            time.sleep(0.05)
            jeu.tk.update()
            jeu.tk.update_idletasks()
        if self.editeur:
            jeu.canvas.create_text(375, 272, fill="#dd0000", text = "Level Maker")
        else:
            jeu.canvas.create_text(375, 272, fill="#999999", text = "Super Bonus")
            time.sleep(0.05)
            jeu.tk.update()
            jeu.tk.update_idletasks()
        self.menuCourant = "demanderNiveau"
        while self.menuCourant == "demanderNiveau":
            jeu.tk.update()

    def reglages(self):
        self.preparerMenu("Réglages", True, 8)
        if self.donnees[2] == 2:
            jeu.canvas.create_text(125, 70, text = "Difficulté : difficile", fill="#ff0000")
        elif self.donnees[2] == 1:
            jeu.canvas.create_text(125, 70, text = "Difficulté : moyen", fill="#ff7700")
        else:
            jeu.canvas.create_text(125, 70, text = "Difficulté : facile", fill="#00aa00")
        time.sleep(0.05)
        jeu.tk.update()
        jeu.tk.update_idletasks()
        jeu.canvas.create_text(375, 70, text = "Se déconnecter")
        time.sleep(0.05)
        jeu.tk.update()
        jeu.tk.update_idletasks()
        jeu.canvas.create_rectangle(10, 100, 240, 145, fill = "#ffffff")
        if self.donnees[3]:
            jeu.canvas.create_text(125, 120, text = "Musique : oui")
        else:
            jeu.canvas.create_text(125, 120, text = "Musique : non")
        time.sleep(0.05)
        jeu.tk.update()
        jeu.tk.update_idletasks()
        jeu.canvas.create_text(375, 120, text = "Sauvegarder")
        time.sleep(0.05)
        jeu.tk.update()
        jeu.tk.update_idletasks()
        if animations:
            jeu.canvas.create_text(125, 170, text = "Animations : oui")
        else:
            jeu.canvas.create_text(125, 170, text = "Animations : non")
        time.sleep(0.05)
        jeu.tk.update()
        jeu.tk.update_idletasks()
        jeu.canvas.create_text(375, 170, text = "Thème : %s" % jeu.theme)
        time.sleep(0.05)
        jeu.tk.update()
        jeu.tk.update_idletasks()
        jeu.canvas.create_text(125, 220, text = "Retour")
        time.sleep(0.05)
        jeu.tk.update()
        jeu.tk.update_idletasks()
        jeu.canvas.create_text(375, 220, text = "Quitter")
        time.sleep(0.05)
        jeu.tk.update()
        jeu.tk.update_idletasks()
        self.menuCourant = "reglages"
        while self.menuCourant == "reglages":
            jeu.tk.update()

    def demanderEditer(self):
        self.preparerMenu("Choisissez un niveau.")
        for x in range(0, 10):
            edit.getDonnees(x + 1)
            if edit.typePics == [] and edit.typePlateformes == []:
                jeu.canvas.create_text(125 + 250 * (x % 2), 50 * int(2 + x / 2) - 30, text = "-- Libre --")
            else:
                jeu.canvas.create_text(125 + 250 * (x % 2), 50 * int(2 + x / 2) - 30, text = "Création %d" % (x + 1))
            if animations:
                time.sleep(0.05)
            jeu.tk.update()
            jeu.tk.update_idletasks()
        self.menuCourant = "demanderEditer"
        while self.menuCourant == "demanderEditer":
            jeu.tk.update()

    def jouer(self):
        if self.niveau == 0:
            self.affectation(typePics1, distancePics1, typePlateformes1, distancePlateformes1)
        elif self.niveau == 1:
            self.affectation(typePics2, distancePics2, typePlateformes2, distancePlateformes2)
        elif self.niveau == 2:
            self.affectation(typePics3, distancePics3, typePlateformes3, distancePlateformes3)
        elif self.niveau == 3:
            self.affectation(typePics4, distancePics4, typePlateformes4, distancePlateformes4)
        elif self.niveau == 4:
            self.affectation(typePics5, distancePics5, typePlateformes5, distancePlateformes5)
        elif self.niveau == 5:
            self.affectation(typePics6, distancePics6, typePlateformes6, distancePlateformes6)
        elif self.niveau == 6:
            self.affectation(typePics7, distancePics7, typePlateformes7, distancePlateformes7)
        elif self.niveau == 7:
            self.affectation(typePics8, distancePics8, typePlateformes8, distancePlateformes8)
        elif self.niveau == 8 and self.highScore:
            self.affectation(typePics0, distancePics0, typePlateformes0, distancePlateformes0)
        elif self.niveau == 9 and self.editeur:
            self.demanderEditer()
        elif self.niveau < 0:
            edit.modifier()

class Editeur():
    def __init__(self):
        self.imageEditeur = PhotoImage(file="fichiers\cadre.gif")
        self.imageEditeur_= PhotoImage(file="fichiers\cadre_.gif")

    def getNiveau(self, niveau):
        self.niveau = niveau
        
    def getDonnees(self, niveau=None):
        if niveau == None:
            niveau = -self.niveau
        index = 1
        nombre = 0
        self.typePics = []
        self.distancePics = []
        self.typePlateformes = []
        self.distancePlateformes = []
        if menu.donnees[4 + niveau][0] != 0:
            while menu.donnees[4 + niveau][index] != ",":
                nombre = nombre * 10 + int(menu.donnees[4 + niveau][index])
                index += 1
            index = 4 + int(math.log10(nombre))
            for x in range(nombre):
                self.typePics.append(int(menu.donnees[4 + niveau][index]))
                index += 3
        virgule = 0
        if menu.donnees[4 + niveau][0] != 0:
            index += 3 + int(math.log10(nombre))
            for x in range(nombre):
                if menu.donnees[4 + niveau][index + 1] == ",":
                    self.distancePics.append(menu.donnees[4 + niveau][index]) # nombre à un chiffre
                else:
                    while menu.donnees[4 + niveau][index + 1] != ",":
                        virgule = 0
                        if menu.donnees[4 + niveau][index - 1] == " ": # début d'un nouveau nombre
                            self.distancePics.append(int(menu.donnees[4 + niveau][index]))
                        else: # nombre à plusieurs chiffres
                            self.distancePics[len(self.distancePics) - 1] = self.distancePics[len(self.distancePics) - 1] * 10 + int(menu.donnees[4 + niveau][index])
                        if menu.donnees[4 + niveau][index + 1] == ".": # nombre décimal
                            index += 1
                            while menu.donnees[4 + niveau][index + 1] != ",":
                                virgule += 1
                                index += 1
                                self.distancePics[len(self.distancePics) - 1] = self.distancePics[len(self.distancePics) - 1] + int(menu.donnees[4 + niveau][index]) / 10**virgule
                        if menu.donnees[4 + niveau][index + 1] != ",":
                            index += 1
                    if not virgule:
                        self.distancePics[len(self.distancePics) - 1] = self.distancePics[len(self.distancePics) - 1] * 10 + int(menu.donnees[4 + niveau][index])
                index += 3
        index_ = index
        nombre = 0
        if menu.donnees[4 + niveau][0] != 0:
            while menu.donnees[4 + niveau][index] != ",":
                nombre = nombre * 10 + int(menu.donnees[4 + niveau][index])
                index += 1
            index = index_ + 3 + int(math.log10(nombre))
            for x in range(nombre):
                self.typePlateformes.append(int(menu.donnees[4 + niveau][index]))
                index += 3
        virgule = 0
        if menu.donnees[4 + niveau][0] != 0:
            index += 3 + int(math.log10(nombre))
            for x in range(nombre):
                if menu.donnees[4 + niveau][index + 1] == ",":
                    self.distancePlateformes.append(menu.donnees[4 + niveau][index]) # nombre à un chiffre
                else:
                    while menu.donnees[4 + niveau][index + 1] != ",":
                        virgule = 0
                        if menu.donnees[4 + niveau][index - 1] == " ": # début d'un nouveau nombre
                            self.distancePlateformes.append(int(menu.donnees[4 + niveau][index]))
                        else: # nombre à plusieurs chiffres
                            self.distancePlateformes[len(self.distancePlateformes) - 1] = self.distancePlateformes[len(self.distancePlateformes) - 1] * 10 + int(menu.donnees[4 + niveau][index])
                        if menu.donnees[4 + niveau][index + 1] == ".": # nombre décimal
                            index += 1
                            while menu.donnees[4 + niveau][index + 1] != ",":
                                virgule += 1
                                index += 1
                                self.distancePlateformes[len(self.distancePlateformes) - 1] = self.distancePlateformes[len(self.distancePlateformes) - 1] + int(menu.donnees[4 + niveau][index]) / 10**virgule
                        if menu.donnees[4 + niveau][index + 1] != ",":
                            index += 1
                    if not virgule:
                        self.distancePlateformes[len(self.distancePlateformes) - 1] = self.distancePlateformes[len(self.distancePlateformes) - 1] * 10 + int(menu.donnees[4 + niveau][index])
                index += 3

    def setDonnees(self):
        self.typePics = []
        self.distancePics = []
        self.typePlateformes = []
        self.distancePlateformes = []
        for lutin in range(1, len(jeu.lutins) - 1):
            if lutin.image == petitBas:
                self.typePics.append(1)
                self.distancePics.append(lutin.x / 100)
            elif lutin.image == petitHaut:
                self.typePics.append(2)
                self.distancePics.append(lutin.x / 100)
            elif lutin.image == grandBas:
                self.typePics.append(3)
                self.distancePics.append(lutin.x / 100)
            elif lutin.image == grandHaut:
                self.typePics.append(4)
                self.distancePics.append(lutin.x / 100)
            elif lutin.image == imagePlateforme:
                self.typePlateformes.append(1)
                self.distancePlateformes.append(lutin.x / 100)
            elif lutin.image == imageCheckPoint:
                self.typePlateformes.append(0)
                self.distancePlateformes.append(lutin.x / 100)
        menu.donnees[4 - menu.niveau] = []
        menu.donnees[4 - menu.niveau].append(len(self.typePics))
        menu.donnees[4 - menu.niveau].append(self.typePics[x] for x in range(len(self.typePics)))
        menu.donnees[4 - menu.niveau].append(len(self.distancePics))
        menu.donnees[4 - menu.niveau].append(self.distancePics[x] for x in range(len(self.distancePics)))
        menu.donnees[4 - menu.niveau].append(len(self.typePlateformes))
        menu.donnees[4 - menu.niveau].append(self.typePlateformes[x] for x in range(len(self.typePlateformes)))
        menu.donnees[4 - menu.niveau].append(len(self.distancePlateformes))
        menu.donnees[4 - menu.niveau].append(self.distancePlateformes[x] for x in range(len(self.distancePlateformes)))

    def modifier(self):
        menu.resetCanvas()
        menu.menuCourant = "edit"
        jeu.tk.update()
        jeu.tk.update_idletasks()
        jeu.xScroll = 0
        self.drapeau = 0
        self.imageDrapeau = None
        jeu.lutins = []
        self.deplace = False
        self.selection = ""
        self.getDonnees()
        jeu.charge = -1
        jeu.chargement()
        jeu.canvas.delete("all")
        jeu.canvas.create_image(0, 0, image=jeu.ap, anchor="nw")
        self.arriereplan = ArrierePlan()
        self.arriereplan.setImage()
        personnage = LutinPersonnage(jeu)
        personnage.setImage()
        personnage.reset()
        personnage.deplacer()
        self.cadre = jeu.canvas.create_image(0, 0, image = self.imageEditeur, anchor='nw')
        while menu.menuCourant == "edit" or menu.menuCourant == "test":
            jeu.canvas.bind_all("<KeyPress-Left>", self.gauche)
            jeu.canvas.bind_all("<KeyPress-Right>", self.droite)
            jeu.canvas.bind_all("<Button-1>", self.clic)
            jeu.canvas.bind_all("<Button-3>", self.effacer)
            for lutin in jeu.lutins:
                if lutin != self.cadre and (lutin != personnage or menu.menuCourant == "test"):
                    lutin.deplacer()
                    if (jeu.mort or jeu.xScroll > self.drapeau + 200) and menu.menuCourant == "test":
                        time.sleep(0.5)
                        menu.menuCourant = "test"
                else:
                    jeu.canvas.itemconfig(lutin.image, image=lutin.imagesAvance[2])
                jeu.tk.update()
                jeu.tk.update_idletasks()
            if menu.menuCourant == "edit":
                jeu.canvas.itemconfig(self.cadre, image=self.imageEditeur)
            else:
                jeu.canvas.itemconfig(self.cadre, image=self.imageEditeur_)
            if self.imageDrapeau:
                self.drapeau = self.imageDrapeau.x
            jeu.tk.update()
            jeu.tk.update_idletasks()
            time.sleep(0.03)

    def clic(self, evt):
        if menu.menuCourant == "edit" or menu.menuCourant == "test":
            if evt.x > 450 and evt.x < 490 : # Pour sélectionner une icône d'action de droite
                if evt.y > 10 and evt.y < 50:
                    self.quitterModeEditer()
                elif evt.y > 250 and evt.y < 290:
                    if menu.menuCourant == "edit":
                        menu.menuCourant = "test"
                    if menu.menuCourant == "test":
                        menu.menuCourant = "edit"
        if menu.menuCourant == "edit":
            if evt.x > 10 and evt.x < 60: # Pour sélectionner une icône de la barre d'outils à gauche
                if evt.y > 10 and evt.y < 50:
                    self.selection = "plateforme"
                elif evt.y > 60 and evt.y < 90:
                    self.selection = "checkpoint"
                elif evt.y > 100 and evt.y < 130:
                    self.selection = "drapeau"
                elif evt.y > 140 and evt.y < 160:
                    self.selection = "petit bas"
                elif evt.y > 170 and evt.y < 190:
                    self.selection = "petit haut"
                elif evt.y > 200 and evt.y < 240:
                    self.selection = "grand bas"
                elif evt.y > 250 and evt.y < 290:
                    self.selection = "grand haut"
            else: # Poser ou déplacer un lutin du jeu
                self.lutinsSelects = 0 # Pour éviter de déplacer deux lutins en même temps
                for lutin in jeu.lutins:
                    if lutin != self.arriereplan:
                        coLutin = lutin.coords()
                        if evt.x - coLutin.x1 <= lutin.x2 and evt.y - coLutin.y1 <= lutin.y2 and self.lutinsSelects < 2:
                            if self.deplace == False:
                                self.decalageX = evt.x - coLutin.x1
                                if lutin == personnage:
                                    self.decalageY = evt.y - coLutin.y1
                                self.lutinSelect = lutin
                                self.deplace = True
                                self.lutinsSelects += 1
                            elif lutin == personnage:
                                jeu.canvas.move(evt.x - self.decalageX - coLutin.x1, evt.y - self.decalageY - coLutin.y1, image=lutin.image)
                            else:
                                jeu.canvas.move(evt.x - self.decalageX - coLutin.x1, 0, image=lutin.image)
                                coLutin = lutin.coords()
                                lutin.x = coLutin.x + jeu.xScroll
                if self.lutinsSelects == 0: # Pour poser un lutin
                    self.decalageX = 25
                    if self.selection == "plateforme":
                        LutinPlateforme(jeu, imagePlateforme, evt.x - 50)
                        self.decalageX = 50
                    elif self.selection == "checkpoint":
                        LutinPlateforme(jeu, imageCheckPoint, evt.x - 50)
                        self.decalageX = 50
                    elif self.selection == "drapeau" and not self.drapeau:
                        self.imageDrapeau = LutinPlateforme(jeu, imageDrapeau, evt.x - 50)
                    elif self.selection == "petit bas":
                        LutinPic(jeu, imageCheckPoint, evt.x - 25)
                    elif self.selection == "petit haut":
                        LutinPic(jeu, imageCheckPoint, evt.x - 25)
                    elif self.selection == "grand bas":
                        LutinPic(jeu, imageCheckPoint, evt.x - 25)
                    elif self.selection == "grand haut":
                        LutinPic(jeu, imageCheckPoint, evt.x - 25)
                    jeu.lutins[lutin.numero].setImage()
                    jeu.lutins[lutin.numero].deplacer()
                    time.sleep(0.25)

    def effacer(self):
        self.lutinsSelects = 0
        for lutin in jeu.lutins:
            if lutin != jeu.arriereplan:
                coLutin = lutin.coords()
                if evt.x - coLutin.x1 <= lutin.x2 and evt.y - coLutin.y1 <= lutin.height.y2 and self.lutinsSelects < 2:
                    jeu.canvas.itemconfig(image=lutin.image, state=hidden)
                    jeu.lutins.remove(lutin.numero)
                    for lutin_ in jeu.lutins[range(lutin.numero + 1, len(jeu.lutins) - 1)]:
                        lutin_.numero -= 1
                    time.sleep(0.2)

    def gauche(self, evt):
        if jeu.xScroll > 0:
            jeu.xScroll -= 15

    def droite(self, evt):
        jeu.xScroll += 15

    def quitterModeEditer(self):
        jeu.canvas.create_text(250, 100, text = "Sauvegarde...", font=('Helvetica', 50))
        self.setDonnees()
        time.sleep(0.5)
        menu.demanderEditer()


# typePlateformes : 0 - checkPoint, 1 - plateforme, 2 - drapeau
#
# etatNiveau : 0 - non fait, 1 - fait en mode facile, 2 - fait en mode difficile
# difficulté : 1 - facile, 2 - difficile
# musique : True ou False
# langue : 0 - anglais, 1 - français
# donnees = [nom, scoreHighScoreChallenge, difficulte, musique, langue, donneesEdit1, donneesEdit2..., donneesEdit10, etatNiveau1, etatNiveau2..., etatNiveau8]

# . = petit bas, ' = petit haut, i = grand bas, ! = grand haut,
# L = petit haut et grand bas, T = petit bas et grand haut
#
# 1 = petit bas, 2 = petit haut, 3 = grand bas, 4 = grand haut
#####
# 1 = plateforme, 0 = checkPoint

jeu = Jeu()

edit = Editeur() 
menu = Menu()

listePics           = []
listePlateformes    = []
imagePlateforme     = PhotoImage(file=r"fichiers\plateforme.gif")
imageCheckPoint     = PhotoImage(file=r"fichiers\checkPoint.gif")
imageDrapeau        = PhotoImage(file=r"fichiers\drapeau.gif")

typePics0 =     [1, 1, 2, 2, 1, 2, 3, 3, 3, 4, 1, 4, 1, 4, 1, 4, 1, 3, 4, 3, 2, 1, 4, 1, 4, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 3, 2, 4, 1, 1, 1, 1, 4, 4, 4, 4, 1, 3, 1, 3, 1, 4, 1, 1, 4, 2, 3, 4, 1, 1, 4, 1, 2, 4, 4, 4, 4, 4, 3, 3, 3, 1, 3, 1, 4, 4, 4, 3, 3, 1, 3, 2, 1, 1, 2, 2, 2, 1, 1, 1, 3, 1, 2, 2, 1, 4, 2, 4, 1, 4, 1]
distancePics0 = [10, 20, 25, 25.9, 27, 27.5, 30, 33, 35, 36, 39, 40, 42, 43, 44.5, 45.8, 47, 47.5, 48.5, 49.5, 50, 51, 52, 53.3, 54.5, 57.5, 58, 60, 60.5, 62, 62.5, 64, 65.3, 66.5, 68, 68.5, 71.5, 72.8, 74, 75.5, 77, 77.5, 79.5, 81, 87, 87, 90, 90, 102, 102.5, 103, 105, 105.5, 106, 106.5, 109, 109.5, 110, 110.5, 111, 115, 115.5, 116, 117, 118, 118, 120, 120.5, 121, 121.8, 130, 140, 145, 145.5, 146, 146.5, 147, 147.5, 148, 148.5, 148.5, 149, 149, 149.5, 150, 150.5, 151, 151.5, 151.5, 152, 155, 155.5, 156, 156.5, 157.25, 158, 158.5, 159, 159.5, 160.25, 161, 161.5, 162, 162.5, 163.5, 166, 168, 169, 172, 172.8]
typePlateformes0 = [0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1]
distancePlateformes0 = [37, 45.9, 55.5, 78, 101.7, 102.7, 103.5, 109, 110, 122.5, 153.5, 155, 156, 158, 159, 161, 165, 169]
typePics1 =     [1, 1, 1, 2, 4, 1, 2, 3, 1, 3, 2, 2, 1, 1, 4, 1, 4, 3, 1, 1, 2, 1, 1, 4, 1, 1, 2, 1, 1, 4, 3, 2, 1, 1, 1, 2, 1, 2, 2, 4, 4, 4, 2, 2, 3, 2]
distancePics1 = [10, 15, 18, 19, 22, 23, 25, 26, 30, 30.5, 32, 32.5, 32.5, 33, 36, 37, 39, 40, 43, 43.5, 44.5, 46.5, 47, 48, 50, 50.5, 52, 53.5, 54, 55.5, 57, 57, 59.5, 60, 62, 62, 62.5, 62.5, 63, 63.5, 64, 64.5, 65, 65.5, 66, 66]
typePlateformes1 = [0, 0]
distancePlateformes1 = [31, 48]
typePics2 =     [1, 2, 3, 1, 3, 1, 2, 2, 2, 3, 4, 1, 4, 1, 1, 2, 2, 2, 2, 4, 3, 2, 2, 4, 4, 1, 2, 2, 4, 4, 1, 2, 2, 4, 1, 2, 2, 4, 1, 2, 2, 2, 2, 1, 2, 4, 1, 2, 2, 1, 1, 1, 1, 1, 1, 4, 1, 1, 2, 4, 4, 1, 4]
distancePics2 = [5, 5, 8, 11, 15, 18, 18, 21, 22, 22.5, 23.75, 24.75, 26, 27, 27, 27.5, 27.5, 28, 28.5, 29, 32, 32, 34, 34.5, 35, 35.5, 35.5, 36, 36.5, 37, 37.5, 37.5, 38, 38.5, 39, 39, 39.5, 40, 40.5, 40.5, 41, 41.5, 45, 47, 47, 49, 51.5, 51.5, 52, 53, 54, 55.5, 56, 58, 58.5, 59.5, 60, 60.5, 61.5, 62, 62.5, 63, 63]
typePlateformes2 = [0, 0]
distancePlateformes2 = [32.5, 42]
typePics3 =     [1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 3, 2, 1, 2, 1, 3, 1, 4, 1, 4, 3, 3, 3, 3, 3, 1, 4, 3, 3, 3, 1, 4, 3, 3, 3, 3, 3, 2, 3, 3, 4, 1, 1, 3]
distancePics3 = [5, 5.5, 6, 6.5, 10, 10, 10.5, 10.5, 11, 11, 11.5, 11.5, 12, 15, 15.5, 16, 17, 18.25, 18.5, 19, 21, 22, 24.5, 26, 27, 30, 30.5, 31, 31.5, 32, 35, 36.5, 37, 37.5, 38, 39.25, 45, 45.5, 47, 47.5, 48, 50, 52, 52.5, 55, 57, 57.5, 58.75]
typePlateformes3 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
distancePlateformes3 = [5.75, 10.75, 15.25, 18.25, 24, 30.5, 36.5, 37.5, 38.5, 43.5, 46, 48.5, 53, 58, 59, 22, 41]
typePics4 =     [1, 1, 1, 1, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 4, 1, 4, 4, 4, 1, 2, 2, 4, 4, 1, 2, 2, 4, 1, 2, 4, 1, 4, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 2, 2, 1, 2, 1, 2, 1, 1, 2, 2, 1, 2, 1, 2, 1, 1, 4, 2, 4, 2, 4, 1, 1, 2, 1, 4, 1, 2, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 4, 1, 2, 1, 4, 1, 1, 1, 1, 1, 1]
distancePics4 = [20, 23, 23, 23.5, 26, 28, 28, 30.5, 32.5, 32.5, 34, 36, 36, 38, 39, 45.25, 47.25, 50, 50.5, 51, 51.5, 51.5, 52, 25.5, 53, 53, 53.5, 54, 54.5, 54.5, 58, 58.75, 58.5, 61, 63.5, 64, 66.5, 67, 68.5, 69, 71, 73, 73.5, 74.5, 75, 75.5, 75.5, 76, 76, 76.5, 77, 80, 80.5, 81, 81.5, 82, 82, 82.5, 83, 85, 85.5, 86, 86.5, 87, 89, 90.5, 91.5, 92.5, 93.25, 94, 95, 96, 96.5, 98, 100.5, 101, 103, 103.5, 106, 106.5, 107, 110, 110.5, 110.5, 111, 111.5, 112, 115, 115.5, 116.75, 117, 118.5, 121, 125, 125.5, 126, 126.5, 127]
typePlateformes4 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
distancePlateformes4 = [23, 43, 44, 45, 46, 47, 75.75, 82.25, 106.75, 110.5, 125, 46, 80, 99]
typePics5 =     [1, 2, 4, 4, 4, 1, 2, 2, 1, 4, 3, 2, 2, 3, 4, 1, 2, 3, 2, 3, 2, 1, 1, 3, 2, 3, 2, 1, 2, 4, 4, 4, 4, 2, 1, 2, 1, 2, 1, 2, 3, 3, 1, 2, 4, 3, 4, 3, 4, 3, 1, 2, 1, 2, 3, 2]
distancePics5 = [5, 5, 6.75, 9.25, 11.75, 13.5, 14, 14.5, 15, 17.25, 19, 20.5, 21, 22, 23.5, 25, 25, 25.5, 25.5, 26, 26, 26.5, 27, 27.5, 27.5, 28, 28, 28.5, 28.5, 30, 30.5, 31, 31.5, 32.25, 32.75, 32.75, 33.25, 33.25, 33.75, 33.75, 34.25, 35, 35.5, 35.5, 36.75, 38, 38.75, 40, 40.75, 42, 45, 45, 45.5, 45.5, 47.25, 47]
typePlateformes5 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
distancePlateformes5 = [4.25, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22.5, 25.75, 26.75, 27.75, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 29]
typePics6 =     [1, 4, 1, 4, 1, 4, 3, 2, 3, 2, 3, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 4, 4, 1, 4, 3, 2, 3, 3, 3, 4, 1, 1, 2, 3, 1, 4, 1, 4, 1, 4, 1, 4, 3, 2, 3, 2, 3, 2, ]
distancePics6 = [3, 3, 5, 5, 7, 7, 9, 9, 11, 11, 13, 13, 15, 15, 15.5, 15.5, 18.5, 18.5, 20.5, 20.5, 21, 21, 21.5, 21.5, 23.5, 23.5, 25, 25, 26.5, 26.5, 27, 27.5, 18, 29, 29.5, 30, 30, 32, 31.5, 33, 33.5, 34, 35, 39, 39.5, 40, 41, 41, 42, 43.5, 43.5, 47, 47, 50, 50, 53, 53, 55, 55, 57, 57, 59, 59]
typePlateformes6 = [1, 1, 1, 1, 0]
distancePlateformes6 = [26.5, 31.25, 33.75, 40, 29]
typePics7 =     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 3, 3, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 3, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3]
distancePics7 = [2.5, 4, 5.5, 7, 8.5, 9, 10.5, 11, 12.5, 13, 14.5, 15, 15.5, 17, 17.5, 18, 19.5, 20, 20.5, 21, 21.5, 22.5, 23, 23.5, 24, 24.5, 27, 27.5, 28, 28.5, 29, 29.5, 30, 30.5, 33, 33.5, 34, 34.5, 35, 35.5, 37, 37.5, 38, 38.5, 39, 39.5, 40, 40.5, 41, 41.5, 43.5, 44, 45.5, 46, 47.5, 48, 50, 51.5, 53, 54.5, 56, 57.5, 58, 58.5, 59, 59.5, 60, 60.5, 61, 61.5, 62, 62.5, 64]
typePlateformes7 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
distancePlateformes7 = [20.25, 23.5, 27.75, 29.75, 33.75, 37.75, 39.75, 46.25, 48.25, 58.75, 61.75, 31.5]
typePics8 =     [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 4, 3, 3, 2, 4, 4, 2, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 4, 1, 2, 1, 2, 1, 2, 1, 3, 3, 3, 3, 3, 2, 3, 3, 1, 4, 3, 3, 1, 4, 3, 4, 3, 2, 2, 3, 2, 2, 2, 3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 4, 3, 2, 4, 3, 2, 4, 3, 2, 1, 3, 1, 2, 2, 1, 4, 1, 4, 1]
distancePics8 = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5.5, 6.5, 7, 7.5, 8, 8.5, 10, 10.5, 11, 11.5, 12, 12.5, 13.25, 14.5, 15.5, 17, 17, 17.5, 17.5, 19, 19, 19.5, 19.5, 20.75, 20.5, 22, 22, 22.5, 22.5, 23, 23, 24.5, 25, 25.5, 26, 26.5, 27, 28, 28, 28, 28.5, 29, 30.5, 31, 31.5, 32.5, 33.5, 34.5, 36, 36, 36.5, 36.5, 37.5, 37.5, 37.5, 40, 40, 43, 43, 45, 45, 47, 47, 49, 49, 51, 51, 53, 53, 55, 56.5, 57.75, 58.5, 59.25, 60, 61.5, 62.25, 63, 63.75, 64.5, 66, 66, 67.5, 69, 69.5, 70.5, 71.5, 73, 73, 80]
typePlateformes8 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
distancePlateformes8 = [25, 27.25, 28.5, 29.75, 31.5, 32.5, 33.5, 67.75, 70.75, 88.5, 89.5, 90.5, 91.5, 92.5, 93.5, 23.25, 38.25]

fin = [7150, 6850, 6600, 13250, 5250, 6450, 6950, 8550, 17500]

# Lancement

menu.demanderCompte()
