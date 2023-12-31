import socket
import os
from os.path import *

s = socket.socket()
s.bind((input('Enter this device ip : '), 12000))
s.listen(10)

client, addr = s.accept()
print('\nConnecting to the other device server...')
ip, port = client.recv(1000).decode().split(' ') # get the info for the other device server
s_ = socket.socket()
s_.connect((ip, int(port)))
print('Connection successfully established.')

print('\nReceiving files...')
while True:
    filename = client.recv(1000).decode() # may contain the name of the file
    if filename == 'done':
        break
    print('File "%s"... ' %filename, end='')
    s_.send(b'ok')
    with open(filename, 'wb') as f:
        f.write(client.recv(1000000))
    s_.send(b'ok')
    print('OK')
print('Done.')

print('\nRemoving install files...')
files = ['installer_recv.py', 'full_installer.py']
for filename in files:
    if exists(filename):
        os.remove(filename)
input('Done.')
