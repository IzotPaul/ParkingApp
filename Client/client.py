import socket
import cv2
import os
import math
import sys
from tkinter import *
from map_utils import init_imgs
from random import randint
from time import sleep

def main():
	HOST = socket.gethostname()
	PORT = 55000
	LOC = (0, 0)
	ORT = 1

	# Initial config (values from client.config file)
	file = open(sys.argv[1], 'r')
	HOST = socket.gethostname()
	PORT = int(file.readline().split("=")[1])
	LOC = file.readline().split("=")[1]
	ORT = file.readline().split("=")[1]
	file.close()

	# Init socket and connect to server
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))

	# Send camera location and orientation to server
	sock.send(str(LOC).encode("ascii"))
	msg = sock.recv(1024)
	sock.send(str(ORT).encode("ascii"))
	msg = sock.recv(1024)

	# person_placeholder = "Person_Name"
	person_placeholder = "IMG_"
	# Simulate 5 cars being scaned by the camera
	for x in range(5):
		if (ORT == 0):
			# Get a random person / image file and send it to the server
			person = person_placeholder + str(randint(1,13))
			print ("Detected " + person + ". Sending image to server...")

			sock.send(person.encode("ascii"))
			msg = sock.recv(1024)

			file_name = person + ".jpg"
			send_file(sock, file_name)

			# Await response
			msg = sock.recv(1024)
			msg = msg.decode("ascii")

			response = msg.split(" ")[0]
			spot = msg.split(" ")[1]
			if (response == "GRANTED"):
				recv_file(sock, "map.layout")
				print ("  - Access granted on spot: " + spot + " ! -   ")
				display_map("map.layout", int(spot), randint(5,10))
			elif (response == "DENIED"):
				print ("  - Access denied (PARKING_FULL)! -   ")

			# Simulate waiting for another car
			sleep(randint(2,5))
		elif (ORT == 1):
			person = person_placeholder + str(randint(1,13))
			print ("Detected " + person + " wanting to leave")

			sock.send(person.encode("ascii"))
			msg = sock.recv(1024)

	goodbye = "GOODBYE"
	sock.send(goodbye.encode("ascii"))

	# Close socket
	sock.shutdown(socket.SHUT_WR)
	sock.close()

def display_map(filename, idx, timeout):
	file = open(filename, "r")
	root = Tk()

	line = file.readline()
	max_x = int(line.split(" ")[0])
	max_y = int(line.split(" ")[1])

	labels = [[0 for y in range(max_y)] for x in range(max_x)]
	layout = [[0 for y in range(max_y)] for x in range(max_x)]
	color = [["" for y in range(max_y)] for x in range(max_x)]
	image = [[0 for y in range(max_y)] for x in range(max_x)]
	img = init_imgs()


	# Read layout
	for x in range(max_x):
		line = file.readline()[:-1]
		for y in range(max_y):
			layout[x][y] = int(line.split(" ")[y])

	# Read image indexes
	for x in range(max_x):
		line = file.readline()[:-1]
		for y in range(max_y):
			image[x][y] = int(line.split(" ")[y])

	# Read colors
	for x in range(max_x):
		line = file.readline()[:-1]
		for y in range(max_y):
			color[x][y] = line.split(" ")[y]

	# Create grid (from labels)
	for x in range(max_x):
		for y in range(max_y):
			labels[x][y] = Label(root, bg=color[x][y],
								image=img[image[x][y]])
			labels[x][y].grid(row=x, column=y)

	# Color spot differently
	print (idx)
	for x in range(max_x):
		for y in range(max_y):
			if (layout[x][y] == idx):
				labels[x][y].configure(bg="purple")

	root.title("Map")
	root.after(timeout * 1000, root.destroy)
	root.mainloop()

def send_file(sock, filename):
	file = open(filename, "rb")
	size = os.path.getsize(filename)

	# Send size of the file first
	size_str = str(math.floor(size / 1024) + 1)
	sock.send(size_str.encode("ascii"))
	msg = sock.recv(1024)

	# Send the file
	payload = file.read(1024)
	while (payload):
		sock.send(payload)
		payload = file.read(1024)

	msg = sock.recv(1024)
	file.close()

def recv_file(sock, file_name):
	file = open(file_name, "wb")
	ack = "ACK"

	size = sock.recv(1024)
	size = size.decode("ascii")
	sock.send(ack.encode("ascii"))

	for x in range(int(size)):
		payload = sock.recv(1024)
		file.write(payload)

	sock.send(ack.encode("ascii"))
	file.close()

if __name__ == "__main__":
    main()