import pygame

def gradient(surf, c1, c2, c3):
    w, h = surf.get_size()
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    r3, g3, b3 = c3
    for x in range(w):
        for y in range(h):
            r = r1 + (r2-r1)*x/w
            g = g1 + (g2-g1)*x/w
            b = b1 + (b2-b1)*x/w
            r += (r3-r)*y/h
            g += (g3-g)*y/h
            b += (b3-b)*y/h
            surf.set_at((x, y), (int(r), int(g), int(b)))

surf = pygame.Surface((1920, 1080))
gradient(surf, (50, 50, 50), (20, 20, 20), (0, 0, 0))
pygame.image.save(surf, 'gradient.png')
