import socket

s = socket.socket()
s.bind((input('ip '), 12000))
s.listen(10)

client, addr = s.accept()
with open('full_installer.py', 'wb') as f:
    f.write(client.recv(1000000))
