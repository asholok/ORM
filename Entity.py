from DBworker import DBworker
import re

def get_class_name(cls):
	return cls.__class__.__name__.lower()

class Entity(object):
	_loaded = False
	_fields 		= []
	_parents 		= []
	_children 		= []
	_siblings 		= []
	_managed_fields = {}
	_row_dict 	= {}

	def __init__(self, row_id=None):
		self._table_name = get_class_name(self)
		self._row_id = row_id
		self._db_worker = DBworker()

	def load(self):
		if self._row_id is None or self._loaded:
			return
		self._row_dict = dict(self._db_worker.select(self._table_name, self._row_id))
		self._loaded = True

	def __managin_input(self, name, value):
		field_name = '{}_{}'.format(self._table_name, name)
		
		self._managed_fields[field_name] = re.escape(value)

	def __make_update_conent(slef):
		fields = []
		values = []

		for key, value in self._managed_fields.items():
			result.append('{} = %s'.format(key))
			values.append(value)
		
		return {"fields": ', '.join(fields), 'values': values}

	def __make_insert_conent(self):
		fields = []
		holders = []
		values = []
		
		for key, value in self._managed_fields.items():
			fields.append(key)
			holders.append('%s')
			values.append(value)

		return {"fields": ', '.join(fields), "holders": ', '.join(holders), 'values': values}

	def save(self):
		if not self._managed_fields:
			return
		
		if self._row_id:
			content = self.__make_update_conent()

			self._db_worker.update(self._table_name, content["fields"], self._row_id, content["values"])
		else:
			content = self.__make_insert_conent()
			
			self._row_id = self._db_worker.insert(self._table_name, content["fields"], 
												  content["holders"], content["values"])

		self._loaded = False
		self._managed_fields = []

	def delete(self):
		if self._row_id is None:
			raise Exception('There is no id maaan!!!')

		self._db_worker.delete(self._table_name, self._row_id)
		self._row_id = None

	def _get_parent(self, name):
		value 	= self._row_dict['{}_id'.format(name)]
		class_ 	= name.title()

		return globals()[class_](value)

	def _get_siblings(self, name):
		relation_table = '{0}_{1}_relation'.format(*(sorted([name, self._table_name])))
		specifyer = {'column': self._table_name, 'id': self._row_id}

		return globals()[name].all(specifyer, relation_table)

	def _get_children(self, name):
		specifyer = {'column': self._table_name, 'id': self._row_id}

		return globals()[name].all(specifyer)

	def __getattr__(self, name):
		if self._row_id == None:
			raise Exception('There is no id maaan!!!')
		
		self.load()
		if name == "id":
			return self._row_id
		elif name in self._fields:
			field_name = '{}_{}'.format(self._table_name, name)
				
			return self._row_dict[field_name]
		elif name in self._parents:
			return self._get_parent(name)
		elif name in self._children:
			return self._get_children(self._children[name])
		elif name in self._siblings:
			return self._get_siblings(self._siblings[name])
		else:
			raise AttributeError('There is no fields like {}.'.format(name))

	def __setattr__(self, name, value):
		if name in self._fields:
			self.load()
			self.__managin_input(name, value)
		
		object.__setattr__(self, name, value)
	
	@classmethod
	def enforce_clas(cls, stack):
		semple = cls()

		semple._loaded = True
		semple._row_id = stack['{}_id'.format(semple._table_name)]
		semple._row_dict = stack

		return semple

	@classmethod
	def all(cls, specifyer=None, relation_table=None):
		worker = DBworker()
		values = [cls.__name__.lower()]

		if specifyer:
			values.append(specifyer)
		if relation_table:
			values.append(relation_table)

		return [cls.enforce_clas(stack) for stack in worker.get_all(*values)]
