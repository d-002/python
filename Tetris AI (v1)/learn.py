import time
import random
from threading import Thread
from tkinter import *
from main import * # file

def stop():
    global running
    running = False

def update_param_texts():
    for x in range(n_params):
        param_texts[x]['text'] = '%s: %.3f' %(parameters[x].__name__, in_range(x, 0.5))

def gui():
    global param_texts, score_text
    tk = Tk()
    tk.title('Control panel')
    param_texts = []
    for x in range(n_params):
        param_texts.append(Label())
        param_texts[-1].grid(sticky='w', pady=(5,0))
    score_text = Label()
    score_text.grid(sticky='w', pady=(10, 0))
    Button(text='Stop', width=15, command=stop).grid(pady=5)
    update_param_texts()
    tk.mainloop()

def in_range(param, x):
    return ranges[param][0] + x * (ranges[param][1]-ranges[param][0])

def launched(index, params): # in a thread
    global threads_done
    try:
        score = from_learn_file(params)
    except:
        print('Error')
        score = 0
    threads_done[index] = score

def launch(param, where): # where in the parameter range
    global threads_done
    threads_done = [None for x in range(n_samples)]
    params = [in_range(x, 0.5) for x in range(n_params)]
    params[param] = in_range(param, where)

    for x in range(n_samples):
        Thread(target=lambda: launched(x, params)).start()
        time.sleep(0.1)
    while None in threads_done:
        time.sleep(5)
    if where == 0.5:
        score_text['text'] = 'Average score: %.3f' %(sum(threads_done)/n_samples)
    return sum(threads_done)/n_samples

parameters = Ai().parameters[:]
n_params = len(parameters)
n_gens = 1000
n_samples = 20
ranges = []
minimaxi = []
for x in range(n_params):
    ranges.append([Ai().multipliers[x]-1, Ai().multipliers[x]+1])
    if Ai().good[x]: # specify if a parameter is good or bad
        minimaxi.append([0, None])
    else:
        minimaxi.append([None, 0])
ranges = [0.359, 4.725, 3.75, 1.375, 1.938, 6.75, 5.562]
for x in range(n_params):
    ranges[x] = [ranges[x]-0.5, ranges[x]+0.5]

Thread(target=gui).start()
time.sleep(1)

running = True

for gen in range(n_gens):
    if not running:
        break
    for param in range(n_params):
        if not running:
            break
        sample0, sample1, sample2 = [launch(param, x) for x in [0.25, 0.5, 0.75]]
        size = ranges[param][1]-ranges[param][0]
        if sample0 < sample1 > sample2: # range found, narrow it down
            if size > 0.01:
                ranges[param] = [in_range(param, 0.25), in_range(param, 0.75)]
        else: # the best value is outside of the range
            add = 0
            if sample0 < sample1:
                if minimaxi[param][0] is None:
                    add = -size/2
                else:
                    add = min(-ranges[param][0], -size/2)
            elif sample2 < sample1:
                if minimaxi[param][1] is None:
                    add = size/2
                else:
                    add = min(-ranges[param][1], size/2)
            ranges[param][0] += add
            ranges[param][1] += add
        update_param_texts()
    print('Generation', gen+1, 'done.')

print('\nDone\nParameters:')
for param in range(n_params):
    print(parameters[param].__name__, in_range(param, 0.5))
