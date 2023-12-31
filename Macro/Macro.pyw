import time
import pygame
from pygame.locals import *
pygame.init()

from threading import Thread
from pynput.mouse import Button, Controller, Listener
mouse = Controller()
mouse_listener = Listener
from pynput.keyboard import Key, Controller, Listener
keyboard = Controller()
keyboard_listener = Listener

class Input:
    def __init__(self, pos, value):
        self.value = value
        self.text = str(value)
        self.type = type(value)
        self.rect = Rect(pos, (75, 20))

        self.active = 0

    def draw(self):
        if self.active and (ticks()-self.active)//333%3:
            blink = '_'
        else:
            blink = ' '
        text = block_font.render(self.text+blink, True, black)
        if text.get_width() > self.rect.width:
            t = text
            text = pygame.Surface((self.rect.width, text.get_height()), SRCALPHA)
            text.blit(t, (100-t.get_width(), 0))
        pygame.draw.rect(screen, white, self.rect)
        screen.blit(text, (self.rect.x, self.rect.y))

    def update(self):
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.active = self.rect.collidepoint(event.pos) * (ticks()-300)
            elif event.type == KEYDOWN and self.active:
                if event.key == K_BACKSPACE:
                    if len(self.text) > 1+('.' in self.text):
                        self.text = self.text[:-1]
                    else:
                        self.text = '0'
                elif event.key == K_RETURN:
                    self.active = 0 # deselect the input
                elif event.unicode == '-':
                    if self.text[0] == '-':
                        self.text = self.text[1:]
                    else:
                        self.text = '-'+self.text
                elif event.unicode and (event.unicode in '0123456789' or (event.unicode == '.' and '.' not in self.text)):
                    self.active = ticks()-300 # keep displaying the cursor
                    if self.text in ['0', '-0']:
                        minus = self.text[0] == '-'
                        if event.unicode == '.':
                            self.text = '0.'
                        else:
                            self.text = event.unicode
                        if minus:
                            self.text = '-' + event.unicode
                    else:
                        self.text += event.unicode

        self.value = self.type(self.text) # convert into usable data

        return self.active

class MouseEvent:
    def __init__(self):
        self.button = Button.left
        self.pressed = False
        self.active = False
        self.cooldown = 0
        Thread(target=self.start_thread).start()

    def __del__(self):
        self.listener.stop() # stop the thread

    def change_pos(self, pos):
        self.rect = Rect(pos, (100, 20))

    def click(self, x, y, button, pressed):
        if self.active and pressed:
            self.button = button
            self.active = False
            self.cooldown = time.time()+0.1
        if button == self.button:
            self.pressed = pressed

    def start_thread(self):
        with mouse_listener(on_click=self.click) as l:
            l.join()
        print('thread stopped.')

    def draw(self):
        surf = pygame.Surface((self.rect.width+6, self.rect.height+6))
        surf.set_alpha(100)
        surf.fill(black)
        screen.blit(surf, (self.rect.x-3, self.rect.y-3))
        if self.active: # blank text
            text = ''
        else:
            text = str(self.button).split('.')[1]
        screen.blit(block_font.render(text, True, white), (self.rect.x, self.rect.y))

    def update(self):
        for event in events:
            if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
                if not self.active and time.time() >= self.cooldown:
                    # next button press will be self.button
                    self.active = True

        return self.active or time.time() < self.cooldown

class KeyEvent:
    def __init__(self):
        self.key = Key.space
        self.pressed = False
        Thread(target=self.start_thread).start()

    def __del__(self):
        self.listener.stop() # stop the thread

    def change_pos(self, pos):
        self.rect = Rect(pos, (100, 20))

    def press(self):
        if key == self.key:
            self.pressed = True

    def release(self):
        if key == self.key:
            self.pressed = False

    def start_thread(self):
        with keyboard_listener(on_press=self.press, on_release=self.release) as l:
            l.join()
        print('thread stopped.')

    def draw(self):
        pass

    def update(self):
        pass

class Block:
    def __init__(self, pos, type_, in_menu, elements, function=''):
        # function will be used as a key for functions()
        def extend_surf(width):
            w, h = self.surf.get_size()
            surf = pygame.Surface((w+width, h), SRCALPHA)
            surf.blit(self.surf, (0, 0))
            pygame.draw.rect(surf, color, Rect((w, 0), (width, h)))
            self.surf = surf

        self.in_menu = in_menu
        self.master = self
        self.function = function
        self.base_elements = elements
        self.type = type_ # 0 for normal block, 1 for event block
        self.dragged = 0
        self.next_in_stack = None
        self.cancel_next_event = False
        self.running = False # is the attached function running?
        if in_menu:
            self.index = 1
            while self.index in [block.index for block in menu_blocks]:
                self.index += 1
            self.pos = [20, 20+70*self.index]
        else:
            self.index = len(blocks)+1 # starts with 1
            self.pos = list(pos)
        if type_:
            color = green2
        else:
            color = green1
        self.z = len(blocks) # used for the block drawing order
        self.origin = self.pos[:] # starting point of dragging
        self.elements = []

        self.surf = pygame.Surface((10, 50), SRCALPHA)
        self.surf.fill(color)
        for element in elements:
            if type(element) == str: # text
                width = self.surf.get_width()
                text = block_font.render(element, True, white)
                extend_surf(text.get_width())
                self.surf.blit(text, (width, 15))
            elif type(element) in [MouseEvent, KeyEvent]:
                element.change_pos((self.pos[0]+self.surf.get_width(), self.pos[1]+15))
                self.elements.append(element)
                extend_surf(100)
            else: # number
                self.elements.append(Input((self.pos[0]+self.surf.get_width(), self.pos[1]+15), element))
                extend_surf(75)
            extend_surf(10) # inner margin
        if not len(elements):
            extend_surf(10) # right margin

        self.better_looking(color)
        self.mask = pygame.mask.from_surface(self.surf) # collisions only for visible pixels

    def __del__(self):
        self.dragged = False
        for element in self.elements:
            del element
        if self in blocks: # can be removed by a block above
            blocks.remove(self)
        next_ = find(self.next_in_stack)
        if next_:
            next_.__del__() # delete the stack below

    def copy(self): # only called by menu blocks
        # add a menu block back to where self used to be, with original arguments
        elements = self.base_elements[:]
        for x in range(len(elements)):
            if type(elements[x]) in [MouseEvent, KeyEvent]:
                elements[x] = type(elements[x])()
        menu_blocks.append(Block(self.origin, self.type, True, elements, self.function))

    def better_looking(self, color):
        # 3D borders
        w, h = self.surf.get_size()
        surf = pygame.Surface((w, h), SRCALPHA)
        surf.set_alpha(100)
        pygame.draw.polygon(surf, white, [(0, 0), (w-1, 0), (w-6, 4), (4, 4), (4, h-6), (0, h-1)])
        pygame.draw.polygon(surf, black, [(w-1, 0), (w-1, h-1), (0, h-1), (5, h-6), (w-5, h-5), (w-6, 4)])
        self.surf.blit(surf, (0, 0))

        # better geometry
        surf = pygame.Surface((w, h+5), SRCALPHA)
        surf.blit(self.surf, (0, 0))
        self.surf = surf
        # top
        pygame.draw.polygon(self.surf, (0, 0, 0, 0), [(20, 0), (23, 4), (37, 4), (40, 0)])
        surf = pygame.Surface((46, 10), SRCALPHA)
        surf.set_alpha(100)
        pygame.draw.polygon(surf, white, [(15, 5), (19, 9), (41, 9), (45, 5)])
        self.surf.blit(surf, (0, 0))
        # bottom
        pygame.draw.polygon(self.surf, color, [(20, h), (23, h+5), (37, h+5), (40, h)])
        surf = pygame.Surface((41, 6), SRCALPHA)
        surf.set_alpha(100)
        pygame.draw.polygon(surf, black, [(20, 0), (23, 5), (37, 5), (40, 0)])
        self.surf.blit(surf, (0, h))
        pygame.draw.polygon(self.surf, color, [(25, h-5), (28, h-1), (32, h-1), (35, h-5)])

    def collide(self, pos):
        pos = (pos[0]-self.pos[0], pos[1]-self.pos[1])
        return self.mask.get_rect().collidepoint(pos) and self.mask.get_at(pos)

    def move_to(self, pos): # move the entire stack as one block
        pos = list(pos)
        block = self
        while block:
            rel_x = pos[0]-block.pos[0]
            rel_y = pos[1]-block.pos[1]
            block.pos[0] += rel_x
            block.pos[1] += rel_y
            for element in block.elements: # move the inner elements as well
                if type(element) != pygame.Surface:
                    element.rect.x += rel_x
                    element.rect.y += rel_y

            pos[1] += block.surf.get_height()-5
            block = find(block.next_in_stack)

    def find_master(self): # find the block at the top of the stack
        self.master = self
        found = True
        while found: # run the first block of the stack
            found = False
            for block in blocks:
                if block.next_in_stack == self.master.index:
                    self.master = block
                    found = True
                    break
        block = self
        while block: # update the master for the entire stack
            block.master = self.master
            block = find(block.next_in_stack)

    def execute_function(self): # in a thread
        functions(self, self.function)
        if self.next_in_stack:
            # execute the next block action
            Thread(target=find(self.next_in_stack).execute_function).start()
        else:
            # stop the glowing effect for the entire stack
            self.master.running = False

    def draw_shadow(self, color):
        w, h = self.surf.get_size()
        surf = pygame.Surface((w, h-5), SRCALPHA)
        surf.set_alpha(100)
        surf.fill(color)
        screen.blit(surf, (self.pos[0]+5, self.pos[1]+5))
        surf = pygame.Surface((41, 6), SRCALPHA)
        surf.set_alpha(100)
        pygame.draw.polygon(surf, color, [(20, 0), (22, 5), (37, 5), (40, 0)])
        screen.blit(surf, (self.pos[0]+5, self.pos[1]+self.surf.get_height()))

    def draw(self):
        # only display if visible
        if self.in_menu:
            rect = menu_rect
        else:
            rect = main_rect
        if rect.colliderect(Rect(self.pos, self.surf.get_size())) or self.master.dragged:
            if self.dragged or self.master.dragged:
                self.draw_shadow(black)
            if self.running or self.master.running:
                self.draw_shadow(yellow)
            screen.blit(self.surf, (self.pos[0], self.pos[1]))

            for element in self.elements:
                element.draw()

    def update(self):
        interacted_with_elements = False
        for element in self.elements:
            if type(element) in [Input, MouseEvent, KeyEvent]:
                if element.update(): # did something to the element
                    interacted_with_elements = True

        other_dragged = False
        for block in blocks:
            if block.dragged and block != self:
                other_dragged = True
                break # only check if at least one dragged

        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.collide(event.pos) and not other_dragged:
                    if self.in_menu: # create a clone of itself that stays in the menu
                        if not menu_rect.collidepoint(event.pos):
                            continue
                        menu_blocks.remove(self)   #
                        blocks.append(self)        # store itself in the blocks list
                        self.index = len(blocks)   #
                        self.copy()
                        self.in_menu = False
                    # can't drag if e.g. other dragged over self
                    if interacted_with_elements: # or interacted with element
                        self.cancel_next_event = True # do not execute the MOUSEBUTTONUP script
                        # if in the menu, delete the wrongly created block
                        if menu_rect.collidepoint(event.pos):
                            self.__del__()
                            return
                    else:
                        self.master.running = False # prevent from infinite glowing

                        for block in blocks:
                            if block != self and block.z > self.z:
                                block.z -= 1
                        self.z = len(blocks)-1 # bring block to the front

                        block = self
                        while block: # update the master for the stack below
                            block.master = self
                            block = find(block.next_in_stack)

                        # unstack from the top block
                        for block in blocks:
                            if block.next_in_stack == self.index:
                                block.next_in_stack = None

                        self.dragged = (self.pos[0]-event.pos[0], self.pos[1]-event.pos[1])
                        self.origin = self.pos[:]
                else:
                    self.cancel_next_event = True # do not execute the MOUSEBUTTONUP script
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if self.cancel_next_event:
                    self.cancel_next_event = False
                    continue
                if self.collide(event.pos):
                    if menu_rect.collidepoint(event.pos):
                        self.__del__()
                        return
                    # check if only moved by a significant amount
                    do_run_function = False # if True, launch a thread
                    if abs(self.origin[0]-self.pos[0]) + abs(self.origin[1]-self.pos[1]) < 10:
                        self.move_to(self.origin)
                        do_run_function = True

                    # check if attached/detached
                    total_height = 0
                    block = last_block = self
                    while block:
                        total_height += block.surf.get_height()-5
                        last_block = block
                        block = find(block.next_in_stack)

                    x, y = self.pos
                    for block in blocks:
                        if block == self:
                            continue
                        x_, y_ = block.pos
                        if abs(x-x_) < 20:
                            if abs(y-y_-block.surf.get_height()+5) < 20: # attached to the bottom
                                if block.next_in_stack: # make the blocks already attached go further down
                                    next_ = find(block.next_in_stack)
                                    next_.move_to((next_.pos[0], next_.pos[1]+total_height))
                                    last_block.next_in_stack = block.next_in_stack
                                    block.next_in_stack = self.index
                                    self.find_master()
                                else:
                                    block.next_in_stack = self.index
                                    self.find_master()
                                self.move_to((block.pos[0], block.pos[1]+block.surf.get_height()-5))
                                break
                            if abs(y+total_height-y_) < 20: # attached to the top
                                block.master.running = False # prevent from infinite glowing
                                last_block.next_in_stack = block.index
                                self.move_to((block.pos[0], block.pos[1]-total_height))
                                self.find_master()
                                break

                    self.dragged = False

                    # do that after updating self.master
                    if do_run_function and not self.master.running: # do not launch if already running
                        Thread(target=self.master.execute_function).start()
                        # the other threads will be launched one after the other

                        self.master.running = True # make the entire stack glow

        if self.dragged:
            x, y = pygame.mouse.get_pos()
            self.move_to((x+self.dragged[0], y+self.dragged[1]))

def functions(self, key):
    if key == 'sleep':
        start = time.time()
        end = start + self.elements[0].value/1000
        while time.time() < end:
            time.sleep(min(end-time.time(), 100)) # update every tenth of a second
            if not self.master.running:
                break
    if key == 'set_mouse':
        mouse.position = (self.elements[0].value, self.elements[1].value)
    if key == 'move_mouse':
        x, y = mouse.position
        mouse.position = (x+self.elements[0].value, y+self.elements[1].value)
    if key == 'press_mouse':
        mouse.press(self.elements[0].button)

def find(index):
    for block in blocks:
        if block.index == index:
            return block

def draw_menu():
    pygame.draw.rect(screen, menu_grey, menu_rect)

    for block in menu_blocks:
        block.update()
        block.draw()

    # stop button
    screen.blit(stop_button, (menu_rect.width-40, 10))
    mask = pygame.mask.from_surface(stop_button)
    for event in events:
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            pos = (event.pos[0]-menu_rect.width+40, event.pos[1]-10)
            if Rect((0, 0), stop_button.get_size()).collidepoint(pos):
                if mask.get_at(pos):
                    for block in blocks:
                        block.master.running = False # stop everything
        

def draw_blocks():
    pygame.draw.rect(screen, grey, main_rect)

    for block in sorted(blocks, key=lambda block:-block.z):
        block.update() # can drag the front elements

    # draw the front element on top of the others, but order the drawing of the stacks
    # call sorted() twice because some blocks may be deleted in between
    blocks_to_draw = [block.index for block in sorted(blocks, key=lambda block:-block.z)]
    scheduled_total = []
    while blocks_to_draw:
        scheduled = [blocks_to_draw.pop()]
        next_ = find(scheduled[-1]).next_in_stack
        while next_:
            if next_ in blocks_to_draw: # not already put in a group
                blocks_to_draw.remove(next_)
            else: # already put in another group: remove it from there
                for group in scheduled_total:
                    if next_ in group:
                        group.remove(next_)
                        break
            scheduled.append(next_)
            next_ = find(scheduled[-1]).next_in_stack
        scheduled_total.append(scheduled)

    for group in scheduled_total:
        for index in group:
            find(index).draw()


WIDTH, HEIGHT = (900, 500)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Macro')
block_font = pygame.font.SysFont('consolas', 20)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

grey = (100, 100, 100)
menu_grey = (150, 150, 150)
black = (20, 20, 20)
white = (255, 255, 255)
yellow = (255, 255, 0)
green1 = (39, 171, 108) # normal
green2 = (29, 135, 82) # darker
icon = pygame.Surface((16, 16))
icon.fill(green1)
pygame.display.set_icon(icon)
del icon

red = [(251, 123, 133), (245, 20, 37), (208, 9, 23)]
stop_button = pygame.Surface((30, 30), SRCALPHA)
pygame.draw.polygon(stop_button, red[1], [(10, 0), (20, 0), (30, 10), (30, 20), (20, 30), (10, 30), (0, 20), (0, 10)])
pygame.draw.polygon(stop_button, red[0], [(10, 0), (20, 0), (20, 3), (12, 3), (3, 12), (3, 20), (0, 20), (0, 10)])
pygame.draw.polygon(stop_button, red[2], [(20, 30), (10, 30), (10, 27), (18, 27), (27, 18), (27, 10), (30, 10), (30, 20)])

menu_rect = Rect((0, 0), (WIDTH//3, HEIGHT))
main_rect = Rect((menu_rect.width, 0), (WIDTH-menu_rect.width, HEIGHT))

menu_blocks = []
blocks = []

menu_blocks.append(Block((0, 0), False, True, ['Wait', 1000, 'milliseconds'], 'sleep'))
menu_blocks.append(Block((0, 0), False, True, ['Move the mouse to x =', 0, ', y =', 0], 'set_mouse'))
menu_blocks.append(Block((0, 0), False, True, ['Move the mouse by x =', 0, ', y =', 0], 'move_mouse'))
menu_blocks.append(Block((0, 0), False, True, ['Press button', MouseEvent()], 'press_mouse'))

time_passed = [0]*100
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            blocks.append(Block((20, 20), 0, ['Hello world n°%d' %(len(blocks)+1)]))
        elif event.type == MOUSEWHEEL:
            if pygame.key.get_pressed()[K_LSHIFT] or pygame.key.get_pressed()[K_RSHIFT]:
                rel = (event.y*30, 0)
            else:
                rel = (0, event.y*30)
            for block in blocks:
                block.pos[0] += rel[0]
                block.pos[1] += rel[1]
                for element in block.elements: # move the inner elements as well
                    if type(element) != pygame.Surface:
                        element.rect.x += rel[0]
                        element.rect.y += rel[1]

    # cut the menu blocks if not in the menu or a block is being dragged
    draw_blocks()

    if sum(time_passed):
        FPS = '%d' %(100000/sum(time_passed))
    else:
        FPS = 'inf'
    screen.blit(block_font.render(FPS+' FPS', True, white), (menu_rect.width, 0))

    if menu_rect.collidepoint(pygame.mouse.get_pos()) and not True in [bool(block.dragged) for block in blocks]:
        draw_menu()
        pygame.display.flip()
    else:
        pygame.display.update(main_rect)
        draw_menu()
        pygame.display.update(menu_rect)

    time_passed.pop(0)
    time_passed.append(clock.tick())
