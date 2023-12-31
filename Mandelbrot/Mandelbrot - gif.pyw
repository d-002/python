import pygame
from math import *
from pygame.locals import *
from threading import Thread

def make_points():
    global points, done
    w = W//2
    h = H//2
    done = False
    for x in range(-w, w):
        for y in range(-h, h):
            c = x/zoom + y/zoom*1j + pos
            if abs(c) <= 2:
                z = z0*z0 + c
                for i in range(1, n):
                    if abs(z) > 2:
                        break
                    z = z*z + c
                if abs(z) > 2:
                    # blue and yellow
                    #quotient = 510*i//(n+1)
                    #if quotient < 256:
                    #    col = (quotient, quotient, 128 + (quotient>>1))
                    #else:
                    #    col = (255, 319 - (quotient>>2), 510 - quotient)
                    # green
                    #if quotient < 256:
                    #    col = (0, quotient, 0)
                    #else:
                    #    col = (quotient-255, 255, quotient-255)
                    # rgb
                    quotient = i/n
                    r = (x+w)*255/W
                    b = (H-y-h)*255/H
                    col = (int(r*quotient), int((255-r)*quotient), int(b*quotient))
                else:
                    col = (0, 0, 0)

                points.append(((x+w, y+h), col))
    done = True

pygame.init()
fullscreen = True
if fullscreen:
    info = pygame.display.Info()
    W, H = info.current_w, info.current_h
    screen = pygame.display.set_mode((W, H), FULLSCREEN)
else:
    W, H = 640, 480
    screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

n = 50
zoom = min(W/4, H/2)
get_pos = lambda n: (-0.5, sin(pi*n)/2 + (0.5-cos(pi*n)/2)*1j)

points = []
last_index_drawn = 0
count = -1
done = True

#screen.fill((0, 0, 127))
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()

    # draw points that have not been drawn
    index = last_index_drawn # needs to have a value if the loop doesn't run
    for index in range(index+1, len(points)):
        screen.set_at(points[index][0], points[index][1])
    last_index_drawn = index

    if done:
        if count != -1:
            pygame.image.save(screen, 'frames/%d.png' %(count))
        count += 1
        if count == 300:
            break

        pos, z0 = get_pos(count/150)
        print(get_pos(count/150))
        points = []
        last_index_drawn = -1
        Thread(target=make_points).start()

    pygame.display.flip()
    clock.tick(10)
