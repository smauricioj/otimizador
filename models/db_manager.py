

from sqlite3 import connect
from os import path


class Db_manager:
	def __init__(self, db_name, db_files_path):
		self.conn = connect(db_name)
		self.c = self.conn.cursor()
		self.files_path = db_files_path

	def execute(self, string):
		return self.c.execute(string)

	def commit(self):
		return self.conn.commit()

	def close(self):
		return self.conn.close()

	def execute_script(self, script_file_name, many = None):
		with open(path.join(self.files_path, script_file_name), 'r') as file:
			data = file.read()
			file.close()
		if not many:
			return self.c.execute(data)
		else:
			return self.c.executemany(data, many)
