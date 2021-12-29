import sqlite3
import csv
import constants
from sqlite3 import Error


class DataController:
	
	def __init__(self, db_file) -> None:
		"""Initialize class object and establishing connection to the DB file.

		Args:
			db_file (str): DB file location

		Raises:
			Error: Could not initialize a database connection from db_file
		"""
		try:
			self.conn = sqlite3.connect(db_file)
			self.cursor = self.conn.cursor()
		# self.cursor.execute("PRAGMA foreign_keys = ON")
		except Error as e:
			raise Error(f"Could not initialize a database connection from file {db_file} - ", e)
	
	# def createDatabaseFromCSV(self):
	# 	"""Imports information from various predetermined CSV files into our connected DB file.
	#
	# 	Raises:
	# 		ValueError: Could not import information to our DB file from the predetermined CSV files.
	# 	"""
	# 	try:
	# 		for k in DataController.tablesCreationSQL.keys():
	# 			self.createTable(k)
	# 		self.conn.commit()
	# 	except Error as e:
	# 		raise ValueError(f"Could not create database from predetermined CSV files - ", e)
	def column_primary_check(self):
		pass
	
	def clear(self):
		"""Clears our DB file.

		Raises:
			ValueError: Could not clear our DB file.
		"""
		try:
			for k in constants.tablesWhereSQL.keys():
				self.cursor.execute(f"DROP TABLE IF EXISTS {k}")
			self.conn.commit()
		except Error as e:
			raise ValueError(f"Could not clear the database - ", e)
	
	def dropTable(self, table: str):
		"""Drop the table {tableName} from our DB.

		Args:
			table (str): The name of the table that we wish to drop.

		Raises:
			ValueError: In case the table wasn't found or any other reason the table couldn't have been dropped.
		"""
		try:
			self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
			self.conn.commit()
		except Error as e:
			raise ValueError(f"Could not drop table {table} - ", e)
	
	def createTable(self, tableFromDict):
		"""Create the table {tableFromDict} into our DB.

		Args:
			tableFromDict (str): The name of the table that we wish to create.

		Raises:
			ValueError: {tableFromDict} is not one of the predetermined tables.
			Exception: {tableFromDict} couldn't have been created.
		"""
		try:
			if tableFromDict not in constants.tablesCreationSQL.keys():
				raise ValueError('Only predetermined tables can be created!')
			self.conn.commit()
			
			self.cursor.execute(f'DROP TABLE IF EXISTS {tableFromDict}')
			
			self.cursor.execute(constants.tablesCreationSQL[tableFromDict])
			with open(f'./chinook/{tableFromDict}.csv', 'r', encoding="utf8") as t:
				dr = csv.DictReader(t)
				to_db = []
				for i in dr:
					del i["index"]
					to_db.append(tuple(i.values()))
		except Error as e:
			raise Exception(f"Could not create table {tableFromDict} - ", e)
		
		self.cursor.executemany(
			f"INSERT OR IGNORE INTO {tableFromDict} VALUES ({','.join(['?'] * len(to_db[0]))});", to_db)
		self.conn.commit()
	
	def deleteRowFromTable(self, table: str, value: str):
		"""Deleted the row that applies primary key = {value} from {table}. If there are multiple primary keys, it checks all of them

		Args:
			table (str): table's name
			value (str): the value that primary key should be equal to

		Raises:
			ValueError: When deleting a row, an INTEGER id OR a list with two ids are needed.
			Exception: Could not delete row with primary key = {value} in {table}
		"""
		try:
			if type(value) is int:
				self.cursor.execute(
					f"DELETE FROM {table} WHERE {constants.tablesWhereSQL[table]} = {value}")
			elif len(value) == 2:
				keys = constants.tablesWhereSQL[table].split()
				self.cursor.execute(
					f"DELETE FROM {table} WHERE {keys[0]} = {value[0]} AND {keys[1]} = {value[1]}")
			else:
				raise ValueError("When deleting a row, an INTEGER id OR a list with two ids are needed.")
			self.conn.commit()
		except Error as e:
			raise Exception(f"Could not delete row with primary key = {value} in table {table} - ", e)
	
	def insertRowToTable(self, table, columns, values):
		"""Inserts a new row with {values} in {columns} to {table}

		Args:
			table (str): table's name
			columns (list(str)): columns to add
			values (list(str)): values to add
		Raises:
			ValueError: Primary key must be unique!
			ValueError: Please check cell types (For example you can't insert 'ABC' into an INTEGER type)
		"""
		try:
			self.cursor.execute(
				f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(values)});")
			self.conn.commit()
		except Error as e:
			if e.args[0].startswith('UNIQUE'):
				raise ValueError(f"Primary key must be unique!")
			else:
				raise ValueError(f"Please check cell types (For example you can't insert 'ABC' into an INTEGER type)")
	
	def checkIfStr(self, table, variable):
		"""Checks if {variable} is of type NVARCHAR(X) in {table}

		Args:
			table (str): table's name
			variable (str): variable's name

		Returns:
			Boolean: True if variable is of type NVARCHAR(x), Otherwise False.
		"""
		variables = constants.tablesCreationSQL[table]
		if variables[variables.index(f'{variable} '):].startswith(f'{variable} NVARCHAR'):
			return True
		return False
	
	def updateRow(self, table, condition, value):
		"""Updates {value} in all rows that apply {condition} in {table}.

		Args:
			table (str): table's name.
			condition (str): the condition with which we find the wanted rows.
			value (str): the new value that we wish to update.

		Raises:
			ValueError: Can't change primary key.
		"""
		try:
			self.cursor.execute(
				f"UPDATE {table} SET {value} WHERE {condition};"
			)
			self.conn.commit()
		except Error as e:
			raise ValueError("Could Not Change Primary Key.")
	
	def getPreTables(self):
		"""Get a list of all the predetermined tables' names.

		Returns:
			list(str): all the predetermined tables' names.
		"""
		return constants.tablesCreationSQL.keys()
	
	def getTables(self):
		"""Get a list of all the predetermined that are currently in our DB.

		Returns:
			list(str): all the predetermined that are currently in our DB.
		"""
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
		return self.cursor.fetchall()
	
	def getAllFromTable(self, table):
		"""Return all rows from {table}.

		Args:
			table (str): table's name.

		Raises:
			ValueError: Could not return all rows from table.

		Returns:
			list: all rows from table.
		"""
		try:
			self.cursor.execute(f"SELECT * FROM {table};")
			return self.cursor.fetchall()
		except Error as e:
			raise ValueError(f"Could not select all from table {table} - ", e)
	
	def getTableColumns(self, table):
		"""Return all columns from {table}.

		Args:
			table (str): table's name.

		Raises:
			ValueError: Could not return all columns from table.

		Returns:
			list: all columns from table.
		"""
		try:
			if (table,) not in self.getTables():
				return ()
			self.cursor.execute(f'SELECT * FROM {table};')
			description = self.cursor.description
			return [d[0] for d in description]
		except Error as e:
			raise ValueError(f"Could not get table ({table})'s columns - ", e)
	
	def dropConn(self):
		"""Drops the connection to our DB file.
		"""
		self.conn.close()


if __name__ == "__main__":
	m = DataController(constants.DATA_BASE)
	# m.createDatabaseFromCSV()
	# m.clear()
	# m.dropTable("playlists")
	# m.createTable("playlists")
	# m.deleteRowFromTable('playlists', 1)
	
	# m.insertRowToTable('playlists', ['1', "'asd'"])
	# m.updateRow('playlists', 'PlaylistId = 1', "Name = 'GOAT'")
	
	# m.getTableColumns('tracks')
	
	# m.cursor.execute("SELECT * FROM playlists;")
	# print(m.cursor.fetchall())
	
	# m.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
	# print(m.cursor.fetchall())
	m.dropConn()
