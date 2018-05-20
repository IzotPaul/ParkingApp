import socket
from random import randint
from time import sleep

HOST = socket.gethostname()
PORT = 55000
LOC = (0, 0)

def initial_config():
	file = open('client.config', 'r')
	LOC = file.readline().split("=")[1]

	file.close()

initial_config()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.send(str(LOC))
sock.recv(1024)

# # Simulate cars being scaned by the camera
# while True:
# 	sock.send('Test Subject')
# 	sock.recv(1024)
# 	sock.send('B 01 AAA')

# 	print sock.recv(1024)
# 	sleep(randint(2,10))

sock.send('Test Subject')
sock.recv(1024)
sock.send('B 01 AAA')
print sock.recv(1024)
sleep(randint(2,10))

sock.send('Another Subject')
sock.recv(1024)
sock.send('TL 32 ALT')
print sock.recv(1024)
sleep(randint(2,10))

sock.send('Surprise Subject')
sock.recv(1024)
sock.send('TL 99 TAB')
print sock.recv(1024)
sleep(randint(2,10))

sock.close()