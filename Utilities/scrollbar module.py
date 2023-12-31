class ScrollBar:
    def __init__(self, master=None, mode='copy', **args):
        """
    |
    * master is by default None. Leaving this empty will make a
    | new tkinter window when griding or packing it.
    |
    * mode is set by default to 'copy'.
    |    |
    |    | mode = 'copy'  -> print 'Copying n files from source to
    |    |                          destination...'
    |    | mode = 'move'   -> print 'Moving n files from source to
    |    |                          destination...'
    |    | mode = 'delete -> print 'Deleting n files from source...'
    |
    * args:
    |    |
    |    * definitions:
    |    |    |
    |    |    | width:     width of the green area
    |    |    | height:    height of the green area
    |    |    |
    |    |    | value:     value printed on screen
    |    |    | value_min: minimum value of the bar
    |    |    | value_max: maximum value of the bar
    |    |    | 
    |    |    | speed:     speed (in octets) of copying/moving/deleting
    |    |    | zoom:      zoom (from 0 to
    |    |    |                  height / zoom octets
    |    |    |                  in the top of the bar)
    |    |    | title:     title of the window (if master == None)
    |    |    |
    |    |    | name:      current name of the copied file
    |    |    | time:      time remaining
    |    |    | elements:  remaining elements (list or int)
    |    |    | index:     element[index] will be printed
    |    |    |            (if elements is a list)
    |    |    | size:      total size of remaining elements
    |    |    |            (automatically calculed if elements is a list)
    |    |
    |    * default values:
    |    |    |
    |    |    | width:     395
    |    |    | height:    80
    |    |    |
    |    |    | value:     value_min
    |    |    | value_max: 100 # taller difference: better resolution
    |    |    | value_min: 0   #                    but slower
    |    |    |
    |    |    | speed:     0
    |    |    | zoom:      1   # auto adjusting
    |    |    | title:     'Loading...'
    |    |    |
    |    |    | name:      None -> 'Name: ...' not appearing if left None
    |    |    | time:      None -> automatically calculed if left None,
    |    |    |                    not appearing if elements is left None
    |    |    | elements:  None -> 'Elements remaining: ...'
    |    |    |                    not appearing if left None
    |    |    | index:     0
    |    |    | size:      None -> automatically calculed if left None,
    |    |    |                    not appearing if elements is left None
    |
    * errors:
    |   |
    |   | mode != 'copy' and mode != 'move' and mode != 'delete'
    |   |  -> TypeError
    |   | unknown argument in __init__
    |   |  -> TypeError
    
"""
        self.width = 395
        self.height = 80
        self.value_max = 100
        self.value_min = 0
        self.value = self.value_min
        self.speed = 0
        self.speeds = []
        self.zoom = 1
        self.master = master
        self.title = 'Loading...'
        self.mode = mode
        self.name = None
        self.time = None
        self.time_auto_calculed = False
        self.elements = None
        self.index = 0
        self.size = None
        self.size_auto_calculed = False
        self.source = None
        self.destination = None
        if mode != 'copy' and mode != 'move' and mode != 'delete':
            raise TypeError("mode must be 'copy', 'move' or 'delete', not %s" % mode)
        for arg in args:
            if arg == 'width':
                self.width = int(args['width'])
            elif arg == 'height':
                self.height = int(args['height'])
            elif arg == 'value':
                self.value = int(args['value'])
            elif arg == 'value_max':
                self.value_max = int(args['value_max'])
            elif arg == 'value_min':
                self.value_min = int(args['value_min'])
            elif arg == 'speed':
                self.speed = int(args['speed'])
            elif arg == 'zoom':
                self.zoom = int(args['zoom'])
            elif arg == 'title':
                self.title = str(args['title'])
            elif arg == 'name':
                self.name = int(args['name'])
            elif arg == 'time':
                self.time = int(args['time'])
            elif arg == 'elements':
                self.elements = args['elements']
                self.elements_start = self.elements
            elif arg == 'index':
                self.index = int(args['index'])
            elif arg == 'size':
                self.size = int(args['size'])
            elif arg == 'source':
                self.source = str(args['source'])
            elif arg == 'destination':
                self.destination = str(args['destination'])
            else:
                raise TypeError('**args of ScrollBar.__init__() must be width, height, value, value_max, value_min, speed, zoom or title, not %s' % arg)
        if self.time is None:
            self.time_auto_calculed = True
        if self.size is None:
            self.size_auto_calculed = True
        if type(self.elements) != list and type(self.elements) != int and self.elements is not None:
            raise TypeError("elements must be <class 'NoneType'>, <class 'list'> or <class 'int'>, not %s" % type(self.elements))

    def _draw(self):
        import tkinter as tk
        if self.master is None:
            self.master = tk.Tk()
            self.master.title(self.title)
        self.canvas = tk.Canvas(self.master, width=40 + self.width, height=170 + self.height, background='white', highlightthickness=0)
        self.canvas.create_rectangle(0, 0, 39 + self.width, 169 + self.height, fill='', outline='#cccccc') # edge
        self.canvas.create_rectangle(0, 125 + self.height, 39 + self.width, 169 + self.height, fill='#fdfdfd', outline='#cccccc') # bottom
        self.canvas.create_oval(20, 137 + self.height, 40, 157 + self.height, outline='#bbbbbb') #
        self.canvas.create_line(25, 148 + self.height, 30, 143 + self.height, fill='#bbbbbb')    # up arrow
        self.canvas.create_line(35, 149 + self.height, 29, 143 + self.height, fill='#bbbbbb')    #
        self.canvas.create_text(45, 147 + self.height, text='Less details', anchor='w')
        self._print_top()
        self._redraw()

    def _print_top(self):
        if self.mode == 'copy' or self.mode == 'move':
            if self.mode == 'copy':
                mode = 'Copying'
            else:
                mode = 'Moving'
            if type(self.elements_start) == list:
                elements = str(len(self.elements_start)) + ' '
            elif type(self.elements_start) == int:
                elements = str(self.elements_start) + ' '
            elif self.elements_start is None:
                elements = ''
            else:
                raise TypeError("Do not modify system vars")
            if self.source is not None:
                if self.destination is not None:
                    self.canvas.create_text(25, 30, text='%s %sfiles from %s to %s' %(mode, elements, self.source, self.destination), anchor='sw')
                else:
                    self.canvas.create_text(25, 30, text='%s %sfiles from %s' % (mode, elements, self.source), anchor='sw')
            else:
                if self.destination is not None:
                    self.canvas.create_text(25, 30, text='%s %sfiles to %s' % (mode, elements, self.destination), anchor='sw')
                else:
                    self.canvas.create_text(25, 30, text='%s %sfiles' % (mode, elements), anchor='sw')
        elif self.mode == 'delete':
            if type(self.elements) == list:
                elements = str(len(self.elements)) + ' '
            elif type(self.elements) == int:
                elements = str(self.elements) + ' '
            elif self.elements is None:
                elements = ''
            else:
                raise TypeError("elements must be <class 'NoneType'>, <class 'list'> or <class 'int'>, not %s" % type(elements))
            if self.destination is not None:
                raise TypeError('In deleting mode, no need destination')
            else:
                if self.source is not None:
                    self.canvas.create_text(25, 30, text='Deleting %sfiles from %s' % (elements, self.destination), anchor='sw')
                else:
                    self.canvas.create_text(25, 30, text='Deleting %sfiles' % elements, anchor='sw')
        
    def _redraw(self):
        try:
            if max(self.speeds) > 0.7 * self.height / self.zoom:
                self.zoom = 1 / max(self.speeds) * self.height * 0.7
                self.canvas.create_rectangle(0, 0, 40 + self.width, 120 + self.height, fill='white', outline='') # fill blank for correction
                self._print_top()
        except:
            pass
        self.width = int(self.width)
        self.height = int(self.height)
        self.speeds.append(self.speed)
        self.canvas.create_rectangle(20, 90 + self.height, 40 + self.width, 120 + self.height, fill='white', outline='') # fill blank for correction
        self.canvas.create_rectangle(19, 59, 21 + self.width, 61 + self.height, outline='#cccccc')               # edge
        self.canvas.create_rectangle(20, 60, 20 + self.width, 60 + self.height, fill='white', outline='#cccccc') #
        self.canvas.create_rectangle(20, 30, 200, 55, fill='white', outline='')
        self.canvas.create_text(25, 50, text='%d%% completed' % (100 * self.value / (self.value_max - self.value_min)), anchor='sw', font=('helvetica', 12))
        if self.name is not None:
            self.canvas.create_text(30, 78 + self.height, text='Name:  %s' %self.name, anchor='w')
        if self.time is not None:
            self.canvas.create_text(30, 93 + self.height, text='Time remaining:  %s' %self.time, anchor='w')
        if self.elements is not None:
            if type(self.elements) == list:
                elements = self.elements[self.index]
            elif type(self.elements) == int:
                elements = self.elements
            elif self.elements is not None:
                raise TypeError('elements must be list or int, not %s' % type(elements))
            self.canvas.create_text(30, 109 + self.height, text='Elements remaining:  %s' %elements, anchor='w')
        if self.value * self.width / (self.value_max - self.value_min) > 22:
            self.canvas.create_rectangle(22, 62, 20 + int(self.value * self.width / (self.value_max - self.value_min)), 59 + self.height, fill='#aaff99', outline='') # green rectangle in the background
        for y in range(15, self.height, 15):                                                                            # lines -
            self.canvas.create_line(22, 60 + self.height - y, self.width + 18, 60 + self.height - y, fill='#a9e490')    #
        for x in range(20 + int(self.width / 10), 20 + self.width, int(self.width / 10)):                               # lines |
            self.canvas.create_line(x, 62, x, 58 + self.height, fill='#aaddaa')                                         #
        self.canvas.create_line(22, 59 + self.height - self.speed * self.zoom, 18 + self.width, 59 + self.height - self.speed * self.zoom)
        if self.speed < 2**10:
            text = 'Speed : %so per second' % int(self.speed)
        elif self.speed < 2**20:
            text = 'Speed : %.2f ko per second' % (self.speed / 10**3)
        elif self.speed < 2**30:
            text = 'Speed : %.2f Mo per second' % (self.speed / 10**6)
        else:
            text = 'Speed : %.2f Go per second' % (self.speed / 10**9)
        self.canvas.create_text(self.width + 10, 55 + self.height - self.speed * self.zoom, text=text, anchor='se')
        for x in range(self.value_max - self.value_min):
            length = self.width / (self.value_max - self.value_min)
            if 20 + int(x * self.width / (self.value_max - self.value_min) - 2 * length - 1) < 20:
                length = 0
            try:
                self.canvas.create_rectangle(20 + int(x * self.width / (self.value_max - self.value_min) - 2 * length - 1),
                                             60 + self.height - self.speeds[x] * self.zoom,
                                             20 + int(x * self.width / (self.value_max - self.value_min) - length - 1),
                                             59 + self.height,
                                             fill='#04b026', outline='')
            except:
                pass
        if self.value == self.value_max:
                self.canvas.create_rectangle(20 + int(x * self.width / (self.value_max - self.value_min) - length - 1),
                                             60 + self.height - self.speeds[x] * self.zoom,
                                             20 + int(x * self.width / (self.value_max - self.value_min) + length),
                                             59 + self.height,
                                             fill='#04b026', outline='')
        self.master.update()
        
    def pack(self, **args):
        """
    |
    | ScrollBar.pack(self, **args) is equivalent to
    | any_tkinter_widget.pack(**args)."""
        self._draw()
        self.canvas.pack(args)
        self.update()

    def grid(self, **args):
        """
    |
    | ScrollBar.grid(self, **args) is equivalent to
    | any_tkinter_widget.grid(**args)."""
        self._draw()
        self.canvas.grid(args)
        self.update()
    
    def update(self):
        """
    |
    | ScrollBar.update(self) redraws the scroll bar."""
        if self.master is None:
            raise AttributeError('You must pack or grid the scroll bar.')
        else:
            self._redraw()

    def reset(self):
        """
    |
    | ScrollBar.reset(self) puts the value to
    | the minimum value and redraws the bar."""
        self.value = self.value_min
        self._redraw()


help(ScrollBar)

bar = ScrollBar(value_max = 100, elements=54685, source='L:\\', destination='D:\\')
bar.pack()

while bar.value < bar.value_max:
    bar.value += 1
    bar.speed = bar.value / 2 + 10
    bar.update()
