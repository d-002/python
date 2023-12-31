import socket
import os
import __help__

def get_user_command():
    command = input('%s> ' %(PATH)).split('"')
    words = []
    for x in range(len(command)):
        if x%2: # word in quotes
            words.append(command[x])
        else: # group of words
            words.extend(command[x].split(' '))

    words = [word for word in words if word] # remove empty words
    if len(words) > 1: # command and arguments
        return words[0], words[1:]
    elif len(words):
        return words[0], []
    return '', []

def view_url_content(*args):
    s.send(args[0].encode())
    print('Waiting...')
    try:
        size = int(server.recv(10).decode())
        s.send(b'ok') # tell to start sending the file
    except 1: # returned 'None', cannot convert into int
        print('Invalid url requested')
        return

    data = b''
    progress = 0
    print('Downloading file, size =', size)
    while len(data) < size:
        block = server.recv(32768)
        data += block
        percent = int(min(100, progress/size*32768*100))
        print('Downloading file... [' + '#'*int(percent/5) + '-'*int(20 - percent/5) + '] %d%%' %percent, end='\r')
        progress += 1
    print('Downloading file... Done' + ' '*23)
    print('\n----- Content of %s -----' %args[0])
    print(data)

def send_file(*args):
    path = args[0]
    if os.path.exists(path):
        size = os.path.getsize(path)
        print('File size: %do' %size)
        s.send(str(size).encode()) # send the size of the file
        server.recv(10) # wait for the server to process the information
        with open(path, 'rb') as f:
            block = f.read(32768)
            progress = 0
            while block:
                s.send(block)
                block = f.read(32768)
                percent = int(min(100, progress/size*32768*100))
                print('Sending to server... [' + '#'*int(percent/5) + '-'*int(20 - percent/5) + '] %d%%' %percent, end='\r')
                progress += 1
            print('Sending to server... Done' + ' '*23)
    else:
        print('File not found')

def download_internet_file(*args):
    s.send(args[0].encode())
    print('Waiting...')
    try:
        size = int(server.recv(10).decode())
        s.send(b'ok') # tell to start sending the file
    except: # returned 'None', cannot convert into int
        print('Invalid url requested')
        return

    data = b''
    progress = 0
    print('File size: %do' %size)
    while len(data) < size:
        block = server.recv(4096)
        data += block
        percent = int(min(100, progress/size*4096*100))
        print('Downloading file... [' + '#'*int(percent/5) + '-'*int(20 - percent/5) + '] %d%%' %percent, end='\r')
        progress += 1
    print('Downloading file... Done' + ' '*23)

    path = os.path.abspath(input('Enter a valid destination path: '))
    # make directories to path
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb') as f:
        f.write(data)
    print('File successully downloaded')

PATH = os.path.dirname(os.path.realpath(__file__))

s = socket.socket()
# the following 2 lines must be the same as server
ip = input('Server IP: ')
port = 12000

my_ip = input('Your IP, leave blank for auto-choose: ')
if not my_ip:
    my_ip = socket.gethostbyname(socket.gethostname())
my_port = 12001
my_s = socket.socket()
my_s.bind((my_ip, my_port))
my_s.listen(10)

s.connect((ip, port))
s.send(('%s %d' %(my_ip, my_port)).encode()) # tell where to send information back
server, addr = my_s.accept()
print('Server found:', addr, '\n')

try:
    while True:
        command, args = get_user_command()
        if command == 'exit':
            s.send(command.encode()) # make the server know about the type of request
            server.recv(10) # wait for the server to process the information
            exit()
        elif command == 'help':
            functions = __help__.get_globals()
            for key in functions.keys():
                print('Help on command %r:' %key)
                print(functions[key])
                print()
        elif command == 'ip':
            print('-'*24)
            print('Client IP:', my_ip)
            print('Client port:', my_port)
            print('\nServer IP:', ip)
            print('Server port:', port)
            print('-'*24)
        elif command == 'cd':
            if len(args):
                if os.path.exists(args[0]):
                    PATH = args[0]
                else:
                    print('Path does not exist')
            else:
                PATH = os.path.dirname(PATH) # go to parent directory
        elif command == 'set_admin':
            s.send(command.encode()) # make the server know about the type of request
            server.recv(10) # wait for the server to process the information
            print('Requesting...')
            if server.recv(1024) == b'accepted':
                print('Request accepted.')
            else:
                print('Request refused.')
        elif command == 'stop_server':
            s.send(command.encode()) # make the server know about the type of request
            server.recv(10) # needed because of how the server side is managed
            s.send(b'ok')   #
            if server.recv(1024) == b'succeeded':
                exit()
            else:
                print('Refused.')
        elif len(args):
            s.send(command.encode()) # make the server know about the type of request
            server.recv(10) # wait for the server to process the information
            if command == 'view_url':
                view_url_content(*args)
            elif command == 'download_url':
                download_internet_file(*args)
            elif command == 'send_file':
                send_file(*args)
            elif command == 'msg':
                message = ''
                for arg in args:
                    message += arg + ' '
                s.send(message[:-1].encode())
        else:
            print('Unknown command')
except ConnectionResetError:
    pass
except ConnectionAbortedError:
    pass
except BrokenPipeError:
    pass
input('Connection lost. Press Enter to quit')
