import _thread
import socket
import cv2
import os
import math
import numpy as np
import scipy.io as sio
from time import sleep
from sklearn import svm
from crop import *
from peewee import *
from map_db import *
global pers_index_global

db = SqliteDatabase("parking_ocr.db")

def main():
	global pers_index_global

	# Init database
	os.remove("parking_ocr.db")
	db.connect()
	db.create_tables([Person, Park_field])
	pers_index_global = 0
	print ("Database created!")

	# Init OCR
	mat = sio.loadmat("emnist.mat")
	images = np.transpose(mat["images"])[9000:9999]
	labels = np.transpose(mat["labels"])[9000:9999]

	ocr = svm.SVC(decision_function_shape='ovo', kernel='rbf')
	print ("Training neural network... ", end="")

	ocr.fit(images, labels.ravel())
	print ("finished !")

	# Init TCP socket
	s = socket.socket()
	host = socket.gethostname()
	port = 55000
	s.bind((host, port))
	s.listen(5)
	print ("Server started!")
	print ("Waiting for clients...")

	# Wait connections
	while True:
		c, addr = s.accept()
		_thread.start_new_thread(on_new_client,(c, addr, ocr))
		
	s.close()


def on_new_client(clientsocket, addr, ocr):
	global pers_index_global
	ack = "ACK"

	# Receive camera location and orientation
	data = clientsocket.recv(1024)
	data = data.decode("ascii")
	data = data.replace("(", "")
	data = data.replace(")", "")
	camera_loc = (int(data.split(",")[0]), int(data.split(",")[1]))
	clientsocket.send(ack.encode("ascii"))

	data = clientsocket.recv(1024)
	data = data.decode("ascii")
	camera_ori = int(data)
	clientsocket.send(ack.encode("ascii"))

	while True:
		if camera_ori == 0:
			# Wait for a person name
			name = clientsocket.recv(1024)
			name = name.decode("ascii")

			# Stop loop if client closed
			if (name == "GOODBYE"):
				break

			clientsocket.send(ack.encode("ascii"))

			print ("\tClient " + str(camera_loc) + " detected " + name)

			file_name = name + ".jpg"

			# Wait for that person's car image
			recv_file(clientsocket, file_name)

			# If the person is found in the database skip image proccessing
			found = False
			for entry in Person.select().where(Person.name == name):
				plate = entry.car_plate
				found = True

			# Get an array of letters (of the license plate) from cropping the image
			if not found:
				letters = crop_plate_letters(file_name)

				# Detect the letters
				result = ocr.predict(letters)
				plate = labels_to_letters(result)
				print ("\tIdentified plate " + plate)

				# Add to database
				pers = Person.create(pers_id=pers_index_global, name=name, car_plate=plate)
			else:
				print ("\Found in database plate " + plate)

			park_field = Park_field.create(pers_id=pers_index_global, park_id=-1,
							entry_x=camera_loc[0], entry_y=camera_loc[1])
			pers_index = pers_index_global
			pers_index_global += 1

			# Wait and check response
			sleep(0.2)
			access_granted = False
			park_index = -1
			for entry in Park_field.select().where(Park_field.pers_id == pers_index):
				access_granted = True
				park_index = entry.park_id
				break

			if (access_granted):
				print ("\tAccess granted on park spot nr. " + str(park_index))
				result = "GRANTED " + str(park_index)
				clientsocket.send(result.encode("ascii"))
				send_file(clientsocket, "map.layout")
			else:
				print ("\nAccess denied")
				result = "DENIED " + str(park_index)
				clientsocket.send(result.encode("ascii"))
		elif camera_ori == 1:
			# Wait for a person name
			name = clientsocket.recv(1024)
			name = name.decode("ascii")

			# Stop loop if client closed
			if (name == "GOODBYE"):
				break

			clientsocket.send(ack.encode("ascii"))

			print ("\tClient " + str(camera_loc) + " detected " + name + " leaving")

			# Find the person in the database
			for entry in Person.select().where(Person.name == name):
				person_id = entry.pers_id
				plate = entry.car_plate

				for park in Park_field.select().where(Park_field.pers_id == person_id):
					park.delete_instance()

	clientsocket.close()

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