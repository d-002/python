import win32api
import win32con
import win32gui
import pygame
from pygame.locals import *

class Bar:
    def __init__(self, color):
        self.pos = [0, 0]
        for x in range(len(bars)): # place itself in the right spot
            self.move(10)
        self.color = color

    def move(self, amount):
        if self.pos[0] <= 0:
            self.pos = [0, self.pos[1]-amount]
            if self.pos[1] < 0:
                self.pos = [amount, 0]
        elif self.pos[0] >= WIDTH-width-1:
            self.pos = [WIDTH-width-1, self.pos[1]+amount]
            if self.pos[1] > HEIGHT-width-1:
                self.pos = [WIDTH-width-1-amount, HEIGHT-width-1-amount]
        elif self.pos[1] <= 0:
            self.pos = [self.pos[0]+amount, 0]
            if self.pos[0] > WIDTH-width-1:
                self.pos = [WIDTH-width-1, amount]
        else:
            self.pos = [self.pos[0]-amount, HEIGHT-width-1]
            if self.pos[0] < 0:
                self.pos = [0, HEIGHT-width-1-amount]

    def update(self, amount):
        self.move(amount)
        x, y = self.pos[0]//10*10, self.pos[1]//10*10
        pygame.draw.rect(screen, self.color, Rect((x, y), (width, width)))

pygame.init()
monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))
work_area = monitor_info.get("Work")
monitor_area = monitor_info.get("Monitor")
WIDTH, HEIGHT = work_area[2:]
screen = pygame.display.set_mode((WIDTH, monitor_area[3]), NOFRAME)
clock = pygame.time.Clock()

transparent = (0, 0, 0)
hwnd = pygame.display.get_wm_info()['window']
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*transparent), 0, win32con.LWA_COLORKEY)

def maxi(color):
    r, g, b = color
    return r==255, g==255, b==255
    if r == 255: r = 1
    elif r:      r = 0.5
    else:        r = 0
    if g == 255: g = 1
    elif g:      g = 0.5
    else:        g = 0
    if b == 255: b = 1
    elif b:      b = 0.5
    else:        b = 0
    return (r, g, b)

width = 15

color = (255, 0, 0)
bars = []
N = (2*WIDTH + 2*HEIGHT)//10
add = [0, 1, 0]
for x in range(N):
    bars.append(Bar(color))
    if 1 in add and color[add.index(1)] == 255 or -1 in add and not color[add.index(-1)]:
        if   add == [1, 0, 0]: add = [0, 0, -1]
        elif add == [0, 1, 0]: add = [-1, 0, 0]
        elif add == [0, 0, 1]: add = [0, -1, 0]
        elif add == [-1, 0, 0]: add = [0, 0, 1]
        elif add == [0, -1, 0]: add = [1, 0, 0]
        elif add == [0, 0, -1]: add = [0, 1, 0]
    r, g, b = color
    r_, g_, b_ = add
    r = min(max(0, r + r_*1530/N), 255)
    g = min(max(0, g + g_*1530/N), 255)
    b = min(max(0, b + b_*1530/N), 255)
    color = (r, g, b)

screen.fill(transparent)
time_passed = 0
clock.tick()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    for bar in bars:
        bar.update(500*time_passed)
    pygame.display.flip()
    time_passed = clock.tick(60)/1000
