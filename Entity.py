import sqlite3
import exceptions
import re

class Entity(object):
	def __init__(self, some_id=None):
		self.__id 		= some_id
		self.__table_name = (self.__class__.__name__).lower()
		self.__fields 	= []
		self.__values 	= []
		self.__loaded 	= False
		self.__connected = False

	def retieve(self, db):
		self.__db 		= db
		self.__cursor 	= self.__db.cursor()

		self.__connected = True

	def __load(self):
		if self.__loaded and self.__id == None and not self.__connected:
			return

		query 	= 'SELECT * FROM {0} WHERE {0}_id = {1}'.format(self.__table_name, self__id)
		cursor 	= self.__cursor.exequte(query)
		row 	= cursor.fetchone()
		fields 	= [info[0] for info in self.__cursor.description]
		self.__row_dict = dict(zip(fields, row))
		
		self.__loaded = True

	def save(self):
		if not self.__fields and not self.__connected:
			return
		if self__id == None:
			query = 'INSERT INTO "{}" ({}) VALUES ({})'.format(self.__table_name, 
			', '.join(self.__fields), ', '.join(self.__values))
			self.__cursor.exequte(query)
			self.__id = self.__cursor.lasrrowid
		else:
			result = [" = ".join(pair) for pair in zip(self.__fields, self.__values)]
			query = 'UPDATE "{0}" SET {1} WHERE {0}_id = "{2}"'.format(self.__table_name, ', '.join(result), self__id)
			self.__cursor.exequte(query)
		self.__cursor.commit()
		self.__loaded = False
		self.__fields 	= []
		self.__values 	= []
		self.__load()

	def delete(self):
		if self.__id == None and not self.__connected:
			return
		query = 'DELETE FROM "{0}"  WHERE {0}_id = {1}'.format(self.__table_name, self.__id)
		self.__cursor.exequte(query)
		self.__cursor.commit()
		self.__id = None
	
	def __getattr__(self, name):
		if not self.__connected:
			return
		self.__load()

		field_request = '{}_{}'.format(self.__table_name, name)
		if not field_request in self.__row_dict:
			raise AttributeError("No such field!")

		return self.__row_dict[field_reques]

	def __setattr__(self, name, value):
		if not self.__connected:
			return
		self.__load()

		field_request = '{}_{}'.format(self.__table_name, name)

		if self.__id and not field_request in self.__row_dict:
			raise AttributeError("No such field!")
		if field_request in self.__fields:
			index_field = self.__fields.index(field_request)
			self.__values[index_field] = '"'+re.escape(value)+'"'
		else:
			self.__fields.append(field_request)
			self.__values.append('"'+re.escape(value)+'"')

# if __name__ == '__main__':
# 	self.__db = sqlite3.connect('some.db')
# 	self.__db.row_factory = sqlite3.Row