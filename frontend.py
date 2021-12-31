from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import backend
import constants

root = Tk()
root.minsize(1200, 800)

# Frames Definition:
tables_frame = Frame(root, width=120)
rows_frame = Frame(root, width=400)
top_container = Frame(root, width=800)
low_container = Frame(root, width=400)
buttons_frame = Frame(top_container, width=400)
error_frame = Frame(top_container, width=1000)
edit_frame = None

# Trees Definition:
tables_tree = ttk.Treeview(tables_frame, columns='Tables', height=11, show="headings")
rows_tree = ttk.Treeview(rows_frame, height=20, selectmode='browse')

# Labels Definition
error_label = Label(error_frame, font=("Arial", 15), wraplength=400)
error_label.pack(side='top', padx=20)
rows_tree_label = Label(rows_frame)

selected_table = None
selected_table_index = None
selected_row_id = None
selected_cell = None

controller = backend.DataController('./chinook.db')


class Button_c:
	def __init__(self, text: str, command: str, i: int, frame=root) -> None:
		"""
			Initialize a button object

			Args:
				text (str): text to appear on button
				command (str): command to be executed upon click
				frame (str, optional): which frame the button will be placed. Defaults to root.
		"""
		self.button = ttk.Button(frame, text=text, command=command)
		self.button.grid(row=1, column=i, padx=constants.BUTTON_PADX, ipady=3, ipadx=10)


def init_tables_tree() -> None:
	"""
		Initialize table tree
	"""

	tables_tree.heading('Tables', text="Tables")
	tables_tree.column('Tables', width=100, anchor=CENTER)

	tables_tree.tag_configure('exists', font=('Helvetica', 10), background='#1a6600', foreground='white')
	tables_tree.tag_configure('deleted', font=('Helvetica', 10), background='#ff6666', foreground='white')

	tables_tree.pack(side='top', fill=BOTH)
	tables_tree.bind('<ButtonRelease-1>', lambda e: select_table())

	import_tables()


def init_rows_tree() -> None:
	"""
		Initialize rows tree
	"""

	# Vertical Scrool Bar
	vertical_scroll = ttk.Scrollbar(rows_tree, orient="vertical", command=rows_tree.yview)
	vertical_scroll.pack(side='right', fill='y')

	# Horizontal Scroll Bar
	horizontal_scroll = ttk.Scrollbar(rows_tree, orient="horizontal", command=rows_tree.xview)
	horizontal_scroll.pack(side='bottom', fill='x')

	rows_tree.tag_configure('exists', background='cyan')
	rows_tree.tag_configure('deleted', background='red')

	rows_tree_label.pack(side='top', anchor='nw')
	rows_tree.pack(side='top', fill=BOTH, expand=True)
	rows_tree.bind('<ButtonRelease-1>', lambda e: select_table_cell(e))  # used to give e

	rows_tree.configure(xscrollcommand=horizontal_scroll.set)
	rows_tree.configure(yscrollcommand=vertical_scroll.set)


def on_ignore():
	clear_edit_frame()


def bottom_frame_insert(columns: list, current_row: str = None, disable_flag: int = 0) -> dict:
	"""
		Inserting to the bottom frame
	"""

	global edit_frame

	edit_frame = Frame(low_container, width=400)
	edit_frame.pack(side='bottom', padx=4, ipady=150, fill=BOTH, expand=False)

	entries = {}
	row = 1

	for index, column in enumerate(columns):
		if index % 6 == 0:
			row += 4
		l = Label(edit_frame, text=column)
		l.grid(row=row, column=index % 6, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)
		edit_entry = Entry(edit_frame)
		edit_entry.grid(row=row + 1, column=index % 6, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)

		try:
			if column in constants.tables_where_SQL[selected_table] and disable_flag:
				edit_entry.config(state='disabled')
			entries[column] = edit_entry.get
			if current_row:
				edit_entry.insert(0, current_row[index])
		except Exception as e:
			messagebox.showerror("Error", e)

	return entries


def edit_input_frame(e) -> None:
	"""
		Creation of a new window which allows the user to change values of a selected row.
		Raises: Error if selected table is None/length of columns is 0 or smaller
		Returns: None
	"""
	global selected_table, edit_frame, selected_cell, selected_row_id

	if edit_frame:
		clear_edit_frame()

	col = int(rows_tree.identify_column(e.x)[1:]) - 1
	current_item = rows_tree.item(rows_tree.focus())['values']

	selected_cell = [rows_tree.column(col)["id"], str(current_item[col]).replace("'", "\'").replace('"', '\"')]
	try:
		if selected_table:
			columns = controller.getTableColumns(selected_table)
			if len(columns) > 0:
				entries = bottom_frame_insert(columns, current_row=current_item, disable_flag=1)
				Button_c("Accept Changes", lambda: update_value(entries), 0, frame=edit_frame)
				Button_c("Ignore Changes", on_ignore, 2, frame=edit_frame)

			else:
				error_label.config(text="Table Has No Columns!", anchor=CENTER)
		else:
			error_label.config(text="No Table Was Selected.", anchor=CENTER)
	except Exception as error:
		messagebox.showerror("Error", error)


def update_value(entries: dict) -> None:
	"""
		Updates the selected value of a cell of a specific row.
		Raises: Error if selected table is None/length of columns is 0 or smaller
	"""
	columns = []
	values = []
	for column, entry in entries.items():
		columns.append(column)
		values.append(entry())
	remove_indexes = [index for index, value in enumerate(values) if value == '']
	for index in sorted(remove_indexes, reverse=True):
		del columns[index]
		del values[index]

	for index, column in enumerate(columns):
		if controller.checkIfStr(selected_table, column):
			values[index] = f'"{values[index]}"'
	new_value_to_insert = ''
	for index, column in enumerate(columns):
		is_str = controller.checkIfStr(selected_table, column)
		if is_str:
			if not index == len(columns) - 1:
				new_value_to_insert += f'{column} = "{entries[column]()}",\n'
			else:
				new_value_to_insert += f'{column} = "{entries[column]()}"'
		else:
			if not index == len(columns) - 1:
				new_value_to_insert += f'{column} = {entries[column]()},\n'
			else:
				new_value_to_insert += f'{column} = {entries[column]()}'

	try:
		if len(selected_row_id) == 2:
			cond_string = f'{selected_row_id[0]} = {selected_row_id[1]}'
		elif len(selected_row_id) == 4:
			cond_string = f'{selected_row_id[0]} = {selected_row_id[1]} AND {selected_row_id[2]} = ' \
				f'{selected_row_id[3]}'
		controller.updateRow(selected_table, cond_string, new_value_to_insert)
	except Exception as error:
		messagebox.showerror("Error", error)

	error_label.config(text="Edit Completed Successfully", fg='#20B519', anchor=CENTER)
	clear_edit_frame()
	refreshTrees()


def error_decorator(func) -> function:
	"""
		Decorator for functions clicks.
		Args:
			func (function): the function we're decorating
		Returns: function
	"""

	def inner(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as e:
			error_label.config(text=e, fg='#D93232', anchor=CENTER)

	return inner


def on_closing():
	controller.dropConn()
	root.destroy()


def fixed_map(style, option: str) -> list:
	return [element for element in style.map("Treeview", query_opt=option) if element[:2] != ("!disabled", "!selected")]


def clear_edit_frame() -> None:
	"""
		Clears the Edit window
	"""
	global edit_frame, selected_cell
	if edit_frame:
		edit_frame.grab_release()
		edit_frame.destroy()


@error_decorator
def select_table() -> None:
	"""
		Upon table selection from table list -> presents the tables' values
	"""
	global selected_table, selected_cell, selected_table_index, selected_row_id
	clear_edit_frame()

	selected_cell = None
	selected_row_id = None
	try:
		if tables_tree.focus() in tables_tree.get_children():
			selected_table_index = tables_tree.get_children().index(tables_tree.focus())
		current_item = tables_tree.item(tables_tree.focus())['values']
		if current_item:
			selected_table = current_item[0]
			populate_rows_table(current_item[0])
			rows_tree_label.config(text=f'{selected_table.capitalize()} Table', font=("Arial", 18))
		elif selected_table:
			current_item = selected_table
			populate_rows_table(current_item)
			rows_tree_label.config(text=f'{selected_table.capitalize()} Table', font=("Arial", 18))
		else:
			populate_rows_table('')
			rows_tree_label.config(text='')
	except Exception as error:
		messagebox.showerror("Error", error)


@error_decorator
def select_table_cell(e) -> None:
	"""
		Select a cell when pressed in the table tree

		Args:
			e (event): the event when pressing on a cell in the table
	"""
	global selected_cell, selected_row_id
	if selected_cell:
		clear_edit_frame()
	edit_input_frame(e)
	current_item = rows_tree.item(rows_tree.focus())['values']
	if current_item == '':
		return
	col = int(rows_tree.identify_column(e.x)[1:]) - 1
	if selected_table != 'playlist_track' and selected_table != 'invoices':
		selected_row_id = [rows_tree.column(0)["id"], current_item[0]]
	else:
		selected_row_id = [rows_tree.column(
			0)["id"], current_item[0], rows_tree.column(1)["id"], current_item[1]]
	selected_cell = [rows_tree.column(col)["id"], str(
		current_item[col]).replace("'", "\'").replace('"', '\"')]


def initWindowAndConnection():
	"""Initiates key variables such as root, style, tables_frame, rows_frame and buttons_frame.
	"""
	root.geometry("1200x800")
	root.title("Database Manager")
	root.wm_attributes("-topmost", 1)

	style = ttk.Style()
	style.map('Treeview', foreground=fixed_map(style, "foreground"), background=fixed_map(style, "background"))

	tables_frame.pack(side='right', padx=5, pady=90, fill=BOTH, expand=False)
	top_container.pack(side='top', padx=5, pady=10, fill=BOTH, expand=False, anchor=CENTER)
	low_container.pack(side='bottom', padx=5, pady=10, fill=BOTH, expand=False, anchor=CENTER)
	buttons_frame.pack(side='left', padx=5, pady=10, fill=BOTH, expand=False)
	error_frame.pack(side='left', padx=5, pady=10, fill=BOTH, expand=False)
	rows_frame.pack(side='top', padx=5, ipady=150, fill=BOTH, expand=False)


def import_tables():
	"""
		Import and insert rows of chosen table, row by row
	"""
	for x in tables_tree.get_children():
		tables_tree.delete(x)

	allPreTables = controller.getPreTables()
	controller.cursor.execute(constants.ALL_TABLES_QUERY)
	currentTables = controller.cursor.fetchall()
	for row in allPreTables:
		if (row,) in currentTables:
			tables_tree.insert('', 'end', values=row, tags=('exists',))
		else:
			tables_tree.insert('', 'end', values=row, tags=('deleted',))


@error_decorator
def fillRowsTree(sql: str):
	"""Filling the rows of the rows_tree

	Args:
		sql (str): the SQL query we're using
	"""
	for x in rows_tree.get_children():
		rows_tree.delete(x)

	controller.cursor.execute(sql)
	for row in controller.cursor:
		row = ['' if v is None else v for v in row]
		rows_tree.insert('', 'end', values=row, tags=('exists',))


@error_decorator
def populate_rows_table(currTable: str):
	"""
		Filling columns of the rows_tree before calling fillRowsTree(sql) to fill the rows right after.
		Args:
			currTable (str): Current table's name
	"""
	columns = tuple(controller.getTableColumns(currTable))
	rows_tree["columns"] = columns
	for c in columns:
		rows_tree.heading(c, text=c)
		rows_tree.column(c, minwidth=rows_frame.winfo_width() // len(columns), width=100)

	rows_tree['show'] = 'headings'
	if columns:
		fillRowsTree(f"SELECT * FROM {currTable};")

@error_decorator
def createDB():
	"""Creates the database from the CSV files.
	"""
	controller.createDatabaseFromCSV()
	refreshTrees()
	error_label.config(text="Created Database From CSV Files Successfully", fg='#20B519', anchor=CENTER)

def clearDb():
	"""Drops Database
	"""
	controller.clear()
	refreshTrees()
	error_label.config(text="Cleared DB Successfully", anchor=CENTER)

def dropTable():
	"""Drop the current table
	"""
	global tables_tree
	if selected_table:
		controller.dropTable(selected_table)
		refreshTrees()
		error_label.config(text="Dropped Table Successfully", fg='#20B519', anchor=CENTER)
	else:
		error_label.config(text="No Table Was Selected.", fg='#D93232', anchor=CENTER)

def open_drop_tbl_popup():
	if not selected_table:
		error_label.config(text="No Table Was Selected.", fg='#D93232', anchor=CENTER)
		return

	MsgBox = messagebox.askquestion(f'Drop Table {selected_table} ', 'Are you sure you want to drop this table ?',
									   icon='warning')
	if MsgBox == 'yes':
		dropTable()


def open_drop_db_popup():
	MsgBox = messagebox.askquestion('WARNING! - Drop Data Base', 'All tables will be deleted.\nAre you sure you want to drop the database?',
									   icon='warning')
	if MsgBox == 'yes':
		clearDb()

def open_delete_row_popup():
	if not selected_table:
		error_label.config(text="In order to delete a row, you need to select a table first", fg='#D93232', anchor=CENTER)
		return
	if not selected_cell:
		error_label.config(text="No row was selected", fg='#D93232', anchor=CENTER)
		return
	MsgBox = messagebox.askquestion('Delete Row', 'Are you sure you want to delete the selected row?',
									   icon='warning')
	if MsgBox == 'yes':
		deleteRow()


def refreshTrees():
	"""Refresh and reshow all tables in the gui based on real time information.
	"""
	import_tables()
	select_table()
	if selected_table_index:
		tables_tree.selection_set(tables_tree.get_children()[selected_table_index])
	error_label.config(text='')


def restore_db():
	pass


@error_decorator
def deleteRow():
	"""Deletes the selected row
	"""
	global edit_frame
	if selected_table is not None and selected_cell is not None:
		if len(selected_row_id) == 2:
			cond = selected_row_id[1]
		elif len(selected_row_id) == 4:
			cond = [selected_row_id[1], selected_row_id[3]]
		controller.deleteRowFromTable(selected_table, cond)
		refreshTrees()
		edit_frame.grab_release()
		edit_frame.destroy()
		error_label.config(text="Deleted Row Successfully", fg='#20B519', anchor=CENTER)
	else:
		error_label.config(text="In order to delete a row, you need to select a table first", fg='#D93232', anchor=CENTER)


@error_decorator
def createInputRowWindow():
	"""Create an input window in order to collect information to add a new row to the current table.
	"""
	if edit_frame:
		clear_edit_frame()
	if selected_table is not None and not selected_cell:
		columns = controller.getTableColumns(selected_table)
		if len(columns) > 0:
			entries = bottom_frame_insert(columns)
			Button_c("Insert new row", lambda: addRowToTable(entries, edit_frame), 0, frame=edit_frame)
		else:
			error_label.config(text="Table Has No Columns!", fg='#D93232', anchor=CENTER)
	elif selected_cell:
		error_label.config(text="Cant add existing row", fg='#D93232', anchor=CENTER)
	else:
		error_label.config(text="In order to add a row, you need to select a table first", fg='#D93232', anchor=CENTER)


def return_to_default():
	global selected_table
	if selected_table:
		selected_table = None
	refreshTrees()
	
	
@error_decorator
def addRowToTable(entries, window_to_close):
	"""collect information to add a new row to the current table.

	Args:
		entries (dictionary): every entry that can be entered to a row in the current table
		windowToDestroy (Toplevel): The window that we'll destroy after adding the new row
	"""
	if not selected_cell:
		columns = []
		values = []
		for c, e in entries.items():
			columns.append(c)
			values.append(e())
		remove_indexes = [i for i, v in enumerate(values) if v == '']
		for i in sorted(remove_indexes, reverse=True):
			del columns[i]
			del values[i]

		for i, c in enumerate(columns):
			if controller.check_if_quotes_needed(select_table, c):
				values[i] = f'"{values[i]}"'
		controller.insertRowToTable(select_table, columns, values)
		window_to_close.grab_release()
		window_to_close.destroy()
		refreshTrees()
		error_label.config(text="Row Inserted Successfully", fg='#20B519', anchor=CENTER)


def init_buttons():
	functions = [open_delete_row_popup, createInputRowWindow, open_drop_db_popup, restore_db, open_drop_tbl_popup,return_to_default]
	texts = ["Delete Row", "Add New Row", "Drop DataBase","Restore DataBase", "Drop Table", 'Default View']
	i = 1
	for text, func in zip(texts, functions):
		Button_c(text, func, i, frame=buttons_frame)
		i += 1


if __name__ == "__main__":
	initWindowAndConnection()
	init_buttons()
	init_rows_tree()
	init_tables_tree()
	print('hi')
	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()
