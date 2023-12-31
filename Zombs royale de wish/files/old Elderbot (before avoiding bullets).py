class Elderbot:
    # (almost) ultimate bot
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = self.pos # movement by steps from start to goal
        self.goal = []
        self.last_move = self.start_move = 0
        self.distance = [300, 500] # min and max distances to fire
        self.safety = 70 # pixels of bullet distance to be considered safe

    def sort(self, entity):
        # get how much the ai should aim at this entity
        # higher return values = more priority

        hitter = entity == self.last_hitter
        invinc = ticks() < entity.invinc
        dist = self.pos.distance_to(entity.pos)
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

        dist = self.pos.distance_to(entity.pos)
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
        if collide_wall((self.goal[-2], self.goal[-1])) or not (0 <= vec.x <= map.width and 0 <= vec.y <= map.height):
            self.goal.pop()
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
            B_ = bullet.pos + B_movement*dist
            S_ = self.pos + S_movement*dist/bullet.speed*self.speed

            if not collide_wall((B_, S_)): # if the bullet will not hit a wall
                if B_.distance_to(S_) < self.safety:
                    B_angle = Vector2().angle_to(B_movement)
                    y = (self.pos-bullet.pos).rotate(-B_angle).y # how much offset it is from the bullet trajectory
                    if y < 0: # avoid the bullet by moving left relatively to the bullet
                        self.goal.insert(0, self.pos+Vector2(0, -self.safety-y).rotate(B_angle))
                    else: # avoid by moving right
                        self.goal.insert(0, self.pos+Vector2(0, self.safety-y).rotate(B_angle))
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
                self.rotation += degrees(tan(entity.speed/weapons[self.weapon][1]))*0.6*mult

            if len(self.goal): # move
                if dev:
                    pygame.draw.line(screen, (0, 0, 255), (self.pos.x-x, self.pos.y-y), (entity.pos.x-x, entity.pos.y-y), 2)
                    pygame.draw.aalines(screen, (0, 0, 255), 0, [(int(x-map.pos.x), int(y-map.pos.y)) for x, y in [list(self.start)]+self.goal])

                if tuple(self.start) == tuple(self.goal[0]): # prevent infinitely heading to the start
                    self.goal.pop(0)
                    self.last_move = ticks()
                else:
                    self.avoid_bullets()

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
            dist = self.pos.distance_to(entity.pos)
            calculated_pos = Vector2((entity.pos-self.pos).length(), 0).rotate(self.rotation)+self.pos
            if dist <= self.distance[1] and dist <= weapons[self.weapon][2] and not collide_wall((self.pos, calculated_pos)):
                self.shoot()

        # refill if far from target or no target
        if (len(self.goal) > 2 or entity is None) and not self.cant_shoot and self.ammo != weapons[self.weapon][6]:
            self.cant_shoot = ticks()
            self.prev_ammo = self.ammo
