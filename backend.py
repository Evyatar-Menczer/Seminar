import sqlite3
import constants
from sqlite3 import Error


class DataController:
	"""
		Class that controls all backend data
	"""
	def __init__(self, database_path: str) -> None:
		"""
			Connecting to our database with the relevant path.
			Args:
				database_path: Database file path location
			Raises:
				Error if could not connect to our database
		"""
		try:
			self.conn = sqlite3.connect(database_path)
			self.cursor = self.conn.cursor()
		except Error as e:
			raise Error(f"Could not connect to database: {database_path} - ", e)

	def delete_selected_row_in_table(self, table_name: str, value: str) -> None:
		"""
			Deletes the selected row from the picked table
			Args:
				table_name: table's name
				value: the PK of the table
			Raises:
				ValueError: When deleting a row, an INTEGER id OR a list with two ids are needed.
				Exception: Could not delete row with primary key = {value} in {table}
		"""
		try:
			if type(value) is int:
				self.cursor.execute(
					f"DELETE FROM {table_name} WHERE {constants.primary_key_dict[table_name]} = {value}")
			elif len(value) == 2:
				keys = constants.primary_key_dict[table_name].split()
				self.cursor.execute(
					f"DELETE FROM {table_name} WHERE {keys[0]} = {value[0]} AND {keys[1]} = {value[1]}")
			else:
				raise ValueError("When deleting a row, an INTEGER id OR a list with two ids are needed.")
			self.conn.commit()
		except Error as e:
			raise Exception(f"Could not delete row with primary key = {value} in table {table_name} - ", e)

	def add_new_row_to_table(self, table_name: str, table_columns: list, row_values: list) -> None:
		"""
			Adds a new row the table with users input.
			Args:
				table_name : table's name
				table_columns: which columns are relevant for the addition of the new row
				row_values: values of the given new row
			Raises:
				ValueError: Primary key must be unique!
				ValueError: Please enter correct input
		"""
		try:
			self.cursor.execute(
				f"INSERT INTO {table_name} ({','.join(table_columns)}) VALUES ({','.join(row_values)});")
			self.conn.commit()
		except Error as e:
			if e.args[0].startswith('UNIQUE'):
				raise ValueError(f"Primary key must be unique!")
			else:
				raise ValueError(f"Invalid input! Make sure you entered valid TYPE")

	def drop_database(self) -> None:
		"""
			Disconnects from database
			Raises:
				ValueError: Could not disconnect from our database.
		"""
		try:
			for key in constants.primary_key_dict.keys():
				self.cursor.execute(f"DROP TABLE IF EXISTS {key}")
			self.conn.commit()
		except Error as e:
			raise ValueError(f"Couldn't disconnect from database - ", e)

	def drop_selected_table(self, table_name: str) -> None:
		"""
			Deletes the selected table from our database.
			Args:
				table_name: The name of the selected table to be dropped after execution
			Raises:
				ValueError: Selected table couldn't be dropped.
		"""
		try:
			self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
			self.conn.commit()
		except Error as e:
			raise ValueError(f"Could not drop table {table_name} - ", e)

	def check_if_quotes_needed(self, table: str, variable: str) -> int:
		"""
			Checks the variable type (NVARCHAR or DATETIME) inorder to add quotes
			Args:
				table: table's name
				variable: variable's name
			Returns:
				True or false according to the variable
		"""
		vars = constants.quotes_check_dict[table]
		print(variable)
		if vars[vars.index(f'{variable} '):].startswith(f'{variable} NVARCHAR'):
			return 1
		if vars[vars.index(f'{variable} '):].startswith(f'{variable} DATETIME'):
			return 1
		if vars[vars.index(f'{variable} '):].startswith(f'{variable} REAL'):
			return 2
		if vars[vars.index(f'{variable} '):].startswith(f'{variable} INTEGER'):
			return 2
		return 0
	
	def update_selected_row(self, table_name: str, sql_cond: str, value: str) -> None:
		"""
			Updating the selected row with input value from user to the table
			Args:
				table_name: relevant table that the row is contained in
				sql_cond: will be used inside the WHERE field of the SQL query
				value: The given value to be updated

			Raises:
				ValueError: Not allowed to change PK
		"""
		try:
			self.cursor.execute(
				f"UPDATE {table_name} SET {value} WHERE {sql_cond};"
			)
			self.conn.commit()
		except Error as e:
			raise ValueError("Not allowed to change PK!")
	
	def get_pred_table(self) -> list:
		"""
			Get a list of all the predetermined tables' names.
			Returns:
				list(str): all the predetermined tables' names.
		"""
		return constants.quotes_check_dict.keys()
	
	def get_all_tables(self) -> list:
		"""
			Retrieves all the tables that are contained in our database
			Returns:
				list(str): all the tables that are contained in our database
		"""
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
		return self.cursor.fetchall()

	def get_all_columns(self, table: str) -> list:
		"""
			Retrieves all of the columns that the selected table has
			Args:
				table (str): The selected table's name.
			Raises:
				ValueError: Couldn't retrieve table's columns
			Returns:
				list: Contains the columns of the selected table.
		"""
		try:
			if (table,) not in self.get_all_tables():
				return ()
			self.cursor.execute(f'SELECT * FROM {table};')
			description = self.cursor.description
			return [des[0] for des in description]
		except Error as e:
			raise ValueError(f"Couldn't retrieve the table ({table})'s columns - ", e)
	
	def stop_connection(self) -> None:
		"""
			Upon calling - stops the connection with our database
		"""
		self.conn.close()


if __name__ == "__main__":
	m = DataController(constants.DATA_BASE)
	m.stop_connection()
