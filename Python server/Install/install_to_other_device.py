import socket

s = socket.socket()
s.connect((input('Device to install to ip: '), 12000))
print('Successfully connected to the server.')

my_ip = input('\nSelf ip: ')
my_port = 12000
my_s = socket.socket()
my_s.bind((my_ip, my_port))
my_s.listen(10)

print('\nSending server info...')
s.send(('%s %d' %(my_ip, my_port)).encode())
server, addr = my_s.accept()
print('Connection successfully established.')

print('\nSending files...')
files = ['client.py', 'server.py', '_help_.py']
for filename in files:
    print('File "%s"... ' %filename, end='')
    s.send(filename.encode())
    server.recv(10) # wait for the other device to say ok
    with open(filename, 'rb') as f:
        s.send(f.read())
    server.recv(10) # wait for the other device to say ok
    print('OK')
s.send(b'done') # tell the other device there are no more files to transfer
input('Done.')
