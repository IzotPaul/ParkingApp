from map_db import *

db = SqliteDatabase('parking_ocr.db')
db.connect()

print ("Printing 'Person' table")
for person in Person.select():
	print(person.pers_id, person.name, person.car_plate)

print ("Printing 'Park_field' table")
for entry in Park_field.select():
	print(entry.park_id, entry.timestamp, entry.entry_x, entry.entry_y)
