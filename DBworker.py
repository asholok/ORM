import psycopg2

class DBworker(object):
	_conn_string = "host = 'localhost' dbname = 'test_asholok' user = 'asholok' password = '123'"
	
	def __init__(self):
		self.__connect()
	
	def __connect(self):
		self._connection = psycopg2.connect(self._conn_string)
		self._cursor = self._connection.cursor()

	def __get_last_id(self, table):
		self._cursor.execute('SELECT MAX({0}_id) FROM "{0}"'.format(table),)

		return self._cursor.fetchone()[0]

	def select(self, table, row_id):
		self._cursor.execute('SELECT * FROM "{0}" WHERE {0}_id = {1}'.format(table, row_id),)
		row = self._cursor.fetchone()
		fields = [info[0] for info in self._cursor.description]

		return dict(zip(fields, row))
	
	def insert(self, table, fields, values):
		self._cursor.execute('INSERT INTO "{}" ({}) VALUES ({})'.format(table, fields, values),)
		self._connection.commit()

		return self.__get_last_id(table)

	def update(self, table, fields_values, row_id):
		self._cursor.execute('UPDATE "{0}" SET {1} WHERE {0}_id = {2}'.format(table, fields_values, row_id),)
		self._connection.commit()

	def delete(self, table, row_id):
		self._cursor.execute('DELETE FROM "{0}" WHERE {0}_id = {1}'.format(table, row_id),)
		self._connection.commit()

	def get_id_list(self, table):
		self._cursor.execute('SELECT {0}_id FROM "{0}"'.format(table),)
		id_list = [row[0] for row in self._cursor.fetchall()]

		return id_list

	def change_connection(self, new_conn_string):
		self._conn_string = new_conn_string
		self.__connect()
