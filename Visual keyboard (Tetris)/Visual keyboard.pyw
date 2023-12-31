import pygame
#import win32gui
#import win32com.client
from pygame.locals import *
from random import randint, choice
from threading import Thread
from pynput.keyboard import Key, Listener

def start_listener():
    def press(key):
        if key in keys:
            keys[key] = True
            keys_pressed.append(ticks())
            create_particles(key)
        elif 'char' in dir(key) and key.char in keys:
            keys[key.char] = True
            create_particles(key.char)
            keys_pressed.append(ticks())

    def release(key):
        if key in keys:
            keys[key] = False
        elif 'char' in dir(key) and key.char in keys:
            keys[key.char] = False

    global l
    with Listener(on_press=press, on_release=release) as l:
        l.join()

class Particle:
    def __init__(self, pos, colors, w):
        self.x, self.y = pos
        self.y += randint(0, 36)
        self.dx = randint(-100, 0)
        self.dy = randint(50, 100)
        if randint(0, 1): # move right instead of left
            self.x += w
            self.dx *= -1
            color = colors[-1] # can change color if multiple
        else:
            color = colors[0]

        self.color = [min(max(x + randint(-50, 50), 0), 255) for x in color]

    def update(self):
        self.dx *= 0.95**(100*time_passed)
        self.dy *= 1.05**(100*time_passed)
        self.x += self.dx*time_passed
        self.y += (self.dy-200)*time_passed
        pygame.draw.rect(screen, self.color, Rect(self.x-2, self.y-2, 5, 5))
        if self.y > 120:
            particles.remove(self)

def create_particles(key):
    x = list(keys.keys()).index(key)
    if type(pos[x]) == Rect:
        w = pos[x].width
        pos_ = (pos[x].x, pos[x].y)
    else:
        w = 46
        pos_ = pos[x]
    for n in range(5):
        if type(colors[x]) == pygame.Surface:
            col = space_cols
        else:
            col = [colors[x]]
        particles.append(Particle(pos_, col, w))

def create_spacebar(rect):
    surf = pygame.Surface((rect.width, rect.height))
    r1, g1, b1 = space_cols[0]
    r2, g2, b2 = space_cols[1]
    for x in range(246):
        x_ = x/246
        r, g, b = r1 + (r2-r1)*x_, g1 + (g2-g1)*x_, b1 + (b2-b1)*x_
        pygame.draw.line(surf, pressed((r, g, b)), (x, 0), (x, 35))

    return surf

def pressed(col):
    r, g, b = col
    return (grey[0] + r//5, grey[1] + g//5, grey[2] + b//5)

black = (20, 20, 20)
grey = (50, 50, 50)
white = (255, 255, 255)

rect = Rect(172, 52, 246, 36) # spacebar rect
space_cols = [(0, 255, 255), (127, 0, 127)]
surf = create_spacebar(rect)
colors = [(255, 255, 0), (127, 255, 0), (0, 255, 0), (0, 255, 127),
          surf, (255, 0, 127), (127, 0, 127), (127, 0, 255),
          (0, 127, 255), (127, 0, 255)]
particles = []

pygame.init()
screen = pygame.display.set_mode((580, 100))
pygame.display.set_caption('Visual keyboard')
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 16, True)
ticks = pygame.time.get_ticks

#hwnd = pygame.display.get_wm_info()['window']
#shell = win32com.client.Dispatch('WScript.Shell')
#shell.SendKeys(' ') # used to force focus on this window

keys = {'a': False, 'q': False, 's': False, 'd': False,
        Key.space: False, Key.left: False, Key.down: False,
        Key.right: False, Key.f2: False, Key.f4: False}
pos = [(12, 12), (22, 52), (72, 52), (122, 52),
       rect, (422, 52), (472, 52),
       (522, 52), (247, 12), (297, 12)]

keys_str = list('AQSD <v>')+['F2', 'F4']

Thread(target=start_listener).start()

start = ticks()
time_passed = 0
keys_pressed = [] # to calculate kps

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            l.stop()
            pygame.quit()
            exit()

    screen.fill(black)

    for x, key in zip(range(len(keys)), keys):
        # special case for spacebar
        if type(colors[x]) == pygame.Surface:
            if keys[key]:
                screen.blit(colors[x], (pos[x].x, pos[x].y))
            else:
                pygame.draw.rect(screen, grey, pos[x])
            continue

        if keys[key]:
            color = pressed(colors[x])
        else:
            color = grey

        pygame.draw.rect(screen, color, Rect(pos[x], (46, 36)))
        text = font.render(keys_str[x], True, white)
        w, h = text.get_size()
        screen.blit(text, (pos[x][0] + 23 - w//2, pos[x][1] + 18 - h//2))

    if ticks()-start > 5000: # only keep the last 5 seconds
        for key in keys_pressed:
            if ticks()-key > 5000:
                keys_pressed.remove(key)

        n = len(keys_pressed)/5
    else:
        n = len(keys_pressed)/(ticks()-start)*1000
    screen.blit(font.render('KPS: %.2f' %n, True, white), (130, 20))

    for particle in particles:
        particle.update()

    pygame.display.flip()
    time_passed = clock.tick(60)/1000
