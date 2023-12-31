##### Requirements: vlc, pygame>=2.0.0

import ssl
import vlc
import json
import time
import pygame
import certifi
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
        self.black_surf.fill((self.black[0], self.black[1], self.black[2], 127))

        self.logos = music.get_logos()

        self.last_image_update = self.scroll = self.start = self.start_pause = 0
        self.artist = self.title = self.last_title = self.lyrics = ''
        self.last_covers = []

        self.artist_font = pygame.font.SysFont('Bradley Hand ITC', 20, True)
        self.title_font = pygame.font.SysFont('Tempus Sans ITC', 20, True)
        self.font = pygame.font.SysFont('Helvetica', 20, True)

        self.update_thread() # in case the thread isn't fast enough

    def update_thread(self, update_cover=True):
        self.artist, self.title = music.get_artist_title()

        if update_cover:
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

        lyrics = music.get_lyrics()
        if lyrics != self.lyrics:
            self.scroll = 0
        self.lyrics = lyrics

    def update(self, events):
        click = False
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        if time.time() - self.last_image_update > 2:
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
        if music.paused:
            time_ = self.start_pause-self.start
        else:
            time_ = time.time()-self.start
        waves.blit(self.waves, (int(cos(time_/2)*300)-300, int(sin(time_/2)*300)-300))
        for cover in range(len(self.last_covers)-1, 0, -1):
            self.screen.blit(self.last_covers[cover], (210 + 10*cover, 10 - 5*cover))
        rect = Rect((210, 10), (300, 300))
        if rect.collidepoint(pygame.mouse.get_pos()):
            self.cover.set_alpha(223)
        else:
            self.cover.set_alpha(255)
        pygame.draw.rect(self.screen, self.colors[music.selected], rect)
        self.screen.blit(waves, (210, 10))
        self.screen.blit(self.cover, (215, 15))

        # lyrics
        if rect.collidepoint(pygame.mouse.get_pos()):
            lyrics_surf = self.black_surf.copy()
            for event in events:
                if event.type == MOUSEWHEEL:
                    self.scroll -= event.y*20
                    self.scroll = max(min(self.scroll, (len(self.lyrics)-15)*20), 0)

            y = -self.scroll
            for line in self.lyrics:
                if 0 <= y <= 290:
                    text = self.artist_font.render(line, 1, self.white)
                    width = text.get_width()
                    lyrics_surf.blit(text, (145 - width//2, y))
                y += 20
            self.screen.blit(lyrics_surf, (215, 15))
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
            self.screen.blit(self.play[music.selected], (60, 250))
        else:
            self.screen.blit(self.pause, (60, 250))
        if self.pausebuttonmask.get_rect().collidepoint((x-60, y-250)):
            if self.pausebuttonmask.get_at((x-60, y-250)):
                self.screen.blit(self.play_pause_black, (60, 250))
                if click:
                    music.toggle_pause()

        # volume bar
        r, g, b = self.colors[music.selected]
        color = ((r + 2*self.white[0]) // 3, (g + 2*self.white[1]) // 3, (b + 2*self.white[2]) // 3)
        pygame.draw.rect(self.screen, self.white, Rect((10, 360), (180, 20)))
        pygame.draw.rect(self.screen, color, Rect((10, 360), (int(music.volume*1.8), 20)))
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
                    self.update_thread(False)
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
        if self.paused:
            self.paused = False
            window.start += time.time()-window.start_pause
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
        if self.paused:
            window.start_pause = time.time()
        else:
            window.start += time.time()-window.start_pause

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
        
    def get_lyrics(self):
        artist = ''
        for char in window.artist.lower():
            if char.isalnum():
                artist += char
            elif char == '&':
                break # do not count featured artists
        if artist[:3] == 'the':
            artist = artist[3:]
        if artist == 'u2':
            artist = 'u2band' # U2 is not U2 for azlyrics
        artist = artist.strip()
        title = ''
        for char in window.title.lower():
            if char.isalnum():
                title += char
        warning = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->'
        try:
            url = urlopen('https://www.azlyrics.com/lyrics/%s/%s.html' %(artist, title), context=context).read()
            lyrics = url.decode().split(warning)[1].split('</div>')[0][1:]
            for char in ['<br>', '<i>', '</i>', '&quot;']:
                lyrics = lyrics.replace(char, '')
        except:
            lyrics = '[Paroles non trouvées]'
        lyrics_raw = lyrics.split('\n')
        lyrics = []
        for line in lyrics_raw:
            text = window.artist_font.render(line, 1, window.white)
            width = text.get_width()
            if width < 290:
                lyrics.append(line)
            else:
                line = line.split(' ')
                block = prev_block = ''
                while line:
                    text = window.artist_font.render(block, 1, window.white)
                    width = text.get_width()
                    if width < 290:
                        prev_block = block
                        block += line.pop(0) + ' '
                    else:
                        lyrics.append(prev_block)
                        block = block.split(' ')[-2] + ' ' # 2 because empty space at the end
                if block:
                    lyrics.append('[ ' + block)
        return lyrics

def intro():
    image = pygame.image.load('files/intro.png')
    window.screen.fill((255, 255, 255))
    window.screen.blit(image, (200, 100))

    text = pygame.font.SysFont('arial', 12, True).render('Paroles par azlyrics.com', 1, (0, 0, 0))
    width = text.get_width()
    window.screen.blit(text, (300 - width//2, 300))

    del image, text
    pygame.display.flip()

music = Music()
window = Window()
clock = pygame.time.Clock()

intro()

window.init()
music.play()
pygame.event.get() # make sure the user didn't click which could crash the program

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()

    window.update(events)

    pygame.display.flip()
    clock.tick(120)
