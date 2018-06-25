import socket
import cv2
from random import randint
from time import sleep

def send_file(seck, filename):
	file = open(filename, "rb")

	payload = file.read(1024)
	while (payload):
		sock.send(payload)
		payload = file.read(1024)

	file.close


def main():
	HOST = socket.gethostname()
	PORT = 55000
	LOC = (0, 0)
	ORT = 1

	# Initial config (values from client.config file)
	file = open('client.config', 'r')
	HOST = socket.gethostname()
	PORT = file.readline().split("=")[1]
	LOC = file.readline().split("=")[1]
	ORT = file.readline().split("=")[1]
	file.close()

	# Init socket and connect to server
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))

	# Send camera location and orientation to server
	sock.send(str(LOC).encode("ascii"))
	sock.send(str(ORT).encode("ascii"))
	msg = sock.recv(1024)

	person_placeholder = "Person_Name"
	# Simulate cars being scaned by the camera
	# while True:
	for x in range(5):
		person = person_placeholder + str(randint(1,13))
		print ("Detected " + person + ". Sending image to server...")

		sock.send(person.encode("ascii"))

		file_name = person + ".jpg"
		send_file(sock, filename)

		msg = sock.recv(1024)
		print (msg.decode("ascii"))

		sleep(randint(2,10))

	sock.close()

if __name__ == "__main__":
    main()