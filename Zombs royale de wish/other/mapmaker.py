import pygame

surf = pygame.image.load('map.png')
w, h = surf.get_size()

colors = {(34, 177, 76): '0',
          (185, 122, 87): '1',
          (255, 242, 0): '2',
          (0, 162, 232): '3',
          (195, 195, 195): '4'}

map = []
for y in range(h):
    map.append('')
    for x in range(w):
        map[-1] += colors[surf.get_at((x, y))[:3]]

with open('map.txt', 'w') as f:
    f.write('\n'.join(map))
