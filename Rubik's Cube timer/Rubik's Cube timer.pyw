import time
import random
import pygame
from pygame.locals import *

class Hands:
    def __init__(self):
        hand = pygame.image.load('files\\hand.png')
        w, h = hand.get_size()
        size = max(w, h) + 20
        self.images = []
        for image in range(3):
            surface = pygame.Surface((size, size), SRCALPHA)
            color = [(255, 50, 0), (255, 220, 0), (0, 210, 10)][image]
            pygame.draw.circle(surface, color, (size//2, size//2), size//2)
            surface.blit(hand, ((size-w) // 2, (size-h) // 2))
            self.images.append(surface)

        self.start_press = None

    def update(self, events):
        global running

        if self.start_press:
            if time.time() - self.start_press >= 0.5:
                state = 2
            else:
                state = 0
        else:
            state = 1
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.start_press = time.time()
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    if running: # no need to wait when stopping
                        running = False
                        times.add_time()
                        scramble.new_scramble()
                    elif self.start_press and time.time() - self.start_press >= 0.5:
                        running = True
                    self.start_press = None
            
        for x in range(2):
            if x:
                image = self.images[state]
            else:
                image = pygame.transform.flip(self.images[state], 1, 0)
            w, h = image.get_size()
            x, y = 200 + 500*x - w//2, 180 - h//2
            screen.blit(image, (x, y))

class Timer:
    def __init__(self):
        self.start = 0
        self.time = 0
        self.font = pygame.font.Font('files\\font.ttf', 50)

    def update(self):
        if hardware:
            self.time = entry_float
        else:
            if running:
                self.time = time.time() - self.start
            else:
                self.start = time.time()
                self.time = 0

        text = self.font.render(to_string(self.time), 1, (200, 200, 200))

        w, h = text.get_size()
        screen.blit(text, (450 - w//2, 180 - h//2))

class Scramble:
    def __init__(self):
        self.moves = [['F'], ['L', 'R'], ['U', 'D']]
        self.add = [' ', "' ", '2 ']
        self.previous = self.scramble = 'None'
        self.new_scramble()
        self.font = pygame.font.SysFont('Consolas', 30)
        self.font_little = pygame.font.SysFont('Consolas', 15)

    def new_scramble(self):
        self.previous, self.scramble = self.scramble, ''
        last_moves = []
        for x in range(scramble_length):
            # cannot move the same face twice
            moves = [move for group in self.moves for move in group if move not in last_moves]
            move = random.choice(moves)
            # new move is a move in another group
            if last_moves and [move in group for group in self.moves].index(True) != [last_moves[0] in group for group in self.moves].index(True):
                last_moves = [] # reset which face is forbidden
            self.scramble += move + random.choice(self.add)
            last_moves.append(move)
        self.scramble = self.scramble[:-1]

    def update(self):
        y = 5
        for scramble, font, header in [(self.scramble, self.font, ''), (self.previous, self.font_little, 'Previous: ')]:
            words = scramble.split(' ')
            line = ''
            while words:
                line += words.pop(0) + ' ' # add word by word
                if len(words): # check the size of the text before adding an extra word
                    next_width = font.render(words[0], 1, (200, 200, 200)).get_width()
                else:
                    next_width = 0
                text = font.render(header + line, 1, (200, 200, 200))
                if text.get_width() + next_width > 890:
                    screen.blit(text, (5, y))
                    y += text.get_height()
                    line = ''
                    text = pygame.Surface((0, 0))
            if text.get_width():
                screen.blit(text, (5, y)) # add the last line
                y += 30
            y += 5

class Times:
    def __init__(self):
        self.times = []
        self.font = pygame.font.SysFont('Consolas', 20)
        self.do_save = True # do you want to update the save file?
        self.load()

    def add_time(self):
        if hardware:
            time = entry_float
        else:
            time = timer.time
        self.times.append([time, False, False])

        # update pb
        if time < self.pb: # self.pb is set to 3600 when resetting
            self.pb = time

        self.save() # update the changes to the save file

    def display_times(self):
        pygame.draw.rect(screen, (50, 50, 50), Rect((5, 285), (160, 210)))
        index = len(self.times)-1
        for y in range(470, 270, -20):
            if index < 0:
                break # reached end of times
            text = self.font.render(to_string(self.times[index][0]), 1, (200, 200, 200))
            if self.times[index][1]:
                screen.blit(self.font.render(' +2', 1, (255, 50, 50)), (10 + text.get_width(), y))
            if self.times[index][2]:
                screen.blit(self.font.render(' DNF', 1, (100, 100, 200)), (10 + text.get_width(), y))
            screen.blit(text, (10, y))
            index -= 1

    def display_analytics(self):
        pygame.draw.rect(screen, (50, 50, 50), Rect((170, 285), (200, 210)))
        if len(self.real_times):
            mean = sum(self.real_times)/len(self.real_times)
            average = ao5 = ao12 = None
            if len(self.real_times) >= 3:
                average = sum(sorted(self.real_times)[1:-1]) / (len(self.real_times)-2)
            if len(self.real_times) >= 5:
                ao5 = sum(self.real_times[-5:]) / 5
            if len(self.real_times) >= 12:
                ao12 = sum(self.real_times[-12:]) / 12
            texts = ['BestOf 12: %s', 'WorstOf12: %s', 'PB: %s', 'Mean: %s', 'Average: %s', 'Av. of 5: %s', 'Av. of 12: %s']
            values = [min(self.real_times[-12:]), max(self.real_times[-12:]), times.pb, mean, average, ao5, ao12]
            for y in range(len(texts)):
                screen.blit(self.font.render(texts[y] %to_string(values[y]), 1, (200, 200, 200)), (175, 290 + 20*y))
            screen.blit(self.font.render('Times: %d' %len(self.real_times), 1, (200, 200, 200)), (175, 310 + 20*y))

    def display_graph(self):
        graph_rect = Rect((375, 285), (200, 210))
        pygame.draw.rect(screen, (150, 150, 150), graph_rect)

        times_float = self.real_times[:]
        if len(times_float) > 50:
            times_float = times_float[-50:]
        if len(times_float):
            scaleX = (graph_rect.width-20) / len(times_float)
            if min(times_float) == max(times_float):
                scaleY = 1
            else:
                scaleY = (graph_rect.height-100) / (max(times_float)-min(times_float))
            for x in range(len(times_float)):
                pos1 = (graph_rect.left + 10 + scaleX*x, graph_rect.bottom - 50 - (times_float[x]-min(times_float))*scaleY)
                pygame.draw.circle(screen, (255, 50, 50), (pos1[0], pos1[1]+1), 4)
                if x < len(times_float) - 1:
                    pos2 = (graph_rect.left + 10 + scaleX*(x+1), graph_rect.bottom - 50 - (times_float[x+1]-min(times_float))*scaleY)
                    pygame.draw.aaline(screen, (255, 50, 50), pos1, pos2)

    def update(self):
        self.real_times = [time + add*2 for time, add, counts in self.times if not counts]
        if len(self.real_times) > 200:
            self.real_times = self.real_times[-200:] # only care about the last times
        self.display_times()
        self.display_analytics()
        self.display_graph()

    def save(self):
        if self.do_save:
            with open('files\\save.txt', 'w') as f:
                for time in self.times:
                    f.write('%.3f %s %s\n' %(time[0], int(time[1]), int(time[2])))
            with open('files\\pb.txt', 'w') as f:
                f.write('%.3f' %self.pb)

    def load(self):
        self.times = []
        with open('files\\save.txt') as f:
            for line in f.read().split('\n'):
                if line:
                    time, add, dnf = line.split(' ')
                    self.times.append([float(time), int(add), int(dnf)])
        with open('files\\pb.txt') as f:
            self.pb = float(f.read())

def button(text, pos, events, color=(200, 200, 200)):
    return_ = False

    text = buttonfont.render(text, 1, color)
    w, h = text.get_size()
    W, H = max(100, w+10), h+10
    rect = Rect(pos, (W, H))

    for event in events:
        if event.type == MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                return_ = True

    if rect.collidepoint(pygame.mouse.get_pos()):
        color = (70, 70, 70)
    else:
        color = (50, 50, 50)
    pygame.draw.rect(screen, color, rect)
    screen.blit(text, (rect.left - w//2 + W//2, rect.top - h//2 + H//2))

    return return_

def to_string(time):
    if time is None:
        return 'None'

    min, sec = time//60, time%60
    decimal = ( '%.3f' %((time-int(time))) ) [2:]
    sec = '%d' %sec
    if min:
        if len(sec) < 2: # add a 0
            sec = '0'+sec
        text = '%d:%s.%s' %(min, sec, decimal)
    else:
        text = '%s.%s' %(sec, decimal)
    return text

hardware = False
scramble_length = 20

pygame.init()
pygame.display.set_caption("Rubik's Cube timer")
screen = pygame.display.set_mode((900, 500))
buttonfont = pygame.font.SysFont('Consolas', 20)

scramble = Scramble()
times = Times()

# hardware
entry = ''
entry_float = 0
# not hardware
running = False
hands = Hands()
timer = Timer()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()

    screen.fill((20, 20, 20))

    scramble.update()
    if hardware:
        # enter time with keyboard, store with Enter
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_RETURN and entry_float:
                    times.add_time()
                    scramble.new_scramble()
                    entry = ''
                elif event.key == K_BACKSPACE:
                    entry = entry[:-1]
                elif event.unicode in ':.' or event.unicode in [str(x) for x in range(10)]:
                    if not True in [event.unicode == char and char in entry for char in ':.']:
                        entry += event.unicode
                if len(entry.split(':')) == 2:
                    min_, sec = entry.split(':') # min_ instead of min because global
                    entry_float = float(min_)*60 # why preventing from entering floating point minutes? :)
                    if sec:
                        entry_float += float(sec)
                elif len(entry):
                    entry_float = float(entry)
                else:
                    entry_float = 0
    else:
        hands.update(events)
    timer.update()
    times.update()

    #if button('Reset', (600, 300), events):
    #    times.times = []
    #    times.pb = 3600
    if button('Saving: %s' %times.do_save, (720, 300), events):
        times.do_save = not times.do_save

    if hardware:
        text = 'Time from IRL timer'
    else:
        text = 'Press Space to time'
    screen.blit(buttonfont.render(text, 1, (200, 200, 200)), (600, 350))
    if button('Toggle', (600, 380), events):
        hardware = not hardware
        if running: # stop the timer if necessary
            running = False
            times.add_time()
            scramble.new_scramble()

    if len(times.times):
        screen.blit(buttonfont.render('Last time:', 1, (200, 200, 200)), (600, 420))
        last_time = times.times[-1]
        if last_time[1]:
            color = (255, 50, 50)
        else:
            color = (200, 200, 200)
        if button('+2', (600, 450), events, color):
            last_time[1] = not last_time[1]
            last_time[2] = False
        if last_time[2]:
            color = (100, 100, 200)
        else:
            color = (200, 200, 200)
        if button('DNF', (720, 450), events, color):
            last_time[1] = False
            last_time[2] = not last_time[2]

    pygame.display.flip()
