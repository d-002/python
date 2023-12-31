#!/usr/bin/python3

"""TODO
support < and > inside of strings (use json)
fix encoding issues
"""

import os
import json
import colorama
from colorama import *
from urllib.request import *

colorama.init(autoreset=True)

def _to_tree(text, n=0): # recursive
  print('Formatting... Discovered %d elements' %n, end='\r')

  tree = [] # pairs: [tag, content] where content can be another list
  while '<' in text and '>' in text:
    index = text.find('<')
    if len(text[:index].strip()): # text before?
      tree.append(['UNDEFINED', text[:index].strip()])
      n += 1
      text = text[index:]

    tag = text.split('<')[1].split('>')[0].split(' ')[0]
    # find content and end of tag
    index = text.find('</%s>' %tag)
    if index == -1:
      text = text[text.find('>')+1:]
      continue # avoid reading e.g. <!DOCTYPE html>

    content = text[text.find('>')+1:index]
    if tag not in ['style', 'script']:
      content, n = _to_tree(content, n)
      tree.append([tag, content])

    text = (text[:text.find('<')] + text[index+len(tag)+3:]).strip()

  # if no more tags, add the text inside if present
  if len(text.strip()):
    if len(tree): # edge case where some text without tag is next to a tag
                  # note: in case some text exists before the tags, it will be skipped by above code
      tree.append(['UNDEFINED', text.strip()])
      n += 1
    else:
      tree = text.strip()

  return tree, n+1

def _format(tree, indent=0, operations_done=1, operations=0): # recursive
  _text = ''
  def display(text, end='\n'):
    return ' '*indent*4 + text + end # this needs to be added to _text

  if not indent: # called from outside, not recursively
    tree, operations = _to_tree(tree.strip().replace('\n', '').replace('\t', ''))
    print(' '*100, end='\r') # clear the text printed by to_tree
    tree = tree[0]

  percent = 100*operations_done/operations
  print('Formatting... [%s%s%s%s] - %d%%)' %(Fore.LIGHTWHITE_EX, '#'*int(percent/5), Fore.WHITE, '-'*int(20 - percent/5), percent), end='\r')

  tag, content = tree
  if type(content) == list:
    for obj in content:
      # avoid indenting too much at once
      while len(content) == 1:
        content = content[0]
      add, operations_done = _format(obj, indent+1, operations_done, operations)
      if add.strip().replace('\n', ''):
        _text += add+'\n'
  else:
      if tag in ['img', 'script', 'style', 'option']:
        pass
      elif tag in ['div', 'p', 'span', 'text', 'u', 'tr', 'td', 'label']:
        _text += display(content)
      elif tag in ['b', 'strong', 'em', 'i']:
        _text += display(Fore.LIGHTWHITE_EX+content+Fore.WHITE, end='')
      elif tag == 'a':
        _text += display(Fore.LIGHTBLUE_EX+content+Fore.WHITE, end='')
      elif tag == 'li':
        _text += display('- '+content)
      elif tag == 'title':
        _text += display(' '*100 + content, end='\n\n\n')
      elif len(tag) == 2 and tag[0] == 'h':
        level = int(tag[1])+1
        if level < 3:
          content = content.upper()
        _text += display('-'*(28 - 4*level) + '  ' + content, end='\n\n')
      elif tag == 'code':
          _text += display(content, end='')
      elif tag in ['kbd', 'button']:
          _text += display(Fore.BLACK+Back.WHITE+content+Fore.WHITE+Back.BLACK)

      elif tag == 'UNDEFINED':
        _text += display(content, end='')

      else:
        _text += display('%s<%s>%s</%s>%s' %(Back.RED, tag, content, tag, Back.BLACK))

  operations_done += 1
  if indent:
    return _text, operations_done
  print('Formatting... %sDone' %Fore.LIGHTGREEN_EX, ' '*100)
  return _text

def _save(text, path):
  output = os.path.abspath(path)
  print('Saving to: %s... ' %path, end='')
  dir = os.path.abspath(os.path.dirname(path))
  if not os.path.exists(dir):
    print(Fore.YELLOW+'Creating unexisting folder(s)... ', end='')
    os.makedirs(dir)
  with open(path, 'w') as f:
      f.write(text)
  print(Fore.LIGHTGREEN_EX+'Done')

def urlopen_auto_protocol(url):
  if url.startswith('http://') or url.startswith('https://'):
    with urlopen(url) as f:
      content = f.read()
    return decode(content)

  try: # check https:// first, then http://
    with urlopen('https://'+url) as f:
      content = f.read()
      add = 'https://'
  except:
    with urlopen('http://'+url) as f:
      content = f.read()
      add = 'http://'
  print('%sEdited url to: %s%s' %(Fore.YELLOW, add, url))
  return decode(content)

def display_interactive(text, blocksize=58):
  text = text.split('\n')
  max_y = len(text)
  for y in range(max_y):
    if not y%blocksize: # split the text in blocks
      if y:
        if input() == 'q':
          return # stop displaying at any time
      else:
        input('Press Enter to show url content')
    print(text[y])
  input('[END]')

def decode(bytes):
  try:
    return bytes.decode('cp1252')
  except:
    print('Error occured while decoding, manual decoding... ', end='')
    text = ''
    for char in bytes:
      text += chr(char)
    return text

def view(url=None, output=False): # if output, save to a file (in binary form)
  if url is None:
    url = input('Enter url: ')
  if output and type(output) == bool: # output can either be: False, True, 'path'
    output = input('Enter destination file: ')
  print('Requesting... ', end='')
  try:
    content = urlopen_auto_protocol(url)
  except Exception as e:
    print(Fore.RED+'\nAn error occured. Error:')
    print(Fore.RED+str(e))
    return
  print(Fore.LIGHTGREEN_EX+'Done')
  text = _format(content)

  if output:
    _save(text, output)
  else:
    display_interactive(text)
  print()

def search(search=None, output=False): # if output, save to file (in binary form)
  if search is None:
    search = input('Enter search: ')
  search = search.replace(' ', '+') # format search

  addr = 'https://www.duckduckgo.com/html/search?q=%s' %search
  print('Address:', addr)
  return view(addr, output)

if __name__ == '__main__':
  # display logo
  colors = (Fore.GREEN, Fore.LIGHTWHITE_EX)
  print()
  print( "%s   ____        %s __      __             __     " %colors)
  print(r"%s /      \ .--. %s|  | __ |  |           |  |    " %colors)
  print( "%s|  .--.  |`--' %s|  ||  ||  |   _____   |  |    " %colors)
  print( "%s|  |__|  |.--. %s|  ||  ||  |  /  __ `\ |  |___ " %colors)
  print( "%s|   ____/ |  | %s|  ||  ||  | |  |__/ | |   _  |" %colors)
  print( "%s|  |      |  | %s|  ||  ||  | |  ___./  |  | | |" %colors)
  print( "%s|  |      |  | %s|  `'  `'  | |  \---.  |  `-' |" %colors)
  print(r"%s`--'      `--' %s`----------'  `-----'   \-----'" %colors)
  print()
  print(   "                when Mozillan't and Operout")
  print()
  print()

  vars = {'to_file' : False}
  vars_str = {'to_file': 'Save to file'}

  while True:
    print()
    print(Fore.LIGHTWHITE_EX+'Enter action code:')
    print('  1 - Search %sduckduckgo.com' %Fore.LIGHTBLUE_EX)
    print('  2 - View webpage')
    print('  3 - View raw webpage')
    print('  4 - Change settings')
    print('  5 - Exit program')
    try:
      request = int(input('>>> '))
      print()
    except:
      print(Fore.RED+'Invalid entry')
      continue
    if request == 1:
      search(None, vars['to_file'])
    elif request == 2:
      view(None, vars['to_file'])
    elif request == 3:
      url = input('Enter url: ')
      if vars['to_file']:
        path = input('Enter destination file: ')
      try:
        content = urlopen_auto_protocol(url)
      except Exception as e:
        print(Fore.RED+'\nAn error occured. Error:')
        print(Fore.RED+str(e))
        continue
      if vars['to_file']:
        _save(content, path)
      else:
        display_interactive(content)

    elif request == 4:
      print(Fore.LIGHTWHITE_EX+'Enter setting code to change it:')
      print('  0 --- Back to menu')
      x = 1
      for var, value in vars.items():
        print('  %d  -  %s: %s%s' %(x, vars_str[var], Fore.LIGHTMAGENTA_EX, value))
        x += 1
      try:
        request = int(input('>>> '))
        print()
      except:
        print(Fore.RED+'Invalid entry')
        continue
      if not request:
        continue # requested 0 to go back
      x = 1
      valid = False
      for var in vars:
        if request == x:
          if var == 'auto_protocol':
            set_auto_protocol(not vars[var])
          vars[var] = not vars[var]
          print('"%s" is now set to: %s%s' %(vars_str[var], Fore.LIGHTMAGENTA_EX, vars[var]))
          valid = True
          break
        x += 1

      if not valid:
        print(Fore.RED+'Invalid entry')

    elif request == 5:
      exit()
    else:
      print(Fore.RED+'Invalid entry')
