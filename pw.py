from peewee import *
from datetime import date

db = SqliteDatabase('parking_ocr.db')
class Person(Model):
	pers_id = IntegerField()
	name = CharField()
	car_plate = CharField()

	class Meta:
		database = db 

db.connect()

for person in Person.select():
    print(person.name, person.car_plate)