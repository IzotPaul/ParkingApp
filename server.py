import socket
import thread
import django
import time
from peewee import *
from datetime import date
from parkingmap import *
# from db_orm import *
from openalpr import Alpr

db = SqliteDatabase('parking_ocr.db')
class Person(Model):
	pers_id = IntegerField()
	name = CharField()
	car_plate = CharField()

	class Meta:
		database = db 

class Park_field(Model):
	person = ForeignKeyField(Person, backref='owner')
	pos_x = IntegerField()
	pos_y = IntegerField()
	timestamp = DateField()

	class Meta:
		database = db 

def main():
	# init database
	db.connect()
	db.create_tables([Person, Park_field])

	# init parking map
	file = open('park.in', 'r')
	line = file.readline()
	length = int(line.split(" ")[0])
	width = int(line.split(" ")[1])
	Park = [[Park_spot(False, 'None', '', 0) for x in xrange(width)] for y in xrange(length)]

	for i in xrange(length):
		line = file.readline()
		for j in xrange(width):
			if int(line.split(" ")[j]) == 1:
				Park[i][j].avl = True

	# init TCP socket
	s = socket.socket()
	host = socket.gethostname()
	port = 55000
	s.bind((host, port))
	s.listen(5)
	print 'Server started!'
	print 'Waiting for clients...'

	# wait connections
	while True:
		c, addr = s.accept()
		thread.start_new_thread(on_new_client,(c,addr, Park))
		
	s.close()


def on_new_client(clientsocket, addr, Park):
	data = clientsocket.recv(1024)
	data = data.replace("(", "")
	data = data.replace(")", "")
	camera_loc = (int(data.split(",")[0]), int(data.split(",")[1]))
	clientsocket.send('ACK')

	while True:
		name = clientsocket.recv(1024)
		clientsocket.send('ACK')
		plate = clientsocket.recv(1024)
		print '\t' + name + ' ' + plate

		# add to database
		pers = Person.create(pers_id=1, name=name, car_plate=plate)

		# get parking spot
		result = find_park_spot(camera_loc, name, plate, Park)
		clientsocket.send(str(result))
		print '\t' + str(result)
	clientsocket.close()


if __name__ == "__main__":
    main()