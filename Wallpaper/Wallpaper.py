import pygame
from pygame.locals import *
from random import *
from threading import Thread

def noise(x, y):
    seed(int(s+x+y))
    a, b, c, d = [randint(-100, 100) for _ in range(4)]
    x %= 1
    A = a + (b-a)*x
    B = c + (d-c)*x
    return (A + (B-A) * (y%1)) / 100

def draw():
    for x in range(W):
        for y in range(H):
            """# blue-red
            c = int(128 + 127*noise(x/100, y/100))
            m = x/W
            screen.set_at((x, y), (m*c, 0, 0.5 + 0.5*(1-m)*c))

            # metals:
            c = 0.5 + noise(x/100, y/100)/2
            m = (x/W)**2
            # gold
            screen.set_at((x, y), (c * (127 + 120*m), c * (127 + 50*m), c * (127 - 30*m)))
            # platinum
            screen.set_at((x, y), (c * (127 + 100*m), c * (127 + 15*m), c * (127 - 5*m)))"""

            # RGB
            c = 0.5 + noise(x/100, y/100)/2
            r = x*255//W
            screen.set_at((x, y), (r*c, (255-r) * c, ((H-y) * 255 / H) * c))

    pygame.image.save(screen, 'wallpaper.png')

s = 69
W, H = 1920, 1080
W, H = 640, 480

pygame.init()
screen = pygame.display.set_mode((W, H))#, FULLSCREEN)
clock = pygame.time.Clock()

Thread(target=draw).start()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

    pygame.display.flip()
    clock.tick(10)
