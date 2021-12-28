from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import tkinter
import backend

root = Tk()

root.minsize(1200, 800)

tablesFrame = Frame(root, width=120)
buttonsFrame = Frame(root, width=400)
rowsFrame = Frame(root, width=400)

tablesTree = ttk.Treeview(tablesFrame, columns='Tables', height=20, show="headings")

rowsTreeLabel = Label(rowsFrame)
rowsTree = ttk.Treeview(rowsFrame, height=20, selectmode='browse')

errorLabel = Label(root)
errorLabel.pack(side='bottom', anchor='sw')


selectedTable = None
selectedTableIndex = None
selectedRowIdentifier = None
selectedCell = None

m = backend.sqlManager('./chinook.db')

class treeviewTable:
	@staticmethod
	def initTablesTree():
		"""Initialize rows tree.

		Returns:
			Treeview: The initialize tables tree.
		"""
		tablesTree.tag_configure('exists', background='cyan', foreground='black')
		tablesTree.tag_configure('deleted', background='#D8D8D8', foreground='#8A8A8A')
		tablesTree.pack(side='top', fill=BOTH)
		tablesTree.heading('Tables', text="Tables")
		tablesTree.column('Tables', width=100)
		tablesTree.bind('<ButtonRelease-1>',
						lambda e: selectTable())  # used to give e
		fillTablesTree()
		return tablesTree

	@staticmethod
	def initRowsTree():
		"""Initialize rows tree.

		Returns:
			Treeview: The initialize rows tree.
		"""
		rowsTree.tag_configure('exists', background='cyan')
		rowsTree.tag_configure('deleted', background='red')

		rowsTreeLabel.pack(side='top', anchor='nw')

		rowsTree.pack(side='top', fill=BOTH, expand=True)
		rowsTree.bind('<ButtonRelease-1>', lambda e: selectTableCell(e))  # used to give e

		# Horizontal Scroll Bar
		horscrlbar = ttk.Scrollbar(rowsTree, orient="horizontal", command=rowsTree.xview)
		horscrlbar.pack(side='bottom', fill='x')

		# Vertical Scrool Bar
		verscrlbar = ttk.Scrollbar(rowsTree, orient="vertical", command=rowsTree.yview)
		verscrlbar.pack(side='right', fill='y')

		rowsTree.configure(xscrollcommand=horscrlbar.set)
		rowsTree.configure(yscrollcommand=verscrlbar.set)

		return rowsTree

class btn():
	def __init__(self, text, command, frame=root, side='bottom', pady=0) -> None:
		"""Initialize a button object

		Args:
			text (str): [description]
			command (str): [description]
			frame (str, optional): [description]. Defaults to root.
			side (str, optional): [description]. Defaults to 'top'.
			pady (int, optional): [description]. Defaults to 0.
		"""
		self.button = ttk.Button(frame, text=text, command=command)

		self.button.pack(side=side, fill='x', pady=pady)

def errorMessage(func):
	"""A decorator that encloses a function with try, except. the except makes the error label print a message.

	Args:
		func (function): the function we're decorating
	"""

	def inner(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as e:
			errorLabel.config(text=e)

	return inner

def on_closing():
	m.dropConn()
	root.destroy()

def fixed_map(style, option):
	return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]

def selectTable():
	"""Select a table when pressed in the tables' names tree
	"""
	global selectedTable, selectedCell, selectedTableIndex, selectedRowIdentifier
	selectedCell = None
	selectedRowIdentifier = None
	if tablesTree.focus() in tablesTree.get_children():
		selectedTableIndex = tablesTree.get_children().index(tablesTree.focus())
	curItem = tablesTree.item(tablesTree.focus())['values']
	if curItem:
		selectedTable = curItem[0]
		populateRowsTable(curItem[0])
		rowsTreeLabel.config(text=selectedTable)
	elif selectedTable:
		curItem = selectedTable
		populateRowsTable(curItem)
		rowsTreeLabel.config(text=selectedTable)
	else:
		populateRowsTable('')
		rowsTreeLabel.config(text='')

def selectTableCell(e):
	"""Select a cell when pressed in the table tree

	Args:
		e (event): the event when pressing on a cell in the table
	"""
	global selectedCell, selectedRowIdentifier
	curItem = rowsTree.item(rowsTree.focus())['values']
	if curItem == '':
		return
	col = int(rowsTree.identify_column(e.x)[1:]) - 1
	if selectedTable != 'playlist_track':
		selectedRowIdentifier = [rowsTree.column(0)["id"], curItem[0]]
	else:
		selectedRowIdentifier = [rowsTree.column(
			0)["id"], curItem[0], rowsTree.column(1)["id"], curItem[1]]
	selectedCell = [rowsTree.column(col)["id"], str(
		curItem[col]).replace("'", "\'").replace('"', '\"')]

def initWindowAndConnection():
	"""Initiates key variables such as root, style, tablesFrame, rowsFrame and buttonsFrame.
	"""
	root.geometry("1200x800")
	root.title("dbManager")
	root.wm_attributes("-topmost", 1)

	style = ttk.Style()
	style.map('Treeview', foreground=fixed_map(style, "foreground"),
			  background=fixed_map(style, "background"))

	tablesFrame.pack(side='left', padx=5, fill=BOTH, expand=False)
	buttonsFrame.pack(side='top', padx=5, fill=BOTH, expand=False,anchor=CENTER)
	rowsFrame.pack(side='top', padx=5, fill=BOTH, expand=True)


@errorMessage
def fillTablesTree():
	"""Filling the tables' name in the tablesTree
	"""
	for x in tablesTree.get_children():
		tablesTree.delete(x)

	allPreTables = m.getPreTables()
	m.cursor.execute(
		"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
	currentTables = m.cursor.fetchall()
	for row in allPreTables:
		if (row,) in currentTables:
			tablesTree.insert('', 'end', values=row, tags=('exists',))
		else:
			tablesTree.insert('', 'end', values=row, tags=('deleted',))

@errorMessage
def fillRowsTree(sql):
	"""Filling the rows of the rowsTree

	Args:
		sql (str): the SQL query we're using
	"""
	for x in rowsTree.get_children():
		rowsTree.delete(x)

	m.cursor.execute(sql)
	for row in m.cursor:
		row = ['' if v == None else v for v in row]
		rowsTree.insert('', 'end', values=row, tags=('exists',))

@errorMessage
def populateRowsTable(currTable):
	"""Filling the columns of the rowsTree before calling fillRowsTree(sql) to fill the rows right after.

	Args:
		currTable (str): Current table's name
	"""
	columns = tuple(m.getTableColumns(currTable))
	rowsTree["columns"] = columns
	for c in columns:
		rowsTree.heading(c, text=c)
		rowsTree.column(c, minwidth=rowsFrame.winfo_width() // len(columns), width=100)

	rowsTree['show'] = 'headings'
	if columns:
		fillRowsTree(f"SELECT * FROM {currTable};")

@errorMessage
def createDB():
	"""Creates the database from the CSV files.
	"""
	m.createDatabaseFromCSV()
	refreshTrees()
	errorLabel.config(text="Created Database From CSV Files Successfully")

def clearDb():
	"""Drops Database
	"""
	m.clear()
	refreshTrees()
	errorLabel.config(text="Cleared DB Successfully")

@errorMessage
def createFocusedTable():
	"""Create the current table
	"""
	global tablesTree
	if selectedTable:
		m.createTable(selectedTable)
		refreshTrees()
		errorLabel.config(text="Created Table Successfully")
	else:
		errorLabel.config(text="No Table Was Selected.")

def dropTable():
	"""Drop the current table
	"""
	global tablesTree
	if selectedTable:
		m.dropTable(selectedTable)
		refreshTrees()
		errorLabel.config(text="Dropped Table Successfully")
	else:
		errorLabel.config(text="No Table Was Selected.")

def refreshTrees():
	"""Refresh and reshow all tables in the gui based on real time information.
	"""
	fillTablesTree()
	selectTable()
	if selectedTableIndex:
		tablesTree.selection_set(tablesTree.get_children()[selectedTableIndex])
	errorLabel.config(text='')

@errorMessage
def deleteRow():
	"""Deletes the selected row
	"""
	if selectedTable != None and selectedCell != None:
		if len(selectedRowIdentifier) == 2:
			cond = selectedRowIdentifier[1]
		elif len(selectedRowIdentifier) == 4:
			cond = [selectedRowIdentifier[1], selectedRowIdentifier[3]]
		m.deleteRowFromTable(selectedTable, cond)
		refreshTrees()
		errorLabel.config(text="Deleted Row Successfully")
	else:
		errorLabel.config(text="No Table/Cell Was Selected.")

@errorMessage
def createInputRowWindow():
	"""Create an input window in order to collect information to add a new row to the current table.
	"""
	if selectedTable != None:
		columns = m.getTableColumns(selectedTable)
		if len(columns) > 0:
			w = Toplevel(root)
			addRowFrame = Frame(w)
			addRowFrame.pack()
			w.geometry(f"300x{(len(columns) // 2 + 1) * 40 + 40}")
			w.lift(root)
			w.grab_set()

			entries = {}
			for i, c in enumerate(columns):
				column = i % 2
				if column == 0:
					row = i
				else:
					row = i - 1

				l = Label(addRowFrame, text=c)
				l.grid(row=row, column=column, stick=W, padx=2)
				e = Entry(addRowFrame)
				e.grid(row=row + 1, column=i % 2, stick=W, padx=2)
				entries[c] = e.get
			btn("Insert new row", lambda: addRowToTable(
				entries, w), frame=w, side='bottom')
		else:
			errorLabel.config(text="Table Has No Columns!")
	else:
		errorLabel.config(text="No Table Was Selected.")

@errorMessage
def addRowToTable(entries, windowToDestroy):
	"""collect information to add a new row to the current table.

	Args:
		entries (dictionary): every entry that can be entered to a row in the current table
		windowToDestroy (Toplevel): The window that we'll destroy after adding the new row
	"""
	columns = []
	values = []
	for c, e in entries.items():
		columns.append(c)
		values.append(e())
	removeIndexes = [i for i, v in enumerate(values) if v == '']
	for i in sorted(removeIndexes, reverse=True):
		del columns[i]
		del values[i]

	for i, c in enumerate(columns):
		if m.checkIfStr(selectedTable, c):
			values[i] = f'"{values[i]}"'
	m.insertRowToTable(selectedTable, columns, values)
	windowToDestroy.grab_release()
	windowToDestroy.destroy()
	refreshTrees()
	errorLabel.config(text="Row Inserted Successfully")

def init_buttons():
	functions = [deleteRow, createInputRowWindow, createDB, clearDb, createFocusedTable, dropTable]
	texts = ["Delete\nrow", "Add\nNew Row", "Create\nDB", "Drop\nDB", "Import\ntable", "Drop\ntable"]
	for text, func in zip(texts, functions):
		btn(text, func, frame=buttonsFrame, side='left')

if __name__ == "__main__":
	initWindowAndConnection()
	init_buttons()
	rowsTree = treeviewTable.initRowsTree()
	tablesTree = treeviewTable.initTablesTree()

	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()
