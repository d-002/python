import pygame

from pygame.math import Vector2
from json import loads

from files.ai import * # ai.py file
from math import *
from random import *
from pygame.locals import *

class Map:
    def __init__(self):
        self.map = []
        with open('files/map.txt') as f:
            for line in f.read().split('\n'):
                self.map.append([int(x) for x in line])

        self.width, self.height = 100*len(self.map[0]), 100*len(self.map)
        self.pos = Vector2(self.width//2, self.height//2)
        self.visible = Rect(self.pos, (self.width, self.height))

        self.line_groups = [[(700, 600), (500, 600), (500, 200), (1100, 200), (1100, 600), (900, 600)],
                            [(500, 800), (500, 700), (200, 700), (200, 1100), (500, 1100), (500, 1000)],
                            [(500, 1400), (500, 1300), (200, 1300), (200, 1700), (500, 1700), (500, 1600)],
                            [(1100, 800), (1100, 700), (1400, 700), (1400, 1100), (1100, 1100), (1100, 1000)],
                            [(900, 1700), (1200, 1700), (1200, 1900)],
                            [(1500, 1700), (1900, 1700), (2000, 1600)],
                            [(2300, 1600), (2700, 1900)],
                            [(2800, 1000), (2800, 1400), (2700, 1500)],
                            [(2700, 100), (2700, 200)], [(2700, 500), (2700, 600), (2600, 700), (2500, 700)],
                            [(1700, 1000), (2300, 1000)],
                            [(1800, 600), (1800, 400), (2000, 200), (2500, 200)]]
        self.spawn = [(800, 600), (600, 1500), (2500, 1200), (2200, 400)]

        textures = ['files/ground/grass.png', 'files/ground/dirt.png', 'files/ground/sand.png', 'files/ground/water.png', 'files/ground/bricks.png']
        self.ground = {x: pygame.image.load(textures[x]) for x in range(len(textures))}
        self.tile_size = self.ground[0].get_width()

        # bounding boxes of groups
        self.line_rects = []
        for x in range(len(self.line_groups)):
            group = self.line_groups[x]
            rect = Rect((min(group, key=lambda point: point[0])[0], min(group, key=lambda point: point[1])[1]),
                        (max(group, key=lambda point: point[0])[0], max(group, key=lambda point: point[1])[1]))
            self.line_groups[x] = [Vector2(point) for point in group]
            self.line_rects.append(rect)

        # create points around wall points
        wall_distance = 50

        self.all_points = []
        for group in self.line_groups:
            for x in range(len(group)):
                if x in [0, len(group)-1]: # end of segment: go a little further than the end
                    angle = Vector2().angle_to(Vector2(group[x + 1 - 2*bool(x)])-group[x])
                    for angle2 in [-45, 45]: # add two points around the end of the group
                        vec = Vector2(-wall_distance, 0).rotate(angle+angle2)+group[x]
                        self.all_points.append(vec)
                else:
                    # old code used when this was in Elderbot
                    """# point in the middle of a group:
                    # needs to know if the player is "inside" the angle or not
                    # If entity (E) on the outside of angle ABC, there is exactly 1 "outer" angle, excluding angle E
                    # ("outer" means the angle at a point that is outside of ABCE) that is less than 180°.
                    # To compute this, we read points in clockwise order around the inner part of ABCE
                    # and check for 3 points R, S and T if (vec(ST).angle - vec(RS).angle) % 360 < 180

                    E = self.goal[-1]
                    A, B, C = [Vector2(group[x+y]) for y in [-1, 0, 1]]
                    angleAB = Vector2().angle_to(B-A)
                    angleBC = Vector2().angle_to(C-B)
                    if (angleBC-angleAB) % 360 < 180:
                        A, C = C, A

                    inside = True
                    for R, S, T in [(E, A, B), (A, B, C), (B, C, E)]:
                        angleRS = Vector2().angle_to(S-R)
                        angleST = Vector2().angle_to(T-R)
                        if (angleST-angleRS) % 360 < 180:
                            inside = False

                    if angleBC < angleAB:
                        angleBC += 360
                    angle = (angleAB+angleBC) / 2
                    if inside:
                        angle += 90
                    else:
                        angle -= 90
                    vec = B + Vector2(self.wall_distance, 0).rotate(angle)"""

                    # add two points on the inside and outside of the angle
                    A, B, C = [Vector2(group[x+y]) for y in [-1, 0, 1]]
                    angleAB = Vector2().angle_to(B-A)
                    angleBC = Vector2().angle_to(C-B)
                    if angleBC < angleAB:
                        angleBC += 360

                    angle = (angleAB+angleBC) / 2
                    for add in [-90, 90]:
                        self.all_points.append(B + Vector2(wall_distance, 0).rotate(angle+add))

    def draw(self):
        # follow the camera holder
        time = max((ticks()-prev_cam_holder[1]) / 500, 0)
        if time < 1:
            pos1 = prev_cam_holder[0]
            pos2 = cam_holder.pos
            pos = Vector2(pos1.x + (pos2.x-pos1.x)*time, pos1.y + (pos2.y-pos1.y)*time)
        else:
            pos = cam_holder.pos

        self.pos.x = min(max(pos.x - WIDTH//2, -WIDTH/2), self.width - WIDTH/2)
        self.pos.y = min(max(pos.y - HEIGHT//2, -HEIGHT/2), self.height - HEIGHT/2)

        """screen.fill((179, 255, 152))

        # lines in the background
        for x in range(0, WIDTH+100, 100):
            pygame.draw.line(screen, (200, 200, 200), (x - self.pos.x%100, 0), (x - self.pos.x%100, HEIGHT))
        for y in range(0, HEIGHT+100, 100):
            pygame.draw.line(screen, (200, 200, 200), (0, y - self.pos.y%100), (WIDTH, y - self.pos.y%100))

        # border
        if self.pos.x < 0:
            pygame.draw.rect(screen, (39, 141, 224), Rect((0, max(-self.pos.y, 0)), (-self.pos.x, min(self.height-self.pos.y, HEIGHT))))
        elif self.pos.x > self.width-WIDTH:
            pygame.draw.rect(screen, (39, 141, 224), Rect((self.width-self.pos.x, max(-self.pos.y, 0)), (WIDTH, min(self.height-self.pos.y, HEIGHT))))
        if self.pos.y < 0:
            pygame.draw.rect(screen, (39, 141, 224), Rect((0, 0), (WIDTH, -self.pos.y)))
        elif self.pos.y > self.height-HEIGHT:
            pygame.draw.rect(screen, (39, 141, 224), Rect((0, self.height-self.pos.y), (WIDTH, HEIGHT)))"""

        # draw tiles of the floor
        X = floor(self.pos.x/100)
        Y = floor(self.pos.y/100)
        for x in range(floor(WIDTH/self.tile_size)+1):
            x += X
            for y in range(floor(HEIGHT/self.tile_size)+1):
                y += Y
                pos = (x*self.tile_size - self.pos.x, y*self.tile_size - self.pos.y)
                if 0 <= x < len(self.map[0]) and 0 <= y < len(self.map):
                    screen.blit(self.ground[self.map[y][x]], pos)
                else:
                    screen.blit(self.ground[3], pos)

        # walls
        self.visible = Rect(self.pos, (self.width, self.height))
        for x in range(len(self.line_groups)):
            group = self.line_groups[x]
            rect = self.line_rects[x]
            if self.visible.colliderect(rect): # line group visible on the screen
                pygame.draw.lines(screen, (0, 0, 0), 0, [point-self.pos for point in group], 5)

class Mob:
    def __init__(self, hp=100):
        self.rotation = 0
        self.speed = 300
        self.max_hp = hp
        self.last_damage = (0, 0) # amount, time
        self.last_hitter = None
        self.kills = 0 # number of kills
        self.mask = pygame.mask.Mask((0, 0))

        self.kills = 0
        self.deaths = 0

        self.respawn()

    def respawn(self):
        global cam_holder

        self.pos = Vector2(choice(map.spawn))
        self.movement = Vector2()
        self.hp = self.max_hp
        self.kills_ = 0 # kills this life

        self.bullets = []
        self.last_shot = -60000 # last sent shot
        self.invinc = ticks() + spawn_invinc
        self.ammo = 0 # force weapon filling
        self.prev_ammo = 0 # ammo before starting to refill
        self.cant_shoot = False # time at which started refilling ammo; can't shoot while refilling

        if type(self) == Player:
            self.game_over = 0
            cam_holder = self

    def common(self): # common things all mobs need to do in the main loop
        # regen
        self.hp = min(self.hp + time_passed * (0.1 + (ticks()-self.last_damage[1]) / 7000), self.max_hp)

        # refill ammo
        if self.ammo == 0 and not self.cant_shoot:
            self.cant_shoot = ticks()
            self.prev_ammo = self.ammo
        if self.cant_shoot:
            max_ammo = weapons[self.weapon]['ammo']
            self.ammo = (ticks()-self.cant_shoot) / 1000 / weapons[self.weapon]['ammo cooldown'] * max_ammo + self.prev_ammo
            if self.ammo >= max_ammo:
                self.cant_shoot = False # refilled, ready to shoot
                self.ammo = max_ammo

        # don't go out of the map
        self.pos.x = min(max(self.pos.x, 5), map.width - 5)
        self.pos.y = min(max(self.pos.y, 5), map.height - 5)

    def collide(self, movement): # change the movement (for this frame), add collisions
        mv = Vector2(movement)
        mv_angle = Vector2().angle_to(mv)
        count = 0

        # create a line from slightly behind the player to its position next frame
        offset = Vector2(10, 0).rotate(mv_angle)
        line = lambda: (self.pos, self.pos+offset+mv)

        for _ in [0, 1]: # need to calculate this twice to avoid corner cutting
            for group in map.line_groups:
                for x in range(len(group)-1):
                    if intersect(line(), (group[x], group[x+1])):
                        x1, y1 = group[x]
                        x2, y2 = group[x+1]
                        angle = Vector2().angle_to(Vector2(x2-x1, y2-y1))
                        # rotate the movement vector as if the line was horizontal
                        mv.rotate_ip(-angle)
                        # cancel the y movement
                        mv.y = 0
                        # rotate back
                        mv.rotate_ip(angle)

                        count += 1
                    if count >= 3: # max collisions in one frame
                        break
                if count >= 3:
                    break
        return mv

    def hit(self, damage, hitter):
        if ticks()-self.invinc > 0:
            if dev: # no player damage
                self.hp -= damage*(self != player) # DEV
            else:
                self.hp -= damage
            self.last_damage = (damage, ticks())
        self.last_hitter = hitter

    def draw(self):
        if is_visible(self) and self.hp > 0:
            # rotate smoothly
            w, h = self.surf.get_size()
            surf = pygame.transform.scale(self.surf, (w*2, h*2))
            surf = pygame.transform.rotate(surf, -self.rotation)
            w, h = surf.get_width()//2, surf.get_height()//2
            surf = pygame.transform.smoothscale(surf, (w, h))
            self.mask = pygame.mask.from_surface(surf) # update the mask

            # transparent when invinc
            if ticks()-self.invinc < 0:
                surf.set_alpha(127)
            pos = (self.pos.x - map.pos.x - w//2, self.pos.y - map.pos.y - h//2)
            screen.blit(surf, pos)

            # draw bars
            hp = self.hp + self.last_damage[0] - min((ticks()-self.last_damage[1]) / 300, 1) * self.last_damage[0]
            if (self == player) or (player.game_over and self == cam_holder): # camera focused on this mob
                # weapon cooldown
                wp = weapons[self.weapon]
                if self.cant_shoot:
                    value = (ticks()-self.cant_shoot)*wp['ammo']/(wp['ammo']-self.prev_ammo)/wp['ammo cooldown'] # show refill cooldown
                else:
                    value = (ticks()-self.last_shot)/wp['cooldown'] # show weapon cooldown
                pygame.draw.rect(screen, (0, 65, 204), Rect(WIDTH-305, HEIGHT-55, 300, 10))
                pygame.draw.rect(screen, (173, 199, 255), Rect(WIDTH-305, HEIGHT-55, min(int(0.3*value), 300), 10))

                # ammo
                pygame.draw.rect(screen, (151, 105, 0), Rect(WIDTH-305, HEIGHT-40, 300, 10))
                pygame.draw.rect(screen, (255, 236, 0), Rect(WIDTH-305, HEIGHT-40, min(300*self.ammo//wp['ammo'], 300), 10))

                # health
                pygame.draw.rect(screen, (0, 0, 0), Rect(WIDTH-305, HEIGHT-25, 300, 20))
                pygame.draw.rect(screen, (237, 28, 36), Rect(WIDTH-303, HEIGHT-23, 296*hp//self.max_hp, 16))
                text = font.render('%d/%d' %(hp, self.max_hp), 1, (255, 255, 255))
                screen.blit(text, (WIDTH-10-text.get_width(), HEIGHT-24))

                # high damage animation
                diff = (ticks()-self.last_damage[1]) / 600
                if self.last_damage[0] > self.hp/3 and 0 <= diff <= 1:
                    size = 150 - (diff*300 % 150)
                    surf = pygame.Surface((300 + size*2, 20 + size*2), SRCALPHA)
                    surf.fill((237, 28, 36, int(diff*150)))
                    screen.blit(surf, (WIDTH-305-size, HEIGHT-25-size))

                # low health overlay for cam_holder
                if hp/self.max_hp < 0.75 and self == player:
                    low_overlay.set_alpha(min(255, 255 - 340*hp//self.max_hp))
                    screen.blit(low_overlay, (0, 0))

            else: # camera not focused on this mob
                pygame.draw.rect(screen, (0, 0, 0), Rect(pos[0] - 20 + w//2, pos[1]-12, 40, 8))
                pygame.draw.rect(screen, (237, 28, 36), Rect(pos[0] - 20 + w//2, pos[1]-12, 40*hp//self.max_hp, 8))

            if self != player: # show username on top if not player
                if self.username == 'Dream':
                    col = rgb()
                    background = (0, 0, 0)
                else:
                    col = (0, 0, 0)
                    background = None
                username = font.render(self.username, 1, col, background)
                screen.blit(username, (pos[0] + (w-username.get_width())//2, pos[1]-32))
        else:
            self.mask = pygame.mask.from_surface(self.surf)

        for bullet in self.bullets:
            bullet.update()
            bullet.draw()

    def shoot(self):
        if not self.cant_shoot and ticks()-self.last_shot > weapons[self.weapon]['cooldown'] * 1000:
            multishot = weapons[self.weapon]['multishot']-1
            for angle in range(-3*multishot//2, 3 + 3*multishot//2, 3):
                if self.ammo:
                    self.bullets.append(Bullet(self, self.weapon, angle))
                    self.ammo -= 1
                else:
                    break
            self.last_shot = ticks()

class Player(Mob):
    def __init__(self, username, index):
        super().__init__()
        self.surf = make_surf((0, 0, 255))
        self.movement_type = 1 # 0: relative to player, 1: fixed angles

        self.top = None
        self.game_over = 0

        self.weapon = index
        self.username = username

    def update(self, events):
        global prev_cam_holder, cam_holder, log

        x, y = pygame.mouse.get_pos()
        self.rotation = Vector2().angle_to(Vector2(x - self.pos.x + map.pos.x, y - self.pos.y + map.pos.y))

        self.movement = Vector2()
        pressed = pygame.key.get_pressed()
        if pressed[K_r] and not self.cant_shoot: # refill ammo
            self.cant_shoot = ticks()
            self.prev_ammo = self.ammo
        if pressed[K_q]: # left
            self.movement.y -= 1
        if pressed[K_d]: # right
            self.movement.y += 1
        if pressed[K_z]: # forwards
            self.movement.x += 1
        if pressed[K_s]: # backwards
            self.movement.x -= 1

        if self.movement_type == 0:
            self.movement.rotate_ip(self.rotation)
        elif self.movement_type == 1:
            self.movement.rotate_ip(-90)
        if self.movement:
            self.movement = self.movement.normalize()*self.speed
        if pressed[K_LCTRL] and dev: # sprint (DEV)
            self.movement *= 3
        offset = Vector2(10, 0).rotate(Vector2().angle_to(self.movement))
        self.pos += self.collide(self.movement*time_passed)

        # shoot
        if pygame.mouse.get_pressed()[0]:
            self.shoot()

        if mode == 'top':
            self.top = len(enemies)+1

        if self.hp <= 0:
            self.deaths += 1
            cam_holder = self.last_hitter
            prev_cam_holder = [Vector2(self.pos), ticks()+500]
            if self.last_hitter:
                self.last_hitter.kills += 1
                self.last_hitter.kills_ += 1
                log.append(('You were killed by %s' %self.last_hitter.username, ticks()))
            else:
                log.append(('You were killed by a stray bullet', ticks()))
                # select a random enemy and make the animation slower
                cam_holder = choice(enemies)
                prev_cam_holder[1] += 1000

            # make particles
            for x in range(20):
                particles.append(Particle(self.pos))

            self.game_over = ticks() # allow for others to know the player lost after things on top

class Enemy(Mob):
    # functions common to all enemy types
    def __init__(self, **kwargs):
        super().__init__()
        self.surf = make_surf((255, 0, 0))

        if 'weapon' in kwargs:
            self.weapon = kwargs['weapon']
        else:
            self.weapon = choice(list(weapons.keys()))
        self.spawn = ticks()

        if 'username' in kwargs:
            self.username = kwargs['username']
        else:
            self.username = get_username()

    def get_dist(self, entity):
        return self.pos.distance_to(entity.pos)

    def update(self):
        global bullets, prev_cam_holder, cam_holder, log

        # call the other file (needs time_passed)
        self.ai(time_passed)

        if self.hp <= 0:
            # make particles
            for x in range(20):
                particles.append(Particle(self.pos))
            self.deaths += 1


            if self == cam_holder:
                if self.last_hitter == player: # don't transmit the camera back to the player
                    self.last_hitter = None
                cam_holder = self.last_hitter # transmit the camera to the killer
                prev_cam_holder = [Vector2(self.pos), ticks()+500]
                if self.last_hitter is None:
                    cam_holder = choice(enemies)
                    prev_cam_holder[1] += 1000
            if self.last_hitter == player:
                player.kills += 1
                player.kills_ += 1
                prompt_kills()
                log.append(('You killed %s' %self.username, ticks()))
            elif self.last_hitter:
                self.last_hitter.kills += 1
                self.last_hitter.kills_ += 1
                log.append(('%s was killed by %s' %(self.username, self.last_hitter.username), ticks()))
            else:
                log.append(('%s was killed by a stray bullet' %self.username, ticks()))

            enemies.remove(self)
            if mode == 'top':
                bullets += self.bullets # make own bullets global
                for bullet in self.bullets:
                    bullet.master = None # do not update own variables from bullets that hit after
            elif mode == 'kdr': # respawn
                scheduled_respawns.append((self, ticks()+respawn_delay))

    def ai(self):
        pass

class Bullet:
    def __init__(self, master, weapon, angle=0):
        wp = weapons[weapon]
        self.damage, self.speed, distance, n, precision = wp['damage'], wp['speed'], wp['maxdist'], wp['multishot'], wp['precision']

        self.master = master
        self.surf = self.make_surf()
        self.mask = pygame.mask.from_surface(self.surf)
        self.rotation = self.master.rotation+angle+randint(-precision*10, precision*10)/10

        self.movement = Vector2(self.speed, 0).rotate(self.rotation)
        self.spawn = ticks()
        self.lifespan = distance/self.speed # s

        # avoid shooting through walls
        self.pos = Vector2(self.master.pos)
        add = Vector2(self.master.surf.get_width()/2 + 10, 0).rotate(self.rotation)
        if Mob.collide(self, add) == add:
            # no collisions: adjust self.pos to be at the front of the maaster texture
            self.pos += add

    def make_surf(self):
        surf = pygame.Surface((10, 10), SRCALPHA)
        pygame.draw.circle(surf, (0, 0, 0), (5, 5), 5)
        return surf

    def update(self):
        entity = False

        if ticks()-self.spawn < self.lifespan*1000:
            # moving bullet
            next_pos = self.pos + self.movement*time_passed
            if collide_wall((self.pos, next_pos)):
                entity = True
            else:
                entity = collide(self)
            self.pos = next_pos

            if type(entity) != bool and entity != self.master: # hit entity
                entity.hit(self.damage, self.master)
            if entity: # hit something but not a mob
                self.remove()
                return
        elif ticks()-self.spawn > self.lifespan*1000 + 200:
            self.remove()

    def remove(self):
        if self.master is None: # deleted master
            bullets.remove(self)
        else:
            self.master.bullets.remove(self)

    def draw(self):
        if is_visible(self):
            screen.blit(self.surf, (self.pos.x - map.pos.x - self.surf.get_width()//2, self.pos.y - map.pos.y - self.surf.get_height()//2))

class Button:
    def __init__(self, text, pos, function):
        self.text = font.render(text, 1, (255, 255, 255))
        w, h = self.text.get_size()
        self.rect = Rect((pos[0] - w//2 - 10, pos[1] - h//2 - 10), (w+20, h+20))
        self.function = function

    def update(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
                self.function()

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            col = (100, 100, 100)
        else:
            col = (50, 50, 50)
        pygame.draw.rect(screen, col, self.rect)
        screen.blit(self.text, (self.rect.x+10, self.rect.y+10))

class Particle:
    def __init__(self, pos):
        self.x, self.y = pos
        self.y += randint(0, 36)
        self.dx = randint(-500, 0)
        self.dy = randint(50, 200)

        if randint(0, 1): # move right
            self.x -= 10
            self.dx *= -1
        else: # move left
            self.x += 10

        self.start = ticks()
        self.delay = randint(200, 400)

        self.color = (200 + randint(-50, 50), 0, 0)

    def update(self):
        self.dx *= 0.95**(100*time_passed)
        self.dy *= 1.05**(100*time_passed)
        self.x += self.dx*time_passed
        self.y += (self.dy-200)*time_passed
        if ticks()-self.start > self.delay:
            particles.remove(self)
            return

        x = self.x-map.pos.x
        y = self.y-map.pos.y
        if 0 <= x < WIDTH and 0 <= y <= HEIGHT:
            pygame.draw.rect(screen, self.color, Rect(x-3, y-3, 7, 7))

def prompt_kills():
    global prompt
    messages = ['']*2 + [s.upper() + ' KILL' for s in 'double triple quadruple quintuple sextuple septuple octuple nonuple decuple'.split(' ')]
    if player.kills_ < len(messages):
        msg = messages[player.kills_]
    else:
        msg = 'FAR TOO MANY KILLS (%d)' %player.kills_
    prompt = [big_font.render(msg, 1, (245, 255, 66)), ticks()]

def draw_other():
    # death overlay, text color
    if player.game_over:
        screen.blit(death_overlay, (0, 0))
        color = (255, 255, 255)
    else:
        color = (0, 0, 0)

    # information
    if sum(times):
        fps = len(times)//sum(times)
    else:
        fps = 'inf'
    screen.blit(font.render('FPS: %s' %fps, 1, color), (0, 0))
    screen.blit(font.render('Kills: %d' %player.kills, 1, color), (0, 20))
    if mode == 'top':
        screen.blit(font.render('Players remaining: %d' %(len(enemies) + (not player.game_over)), 1, color), (0, 40))
        if player.game_over:
            screen.blit(font.render('Top: %d out of %d' %(player.top, n_enemies+1), 1, color), (0, 60))
    elif mode == 'kdr':
        screen.blit(font.render('Deaths: %d' %player.deaths, 1, color), (0, 40))
        if player.deaths:
            kdr = player.kills/player.deaths
        else:
            kdr = player.kills
        screen.blit(font.render('KDR: %.2f' %kdr, 1, color), (0, 60))

    # chat/log
    while len(log) > 5:
        log.pop(0) # remove oldest messages if too many of them
    w = None
    to_remove = []
    for line in range(len(log)):
        text, time = log[line]
        if ticks()-time > 5000: # remove old text
            to_remove.append(log[line])
        elif line < 5:
            text = font.render(text, 1, (255, 100, 100))
            if w is None or text.get_width() > w:
                w = text.get_width()
            text.set_alpha(min(int((5000-ticks()+time) * 0.255), 255))
            screen.blit(text, (5, HEIGHT - 5 - 20*min(len(log), 5) + 20*line))
    if w:
        h = 20*len(log) + 10
        black = pygame.Surface((w+10, h), SRCALPHA)
        black.fill((0, 0, 0, 100))
        screen.blit(black, (0, HEIGHT - h))
    for line in to_remove:
        log.remove(line)

    # prompt
    if ticks()-prompt[1] <= 5000:
        prompt[0].set_alpha(min(int((5000-ticks()+prompt[1]) * 0.255), 255))
        screen.blit(prompt[0], (WIDTH//2 - prompt[0].get_width()//2, 20))

    # leaderboard
    if mode == 'kdr':
        mobs = get_leaderboard(5)
        names = []
        w = 0
        index = 1
        for mob in mobs:
            if mob.deaths:
                add = '%.2f KDR' %(mob.kills/mob.deaths)
            else:
                add = '%.2f KDR' %mob.kills
            if mob == player:
                color = (127, 255, 127)
            else:
                color = (255, 255, 255)
            text = small_font.render('%s (%s) -- %d' %(mob.username, add, index), 1, color)
            w = max(w, text.get_width())
            names.append(text)
            index += 1
        black = pygame.Surface((w, 14*len(names)), SRCALPHA)
        black.fill((0, 0, 0, 100))
        screen.blit(black, (WIDTH-w, 0))
        y = 0
        for name in names:
            screen.blit(name, (WIDTH-name.get_width(), y))
            y += 14

    # killer information
    if player.game_over:
        text = font.render('Following %s (%s) - %d kills' %(cam_holder.username, type(cam_holder).__name__, cam_holder.kills), 1, (255, 255, 255))
        screen.blit(text, (450 - text.get_width()//2, 300))

    # buttons
    if player.game_over and ticks()-player.game_over > respawn_delay:
        if mode == 'top':
            restart.update(events)
        elif mode == 'kdr':
            respawn.update(events)

    # crosshair and aim line
    if pygame.mouse.get_focused():
        X, Y = pygame.mouse.get_pos()
        for x in range(-10, 11):
            for y in range(-1, 2):
                if 0 < X+x < WIDTH and 0 < Y+y < HEIGHT:
                    r, g, b = screen.get_at((X+x, Y+y))[:3]
                    screen.set_at((X+x, Y+y), (255-r, 255-g, 255-b))
                if 0 < X+y < WIDTH and 0 < Y+x < HEIGHT and not -1 <= x <= 1:
                    r, g, b = screen.get_at((X+y, Y+x))[:3]
                    screen.set_at((X+y, Y+x), (255-r, 255-g, 255-b))
        if not player.game_over:
            center = Vector2(WIDTH//2, HEIGHT//2) # center of the screen
            relative = Vector2(X, Y)-center # mouse pos relative to the center
            angle = Vector2().angle_to(relative)
            pos1 = Vector2(player.surf.get_width()/2 + 20, 0).rotate(angle) + center
            pos2 = Vector2(max(relative.length()-20, player.surf.get_width()/2 + 20), 0).rotate(angle) + center
            pygame.draw.aaline(screen, (127, 127, 127), pos1, pos2, 3)

def make_surf(col):
    def color(col, bright):
        return int(col[0] * bright), int(col[1] * bright), int(col[2] * bright)

    surf = pygame.Surface((70, 30), SRCALPHA)
    pygame.draw.rect(surf, color(col, 0.2), Rect(50, 12, 20, 6))
    pygame.draw.rect(surf, color(col, 1), Rect(20, 0, 30, 30))

    return surf

def get_username():
    name = choice(list(usernames.keys()))
    usernames[name] += 1
    if usernames[name] > 1: # username was taken: add a number
        return name + str(usernames[name])
    return name

def get_leaderboard(n):
    def key(self):
        if self.deaths:
            return self.kills/self.deaths
        return self.kills

    scheduled = [entity[0] for entity in scheduled_respawns]
    return sorted(enemies+scheduled+[player], key=key, reverse=True)[:n]

def in_bounds(pos):
    return (0 <= pos.x <= map.width) and (0 <= pos.y <= map.height)

def collide(self):
    entities = enemies + [player]
    if type(self) != Bullet:
        entities.remove(self)

    for entity in entities:
        if type(self) == Bullet and entity == self.master:
            continue

        w, h = self.mask.get_size()
        rect1 = Rect((self.pos.x - w//2, self.pos.y - h//2), (w, h))
        w, h = entity.mask.get_size()
        rect2 = Rect((entity.pos.x - w//2, entity.pos.y - h//2), (w, h))
        if rect1.colliderect(rect2):
            if self.mask.overlap(entity.mask, (rect2.x-rect1.x, rect2.y-rect1.y)):
                return entity

    if not(0 < self.pos.x < map.width) or not (0 < self.pos.y < map.height):
        return True
    return False

def intersect(s0,s1): # check if two segments s0 and s1 intersect
    dx0 = s0[1][0]-s0[0][0]
    dx1 = s1[1][0]-s1[0][0]
    dy0 = s0[1][1]-s0[0][1]
    dy1 = s1[1][1]-s1[0][1]
    p0 = dy1*(s1[1][0]-s0[0][0]) - dx1*(s1[1][1]-s0[0][1])
    p1 = dy1*(s1[1][0]-s0[1][0]) - dx1*(s1[1][1]-s0[1][1])
    p2 = dy0*(s0[1][0]-s1[0][0]) - dx0*(s0[1][1]-s1[0][1])
    p3 = dy0*(s0[1][0]-s1[1][0]) - dx0*(s0[1][1]-s1[1][1])
    return (p0*p1 <= 100) & (p2*p3 <= 100)

def collide_wall(line):
    for group in map.line_groups:
        for x in range(len(group)-1):
            if intersect(line, (group[x], group[x+1])):
                return True
    return False

def is_visible(self):
    visible = Rect(map.pos, (WIDTH, HEIGHT))
    w, h = self.surf.get_size()
    rect = Rect(self.pos, (w, h))
    rect.x, rect.y = rect.x - w//2, rect.y - h//2
    return visible.colliderect(rect)

def restart():
    for self in enemies + [player]:
        self.respawn()
        self.kills = self.deaths = 0

def rgb():
    t = ticks()/500%3
    r = g = b = 255
    if t < 1:
        g = 255*t
        b = 255-g
    elif t < 2:
        b = 255 * (t-1)
        r = 255-b
    else:
        r = 255 * (t-2)
        g = 255-r
    return (int(r), int(g), int(b))

with open('files/usernames.txt') as f:
    usernames = {name: 0 for name in f.read().split('\n')}

pygame.init()
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))#, FULLSCREEN|SCALED)
font = pygame.font.SysFont('consolas', 20)
small_font = pygame.font.SysFont('consolas', 14)
big_font = pygame.font.SysFont('consolas', 40)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks
pygame.mouse.set_visible(0)

with open('files/weapons.json') as f:
    weapons = loads(f.read())

low_overlay = pygame.image.load('files/low_overlay.png')
death_overlay = pygame.image.load('files/death_overlay.png')

map = Map()

##########
# mode: either 'top' or 'kdr'
mode = 'kdr'
spawn_invinc = 2000 # ms of invincibility after spawning
respawn_delay = 2000
n_enemies = 8

dev = False
##########

player = Player('Tryharder', 'MAC-10')
# send information to other file

scheduled_respawns = [] # (entity, ticks of respawning)
bullets = [] # bullets from removed mobs
prev_cam_holder = [None, -60000] # old camera holder and moment of transmission
cam_holder = player # mob to follow
log = []
particles = []
prompt = [None, -60000]

enemies = init_ai(n_enemies, Enemy, screen, Player, player, map, collide_wall, in_bounds, weapons, bullets, dev)

restart = Button('Restart', (450, 400), restart)
respawn = Button('Respawn', (450, 400), player.respawn)

time_passed = 0
times = [time_passed]*100
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == KEYDOWN and player.game_over:
            if event.key in [K_LEFT, K_RIGHT]:
                prev_cam_holder = [cam_holder.pos, ticks()]
                others = [enemy for enemy in enemies if enemy != cam_holder]
                if len(others):
                    cam_holder = choice(others)

    map.draw()

    if not player.game_over:
        player.update(events)
        player.common()

    for mob, time in scheduled_respawns[:]:
        if ticks() >= time:
            mob.respawn()
            enemies.append(mob)
            scheduled_respawns.remove((mob, time))
    for enemy in enemies:
        enemy.update()
        enemy.common()
        enemy.draw()
    for bullet in bullets:
        bullet.update()
        bullet.draw()
    player.draw()

    for particle in particles:
        particle.update()

    draw_other()

    pygame.display.flip()
    time_passed = clock.tick() / 1000
    times.pop(0)
    times.append(time_passed)
