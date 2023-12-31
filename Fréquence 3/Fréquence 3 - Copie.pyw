##### Requirements: vlc, pygame>=2.0.0

import ssl
import vlc
import json
import time
import pygame
import certifi
import webbrowser
from math import cos, sin
from threading import Thread
from pygame.locals import *
from urllib.request import *

context = ssl.create_default_context(cafile=certifi.where())
pygame.init()

class Window:
    def __init__(self):
        self.screen = pygame.display.set_mode((600, 400))

    def init(self):
        self.colors = [(242, 177, 0), (0, 157, 233), (245, 0, 0), (106, 59, 20), (75, 182, 132)]

        self.black = (17, 17, 17)
        self.grey = (33, 37, 41)
        self.grey_ = (self.grey[0]+20, self.grey[1]+20, self.grey[2]+20)
        self.light_grey = (195, 195, 195)
        self.white = (250, 246, 249)

        pygame.display.set_icon(pygame.image.load('files/icon.png'))

        play = pygame.image.load('files/play.png')
        play_inner = pygame.image.load('files/play_inner.png')
        self.play = []
        for r, g, b in self.colors:
            surf = play.copy()
            for x in range(surf.get_width()):
                for y in range(surf.get_height()):
                    r_, g_, b_, a_ = surf.get_at((x, y))
                    surf.set_at((x, y), (r*r_//255, g*g_//255, b*b_//255, a_))
            surf.blit(play_inner, (0, 0))
            self.play.append(surf)

        self.pause = pygame.image.load('files/pause.png')
        self.play_pause_black = pygame.image.load('files/play_pause_black.png')
        self.pausebuttonmask = pygame.mask.from_surface(self.pause)
        self.waves = pygame.image.load('files/waves.png')
        self.black_surf = pygame.Surface((290, 290), SRCALPHA)
        self.black_surf.fill((self.black[0], self.black[1], self.black[2], 100))

        self.logos = music.get_logos()

        self.last_image_update = 0
        self.artist = self.title = self.last_title = ''
        self.last_covers = []

        self.artist_font = pygame.font.SysFont('Bradley Hand ITC', 20, True)
        self.title_font = pygame.font.SysFont('Tempus Sans ITC', 20, True)
        self.font = pygame.font.SysFont('Helvetica', 20, True)

        self.update_thread() # in case the thread isn't fast enough

    def update_thread(self):
        self.artist, self.title = music.get_artist_title()

        self.logo, cover = music.get_logo(), music.get_cover()
        self.cover = pygame.transform.smoothscale(cover, (290, 290)).convert_alpha()
    
        if not len(self.last_covers) or self.title != self.last_title:
            self.last_covers.insert(0, pygame.transform.smoothscale(cover, (300, 300)))
            if len(self.last_covers) >= 12:
                self.last_covers.pop()
            # each cover is more and more black
            surf = pygame.Surface((300, 300), SRCALPHA)
            surf.fill((self.grey[0], self.grey[1], self.grey[2], 50))
            for cover in self.last_covers:
                cover.blit(surf, (0, 0))
            self.last_title = self.title

    def update(self, events):
        click = False
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        if time.time() - self.last_image_update > 10:
            Thread(target=self.update_thread).start()
            pygame.display.set_caption('%s - %s - %s' %(music.titles[music.selected], self.artist, self.title))
            self.last_image_update = time.time()

        x, y = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if 10 <= x <= 190 and 360 <= y <= 380:
                music.volume = int((x-10) / 1.8)
                music.adjust_volume()

        self.screen.fill(self.grey)

        # songs images + radio logo
        waves = pygame.Surface((300, 300), SRCALPHA)
        waves.blit(self.waves, (int(cos(time.time()/2)*300)-300, int(sin(time.time()/2)*300)-300))
        for cover in range(len(self.last_covers)-1, 0, -1):
            self.screen.blit(self.last_covers[cover], (210 + 10*cover, 10 - 5*cover))
        rect = Rect((210, 10), (300, 300))
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.cover.set_alpha(200)
            if click:
                artist = ''
                for char in self.artist.lower():
                    if char.isalnum():
                        artist += char
                    elif char == '&':
                        break # do not count featured artists
                title = ''
                for char in self.title.lower():
                    if char.isalnum():
                        title += char
                webbrowser.open('https://www.azlyrics.com/lyrics/%s/%s.html' %(artist, title), new=2)
        else:
            self.cover.set_alpha(255)
        pygame.draw.rect(self.screen, self.colors[music.selected], rect)
        self.screen.blit(waves, (210, 10))
        self.screen.blit(self.cover, (215, 15))
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.black_surf, (215, 15))
            text = self.font.render('Afficher les paroles', 1, self.white)
            width = text.get_width()
            self.screen.blit(text, (360 - width//2, 150))
        self.screen.blit(self.logo, (480, 230))

        # artist / title
        text = self.artist_font.render(self.artist, 1, self.light_grey)
        width = text.get_width()
        self.screen.blit(text, (590-width, 340))
        text = self.title_font.render(self.title, 1, self.white)
        width = text.get_width()
        self.screen.blit(text, (590-width, 365))

        ##### Left side
        pygame.draw.rect(self.screen, self.black, Rect((0, 0, 200, 400)))

        # play/pause button
        if music.paused:
            self.screen.blit(self.play[music.selected], (60, 260))
        else:
            self.screen.blit(self.pause, (60, 260))
        if self.pausebuttonmask.get_rect().collidepoint((x-60, y-260)):
            self.screen.blit(self.play_pause_black, (60, 260))
            if click:
                if self.pausebuttonmask.get_at((x-60, y-260)):
                    music.toggle_pause()

        # volume bar
        pygame.draw.rect(self.screen, self.white, Rect((10, 360), (180, 20)))
        pygame.draw.rect(self.screen, self.colors[music.selected], Rect((5 + music.volume*1.8, 350), (15, 40)))

        # radio list
        for y in range(len(music.radios)):
            rect = Rect((5, 5 + 45*y), (190, 40))
            if rect.collidepoint(pygame.mouse.get_pos()) and not pygame.mouse.get_pressed()[0]:
                pygame.draw.rect(self.screen, self.grey_, rect)
            else:
                pygame.draw.rect(self.screen, self.grey, rect)
            self.screen.blit(self.logos[y], (rect.left+2, rect.top+2))
            self.screen.blit(self.font.render(music.titles[y], 1, self.white), (rect.left+50, rect.top+10))

            if click:
                if rect.collidepoint(event.pos):
                    music.selected = y
                    music.play()
                    self.last_image_update = time.time() - 9
                    self.logo = music.get_logo() # update only the logo instantly
                    self.last_covers = []

class Music:
    def __init__(self):
        self.player = vlc.Instance('--verbose', '2').media_player_new()
        self.titles = ['Fréquence 3', 'F3 Dance', 'F3 Gold', 'F3 Urban', 'F3 World']
        self.radios = ['-128', 'dance', 'gold', 'urban', 'world']
        self.api_index = [0, 3, -1, 1, 2, 4] # not organised in the same order

        self.selected = 0
        self.paused = False
        self.volume = 70 # %

    def play(self):
        self.player.set_mrl('http://ice.stream.frequence3.net/frequence3%s.mp3' %self.radios[self.selected])
        self.player.play()
        self.paused = False
        self.adjust_volume()

    def adjust_volume(self):
        self.player.audio_set_volume(self.volume)

    def toggle_pause(self):
        self.paused = not self.paused
        if self.player.can_pause():
            self.player.set_pause(self.paused)
            self.player.audio_set_mute(False) # in case the media can suddenly be paused
        else:
            self.player.audio_set_mute(self.paused)

    def get_data(self, allofthem=False):
        data = json.load(urlopen('https://api2.frequence3.net/v2/mobile/getCurrentTracks', context=context))
        if allofthem:
            return data # do not filter for the selected radio only

        radio_dict = data[self.api_index.index(self.selected)]
        return radio_dict

    def get_artist_title(self):
        radio_dict = self.get_data()['track']
        return radio_dict['artist'], radio_dict['title']

    def get_logo(self):
        radio_dict = self.get_data()
        with urlopen(radio_dict['picture'], context=context) as url:
            with open('files/_current_radio_logo_.png', 'wb') as f:
                f.write(url.read())
        logo = pygame.image.load('files/_current_radio_logo_.png')
        return pygame.transform.smoothscale(logo, (100, 100))

    def get_cover(self):
        radio_dict = self.get_data()
        with urlopen(radio_dict['track']['cover300'], context=context) as url:
            with open('files/_current_track_cover_.png', 'wb') as f:
                f.write(url.read())
        return pygame.image.load('files/_current_track_cover_.png')

    def get_logos(self):
        radio_dict = self.get_data(True)
        logos = []
        for x in range(5):
            with urlopen(radio_dict[self.api_index.index(x)]['pictures']['dark_theme'], context=context) as url:
                with open('files/_radio_logo_.png', 'wb') as f:
                    f.write(url.read())
                logos.append(pygame.image.load('files/_radio_logo_.png'))
                logos[-1] = pygame.transform.smoothscale(logos[-1], (36, 36))
        return logos

music = Music()
window = Window()

image = pygame.image.load('files/intro.png')
window.screen.fill((255, 255, 255))
window.screen.blit(image, (200, 100))
del image
pygame.display.flip()

window.init()
music.play()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()

    window.update(events)

    pygame.display.flip()
