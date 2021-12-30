from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import backend
import constants

root = Tk()
root.minsize(1200, 800)

# Frames:
tablesFrame = Frame(root, width=120)
rowsFrame = Frame(root, width=400)
top_container = Frame(root, width=800)
low_container = Frame(root, width=400)
buttonsFrame = Frame(top_container, width=400)
error_frame = Frame(top_container, width=1000)
edit_frame = None

# Trees:
tablesTree = ttk.Treeview(tablesFrame, columns='Tables', height=11, show="headings")
rowsTree = ttk.Treeview(rowsFrame, height=20, selectmode='browse')

# Labels
errorLabel = Label(error_frame, font=("Arial", 15), wraplength=400)
errorLabel.pack(side='top', padx=20)
rowsTreeLabel = Label(rowsFrame)

selectedTable = None
selectedTableIndex = None
selectedRowIdentifier = None
selectedCell = None

controller = backend.DataController('./chinook.db')


class Button_c:
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
		self.button.grid(row=1, column=i, padx=constants.BUTTON_PADX, ipady=3, ipadx=10)


def init_tables_tree() -> None:
	"""Initialize rows tree.

	Returns:
		Treeview: The initialize tables tree.
	"""
	tablesTree.tag_configure('exists', font=('Helvetica', 10), background='#1a6600', foreground='white')
	tablesTree.tag_configure('deleted', font=('Helvetica', 10), background='#ff6666', foreground='white')
	tablesTree.pack(side='top', fill=BOTH)
	tablesTree.heading('Tables', text="Tables")
	tablesTree.column('Tables', width=100, anchor=CENTER)
	tablesTree.bind('<ButtonRelease-1>', lambda e: selectTable()) 
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


def on_ignore():
	clear_edit_frame()


def buttom_frame_insert(columns, current_row=None, disable_flag=0):
	global edit_frame
	edit_frame = Frame(low_container, width=400)
	edit_frame.pack(side='bottom', padx=4, ipady=150, fill=BOTH, expand=False)
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
	if edit_frame:
		clear_edit_frame()
	curItem = rowsTree.item(rowsTree.focus())['values']
	col = int(rowsTree.identify_column(e.x)[1:]) - 1
	selectedCell = [rowsTree.column(col)["id"], str(curItem[col]).replace("'", "\'").replace('"', '\"')]
	if selectedTable:
		columns = controller.getTableColumns(selectedTable)
		if len(columns) > 0:
			entries = buttom_frame_insert(columns, current_row=curItem, disable_flag=1)
			Button_c("Accept Changes", lambda: updateValue(entries), 0, frame=edit_frame)
			Button_c("Ignore Changes", on_ignore, 2, frame=edit_frame)

		else:
			errorLabel.config(text="Table Has No Columns!", anchor=CENTER)
	else:
		errorLabel.config(text="No Table Was Selected.", anchor=CENTER)


def updateValue(entries):
	columns = []
	values = []
	for c, e in entries.items():
		columns.append(c)
		values.append(e())
	remove_list = [i for i, value in enumerate(values) if value == '']
	for i in sorted(remove_list, reverse=True):
		del columns[i]

	new_value_to_insert = ''
	for i, col in enumerate(columns):
		quotes_needed = controller.check_if_quotes_needed(selectedTable, col)
		if quotes_needed:
			if not i == len(columns) - 1:
				new_value_to_insert += f'{col} = "{entries[col]()}",\n'
			else:
				new_value_to_insert += f'{col} = "{entries[col]()}"'
		else:
			if not i == len(columns) - 1:
				new_value_to_insert += f'{col} = {entries[col]()},\n'
			else:
				new_value_to_insert += f'{col} = {entries[col]()}'
	try:
		if len(selectedRowIdentifier) == 2:
			condition_to_query = f'{selectedRowIdentifier[0]} = {selectedRowIdentifier[1]}'
		elif len(selectedRowIdentifier) == 4:
			condition_to_query = f'{selectedRowIdentifier[0]} = {selectedRowIdentifier[1]} AND {selectedRowIdentifier[2]} = ' \
						 f'{selectedRowIdentifier[3]}'
		controller.updateRow(selectedTable, condition_to_query, new_value_to_insert)
	except Exception as e:
		messagebox.showerror("Error", e)

	errorLabel.config(text="Edit Completed Successfully", fg='#20B519', anchor=CENTER)
	clear_edit_frame()
	refreshTrees()


def error_decorator(func):
	"""Decorator for functins clicks.

		Args:
			func (function): the function we're decorating
	"""

	def inner(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as e:
			errorLabel.config(text=e, fg='#D93232', anchor=CENTER)

	return inner


def on_closing():
	controller.dropConn()
	root.destroy()


def fixed_map(style, option) -> dict:
	"""
	
	Params:
	style: style.map
	option:
	"""
	return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]


def clear_edit_frame():
	global edit_frame, selectedCell
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


@error_decorator
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
	if selectedTable != 'playlist_track' and selectedTable != 'invoices':
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
	style.map('Treeview', foreground=fixed_map(style, "foreground"), background=fixed_map(style, "background"))

	tablesFrame.pack(side='right', padx=5,pady=90, fill=BOTH, expand=False)
	top_container.pack(side='top', padx=5, pady=10, fill=BOTH, expand=False, anchor=CENTER)
	low_container.pack(side='bottom', padx=5, pady=10, fill=BOTH, expand=False, anchor=CENTER)
	buttonsFrame.pack(side='left', padx=5, pady=10, fill=BOTH, expand=False)
	error_frame.pack(side='left', padx=5, pady=10, fill=BOTH, expand=False)
	rowsFrame.pack(side='top', padx=5, ipady=150, fill=BOTH, expand=False)


def import_tables():
	"""
	Import and insert rows of chosen table, row by row
	"""
	for x in tablesTree.get_children():
		tablesTree.delete(x)

	allPreTables = controller.getPreTables()
	controller.cursor.execute(constants.ALL_TABLES_QUERY)
	currentTables = controller.cursor.fetchall()
	for row in allPreTables:
		if (row,) in currentTables:
			tablesTree.insert('', 'end', values=row, tags=('exists',))
		else:
			tablesTree.insert('', 'end', values=row, tags=('deleted',))


@error_decorator
def fillRowsTree(sql: str):
	"""Filling the rows of the rowsTree

	Args:
		sql (str): the SQL query we're using
	"""
	for x in rowsTree.get_children():
		rowsTree.delete(x)

	controller.cursor.execute(sql)
	for row in controller.cursor:
		row = ['' if v is None else v for v in row]
		rowsTree.insert('', 'end', values=row, tags=('exists',))


@error_decorator
def populateRowsTable(currTable: str):
	"""Filling the columns of the rowsTree before calling fillRowsTree(sql) to fill the rows right after.

	Args:
		currTable (str): Current table's name
	"""
	columns = tuple(controller.getTableColumns(currTable))
	rowsTree["columns"] = columns
	for c in columns:
		rowsTree.heading(c, text=c)
		rowsTree.column(c, minwidth=rowsFrame.winfo_width() // len(columns), width=100)

	rowsTree['show'] = 'headings'
	if columns:
		fillRowsTree(f"SELECT * FROM {currTable};")

@error_decorator
def createDB():
	"""Creates the database from the CSV files.
	"""
	controller.createDatabaseFromCSV()
	refreshTrees()
	errorLabel.config(text="Created Database From CSV Files Successfully", fg='#20B519', anchor=CENTER)

def clearDb():
	"""Drops Database
	"""
	controller.clear()
	refreshTrees()
	errorLabel.config(text="Cleared DB Successfully", anchor=CENTER)

def dropTable():
	"""Drop the current table
	"""
	global tablesTree
	if selectedTable:
		controller.dropTable(selectedTable)
		refreshTrees()
		errorLabel.config(text="Dropped Table Successfully", fg='#20B519', anchor=CENTER)
	else:
		errorLabel.config(text="No Table Was Selected.", fg='#D93232', anchor=CENTER)

def open_drop_tbl_popup():
	if not selectedTable:
		errorLabel.config(text="No Table Was Selected.", fg='#D93232', anchor=CENTER)
		return

	MsgBox = messagebox.askquestion(f'Drop Table {selectedTable} ', 'Are you sure you want to drop this table ?',
									   icon='warning')
	if MsgBox == 'yes':
		dropTable()


def open_drop_db_popup():
	MsgBox = messagebox.askquestion('WARNING! - Drop Data Base', 'All tables will be deleted.\nAre you sure you want to drop the database?',
									   icon='warning')
	if MsgBox == 'yes':
		clearDb()

def open_delete_row_popup():
	if not selectedTable:
		errorLabel.config(text="In order to delete a row, you need to select a table first", fg='#D93232', anchor=CENTER)
		return
	if not selectedCell:
		errorLabel.config(text="No row was selected", fg='#D93232', anchor=CENTER)
		return
	MsgBox = messagebox.askquestion('Delete Row', 'Are you sure you want to delete the selected row?',
									   icon='warning')
	if MsgBox == 'yes':
		deleteRow()


def refreshTrees():
	"""Refresh and reshow all tables in the gui based on real time information.
	"""
	import_tables()
	selectTable()
	if selectedTableIndex:
		tablesTree.selection_set(tablesTree.get_children()[selectedTableIndex])
	errorLabel.config(text='')


def restore_db():
	pass


@error_decorator
def deleteRow():
	"""Deletes the selected row
	"""
	global edit_frame
	if selectedTable is not None and selectedCell is not None:
		if len(selectedRowIdentifier) == 2:
			cond = selectedRowIdentifier[1]
		elif len(selectedRowIdentifier) == 4:
			cond = [selectedRowIdentifier[1], selectedRowIdentifier[3]]
		controller.deleteRowFromTable(selectedTable, cond)
		refreshTrees()
		edit_frame.grab_release()
		edit_frame.destroy()
		errorLabel.config(text="Deleted Row Successfully", fg='#20B519', anchor=CENTER)
	else:
		errorLabel.config(text="In order to delete a row, you need to select a table first", fg='#D93232', anchor=CENTER)


@error_decorator
def createInputRowWindow():
	"""Create an input window in order to collect information to add a new row to the current table.
	"""
	if edit_frame:
		clear_edit_frame()
	if selectedTable is not None and not selectedCell:
		columns = controller.getTableColumns(selectedTable)
		if len(columns) > 0:
			entries = buttom_frame_insert(columns)
			Button_c("Insert new row", lambda: addRowToTable(entries, edit_frame), 0, frame=edit_frame)
		else:
			errorLabel.config(text="Table Has No Columns!", fg='#D93232', anchor=CENTER)
	elif selectedCell:
		errorLabel.config(text="Cant add existing row", fg='#D93232', anchor=CENTER)
	else:
		errorLabel.config(text="In order to add a row, you need to select a table first", fg='#D93232', anchor=CENTER)


def return_to_default():
	global selectedTable
	if selectedTable:
		selectedTable = None
	refreshTrees()
	
	
@error_decorator
def addRowToTable(entries, window_to_close):
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
			if controller.check_if_quotes_needed(selectedTable, c):
				values[i] = f'"{values[i]}"'
		controller.insertRowToTable(selectedTable, columns, values)
		window_to_close.grab_release()
		window_to_close.destroy()
		refreshTrees()
		errorLabel.config(text="Row Inserted Successfully", fg='#20B519', anchor=CENTER)


def init_buttons():
	functions = [open_delete_row_popup, createInputRowWindow, open_drop_db_popup, restore_db, open_drop_tbl_popup,return_to_default]
	texts = ["Delete Row", "Add New Row", "Drop DataBase","Restore DataBase", "Drop Table", 'Default View']
	i = 1
	for text, func in zip(texts, functions):
		Button_c(text, func, i, frame=buttonsFrame)
		i += 1


if __name__ == "__main__":
	initWindowAndConnection()
	init_buttons()
	init_rows_tree()
	init_tables_tree()
	print('hi')
	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()
