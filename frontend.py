from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import tkinter
import backend
import constants

root = Tk()
root.minsize(800, 800)

# Frames:
tablesFrame = Frame(root, width=120)
rowsFrame = Frame(root, width=400)
top_container = Frame(root, width=800)
low_container = Frame(root, width=400)
buttonsFrame = Frame(top_container, width=400)
error_frame = Frame(top_container, width=200)
edit_frame = None

# Trees:
tablesTree = ttk.Treeview(tablesFrame, columns='Tables', height=20, show="headings")
rowsTree = ttk.Treeview(rowsFrame, height=20, selectmode='browse')

# Labels
errorLabel = Label(error_frame, font=("Arial", 15))
errorLabel.pack(side='top', anchor=CENTER)
rowsTreeLabel = Label(rowsFrame)


selectedTable = None
selectedTableIndex = None
selectedRowIdentifier = None
selectedCell = None
edit_pressed = False

m = backend.DataController('./chinook.db')


def init_tables_tree() -> None:
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
	import_tables()


def init_rows_tree() -> None:
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


# def on_edit(e):
# 	if selectedTable:
# 		global edit_pressed
# 		edit_pressed = not edit_pressed
# 		edit_input_frame(e)
# 	else:
# 		errorLabel.config(text='Please choose table')


def on_ignore():
	clear_edit_frame()


def buttom_frame_insert(columns, current_row=None,disable_flag=0):
	global edit_frame
	edit_frame = Frame(low_container, width=400)
	edit_frame.pack(side='top', padx=4, ipady=150, fill=BOTH, expand=False)
	entries = {}
	row = 1
	for i, c in enumerate(columns):
		if i % 6 == 0:
			row += 4
		l = Label(edit_frame, text=c)
		l.grid(row=row, column=i % 6, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)
		edit_entry = Entry(edit_frame)
		edit_entry.grid(row=row + 1, column=i % 6, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)
		if c in constants.tablesWhereSQL[selectedTable] and disable_flag:
			edit_entry.config(state='disabled')
		entries[c] = edit_entry.get
		if current_row:
			edit_entry.insert(0, current_row[i])

	return entries
	
	
def edit_input_frame(e):
	"""Create an input window in order to collect information to add a new row to the current table.
	"""
	global selectedTable, edit_frame, selectedCell, selectedRowIdentifier
	curItem = rowsTree.item(rowsTree.focus())['values']
	col = int(rowsTree.identify_column(e.x)[1:]) - 1
	selectedCell = [rowsTree.column(col)["id"], str(curItem[col]).replace("'", "\'").replace('"', '\"')]
	if selectedTable:
		columns = m.getTableColumns(selectedTable)
		if len(columns) > 0:
			entries = buttom_frame_insert(columns, current_row=curItem,disable_flag=1)
			btn("Accept Changes", lambda: updateValue(
				entries), 0, frame=edit_frame)
			btn("Ignore Changes", on_ignore, 2, frame=edit_frame)
		
		else:
			errorLabel.config(text="Table Has No Columns!")
	else:
		errorLabel.config(text="No Table Was Selected.")


def updateValue(entries):
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
	new_value_to_insert = ''
	for i,col in enumerate(columns):
		isStr = m.checkIfStr(selectedTable, col)
		if isStr:
			if not i == len(columns)-1:
				new_value_to_insert += f'{col} = "{entries[col]()}",\n'
			else:
				new_value_to_insert += f'{col} = "{entries[col]()}"'
		else:
			if not i == len(columns)-1:
				new_value_to_insert += f'{col} = {entries[col]()},\n'
			else:
				new_value_to_insert += f'{col} = {entries[col]()}'
	try:
		if len(selectedRowIdentifier) == 2:
			condString = f'{selectedRowIdentifier[0]} = {selectedRowIdentifier[1]}'
		elif len(selectedRowIdentifier) == 4:
			condString = f'{selectedRowIdentifier[0]} = {selectedRowIdentifier[1]} AND {selectedRowIdentifier[2]} = {selectedRowIdentifier[3]}'
		m.updateRow(selectedTable, condString, new_value_to_insert)
	except Exception as e:
		messagebox.showerror("Error", e)
		
	errorLabel.config(text="Edit Completed Successfully", fg='#20B519')
	clear_edit_frame()
	refreshTrees()


class btn:
	def __init__(self, text, command, i, frame=root) -> None:
		"""Initialize a button object

		Args:
			text (str): [description]
			command (str): [description]
			frame (str, optional): [description]. Defaults to root.
			side (str, optional): [description]. Defaults to 'top
			pady (int, optional): [description]. Defaults to 0.
		"""
		self.button = ttk.Button(frame, text=text, command=command)
		
		self.button.grid(row=1, column=i, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)


def errorMessage(func):
	"""Decorator for functins clicks.

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


def clear_edit_frame():
	global edit_frame,selectedCell
	if edit_frame:
		edit_frame.grab_release()
		edit_frame.destroy()


def selectTable():
	"""Selects and shows the table that pressed from the tables list.
	"""
	global selectedTable, selectedCell, selectedTableIndex, selectedRowIdentifier
	selectedCell = None
	selectedRowIdentifier = None
	clear_edit_frame()
	if tablesTree.focus() in tablesTree.get_children():
		selectedTableIndex = tablesTree.get_children().index(tablesTree.focus())
	curItem = tablesTree.item(tablesTree.focus())['values']
	if curItem:
		selectedTable = curItem[0]
		populateRowsTable(curItem[0])
		rowsTreeLabel.config(text=f'{selectedTable.capitalize()} Table', font=("Arial", 18))
	elif selectedTable:
		curItem = selectedTable
		populateRowsTable(curItem)
		rowsTreeLabel.config(text=f'{selectedTable.capitalize()} Table', font=("Arial", 18))
	else:
		populateRowsTable('')
		rowsTreeLabel.config(text='')

@errorMessage
def selectTableCell(e):
	"""Select a cell when pressed in the table tree

	Args:
		e (event): the event when pressing on a cell in the table
	"""
	global selectedCell, selectedRowIdentifier
	if selectedCell:
		clear_edit_frame()
	edit_input_frame(e)
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
	root.title("Database Manager")
	root.wm_attributes("-topmost", 1)
	
	style = ttk.Style()
	style.map('Treeview', foreground=fixed_map(style, "foreground"),
			  background=fixed_map(style, "background"))
	
	tablesFrame.pack(side='left', padx=5, fill=BOTH, expand=False)
	
	top_container.pack(side='top', padx=5, pady=10, fill=BOTH, expand=False, anchor=CENTER)
	low_container.pack(side='bottom', padx=5, pady=10, fill=BOTH, expand=False, anchor=CENTER)
	buttonsFrame.pack(side='left', padx=5, pady=10, fill=BOTH, expand=False)
	error_frame.pack(side='right', padx=5, pady=10, fill=BOTH, expand=False)
	rowsFrame.pack(side='top', padx=5, ipady=150, fill=BOTH, expand=False)


# @errorMessage
def import_tables() -> None:
	"""
	Import and insert rows of chosen table, row by row
	"""
	for x in tablesTree.get_children():
		tablesTree.delete(x)
	
	allPreTables = m.getPreTables()
	m.cursor.execute(constants.ALL_TABLES_QUERY)
	currentTables = m.cursor.fetchall()
	for row in allPreTables:
		if (row,) in currentTables:
			tablesTree.insert('', 'end', values=row, tags=('exists',))
		else:
			tablesTree.insert('', 'end', values=row, tags=('deleted',))


@errorMessage
def fillRowsTree(sql: str):
	"""Filling the rows of the rowsTree

	Args:
		sql (str): the SQL query we're using
	"""
	for x in rowsTree.get_children():
		rowsTree.delete(x)
	
	m.cursor.execute(sql)
	for row in m.cursor:
		row = ['' if v is None else v for v in row]
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
	errorLabel.config(text="Created Database From CSV Files Successfully", fg='#20B519')


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
		errorLabel.config(text="Created Table Successfully", fg='#20B519')
	else:
		errorLabel.config(text="No Table Was Selected.", fg='#D93232')


def dropTable():
	"""Drop the current table
	"""
	global tablesTree
	if selectedTable:
		m.dropTable(selectedTable)
		refreshTrees()
		errorLabel.config(text="Dropped Table Successfully", fg='#20B519')
	else:
		errorLabel.config(text="No Table Was Selected.", fg='#D93232')


def refreshTrees():
	"""Refresh and reshow all tables in the gui based on real time information.
	"""
	import_tables()
	selectTable()
	if selectedTableIndex:
		tablesTree.selection_set(tablesTree.get_children()[selectedTableIndex])
	errorLabel.config(text='')


@errorMessage
def deleteRow():
	"""Deletes the selected row
	"""
	global edit_frame
	if selectedTable != None and selectedCell != None:
		if len(selectedRowIdentifier) == 2:
			cond = selectedRowIdentifier[1]
		elif len(selectedRowIdentifier) == 4:
			cond = [selectedRowIdentifier[1], selectedRowIdentifier[3]]
		m.deleteRowFromTable(selectedTable, cond)
		refreshTrees()
		edit_frame.grab_release()
		edit_frame.destroy()
		errorLabel.config(text="Deleted Row Successfully", fg='#20B519')
	else:
		errorLabel.config(text="No Table/Cell Was Selected.", fg='#D93232')


@errorMessage
def createInputRowWindow():
	"""Create an input window in order to collect information to add a new row to the current table.
	"""
	
	if selectedTable is not None and not selectedCell:
		columns = m.getTableColumns(selectedTable)
		if len(columns) > 0:
			entries = buttom_frame_insert(columns)
			btn("Insert new row", lambda: addRowToTable(entries, edit_frame),0, frame=edit_frame)
		else:
			errorLabel.config(text="Table Has No Columns!", fg='#D93232')
	elif selectedCell:
		errorLabel.config(text="Cant add existing row.", fg='#D93232')
	else:
		errorLabel.config(text="Please choose Table.", fg='#D93232')
	

@errorMessage
def addRowToTable(entries, windowToDestroy):
	"""collect information to add a new row to the current table.

	Args:
		entries (dictionary): every entry that can be entered to a row in the current table
		windowToDestroy (Toplevel): The window that we'll destroy after adding the new row
	"""
	if not selectedCell:
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
		errorLabel.config(text="Row Inserted Successfully", fg='#20B519')


def init_buttons():
	functions = [deleteRow, createInputRowWindow, clearDb, createFocusedTable, dropTable]
	texts = ["Delete Row", "Add New Row", "Drop DataBase", "Import Table", "Drop Table"]
	i = 1
	for text, func in zip(texts, functions):
		btn(text, func, i, frame=buttonsFrame)
		i += 1


if __name__ == "__main__":
	initWindowAndConnection()
	init_buttons()
	init_rows_tree()
	init_tables_tree()
	
	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()
