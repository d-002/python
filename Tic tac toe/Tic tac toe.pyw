import time, threading, random, pygame, math
from pygame.locals import *

class MenuPlayer:
    def __init__(self, as_):
        self.as_ = as_
    
    def play(self):
        for player_ in menu_players:
            if player_ != self:
                pos = can_win(self.as_, False) # try to win
                if pos is not None:
                    tile_at(pos).set(self.as_, True)
                    return # to avoid placing again
                pos = can_win(player_.as_, False) # try to block the other player from winning
                if pos is not None:
                    place(self.as_, pos)
                    return
                else:
                    if winner == 'draw':
                        return
                    free_tiles = [tile for tile in tiles if tile.state is None]
                    try:
                        chosen = random.choice(free_tiles)
                        place(self.as_, (chosen.x, chosen.y))
                    except: # if the tiles are being reset (+ it allow to change the starter player)
                        pass

class Computer:
    def ez(self):
        if first_player == player:
            player.play()
            clock.tick(2)
        while winner is None:
            self.random_choose()
            player.play()
            clock.tick(2)
            if winner is not None:
                return
            if can_win(self):
                clock.tick(2)
                return

    def human(self):
        if first_player == player:
            player.play()
            clock.tick(2)
        while winner is None:
            tile_place = can_win(player) # check if the player can win - place a block here then
            if tile_place:
                place(self, tile_place)
            else:
                self.random_choose()
            player.play()
            clock.tick(2)
            if winner is not None:
                return
            if can_win(self):
                clock.tick(2)
                return

    def hell(self):
        global winner
        if first_player == player: # player begins
            
            first_tile = player.play()
            clock.tick(2)

            corner = False # check if the player has placed in a corner
            for pos in [(0, 0), (0, 2), (2, 0), (2, 2)]:
                if tile_at(pos).state == player:
                    corner = True
            side = False # check if the player has placed in a side
            for pos in [(1, 0), (2, 1), (1, 2), (0, 1)]:
                if tile_at(pos).state == player:
                    side = True
            center = False # check if the player has placed in the center
            if tile_at((1, 1)).state == player:
                center = True

            if corner: # corner script
                place(self, (1, 1))

                tile2 = player.play()
                clock.tick(2)
                if can_win(self):
                    clock.tick(2)
                    return

                if first_tile.x + first_tile.y + tile2.x + tile2.y == 4: # if placed on the opposite then do not place in a corner
                    ok = False
                    while not ok:
                        pos = random.choice([(1, 0), (2, 1), (1, 2), (0, 1)])
                        if tile_at(pos).state is None:
                            place(self, pos)
                            ok = True
                else:
                    already_placed = False
                    for pos in [(1, 0), (2, 1), (1, 2), (0, 1)]: # if the player has a side and an opposite corner, place next to the side
                        tile = tile_at(pos)
                        if tile.state == player:
                            if tile.x == 1:
                                for x in [0, 2]:
                                    if tile_at((x, 2 - tile.y)).state == player:
                                        if tile_at((x, tile.y)).state is None:
                                            place(self, (x, tile.y))
                                            already_placed = True
                            else:
                                for y in [0, 2]:
                                    if tile_at((2 - tile.x, y)).state == player:
                                        if tile_at((tile.x, y)).state is None:
                                            place(self, (tile.x, y))
                                            already_placed = True
                    
                    if not already_placed:
                        pos = can_win(player) # check if the player can win - place a block here then
                        if pos:
                            place(self, pos)
                        else:
                            self.random_choose()
                
                while not winner:
                    player.play()
                    clock.tick(2)
                    if can_win(self):
                        clock.tick(2)
                        return

                    self.try_to_survive_hell()
            elif side: # side script
                place(self, (1, 1))
                while not winner:
                    player.play()
                    clock.tick(2)
                    if can_win(self):
                        clock.tick(2)
                        return

                    self.try_to_survive_hell()

            elif center: # center script
                ok = False
                while not ok:
                    pos = random.choice([(0, 0), (2, 0), (2, 2), (0, 2)])
                    if tile_at(pos).state is None:
                        ok = True

                tile1 = place(self, pos)
                tile2 = player.play()
                clock.tick(2)
                if can_win(self):
                    clock.tick(2)
                    return

                if tile1.x + tile1.y + tile2.x + tile2.y == 4: # if player placed in the opposite corner then place in a corner too
                    if random.randint(0, 1):
                        place(self, (tile1.x, 2 - tile1.y))
                    else:
                        place(self, (2 - tile1.x, tile1.y))
                else:
                    pos = can_win(player) # check if the player can win - place a block here then
                    if pos:
                        place(self, pos)
                    else:
                        self.random_choose()

                while not winner:
                    player.play()
                    clock.tick(2)
                    if can_win(self):
                        clock.tick(2)
                        return

                    self.try_to_survive_hell()

        else: # computer begins
            first_tile = random.choice([(0, 0), (2, 0), (2, 2), (0, 2)]) # place on a corner
            
            place(self, first_tile)
            
            player.play()
            clock.tick(2)
            if can_win(self):
                clock.tick(2)
                return

            corner = False # check if the player has placed in a corner
            for pos in [(0, 0), (0, 2), (2, 0), (2, 2)]:
                if tile_at(pos).state == player:
                    corner = True
            side = False # check if the player has placed in a side
            for pos in [(1, 0), (2, 1), (1, 2), (0, 1)]:
                if tile_at(pos).state == player:
                    side = True
            center = False # check if the player has placed in the center
            if tile_at((1, 1)).state == player:
                center = True
            
            if corner: # corner script
                while not winner:
                    already_placed = False
                    for pos in [(0, 0), (0, 2), (2, 0), (2, 2)]: # place in a corner if possible
                        if not already_placed:
                            tile = tile_at(pos)
                            if tile.state is None:
                                tile.set(self)
                                already_placed = True
            
                    player.play()
                    clock.tick(2)
                    if can_win(self):
                        clock.tick(2)
                        return

            elif side: # side script
                place(self, (1, 1))
                
                player.play()
                clock.tick(2)
                if can_win(self):
                    clock.tick(2)
                    return

                pos = can_win(player) # check if the player can win - place a block here then
                if pos:
                    place(self, pos)
                else:
                    number = 0
                    for x in range(3):
                        if tile_at((x, first_tile[1])).state == player:
                            number += 1
                    if number:
                        place(self, (first_tile[0], 2 - first_tile[1]))
                    else:
                        place(self, (2 - first_tile[0], first_tile[1]))

                player.play()
                clock.tick(2)
                if can_win(self):
                    clock.tick(2)
                    return

            elif center: # center script
                # place in an opposite side from the first tile
                if random.randint(0, 1):
                    place(self, (2 - first_tile[0], 1))
                    next_corner = (2 - first_tile[0], first_tile[1])
                else:
                    place(self, (1, 2 - first_tile[1]))
                    next_corner = (first_tile[0], 2 - first_tile[1])
            
                tile = player.play()
                clock.tick(2)
                if can_win(self):
                    clock.tick(2)
                    return

                pos = can_win(player) # check if the player can win - place a block here then
                if pos is not None:
                    place(self, pos)
                elif tile_at(next_corner).state is None: # place next to the side placed before
                    place(self, next_corner)
                else:
                    pos = can_win(player) # check if the player can win - place a block here then
                    if pos:
                        place(self, pos)
                    else:
                        self.random_choose()

                self.try_to_survive()

    def try_to_survive_hell(self):
        pos = can_win(player) # check if the player can win - place a block here then
        if pos:
            place(self, pos)
        else:
            has_center = tile_at((1, 1)).state == computer
            if has_center: # if the center is computer then...
                on_2nd_col = 0
                on_2nd_line = 0
                for pos in [(1, 0), (2, 1), (1, 2), (0, 1)]:
                    tile = tile_at(pos)
                    if tile.state == player:
                        if tile.x == 1:
                            on_2nd_col += 1
                        elif tile.y == 1:
                            on_2nd_line += 1
                if on_2nd_col == 2 or on_2nd_line == 2: # place on a corner if player has two opposite sides
                    if winner == 'draw':
                        return
                    while True:
                        pos = random.choice([(0, 0), (2, 0), (2, 2), (0, 2)])
                        if tile_at(pos).state is None:
                            place(self, pos)
                            return

                following_sides = [[(1, 0), (2, 1)], [(2, 1), (1, 2)], [(1, 2), (0, 1)], [(0, 1), (1, 0)]]
                for index in range(4): # place on a corner between two following sides occuped by the player
                    number = 0
                    for pos in following_sides[index]:
                        tile = tile_at(pos)
                        if tile.state == player:
                            number += 1
                    if number == 2:
                        if index == 0:
                            if tile_at((2, 0)).state is None:
                                place(self, (2, 0))
                                return
                        elif index == 1:
                            if tile_at((2, 2)).state is None:
                                place(self, (2, 2))
                                return
                        elif index == 2:
                            if tile_at((0, 2)).state is None:
                                place(self, (0, 2))
                                return
                        elif index == 3:
                            if tile_at((0, 0)).state is None:
                                place(self, (0, 0))
                                return

                for pos in [(1, 0), (2, 1), (1, 2), (0, 1)]: # if the player has a side and an opposite corner, place next to the side
                    tile = tile_at(pos)
                    if tile.state == player:
                        if tile.x == 1:
                            for x in [0, 2]:
                                if tile_at((x, 2 - tile.y)).state == player:
                                    if tile_at((x, tile.y)).state is None:
                                        place(self, (x, tile.y))
                                        return
                        else:
                            for y in [0, 2]:
                                if tile_at((2 - tile.x, y)).state == player:
                                    if tile_at((tile.x, y)).state is None:
                                        place(self, (tile.x, y))
                                        return

                self.random_choose()
            else:
                self.random_choose()

    def try_to_survive(self):
        while not winner:
            tile = player.play()
            clock.tick(2)
            if can_win(self):
                clock.tick(2)
                return
            
            pos = can_win(player) # check if the player can win - place a block here then
            if pos:
                place(self, pos)
            else:
                self.random_choose() # or place randomly to kill time

    def random_choose(self):
        if winner == 'draw':
            return
        free_tiles = [tile for tile in tiles if tile.state is None]
        tile = random.choice(free_tiles)
        place(self, (tile.x, tile.y))

    def multiplayer(self):
        global winner
        while pygame.mouse.get_pressed()[0]:
            pass
        ok = None
        while not winner and ok is None:
            if pygame.mouse.get_pressed()[0]:
                xmouse, ymouse = pygame.mouse.get_pos()
                for tile in tiles:
                    xtile = tile.x * 210 + 10
                    ytile = tile.y * 210 + 10
                    if xtile < xmouse < xtile + 210:
                        if ytile < ymouse < ytile + 210:
                            if tile.state is None:
                                tile.state = self
                                if has_won(self): # if the tile make you win then change the animation
                                    tile.set(self, True)
                                else:
                                    tile.set(self)
                                ok = tile

        if has_won(self):
            winner = self
            win_sound.play()
        return ok

class Player:
    def play(self):
        global winner
        while pygame.mouse.get_pressed()[0]: # wait for the mouse button to release
            pass
        ok = None
        while not winner and ok is None:
            while pause: # wait if pause
                pass
            if pygame.mouse.get_pressed()[0]:
                xmouse, ymouse = pygame.mouse.get_pos()
                for tile in tiles:
                    xtile = tile.x * 210 + 10
                    ytile = tile.y * 210 + 10
                    if xtile < xmouse < xtile + 210:
                        if ytile < ymouse < ytile + 210:
                            if tile.state is None:
                                tile.state = self
                                if has_won(self): # if the tile make you win then change the animation
                                    tile.set(self, True)
                                else:
                                    tile.set(self)
                                ok = tile

        if has_won(self):
            winner = self
            win_sound.play()
        return ok

class Tile:
    def __init__(self, pos):
        self.state = None
        self.reset_state = None
        self.x, self.y = pos
        self.time = 0
        self.tile_make_win = False

    def set(self, state, tile_make_win=False): # different to Tile.state = ...  because it starts the animation
        self.state = state
        self.time = time.time()
        self.tile_make_win = tile_make_win
    
    def reset(self):
        self.reset_state = self.state
        self.tile_make_win = False
        self.time = time.time()
    
    def render(self):
        size = 200
        offset = 0
        if time.time() - self.time < 0.1: # time when the animation is played
            if self.tile_make_win:
                size = int(600 - 300 * 10 * (time.time() - self.time))
                offset = int((size - 200) / 2)
            else:
                size = int(200 * 10 * (time.time() - self.time))
                if self.reset_state is not None:
                    size = max(1, 200 - size)
                offset = int((size - 200) / 2)
        else:
            if self.reset_state and self.reset_state != 'half':
                self.reset_state = None
                self.state = None
        
        if self.state == computer:
            image = pygame.transform.scale(computer_image, (size, size))
        elif self.state == player:
            image = pygame.transform.scale(player_image, (size, size))

        if self.reset_state is not None: # in the menu, to reset the tiles with an animation
            if self.reset_state == 'half': # when someone won, but this tile didn't
                if self.state == computer:
                    image_ = pygame.transform.scale(computer_image, (size, size))
                elif self.state == player:
                    image_ = pygame.transform.scale(player_image, (size, size))
                else:
                    image_ = pygame.Surface((1, 1))
                image = pygame.Surface((size, size), SRCALPHA)
                image.set_alpha(100)
                image.blit(image_, (0, 0))
            else:
                if self.reset_state == computer:
                    image = pygame.transform.scale(computer_image, (size, size))
                elif self.reset_state == player:
                    image = pygame.transform.scale(player_image, (size, size))
        
        if self.state is not None:
            screen.blit(image, (210 * self.x + 10 - offset, 210 * self.y + 10 - offset))

class Background: # black game background with white lines
    def __init__(self):
        self.image = pygame.Surface((640, 640))
        self.image.fill((0, 0, 0))
        pygame.draw.line(self.image, (255, 255, 255), (214, 10), (214, 630), 10)
        pygame.draw.line(self.image, (255, 255, 255), (424, 10), (424, 630), 10)
        pygame.draw.line(self.image, (255, 255, 255), (10, 214), (630, 214), 10)
        pygame.draw.line(self.image, (255, 255, 255), (10, 424), (630, 424), 10)

    def render(self):
        screen.blit(self.image, (0, 0))

def tile_at(pos):
    for tile in tiles:
        if (tile.x, tile.y) == pos:
            return tile

def place(state, pos):
    tile = tile_at(pos)
    if tile.state is None:
        tile.set(state)
    return tile

def can_win(as_, auto_fill=True): # auto_fill is used to leave the tile to None even if as_ is computer
    free_tiles = [tile for tile in tiles if tile.state is None]
    for tile in free_tiles:
        tile.state = as_
        if has_won(as_):
            if as_ == computer and auto_fill: # computer call this function to win if possible...
                global winner
                winner = computer
                tile.set(computer, True)
                win_sound.play()
                return True # ...so no need to reset the tile.state to None
            tile.state = None
            return (tile.x, tile.y)
        tile.state = None
    return None

def has_won(as_):
    as_tiles = [tile for tile in tiles if tile.state == as_]
    
    # check |
    for x in range(3):
        number = 0
        for tile in as_tiles:
            if tile.x == x:
                number += 1
        if number == 3:
            return [tile for tile in as_tiles if tile.x == x]
    
    # check -
    for y in range(3):
        number = 0
        for tile in as_tiles:
            if tile.y == y:
                number += 1
        if number == 3:
            return [tile for tile in as_tiles if tile.y == y]
    
    # check / and \
    has_middle = False
    for tile in tiles:
        if tile.x == tile.y == 1:
            if tile.state == as_:
                has_middle = True
    
    if has_middle:
        
        number = 0
        
        for tile in tiles: # check \
            if tile.x == tile.y == 0:
                if tile.state == as_:
                    number += 1
            if tile.x == tile.y == 2:
                if tile.state == as_:
                    number += 1
        
        if number == 2:
            return [tile for tile in as_tiles if tile.x == tile.y]
        
        number = 0
        
        for tile in tiles: # check /
            if tile.x == 2 and tile.y == 0:
                if tile.state == as_:
                    number += 1
            if tile.x == 0 and tile.y == 2:
                if tile.state == as_:
                    number += 1
        
        if number == 2:
            return [tile for tile in as_tiles if tile.x + tile.y == 2]
    
    return False

def end_game_message():
    global surface, display_text, buttons
    alpha = 0
    start = time.time()
    while time.time() - start <= 0.5:
        alpha = ((time.time() - start) * 2)**(1/3) * 150
        surface.set_alpha(alpha)

    # this text is displayed in the main thread
    if difficulty == 'multiplayer':
        if winner == 'draw':
            display_text = random.choice(draw_msg)
        else:
            display_text = random.choice(multiplayer_msg)
    else:
        if winner == computer:
            display_text = random.choice(computer_msg)
        elif winner == player:
            display_text = random.choice(player_msg)
        else:
            display_text = random.choice(draw_msg)
    
    buttons.append((('Play again', (320, 325)), play_again)) # these buttons are displayed in the main thread
    buttons.append((('Back to menu', (320, 400)), back_))
    
    while not back:
        pass

    buttons = []

    display_text = None
    surface.set_alpha(0)

def back_():
    global back
    back = True

def play_again():
    global back
    back = -1

def launch():
    global play, first_player, winner, start_time, image_to_display, back
    
    # reset all
    winner = None
    for tile in tiles:
        tile.state = None
        tile.reset_state = None
    
    start_time = time.time()
    if difficulty == 'ez':
        computer.ez()
    elif difficulty == 'human':
        computer.human()
    elif difficulty == 'hell':
        computer.hell()
    elif difficulty == 'multiplayer':
        if random.randint(0, 1): # a random player begins
            image = pygame.transform.scale(computer_image, (100, 100))
            image_to_display = pygame.Surface((100, 100), SRCALPHA)
            image_to_display.set_alpha(100)
            image_to_display.blit(image, (0, 0))
            
            computer.multiplayer()
        while not winner:
            image = pygame.transform.scale(player_image, (100, 100))
            image_to_display = pygame.Surface((100, 100), SRCALPHA)
            image_to_display.set_alpha(100)
            image_to_display.blit(image, (0, 0))
            
            player.play()
            
            if has_won(player):
                winner = player
            else:
                image = pygame.transform.scale(computer_image, (100, 100))
                image_to_display = pygame.Surface((100, 100), SRCALPHA)
                image_to_display.set_alpha(100)
                image_to_display.blit(image, (0, 0))
                
                computer.multiplayer()
            if has_won(computer):
                winner = computer

    image_to_display = pygame.Surface((50, 50), SRCALPHA)
    fill_stats()
    end_game_message()

    if first_player == computer: # switch the first player
        first_player = player
    else:
        first_player = computer

def fill_stats():
    try:
        with open('files\\stats.txt') as f:
            ez, human, hell = f.read().split('\n')
    except:
        with open('files\\stats.txt', 'w') as f:
            f.write('0,0,0\n0,0,0\n0,0,0')
    
    with open('files\\stats.txt') as f:
        ez, human, hell = f.read().split('\n')
    
    if difficulty == 'ez':
        p, d, c = ez.split(',')
        if winner == player:
            p = str(int(p) + 1)
        elif winner == 'draw':
            d = str(int(d) + 1)
        elif winner == computer:
            c = str(int(c) + 1)
        ez = p+','+d+','+c
        
    elif difficulty == 'human':
        p, d, c = human.split(',')
        if winner == player:
            p = str(int(p) + 1)
        elif winner == 'draw':
            d = str(int(d) + 1)
        elif winner == computer:
            c = str(int(c) + 1)
        human = p+','+d+','+c
        
    elif difficulty == 'hell':
        p, d, c = hell.split(',')
        if winner == player:
            p = str(int(p) + 1)
        elif winner == 'draw':
            d = str(int(d) + 1)
        elif winner == computer:
            c = str(int(c) + 1)
        hell = p+','+d+','+c
    
    with open('files\\stats.txt', 'w') as f:
        f.write(ez+'\n'+human+'\n'+hell)

def __game__():
    global winner, mouse_pressed, back, pause

    while not back:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                if winner is None:
                    if pause:
                        pause = False
                        surface.set_alpha(0)
                    else:
                        pause = True
                        surface.set_alpha(127)

        background.render()
        for tile in tiles:
            tile.render()

        if difficulty == 'multiplayer':
            screen.blit(image_to_display, (0, 0))
        
        screen.blit(surface, (0, 0))

        if display_text is not None:
            y = 150
            for line in display_text.split('\n'):
                if '%' in line:
                    line = line % (time.time() - start_time)
                text = font.render(line, 1, (255, 255, 255))
                w, h = text.get_size()
                screen.blit(text, (int(320 - w / 2), int(y - h / 2)))
                y += 25
        
        if not len([tile for tile in tiles if tile.state is None]) and winner is None:
            winner = 'draw'

        for b in buttons:
            if button(*b[0]): # draw a button with arguments
                b[1]() # do the function contained here
                buttons.remove(b)

        # display this in pause
        if pause and winner is None:
            screen.blit(title.render('Pause', 1, (255, 255, 255)), (100, 100))
            if button('Back to game', (320, 320)):
                pause = False
                surface.set_alpha(0)
        
        # if someone won, leave only the tiles who make him won
        for winner_ in [player, computer]:
            won = has_won(winner_)
            if won:
                for tile in tiles:
                    if tile not in won:
                        tile.reset_state = 'half'
        
        if back == -1: # back can be -1 (play again), then back is reset to False
            clock.tick(5) # leave the game thread time to get the information
            back = False
            start_game_thread(False) # restart a new game without restarting the music
        
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        pygame.display.flip()
        time_passed = clock.tick() / 1000

def button(text, pos, can_activate=True):
    global mouse_pressed
    
    # draw the button
    x, y = pos
    text = font.render(text, 1, (255, 255, 255))
    w, h = text.get_size()
    
    buttonw = max(200, w + 50)
    buttonh = h + 25
    button_surface = pygame.Surface((buttonw, buttonh), SRCALPHA)
    
    collide = False
    mousex, mousey = pygame.mouse.get_pos()
    if x - buttonw / 2 <= mousex <= x + buttonw / 2:
        if y - buttonh / 2 <= mousey <= y + buttonh / 2:
            collide = True

    if collide and can_activate: # change the size and the color of the button if the mouse pass on
        buttonw += 10
        buttonh += 5
        button_surface = pygame.Surface((buttonw, buttonh), SRCALPHA)
        button_surface.fill((75, 75, 75, 200))
    else:
        button_surface.fill((50, 50, 50, 127))
    
    screen.blit(button_surface, (int(x - buttonw / 2), int(y - buttonh / 2)))
    screen.blit(text, (int(x - w / 2), int(y - h / 2)))

    # detect if the button is pressed
    if collide:
        if pygame.mouse.get_pressed()[0]:
            mouse_pressed = True
        else: # if the mouse is just released
            if mouse_pressed:
                button_sound.play()
                return True
            mouse_pressed = True
    return False

def play_in_background(wait):
    global cooldown, last_player, winner
    background.render()
    for tile in tiles:
        tile.render()

    for player_ in menu_players:
        if time.time() - cooldown > wait and last_player != player_:
            last_player = player_
            cooldown = time.time()
                
            if not len([tile for tile in tiles if tile.state is None]):
                winner = 'draw'
            
            if winner is None:
                player_.play()
            else:
                for tile in tiles:
                    tile.reset()
                winner = None

            if has_won(player_.as_):
                winner = player_

    screen.blit(surface, (0, 0))
        
def start_game_thread(from_menu=True):
    global play, music_played

    # animation1
    screen_ = pygame.Surface((640, 640))
    screen_.blit(screen, (0, 0)) # get the screen image

    start = time.time()
    while time.time() - start < 0.5:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        if from_menu:
            music_played.set_volume(1 + (start - time.time()) * 2)
        surface.set_alpha(int((time.time() - start) * 510))
        
        screen.blit(screen_, (0, 0))
        screen.blit(surface, (0, 0))

        pygame.display.flip()

    # wait half a second with black screen
    start = time.time()
    while time.time() - start < 0.5:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))

        pygame.display.flip()

    if from_menu:
        music_played = pygame.mixer.find_channel(True)
        music_played.play(game_music, -1)
        music_played.set_volume(0.5)
    
    # animation 2
    start = time.time()
    while time.time() - start < 0.5:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        if from_menu:
            music_played.set_volume(0.5 + time.time() - start)
        surface.set_alpha(int((0.5 - time.time() + start) * 510))
        
        background.render()
        screen.blit(surface, (0, 0))

        pygame.display.flip()

    surface.set_alpha(0)
    play = threading.Thread(target=launch)
    play.start()

def stop_game():
    global music_played

    # animation1
    screen_ = pygame.Surface((640, 640))
    screen_.blit(screen, (0, 0)) # get the screen image

    start = time.time()
    while time.time() - start < 0.5:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        music_played.set_volume(1 + (start - time.time()) * 2)
        surface.set_alpha(int((time.time() - start) * 510))
        
        screen.blit(screen_, (0, 0))
        screen.blit(surface, (0, 0))

        pygame.display.flip()

    # wait half a second with black screen
    start = time.time()
    while time.time() - start < 0.5:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))

        pygame.display.flip()

    music_played = pygame.mixer.find_channel(True)
    music_played.play(menu_music, -1)
    music_played.set_volume(0.5)
    
    # animation 2
    start = time.time()
    while time.time() - start < 0.5:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        music_played.set_volume(0.5 + time.time() - start)
        surface.set_alpha(int(127 + (0.5 - time.time() + start) * 255))
        
        background.render()
        screen.blit(surface, (0, 0))

        pygame.display.flip()

    music_played.set_volume(1)
    surface.set_alpha(127)

def menu():
    global back, play, difficulty, mouse_pressed, cooldown, last_player, time_passed
    
    surface.set_alpha(127)
    last_player = menu_players[0]
    cooldown = 0

    if difficulty == 'ez':
        color = (50, 255, 0)
        wait = 0.7
    elif difficulty == 'human':
        color = (255, 200, 0)
        wait = 0.3
    elif difficulty == 'hell':
        color = (255, 0, 0)
        wait = 0.1
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
        
        play_in_background(wait)
        
        screen.blit(title.render('Tic tac toe', 1, (255, 255, 255)), (100, 100))
        
        splash = splashfont.render(difficulty + ' mode', 1, color)
        splash = pygame.transform.rotate(splash, -20)
        w, h = 30, 30*splash.get_height()/splash.get_width()
        splash = pygame.transform.smoothscale(splash, (int(w * (math.sin(time.time() * 10) + 5)), int(h * (math.sin(time.time() * 10) + 5))))
        w, h = splash.get_size()
        screen.blit(splash, (int(330 - w / 2), int(100 - h / 2)))
        
        if button('PLAY', (200, 250)):
            back = False
            start_game_thread()
            surface.set_alpha(0)
            __game__()
            stop_game()
            back = False
        
        if button('Multiplayer', (200, 325)):
            last_difficulty = difficulty # start the game in multiplayer difficulty, and store the difficulty to get it back after
            difficulty = 'multiplayer'
            
            back = False
            start_game_thread()
            surface.set_alpha(0)
            __game__()
            stop_game()
            back = False
            
            difficulty = last_difficulty
        
        if button('Difficulty', (200, 400)):
            if difficulty == 'ez':
                pygame.display.set_caption('Tic Tac Toe - Human mode')
                difficulty = 'human'
                color = (255, 200, 0)
                wait = 0.3
            elif difficulty == 'human':
                pygame.display.set_caption('Tic Tac Toe - HELL mode')
                difficulty = 'hell'
                color = (255, 0, 0)
                wait = 0.1
            elif difficulty == 'hell':
                pygame.display.set_caption('Tic Tac Toe - Ez mode')
                difficulty = 'ez'
                color = (50, 255, 0)
                wait = 0.7
        
        if button('Statistics', (200, 475)):
            with open('files\\stats.txt') as f:
                ez, human, hell = f.read().split('\n')
            ez = [int(score) for score in ez.split(',')]
            human = [int(score) for score in human.split(',')]
            hell = [int(score) for score in hell.split(',')]

            frame = pygame.Surface((640, 350), SRCALPHA)
            frame.fill((0, 0, 0, 127))
            
            while not back:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        exit()

                play_in_background(wait)

                screen.blit(frame, (0, 150))
                
                screen.blit(title.render('Statistics', 1, (255, 255, 255)), (100, 80))

                colors = [(50, 255, 0), (255, 200, 0), (255, 0, 0)]
                
                for x in range(3):
                    text = font.render(['Wins', 'Draws', 'Losses'][x], 1, colors[x])
                    w = text.get_width()
                    screen.blit(text, (int(225 + 150 * x - w / 2), 175))
                
                for y in range(3):
                    text = font.render(['Ez mode', 'Human mode', 'Hell mode'][y], 1, colors[y])
                    screen.blit(text, (20, 250 + 100 * y))

                modes = [ez, human, hell]
                for mode in range(3):
                    y = mode * 100

                    for x in range(3):
                        text = font.render(str(modes[mode][x]), 1, (255, 255, 255))
                        w = text.get_width()
                        screen.blit(text, (int(225 + 150 * x - w / 2), 250 + y))
                
                if button('Back', (520, 600)):
                    back = True
                
                mouse_pressed = pygame.mouse.get_pressed()[0]
                
                pygame.display.flip()
                time_passed = clock.tick() / 1000
            
            back = False
        
        if button('Quit game', (200, 550)):
            pygame.quit()
            exit()

        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        pygame.display.flip()
        time_passed = clock.tick() / 1000

pygame.init()
screen = pygame.display.set_mode((640, 640))
pygame.display.set_caption('Tic Tac Toe')
pygame.display.set_icon(pygame.image.load('files\\icon.png'))
font = pygame.font.SysFont('calibri', 25, True)
splashfont = pygame.font.SysFont('calibri', 50, True)
title = pygame.font.SysFont('impact', 50)
clock = pygame.time.Clock()

screen.fill((0, 0, 0))
text = title.render('Loading...', 1, (255, 255, 255))
w, h = text.get_size()
screen.blit(text, (int(320 - w / 2), int(320 - h / 2)))
pygame.display.flip()

pygame.mixer.set_reserved(2) # 2 channels reserved for playing win sound and music

game_music = pygame.mixer.Sound('files\\game.mp3')
menu_music = pygame.mixer.Sound('files\\menu.mp3')

music_played = pygame.mixer.find_channel(True) # should always find a channel
music_played.play(menu_music, -1)

pos = [(0, 0),
       (1, 0),
       (2, 0),
       (2, 1),
       (2, 2),
       (1, 2),
       (0, 2),
       (0, 1),
       (1, 1)]

tiles = []
for p in pos:
    tiles.append(Tile(p))

player = Player()
computer = Computer()
menu_players = [MenuPlayer(player), MenuPlayer(computer)]

background = Background()
buttons = []

mouse_pressed = False
pause = False
back = False
winner = None
first_player = player
difficulty = 'hell'
time_passed = 0
display_text = None
surface = pygame.Surface((640, 640), SRCALPHA)
surface.fill((0, 0, 0)) # black transparent image
surface.set_alpha(0)

player_image = pygame.image.load('files\\player.png')
computer_image = pygame.image.load('files\\computer.png')
image_to_display = pygame.Surface((100, 100), SRCALPHA)

win_sound = pygame.mixer.Sound('files\\hit.mp3')
button_sound = pygame.mixer.Sound('files\\button.mp3')

computer_msg = ['Computer wins (as always), u little loser',
                'Ha ha ha ha haaaaaaaaaaaaaaaaa!!!',
                'What were u thinking? It\'s the only way to go',
                'Am such a genius!',
                'Did u c that? impossibly impossible',
                'U know what? Am so unbeatable in hell mode\nthat am not coded to handle ur victory']
player_msg = ['I had kinda bug - it will never happen again',
              'I name this "luck". Ok? Just luck.',
              'No way...',
              'Wanna try more difficult?',
              'Have you tried hell mode? ;)']
draw_msg = ['Congrats.\nYou wasted approx. %d seconds of ur life',
            'Useless game - try again?',
            'Don\'t leave! This could potentially\nprobably possibly imaginably maybe be fun']
            
multiplayer_msg = ['U lucky guy - keep randomly clicking xD',
                   'NOICE. Now wanna try to beat a REAL player (me)?',
                   'Cool! Ur not as bad as I thought',
                   'HELLOOOOOOO! I do exist, u know\nU can try to beat me if you have no friends',
                   'WEEEE ARE THE CHAMPIONS, MY FRIEND!!!!!']

menu()
