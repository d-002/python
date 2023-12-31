import socket

s = socket.socket()
s.connect((input('Receiver ip: '), 12000))
print('Successfully connected to the server.')

print('\nSending installer...')
with open('full_installer.py') as f:
    s.send(f.read().encode())
input('Done.')
