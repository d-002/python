import pygame
from pygame.locals import *
from threading import Thread

def fill_surf(rect, size=1): # redistribute into smaller chunks of points
    global thread_running
    z = zoom # make a copy so that all blocks have the same zoom
    size = int(size*zoom)

    modx, mody = rect.x%size, rect.y%size
    existing_pos = [(info[0].x, info[0].y) for info in chunk_info.values()]
    new_pos = []
    for x in range(rect.x-modx, rect.x+rect.w+size-modx, size):
        for y in range(rect.y-mody, rect.y+rect.h+size-mody, size):
            new_pos.append(x + 1j*y)
            if zoom != z:
                break

    new_pos.sort(key=lambda point: abs(point - pos*zoom))

    for point in new_pos:
        x, y = point.real, point.imag
        if (x, y) not in existing_pos:
            make_points(Rect(x, y, size, size), z)

    # remove surfaces if too many have been generated
    if len(chunk_info) > max_chunks:
        for id in dict(chunk_info):
            if not cam.colliderect(chunk_info[id][0]):
                del chunks[id]
                del chunk_info[id]
    thread_running = False # done

def make_points(rect, zoom):
    surf = pygame.Surface((rect.w, rect.h))
    surf.fill((0, 0, 127))

    X = 0
    for x in range(rect.x, rect.x+rect.w):
        Y = 0
        for y in range(rect.y, rect.y+rect.h):
            c = x/zoom + y/zoom*1j
            if abs(c) <= 2:
                z = c
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

                surf.set_at((X, Y), col)
            Y += 1
        X += 1

    id = new_chunk_id()
    chunks[id] = surf
    chunk_info[id] = [rect, zoom]

def move(events):
    global needs_thread, pos

    pressed = pygame.key.get_pressed()
    movement = speed/zoom*time_passed
    if pressed[K_z]:
        pos += movement*1j
        needs_thread = True
    if pressed[K_q]:
        pos -= movement
        needs_thread = True
    if pressed[K_s]:
        pos -= movement*1j
        needs_thread = True
    if pressed[K_d]:
        pos += movement
        needs_thread = True

def draw_ui():
    screen.blit(font.render('Pos: %.5f+%.5fj' %(pos.real, pos.imag), True, (255, 255, 255)), (0, 0))
    screen.blit(font.render('Zoom: %d' %zoom, True, (255, 255, 255)), (0, 16))
    screen.blit(font.render('Toggle UI: F3', True, (255, 255, 255)), (0, 32))
    screen.blit(font.render('Toggle fullscreen: F11', True, (255, 255, 255)), (0, 48))

def draw():
    for id in iter(chunk_info):
        rect, z = chunk_info[id]
        if z == zoom:
            surf = chunks[id]
            if cam.colliderect(rect):
                screen.blit(surf, (rect.x-cam.x, rect.y-cam.y))

def cam_rect():
    return Rect(pos.real*zoom - WIDTH/2, -pos.imag*zoom - HEIGHT/2, WIDTH, HEIGHT)

def new_chunk_id():
    global id_
    id_ += 1
    return id_-1

def toggle_fullscreen(toggle=True):
    global fullscreen, needs_thread, screen, WIDTH, HEIGHT
    if toggle:
        fullscreen = not fullscreen
        needs_thread = True
    if fullscreen:
        WIDTH, HEIGHT = info.current_w, info.current_h
        screen = pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN)
    else:
        WIDTH, HEIGHT = 640, 480
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.init()
fullscreen = False
info = pygame.display.Info()
toggle_fullscreen(False)
font = pygame.font.SysFont('consolas', 16)
clock = pygame.time.Clock()

n = 20
zoom = zoom_min = min(WIDTH/4, HEIGHT/2)
pos = -0.5+1j
#zoom = 800000
#pos = -0.8131+0.20331j
speed = 200 # movement speed
ui = True

chunk_info = {} # indices correcponding to chunks keys
chunks = {}
max_chunks = 100
id_ = 0
thread_running = 0 # is there a thread running
needs_thread = True # needs to create surfaces
time_passed = 0

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            quit()
        elif event.type == KEYDOWN:
            if event.key == K_F3:
                ui = not ui
            elif event.key == K_F11:
                toggle_fullscreen()
            elif event.key == K_UP:
                zoom *= 2
                needs_thread = True
            elif event.key == K_DOWN:
                if zoom >= 200:
                    zoom = zoom//2
                needs_thread = True

    screen.fill((127, 127, 127))

    cam = cam_rect()

    move(events)
    if needs_thread and not thread_running: # start thread if needed
        thread_running = True
        needs_thread = False
        Thread(target=fill_surf, args=(cam_rect(),)).start()
    draw()
    if ui:
        draw_ui()

    pygame.display.flip()
    time_passed = clock.tick(60)/1000
