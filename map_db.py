from peewee import *

class Person(Model):
	pers_id = IntegerField(unique=True)
	name = CharField()
	car_plate = CharField()

	class Meta:
		database = SqliteDatabase('parking_ocr.db')

class Park_field(Model):
	pers_id = ForeignKeyField(Person, backref='owner')
	park_id = IntegerField()
	entry_x = IntegerField()
	entry_y = IntegerField()

	class Meta:
		database = SqliteDatabase('parking_ocr.db')