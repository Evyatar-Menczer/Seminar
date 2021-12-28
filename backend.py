import sqlite3
from dataclasses import dataclass
import constants


class Database(object):
	"""sqlite3 database class that holds testers jobs"""

	def __init__(self):
		"""Initialize db class variables"""
		self.connection = sqlite3.connect(constants.DATA_BASE)
		self.cur = self.connection.cursor()

	def close(self):
		"""close sqlite3 connection"""
		self.connection.close()

	def execute(self, query: str):
		"""execute a row of data to current cursor"""
		return self.cur.execute(query).fetchall()

	def executemany(self, many_new_data):
		"""add many new data to database in one go"""
		self.create_table()
		self.cur.executemany('REPLACE INTO jobs VALUES(?, ?, ?, ?)', many_new_data)

	def create_table(self):
		"""create a database table if it does not exist already"""
		self.cur.execute('''CREATE TABLE IF NOT EXISTS jobs(title text, \
                                                            job_id integer PRIMARY KEY, 
                                                            company text,
                                                            age integer)''')

	def commit(self):
		"""commit changes to database"""
		self.connection.commit()

	def get_tables(self) -> tuple:
		self.cursor.execute(constants.ALL_TABLES_QUERY)
		return self.cursor.fetchall()

	def get_all_table_column(self, table) -> list:
		try:
			if (table,) not in self.get_tables():
				return ()
			return [disc[0] for disc in self.execute(f'SELECT * FROM {table};')]
		except Exception as e:
			raise f'could not get table`s column - {e}'


def view():
	conn = sqlite3.connect(constants.DATA_BASE)
	cur = conn.cursor()
	cur.execute('SELECT * FROM Customers')
	rows = cur.fetchall()
	conn.close()
	return rows

# def sort_by_name():
# 	conn = sqlite3.connect(DATA_BASE)
# 	cur = conn.cursor()
# 	cur.execute(f'SELECT * FROM Customers ORDER BY FirstName ASC')
# 	rows = cur.fetchall()
# 	conn.close()
# 	return rows


# def sort_by_type():
# 	#  Provide a query that includes the purchased track name AND artist name with each invoice line item
# 	q1 = '''
# 	select i.*, t.name as 'track', ar.name as 'artist'
# 	from invoice_items as i
# 	join tracks as t on i.trackid = t.trackid
# 	join albums as al on al.albumid = t.albumid
# 	join artists as ar on ar.artistid = al.artistid
# 	'''
# 	conn = sqlite3.connect(DATA_BASE)
# 	cur = conn.cursor()
# 	cur.execute(q1)
# 	rows = cur.fetchall()
# 	conn.close()
# 	return rows
#
#
# def sort_by_best_seller():
# 	# Which sales agent made the most in sales over all?
# 	q2 = """
# 	select *, max(total) from
# 	(select e.*, sum(total) as 'Total'
# 	from Employees as e
# 	join Customers as c on e.employeeid = c.supportrepid
# 	join Invoices as i on i.customerid = c.customerid
# 	group by e.employeeid)
# 	"""
# 	conn = sqlite3.connect(DATA_BASE)
# 	cur = conn.cursor()
# 	cur.execute(q2)
# 	rows = cur.fetchall()
# 	conn.close()
# 	return rows
