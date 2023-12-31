import pygame
from math import *
from random import *
from pygame.math import Vector2

pygame.init()
ticks = pygame.time.get_ticks

class BotMovement:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = self.pos
        self.goal = None # force new goal

    def aim(self):
        # aim at the nearest visible entity
        if player.game_over:
            entities = list(enemies)
        else:
            entities = enemies + [player]
        entities.remove(self)
        entities = [entity for entity in entities if not collide_wall((self.pos, entity.pos))]

        nearest = sorted(entities, key=self.get_dist)
        if len(nearest):
            if self.get_dist(nearest[0]) <= self.track_distance:
                return nearest[0]

    def new_goal(self):
        self.start = Vector2(self.pos)

        entity = self.aim()
        if entity:
            angle = Vector2().angle_to(entity.pos-self.pos)
            goal = Vector2(randint(200, 400), randint(50, 50)).rotate(angle)+self.pos
        else:
            # move randomly if no near target
            x = min(max(self.pos.x+randint(-400, 400), 0), map.width)
            y = min(max(self.pos.y+randint(-400, 400), 0), map.height)
            goal = Vector2(x, y)
        self.goal = [goal, ticks()+randint(0, 2000)]

    def rotate(self, entity, time_passed):
        angle = Vector2().angle_to(entity.pos-self.pos)

        diff = abs(angle-self.rotation) % 360
        if diff <= 10 or 350 <= diff:
            self.rotation = angle # close enough: lock to angle

        # humanly rotate towards the target
        if (angle-self.rotation) % 360 < 180:
            self.rotation += 300*time_passed
        else:
            self.rotation -= 300*time_passed

    def move(self, time_passed):
        if self.goal is None:
            self.new_goal()

        if dev:
            x, y = map.pos
            pygame.draw.aaline(screen, (0, 0, 255), [self.start.x-x, self.start.y-y], [self.goal[0].x-x, self.goal[0].y-y])

        # move towards goal
        if ticks() >= self.goal[1]:
            self.movement = (self.goal[0]-self.start).normalize()*self.speed
            self.pos += self.collide(self.movement*time_passed)

            # check if reached goal
            angle1 = Vector2().angle_to(self.pos-self.start)
            angle2 = Vector2().angle_to(self.goal[0]-self.pos)
            # took too long to get to goal (ran into a wall)
            too_long = (ticks()-self.goal[1]) / 1000 > (self.goal[0]-self.start).length()/self.speed + 0.5
            if 90 < (angle1-angle2) % 360 < 270 or too_long:
                self.new_goal()
        else:
            self.movement = Vector2()

class AFKbot:
    def ai(self, time_passed):
        pass

class Fearfulbot(BotMovement):
    # bot that tries to avoid players by hiding, if not hidden then shoot
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.track_distance = 400
        self.reaction_time = 500
        self.start_see = 0

    def new_goal(self):
        def sort_moves(move):
            pos = self.pos+move
            inaccessible = collide_wall((self.pos, pos)) # wall in between
            if entity:
                # try to hide behind a wall or far from the entity
                return inaccessible*5 - collide_wall((pos, entity.pos)) - self.get_dist(entity)/500
            # try not to move towards a wall
            return inaccessible

        self.start = Vector2(self.pos)

        entity = self.aim()
        move = Vector2(randint(200, 400), 0).rotate(randint(0, 359))
        # try differently oriented moves and find the best
        moves = [move.rotate(angle) for angle in range(0, 360, 30)]

        if ticks()-self.start_see > self.reaction_time:
            delay = 0 # continuously try to move away once the entity has been found
        else:
            delay = randint(0, 2000) # not forced to always move
        self.goal = [self.pos+sorted(moves, key=sort_moves)[0], ticks()+delay]

    def ai(self, time_passed):
        self.move(time_passed)

        entity = self.aim()
        if entity and not collide_wall((self.pos, entity.pos)):
            if not self.start_see:
                self.start_see = ticks()
            elif ticks()-self.start_see > self.reaction_time: # don't shoot right away
                # start moving immediately
                self.goal[1] = ticks()

                # rotate towards the target
                self.rotate(entity, time_passed)

                self.shoot()
        else:
            self.start_see = 0

class Wanderbot(BotMovement):
    # bot that randomly moves until it sees an entity then chases it
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.track_distance = 500
        self.shoot_distance = 500
        self.reaction_time = 300 # ms
        self.start_see = 0

    def ai(self, time_passed):
        self.move(time_passed)

        entity = self.aim()
        if entity:
            if not self.start_see:
                self.start_see = ticks()
            elif ticks()-self.start_see > self.reaction_time:
                # rotate towards the target and shoot
                self.rotate(entity, time_passed)

                self.shoot()
        else:
            # walk forward
            if self.goal and ticks() >= self.goal[1]:
                self.rotation = Vector2().angle_to(self.goal[0]-self.start)
            self.start_see = 0

class Huntingbot(BotMovement):
    # bot that shoots whenever it can, always try to target an entity
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.track_distance = 1000
        self.shoot_distance = 300

    def aim(self):
        # aim at the nearest mob, no matter if there is a wall in between
        if player.game_over:
            entities = list(enemies)
        else:
            entities = enemies + [player]
        entities.remove(self)

        nearest = sorted(entities, key=self.get_dist)
        if len(nearest):
            if self.get_dist(nearest[0]) <= self.track_distance:
                return nearest[0]

    def ai(self, time_passed):
        self.move(time_passed)

        entity = self.aim()
        if entity:
            self.rotate(entity, time_passed)
            if self.get_dist(entity) <= self.shoot_distance:
                self.shoot()

class Elderbot_old:
    # almost ultimate bot
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = self.pos # movement by steps from start to goal
        self.goal = []
        self.last_move = self.start_move = 0 # start and end of last movement
        self.distance = [300, 500] # min and max distances to fire
        self.safety = 70 # pixels of bullet distance to be considered safe

    def get_bullet_dist(self, bullet):
        return self.pos.distance_to(bullet.pos)/bullet.speed

    def sort(self, entity):
        # get how much the ai should aim at this entity
        # higher return values = more priority

        hitter = entity == self.last_hitter
        invinc = ticks() < entity.invinc
        dist = self.get_dist(entity)
        direct = not collide_wall((self.pos, entity.pos))
        hp = entity.hp/entity.max_hp
        return hitter*5 + direct*2 - dist/100 - hp*5 - invinc*100

    def aim(self):
        # aim at the nearest mob
        if player.game_over:
            entities = list(enemies)
        else:
            entities = enemies + [player]
        entities.remove(self)

        nearest = sorted(entities, key=self.sort)
        if len(nearest):
            return nearest[-1]

    def new_goal(self, entity):
        if self.goal is None: # move towards the aimed entity
            vec_add = (entity.pos-self.pos) * 2
            if vec_add.length() > 500:
                vec_add = vec_add.normalize()*500
            self.goal = []
        else:
            vec_add = (0, 0)

        self.start = Vector2(self.pos)
        self.goal = [self.start]
        self.forbidden = []

        last_rotation = self.rotation
        for x in range(5): # go around (set max number) walls if needed
            line = (tuple(self.goal[-1]), tuple(entity.pos))
            if collide_wall(line):
                nearest = (0, 0)
                nearest_dist = -1
                rotation = 0
                for x in range(len(map.line_groups)):
                    group = map.line_groups[x]
                    for y in range(len(group)):
                        if (x, y) in self.forbidden:
                            continue # can't reuse the same one twice

                        dist = self.goal[-1].distance_to(group[y])
                        nearer = dist < nearest_dist or nearest_dist < 0
                        if y == 0 or y == len(group)-1: # end of line group
                            if nearer:
                                nearest, nearest_dist = (x, y), dist
                        else:
                            A, O, B = [Vector2(group[z]) for z in range(y-1, y+2)]
                            area = (-A.y*B.x + O.y*(-A.x+B.x) + O.x*(A.y-B.y) + A.x*B.y) / 2
                            s = (O.y*B.x - O.x*B.y + (B.y-O.y)*self.goal[-1].x + (O.x-B.x) * self.goal[-1].x) / (2*area)
                            t = (O.x*A.y - O.y*A.x + (O.y-A.y)*self.goal[-1].x + (A.x-O.x) * self.goal[-1].y) / (2*area)
                            if not (0 < s < 1 and 0 < t < 1) and nearer: # check if angle > 180
                                nearest, nearest_dist = (x, y), dist

                pos1 = map.line_groups[nearest[0]][nearest[1]]
                if nearest[1] in [0, len(map.line_groups[nearest[0]])-1]: # end of group
                    if nearest[1]:
                        pos2 = map.line_groups[nearest[0]][nearest[1]-1]
                    else:
                        pos2 = map.line_groups[nearest[0]][1]
                    rotation, rotation_add = Vector2().angle_to(pos1-pos2), 60
                else: # middle of group
                    pos2 = map.line_groups[nearest[0]][nearest[1]-1]
                    pos3 = map.line_groups[nearest[0]][nearest[1]+1]
                    angle2, angle3 = Vector2().angle_to(pos1-pos2), Vector2().angle_to(pos1-pos3)
                    angle_diff = abs((angle2-angle3+180)%360 - 180)
                    rotation, rotation_add = (angle2+angle3) / 2 % 360, angle_diff/3
                vec = Vector2(50, 0).rotate(rotation)

                self.forbidden.append(nearest)
                for x in range(2):
                    if vec+pos1 in self.goal:
                        continue # do not go to the same location twice
                    else:
                        self.goal.append(vec+pos1)
                    if collide_wall((self.goal[-2], self.goal[-1])):
                        self.goal.pop()
                        break # tried to go through a wall
                    if (last_rotation-rotation) % 360 < 180: # add a second point rotated away
                        vec.rotate_ip(rotation_add)
                    else:
                        vec.rotate_ip(-rotation_add)
                if self.goal[-1] == (vec+pos1):
                    last_rotation = rotation
            else:
                break # last move, no obstacles remain

        # went around all blocking walls: head strategically towards the player
        vec = Vector2()
        # hide if entity is invincible, low hp or can't shoot
        hide_factor = ((ticks() < entity.invinc)*3 + (self.hp < self.max_hp/2) + (self.hp < entity.hp)*2 + bool(self.cant_shoot)*3 + 1)

        dist = self.get_dist(entity)
        if dist < self.distance[0]*hide_factor: # too near
            vec.x -= randint(0, self.speed*hide_factor)
        elif dist > self.distance[1]*hide_factor: # too far
            vec.x += randint(self.speed*hide_factor/2, self.speed*hide_factor)
        if ticks()-self.start_move < 300: # too short move = stuck in corner
            vec.x += self.speed
        vec.y += randint(-100, 100)/100*self.speed
        vec = vec.rotate(self.rotation) + self.pos + vec_add

        # do not try to go out of bounds or through a wall
        self.goal.append(vec)
        if collide_wall((self.goal[-2], self.goal[-1])) or not in_bounds(vec):
            self.goal.pop()
        self.last_move = ticks()

    def ai(self, time_passed):
        if self.last_hitter and self.last_hitter.hp < 0:
            last_hitter = None # don't track a dead mob
        else:
            last_hitter = self.last_hitter

        entity = self.aim()
        if entity: # found a near entity
            x, y = map.pos
            if last_hitter and not collide_wall((self.pos, last_hitter.pos)):
                if last_hitter.hp/last_hitter.max_hp < entity.hp/entity.max_hp:
                    # hit the last hitter if their hp is lower + no wall in between
                    entity = last_hitter

            # adjust the angle to shoot where the entity is moving to
            self.rotation = Vector2().angle_to(entity.pos-self.pos)
            if entity.movement:
                if (Vector2().angle_to(entity.movement)-self.rotation) % 360 < 180:
                    mult = 1
                else:
                    mult = -1
                self.rotation += degrees(tan(entity.speed/weapons[self.weapon]['speed']))*0.6*mult

            if len(self.goal): # move
                if dev:
                    pygame.draw.line(screen, (0, 0, 255), (self.pos.x-x, self.pos.y-y), (entity.pos.x-x, entity.pos.y-y), 2)
                    pygame.draw.aalines(screen, (0, 0, 255), 0, [(int(x-map.pos.x), int(y-map.pos.y)) for x, y in [list(self.start)]+self.goal])

                if tuple(self.start) == tuple(self.goal[0]): # prevent infinitely heading to the start
                    self.goal.pop(0)
                    self.last_move = ticks()
                else:
                    if self.goal[0] != self.start:
                        self.movement = (self.goal[0]-self.start).normalize()*self.speed
                        self.pos += self.collide(self.movement*time_passed)

                    # check if reached the goal
                    angle1 = Vector2().angle_to(self.pos-self.start)
                    angle2 = Vector2().angle_to(self.goal[0]-self.pos)
                    if 90 < (angle1-angle2) % 360 < 270:
                        self.start = Vector2(self.goal.pop(0))
                        self.last_move = ticks()
                    elif (ticks()-self.last_move) / 1000 > (self.goal[0]-self.start).length()/self.speed + 0.5: # too long to reach a spot
                        self.goal = [self.start] # recalculate

            if self.goal is None or not len(self.goal): # new goals list
                self.new_goal(entity)

            # shoot
            dist = self.get_dist(entity)
            calculated_pos = Vector2((entity.pos-self.pos).length(), 0).rotate(self.rotation)+self.pos
            if dist <= self.distance[1] and dist <= weapons[self.weapon]['maxdist'] and not collide_wall((self.pos, calculated_pos)):
                self.shoot()

        # refill if far from target or no target
        if (len(self.goal) > 2 or entity is None) and not self.cant_shoot and self.ammo != weapons[self.weapon]['ammo']:
            self.cant_shoot = ticks()
            self.prev_ammo = self.ammo

class Elderbot:
    # ultimate bot
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = self.pos # movement by steps from start to goal
        self.hide = False
        self.distance = [300, min(500, weapons[self.weapon]['maxdist'])*0.7] # min and max distances to fire
        self.safety = 70 # pixels of bullet distance to be considered safe

    def respawn(self):
        super().respawn()
        self.goal = []
        self.start_move = 0 # start of last move
        self.avoiding = False # currently avoiding a bullet

    def get_bullet_dist(self, bullet):
        return self.pos.distance_to(bullet.pos)/bullet.speed

    def sort(self, entity):
        # get how much the ai should aim at this entity
        # higher return values = more priority

        hitter = entity == self.last_hitter
        invinc = ticks() < entity.invinc
        dist = self.get_dist(entity)
        direct = not collide_wall((self.pos, entity.pos))
        hp = entity.hp/entity.max_hp
        return hitter*5 + direct*2 - dist/100 - hp*5 - invinc*100

    def aim(self):
        # aim at the nearest mob
        if player.game_over:
            entities = list(enemies)
        else:
            entities = enemies + [player]
        entities.remove(self)

        nearest = sorted(entities, key=self.sort)
        if len(nearest):
            return nearest[-1]

    def point_value(self, point, entity, hide):
        # the point with the lowest value will be selected
        d1 = self.pos.distance_to(point)
        d2 = entity.pos.distance_to(point)
        invisible = collide_wall((point, entity.pos))
        if hide:
            # try to hide as fast as possible (better score for hiding fast and distance)
            return -d2*invisible + d1
        else:
            # try to get closer as fast as possible (bonus for seeing entity once at point)
            return d1*invisible + d2

    def new_goal(self, entity):
        min_dist = min([self.pos.distance_to(point) for point in sum(map.line_groups, start=[])])
        cant_shoot_factor = self.cant_shoot and not collide_wall((self.pos, entity.pos)) and min_dist < 500
        if ticks() < entity.invinc or self.hp < self.max_hp/3 or self.hp*1.5 < entity.hp or cant_shoot_factor:
            self.hide = True # hide form the entity
        else:
            self.hide = False # hunt the entity
        sort_function = lambda point: self.point_value(point, entity, self.hide)

        self.start = Vector2(self.pos)
        self.goal = [self.start] # will be removed, but useful to add it
        forbidden = [self.start] # don't go to the same location twice - avoid aiming towards self.pos because sitting on a map point

        n = 0
        while len(self.goal) <= 5 and n < 20: # limit the number of segments in path and total number of loops
            # use all valid pre-generated points around wall points
            points = [Vector2(point) for point in map.all_points if not collide_wall((self.goal[-1], point)) and in_bounds(point) and point not in forbidden]
            points.sort(key=sort_function)

            if len(points):
                self.goal.append(points[0])
                forbidden.append(points[0])
            else: # hidden quicker than anticipated: stop
                break

            wall = collide_wall((self.goal[-1], entity.pos))
            if self.hide: # stop when far away and wall in between
                if len(self.goal) >= 2 and wall:
                    break
            else: # stop when no wall in between
                if len(self.goal) >= 2 and not wall:
                    break

            n += 1

        # optimise path: if can go directly from a point to a later one, remove the path in between
        for x in range(len(self.goal)-2):
            if not collide_wall((self.goal[x], self.goal[-1])):
                self.goal = self.goal[:x+1] + [self.goal[-1]]
                break

        if not self.hide:
            # add one final point to go near the player (before rotating vec, it means that vec.x > 0)
            vec = Vector2()

            dist = self.get_dist(entity)
            if dist < self.distance[0]: # too near
                vec.x -= randint(50, 200)
            elif dist > self.distance[1]: # too far
                vec.x += randint(50, 200)
            if ticks()-self.start_move < 300: # last move was too short = stuck in corner
                vec.x += self.goal[-1].distance_to(entity.pos)*2
            vec.y += randint(-200, 200) # randomly move left or right
            vec = vec.rotate(Vector2().angle_to(entity.pos-self.goal[-1])) + self.goal[-1]

            # do not try to go out of bounds or through a wall
            if not collide_wall((self.goal[-1], vec)) and in_bounds(vec):
                self.goal.append(vec)

        self.start_move = ticks()

    def avoid_bullets(self):
        # avoid the nearest bullet
        total_bullets = player.bullets+bullets
        for enemy in enemies:
            if enemy == self:
                continue
            total_bullets += enemy.bullets

        if len(total_bullets):
            bullet = sorted(total_bullets, key=self.get_bullet_dist)[0]
            # B: bullet, S: self
            B_movement = bullet.movement.normalize()
            if self.movement:
                S_movement = self.movement.normalize()
            else:
                S_movement = Vector2()
            dist = self.pos.distance_to(bullet.pos)
            # B_ and S_ are calculated positions when the bullet will hit
            B_ = bullet.pos + B_movement*dist
            S_ = self.pos + S_movement*dist/bullet.speed*self.speed
            B_angle = Vector2().angle_to(B_movement)

            if not collide_wall((B_, S_)) and (self.pos-bullet.pos).rotate(-B_angle).x > 0: # if the bullet will not hit a wall and is not moving away
                if B_.distance_to(S_) < self.safety:
                    if self.avoiding: # cancel any bullet avoiding movement
                        self.goal.pop(0)

                    y = (self.pos-bullet.pos).rotate(-B_angle).y # how much offset it is from the bullet trajectory
                    if y < 0: # avoid the bullet by moving left relatively to the bullet
                        self.goal.insert(0, self.pos+Vector2(0, -self.safety-y).rotate(B_angle))
                    else: # avoid by moving right
                        self.goal.insert(0, self.pos+Vector2(0, self.safety-y).rotate(B_angle))
                    self.start_move = ticks()
                    self.start = Vector2(self.pos)
                    self.avoiding = True

    def ai(self, time_passed):
        if self.last_hitter and self.last_hitter.hp < 0:
            last_hitter = None # don't track a dead mob
        else:
            last_hitter = self.last_hitter

        entity = self.aim()
        if entity: # found a near entity
            x, y = map.pos
            if last_hitter and not collide_wall((self.pos, last_hitter.pos)):
                if last_hitter.hp/last_hitter.max_hp < entity.hp/entity.max_hp:
                    # hit the last hitter if their hp is lower + no wall in between
                    entity = last_hitter

            # adjust the angle to shoot where the entity is moving to
            self.rotation = Vector2().angle_to(entity.pos-self.pos)
            if entity.movement:
                if (Vector2().angle_to(entity.movement)-self.rotation) % 360 < 180:
                    mult = 1
                else:
                    mult = -1
                self.rotation += degrees(tan(entity.speed/weapons[self.weapon]['speed']))*0.6*mult

            self.avoid_bullets()
            if len(self.goal): # move
                if dev:
                    if self.hide:
                        color = (255, 0, 0)
                    else:
                        color = (0, 0, 255)
                    pygame.draw.line(screen, color, self.pos-map.pos, entity.pos-map.pos, 2)
                    pygame.draw.aalines(screen, color, 0, [pos-map.pos for pos in [self.start]+self.goal])

                if self.goal[0] == self.start: # don't try to get the angle of the null vector
                    self.goal.pop(0)
                    self.start_move = ticks()
                    self.avoiding = False
                else:
                    self.avoid_bullets()

                    if self.goal[0] != self.start:
                        self.movement = (self.goal[0]-self.start).normalize()*self.speed
                        self.pos += self.collide(self.movement*time_passed)

                    # check if reached the goal
                    angle1 = Vector2().angle_to(self.pos-self.start)
                    angle2 = Vector2().angle_to(self.goal[0]-self.pos)
                    if 90 <= (angle1-angle2) % 360 <= 270:
                        self.start = Vector2(self.goal.pop(0))
                        self.avoiding = False

                        # if entity is visible and it's still in the wall avoiding state, skip it
                        if not collide_wall((self.pos, entity.pos)) and len(self.goal) > 1 and not self.hide:
                            self.goal = []

                        if len(self.goal): # don't update self.start_move when going to get a new pos right away
                            self.start_move = ticks()
                    elif (ticks()-self.start_move) / 1000 > (self.goal[0]-self.start).length()/self.speed + 0.5: # too long to reach a spot
                        self.goal = [] # recalculate

            if self.goal is None or not len(self.goal): # new goals list
                self.new_goal(entity)

            # shoot
            dist = self.get_dist(entity)
            calculated_pos = Vector2((entity.pos-self.pos).length(), 0).rotate(self.rotation)+self.pos
            if dist <= self.distance[1] and dist <= weapons[self.weapon]['maxdist'] and not collide_wall((self.pos, calculated_pos)):
                self.shoot()

        # refill if far from target or no target
        if (len(self.goal) > 2 or entity is None) and not self.cant_shoot and self.ammo != weapons[self.weapon]['ammo']:
            self.cant_shoot = ticks()
            self.prev_ammo = self.ammo

def init_ai(n_enemies, base_class, *args):
    global screen, Player, player, map, enemies, collide_wall, in_bounds, weapons, bullets, dev
    global Enemy, AFKbot, Fearfulbot, Wanderbot, Huntingbot, Elderbot_old, Elderbot # enemy classes
    Enemy = base_class
    AFKbot = type('AFKbot', (AFKbot, Enemy), {})
    Fearfulbot = type('Fearfulbot', (Fearfulbot, Enemy), {})
    Wanderbot = type('Wanderbot', (Wanderbot, Enemy), {})
    Huntingbot = type('Huntingbot', (Huntingbot, Enemy), {})
    Elderbot_old = type('Elderbot_old', (Elderbot_old, Enemy), {})
    Elderbot = type('Elderbot', (Elderbot, Enemy), {})

    screen, Player, player, map, collide_wall, in_bounds, weapons, bullets, dev = args

    # spawn random enemies
    types = [Fearfulbot, Wanderbot, Huntingbot]
    enemies = [choice(types)() for x in range(n_enemies)]
    enemies.append(Elderbot(username='Dream', weapon='AR9'))
    #enemies = [Elderbot(username='Technoblade', weapon='Shark'), Elderbot(username='Dream', weapon='Shark')]
    return enemies

if __name__ == '__main__':
    raise Exception('Wrong file bruh')
