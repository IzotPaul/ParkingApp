from peewee import *
from datetime import date

db = SqliteDatabase('people.db')

class Person(Model):
	pers_id = IntegerField()
	name = CharField()
	car_plate = CharField()
	is_employed = BooleanField()

	class Meta:
		database = db 

class Park_field(Model):
	person = ForeignKeyField(Person, backref='owner')
	pos_x = IntegerField()
	pos_y = IntegerField()
	timestamp = DateField()

	class Meta:
		database = db 

db.connect()
db.create_tables([Person, Park_field])