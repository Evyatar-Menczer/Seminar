import sqlite3
import csv
import constants
from sqlite3 import Error


class DataController:
	"""
		Class that controls all backend data
	"""
	def __init__(self, db_file: str) -> None:
		"""
			Initialize class object and establishing connection to the DB file.
			Args:
				db_file: Database file path location
			Raises:
				Error: Could not initialize a database connection from db_file
		"""
		try:
			self.conn = sqlite3.connect(db_file)
			self.cursor = self.conn.cursor()
		except Error as e:
			raise Error(f"Could not initialize a database connection from file {db_file} - ", e)
	
	def clear_DB(self) -> None:
		"""
			Clears our database file.

			Raises:
				ValueError: Could not clear our database file.
		"""
		try:
			for key in constants.primary_key_dict.keys():
				self.cursor.execute(f"DROP TABLE IF EXISTS {key}")
			self.conn.commit()
		except Error as e:
			raise ValueError(f"Could not clear the database - ", e)
	
	def drop_selected_table(self, table: str) -> None:
		"""
			Drop the table from our database.
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

	def delete_row_in_table(self, table: str, value: str) -> None:
		"""
			Deleted the row that applies primary key = {value} from {table}. If there are multiple primary keys, it checks all of them
			Args:
				table: table's name
				value: the value that primary key should be equal to

			Raises:
				ValueError: When deleting a row, an INTEGER id OR a list with two ids are needed.
				Exception: Could not delete row with primary key = {value} in {table}
		"""
		try:
			if type(value) is int:
				self.cursor.execute(
					f"DELETE FROM {table} WHERE {constants.primary_key_dict[table]} = {value}")
			elif len(value) == 2:
				keys = constants.primary_key_dict[table].split()
				self.cursor.execute(
					f"DELETE FROM {table} WHERE {keys[0]} = {value[0]} AND {keys[1]} = {value[1]}")
			else:
				raise ValueError("When deleting a row, an INTEGER id OR a list with two ids are needed.")
			self.conn.commit()
		except Error as e:
			raise Exception(f"Could not delete row with primary key = {value} in table {table} - ", e)
	
	def insert_new_row_to_table(self, table: str, columns: list, values: list) -> None:
		"""Inserts a new row with {values} in {columns} to {table}

		Args:
			table (str): table's name
			columns (list(str)): columns to add
			values (list(str)): values to add
		Raises:
			ValueError: Primary key must be unique!
			ValueError: Please enter correct input"
		"""
		try:
			self.cursor.execute(
				f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(values)});")
			self.conn.commit()
		except Error as e:
			if e.args[0].startswith('UNIQUE'):
				raise ValueError(f"Primary key must be unique!")
			else:
				raise ValueError(f"Invalid input! Make sure you entered valid TYPE")

	def check_if_quotes_needed(self, table: str, variable: str) -> bool:
		"""
			Checks if var is instance of str or datetime in {table}

			Args:
				table: table's name
				variable: variable's name

			Returns:
				Boolean
		"""

		variables = constants.quotes_check_dict[table]
		print(variables)
		if variables[variables.index(f'{variable} '):].startswith(f'{variable} NVARCHAR'):
			return True
		if variables[variables.index(f'{variable} '):].startswith(f'{variable} DATETIME'):
			return True
		return False
	
	def update_selected_row(self, table: str, condition: str, value: str) -> None:
		"""
			Updates {value} in all rows that apply {condition} in {table}.

			Args:
				table: table's name.
				condition: the condition with which we find the wanted rows.
				value: the new value that we wish to update.

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
	
	def get_pred_table(self) -> list:
		"""
			Get a list of all the predetermined tables' names.
			Returns:
				list(str): all the predetermined tables' names.
		"""
		return constants.quotes_check_dict.keys()
	
	def get_all_tables(self) -> list:
		"""
			Get a list of all the predetermined that are currently in our DB.

			Returns:
				list(str): all the predetermined that are currently in our DB.
		"""
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
		return self.cursor.fetchall()
	
	def get_all_columns(self, table: str) -> list:
		"""
			Return all columns from selected table.

			Args:
				table (str): table's name.

			Raises:
				ValueError: If could not return all columns from selected table.

			Returns:
				list: all columns from selected table.
		"""
		try:
			if (table,) not in self.get_all_tables():
				return ()
			self.cursor.execute(f'SELECT * FROM {table};')
			description = self.cursor.description
			return [des[0] for des in description]
		except Error as e:
			raise ValueError(f"Could not get table ({table})'s columns - ", e)
	
	def stop_connection(self):
		"""Drops the connection to our DB file.
		"""
		self.conn.close()


if __name__ == "__main__":
	m = DataController(constants.DATA_BASE)
	m.stop_connection()
