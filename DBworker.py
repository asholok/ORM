import psycopg2

class DBworker(object):
	_conn_string = "host = 'localhost' dbname = 'test_asholok' user = 'asholok' password = '123'"
	
	def __init__(self):
		self.__connect()
	
	def __connect(self):
		self._connection = psycopg2.connect(self._conn_string)
		self._cursor = self._connection.cursor()

	def select(self, table, row_id):
			self._cursor.execute('SELECT * FROM "{0}" WHERE {0}_id = {1}'.format(table, row_id),)
			row = self._cursor.fetchone()
			fields = [info[0] for info in self._cursor.description]

			return dict(zip(fields, row))
	
	def insert(self, table, fields, holders, values):
		query = 'INSERT INTO "{0}" ({1}) VALUES ({2}) RETURNING "{0}_id"'.format(table, fields, holders)

		try:
			self._cursor.execute(query, values)
			self._connection.commit()

			return self._cursor.fetchone()[0]
		except:
			self._connection.rollback()

	def update(self, table, fields, row_id, values):
		query = 'UPDATE "{0}" SET {1} WHERE {0}_id = {2}'.format(table, fields, row_id)

		try:
			self._cursor.execute(query, values)
			self._connection.commit()
		except:
			self._connection.rollback()

	def delete(self, table, row_id):
		try:
			self._cursor.execute('DELETE FROM "{0}" WHERE {0}_id = {1}'.format(table, row_id),)
			self._connection.commit()
		except:
			self._connection.rollback()

	def get_all(self, table):
		self._cursor.execute('SELECT * FROM "{0}"'.format(table),)
		fields = [info[0] for info in self._cursor.description]

		return [dict(zip(fields, row)) for row in self._cursor.fetchall()]

	def change_connection(self, new_conn_string):
		self._conn_string = new_conn_string
		self.__connect()
