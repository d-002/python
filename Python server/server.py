import socket, os, time, sys
from urllib.request import *
from urllib.error import *
from threading import Thread

def waiting():
    global clients
    print('Server started:', (ip, port))
    print('Waiting for clients to join')
    while running:
        try:
            client, addr = s.accept()
            client_ip, client_port = client.recv(100).decode().split(' ')
            client_port = int(client_port)
            client_socket = socket.socket()
            print('Client info (trying to connect):', (client_ip, client_port))
            client_socket.connect((client_ip, client_port)) # where to send information back
            clients.append((client, client_socket))
            print('\n----- New client connected -----')
            print('Client ADDR:', addr)
            print('Client info:', client)
            print('Waiting for new request\n')
        except ConnectionResetError:
            print('Client disconnected before complete connection')

def send_url_content():
    url = client.recv(1024).decode()
    print('Requested url:', url)
    try:
        data = urlopen(url).read()
        size = len(data) # get and send the size of the file
        client_socket.send(str(size).encode())
        client.recv(10) # wait for the client to process the information
        print('File size: %do' %size.decode())
        if size >= 32768:
            block = data[0:32768]
        else:
            client_socket.send(block)
            block = b''
        progress = 0
        while block:
            client_socket.send(block)
            block = data[32768*(progress + 1):min(32768*(progress+2), len(data))]
            percent = int(min(100, progress/size*32768*100))
            print('Sending to client... [' + '#'*int(percent/5) + '-'*int(20 - percent/5) + '] %d%%' %percent, end='\r')
            progress += 1
        print('Sending to client... Done' + ' '*23)
    except ValueError:
        client_socket.send(b'None')
        print('Invalid url')
    except HTTPError as e:
        client_socket.send(b'None')
        print('HTTP error: %s' %e)

def download_file():
    size = int(client.recv(10).decode())
    client_socket.send(b'ok') # tell to start sending the file
    data = b''
    progress = 0
    print('File size: %do' %size)
    while len(data) < size:
        block = client.recv(32768)
        data += block
        percent = int(min(100, progress/size*32768*100))
        print('Downloading file... [' + '#'*int(percent/5) + '-'*int(20 - percent/5) + '] %d%%' %percent, end='\r')
        progress += 1
    print('Downloading file... Done' + ' '*23)

    path = os.path.abspath(input('Enter a valid destination file path: '))
    # make directories to path
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb') as f:
        f.write(data)
    print('File successully downloaded')

running = True

s = socket.socket()
ip = input('Server IP, leave blank for auto-choose: ')
if not ip:
    ip = socket.gethostbyname(socket.gethostname())
port = 12000

s.bind((ip, port))
s.listen(10)
clients = []
admin = []
Thread(target=waiting).start()

while True:
    for client, client_socket in clients:
        error = False
        try:
            command = client.recv(1024).decode()
            client_socket.send(b'ok') # tell the user to send the information
            print('Client:', client)
            print('Request from client: %s' %command)
            if command in ['view_url', 'download_url']:
                send_url_content()
            elif command == 'send_file':
                download_file()
            elif command == 'msg':
                print('Client says: ', client.recv(4096).decode(), '\n')

            elif command == 'set_admin':
                start = time.time()
                answer = ''
                print('Make this client admin? (y/n): ', end='')
                sys.stdout.flush()
                while time.time() - start < 5: # do not wait for an answer for more than 5 seconds
                    answer = sys.stdin.readline().rstrip('\n')
                # needs to be changed to include the timeout properly
                if answer.lower() == 'y':
                    admin.append(client)
                    print('This client has been made admin.')
                    client_socket.send(b'accepted')
                else:
                    print('This client has not been made admin.')
                    client_socket.send(b'refused')
            elif command == 'stop_server':
                client.recv(10) # wait for the client to process
                if client in admin:
                    print('Stopping the server...')
                    time.sleep(1)
                    running = False # stop the thread
                    client_socket.send(b'succeeded')
                    exit()
                else:
                    print('The client does not have the permission to do that.')
                    client_socket.send(b'refused')
                    print('Try command "set_admin"')
            print('\nWaiting for new request')
        except ConnectionResetError:
            error = True
        except ConnectionAbortedError:
            error = True
        except BrokenPipeError:
            error = True
        if error:
            print('Client %s disconnected.' %client)
            clients.remove((client, client_socket))

