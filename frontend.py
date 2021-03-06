from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import csv
import backend
import constants
from constants import error_messages as err_msgs
from constants import success_messages as success_msgs
from constants import warning_messages as warn_msgs
from constants import button_disable_dict,button_enable_dict

root = Tk()
root.minsize(1300, 800)
controller = backend.DataController('./chinook.db')

selected_table = None
selected_table_index = None
selected_row_id = None
selected_cell = None
db_dropped = False
total_tables = 0
deleted_counter = 0

#Buttons
buttons = []
create_button = None

# Frames Definition:
tables_frame = Frame(root, width=120)
table_data_frame = Frame(root, width=400)
top_container = Frame(root, width=800)
low_container = Frame(root, width=400, )
buttons_frame = Frame(top_container, width=400)
msgs_frame = Frame(top_container, width=1000)
edit_frame = None

# Labels Definition
table_label = Label(table_data_frame)
msg_label = Label(msgs_frame, font=("Arial", 15), wraplength=300)
msg_label.pack(side='top', padx=20)

# Trees Definition:
tables_tree = ttk.Treeview(tables_frame, columns='Tables', height=11, show="headings")
rows_tree = ttk.Treeview(table_data_frame, height=20, selectmode='browse')


class ButtonCustom:
	def __init__(self, btn_text: str, btn_command: str, i: int, frame=root) -> None:
		"""
				Initialize a button object

				Args:
						btn_text: text to appear on button
						btn_command: command to be executed upon click
						frame: which frame the button will be placed. Defaults to root.
		"""
		self.text = btn_text
		self.button = ttk.Button(frame, text=btn_text, command=btn_command)
		self.button.grid(row=1, column=i, padx=constants.BUTTON_PADX, ipady=3, ipadx=10)


def initialize_tree_table() -> None:
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


def initialize_tree_rows() -> None:
	# Vertical Scrool Bar
	vertical_scroll = ttk.Scrollbar(rows_tree, orient="vertical", command=rows_tree.yview)
	vertical_scroll.pack(side='right', fill='y')
	
	# Horizontal Scroll Bar
	horizontal_scroll = ttk.Scrollbar(rows_tree, orient="horizontal", command=rows_tree.xview)
	horizontal_scroll.pack(side='bottom', fill='x')
	
	rows_tree.tag_configure('exists', background='#80ffcc')
	rows_tree.tag_configure('deleted', background='#ff6666')
	
	table_label.pack(side='top', anchor='nw')
	rows_tree.pack(side='top', fill=BOTH, expand=True)
	rows_tree.bind('<ButtonRelease-1>', lambda e: select_table_row(e))  # used to give e
	
	rows_tree.configure(xscrollcommand=horizontal_scroll.set)
	rows_tree.configure(yscrollcommand=vertical_scroll.set)


def on_ignore():
	clear_edit_frame()


def bottom_frame_insert(columns: list, current_row: str = None, disable_flag: int = 0) -> dict:
	"""
			Inserting to the bottom frame
			Args:
				columns: which columns are relevant to the current table
				current_row: the selected row - presents its values
				disable_flag: which cell won't be changed (PK)
			Returns:
				Dictionary
	"""
	
	global edit_frame
	
	edit_frame = Frame(low_container, width=400)
	edit_frame.pack(side='top', padx=4, ipady=150)
	
	entries = {}
	row = 1
	
	for index, column in enumerate(columns):
		if index % 6 == 0:
			row += 4
		label = Label(edit_frame, text=column)
		label.grid(row=row, column=index % 6, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)
		edit_entry = Entry(edit_frame)
		edit_entry.grid(row=row + 1, column=index % 6, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)
		
		try:
			if column in constants.primary_key_dict[selected_table] and disable_flag:
				edit_entry.config(state='disabled')
			entries[column] = edit_entry.get
			if current_row:
				edit_entry.insert(0, current_row[index])
		except Exception as e:
			messagebox.showerror("Error", e)
	
	return entries


def edit_input_frame(event) -> None:
	"""
			Opens an edit section that allows the user to change values of the selected row
			Raises: Error if selected table is None/length of columns is 0 or smaller
			Returns: None
	"""
	global selected_table, edit_frame, selected_cell, selected_row_id
	
	if edit_frame:
		clear_edit_frame()
	
	col = int(rows_tree.identify_column(event.x)[1:]) - 1
	current_item = rows_tree.item(rows_tree.focus())['values']
	
	selected_cell = [rows_tree.column(col)["id"], str(
		current_item[col]).replace("'", "\'").replace('"', '\"')]
	try:
		if selected_table:
			columns = controller.get_all_columns(selected_table)
			if len(columns) > 0:
				entries = bottom_frame_insert(columns, current_row=current_item, disable_flag=1)
				ButtonCustom("Accept Changes", lambda: update_cell_value(entries), 0, frame=edit_frame)
				ButtonCustom("Ignore Changes", on_ignore, 2, frame=edit_frame)
			
			else:
				msg_label.config(text=err_msgs["empty_table"], anchor=CENTER)
		else:
			msg_label.config(text=err_msgs["no_tbl_selected"], anchor=CENTER)
	except Exception as error:
		messagebox.showerror("Error", error)


def update_cell_value(entries: dict) -> None:
	"""
			Updates the changed value of a specific row.
			ARGS:
				entries: the changed values of a row
			Raises:
				 Error if selected table is None/length of columns is 0 or smaller
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
		if controller.check_if_quotes_needed(selected_table, column):
			values[index] = f'"{values[index]}"'
	new_value_to_insert = ''
	for index, column in enumerate(columns):
		is_str = controller.check_if_quotes_needed(selected_table, column)
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
		controller.update_selected_row(
			selected_table, cond_string, new_value_to_insert)
	except Exception as error:
		messagebox.showerror("Error", error)
	
	msg_label.config(text=success_msgs["edit_completed"], fg='#20B519', anchor=CENTER)
	clear_edit_frame()
	present_new_trees()


def check_if_db_exists():
	global total_tables
	if deleted_counter == total_tables:
		msg_label.config(text=err_msgs["db_dropped"], fg='#D93232', anchor=CENTER)
		return False
	return True


def msg_decorator(function_to_be_wrapped):
	"""
			Decorator for functions that need try, except blocks.
			Args:
					function_to_be_wrapped: the same function we wrapped with the decorator
			Returns:
				function that we wrapped with this decorator
	"""
	def wrapped_func(*args, **kwargs):
		try:
			return function_to_be_wrapped(*args, **kwargs)
		except Exception as exception:
			msg_label.config(text=exception, fg='#D93232', anchor=CENTER)
	
	return wrapped_func


def on_closing():
	controller.stop_connection()
	root.destroy()


def cursor_highlight(style, option: str) -> list:
	return [element for element in style.map("Treeview", query_opt=option) if element[:2] != ("!disabled", "!selected")]


def clear_edit_frame() -> None:
	"""
			Clears the Edit section
	"""
	global edit_frame, selected_cell
	if edit_frame:
		edit_frame.grab_release()
		edit_frame.destroy()


@msg_decorator
def select_table() -> None:
	"""
			Upon table selection from table list -> presents the tables' values
	"""
	global selected_table, selected_cell, selected_table_index, selected_row_id
	clear_edit_frame()
	selected_cell = None
	selected_row_id = None
	if tables_tree.focus() in tables_tree.get_children():
		selected_table_index = tables_tree.get_children().index(tables_tree.focus())
	current_item = tables_tree.item(tables_tree.focus())['values']
	tags = tables_tree.item(tables_tree.focus())['tags']
	if 'deleted' in tags:
		disable_buttons(button_disable_dict["on_table_select_deleted"])
		enable_buttons(button_enable_dict["on_table_select_deleted"])
	elif 'exists' in tags:
		enable_buttons(button_enable_dict["on_table_select_enabled"])
		disable_buttons(button_disable_dict["on_table_select_enabled"])
	if current_item:
		selected_table = current_item[0]
		insert_table_rows(current_item[0])
		table_label.config(text=f'{selected_table.capitalize()} Table', font=("Arial", 18))
	elif selected_table:
		current_item = selected_table
		insert_table_rows(current_item)
		table_label.config(text=f'{selected_table.capitalize()} Table', font=("Arial", 18))
	else:
		insert_table_rows('')
		table_label.config(text='')


@msg_decorator
def select_table_row(event) -> None:
	"""
			Select a cell when pressed in the table tree

			Args:
					event (event): the event when pressing on a row in the table
	"""
	global selected_cell, selected_row_id
	try:
		if rows_tree.focus() == '':
			return
		if selected_cell:
			clear_edit_frame()
		current_item = rows_tree.item(rows_tree.focus())['values']
		if current_item == '':
			return
		col = int(rows_tree.identify_column(event.x)[1:]) - 1
		if selected_table != 'playlist_track' and selected_table != 'invoices':
			selected_row_id = [rows_tree.column(0)["id"], current_item[0]]
		else:
			selected_row_id = [rows_tree.column(0)["id"], current_item[0], rows_tree.column(1)["id"], current_item[1]]
		
		selected_cell = [rows_tree.column(col)["id"], str(current_item[col]).replace("'", "\'").replace('"', '\"')]
		edit_input_frame(event)
	except:
		return


def init_frames():
	"""
			Initiates key variables such as root, style, tables_frame, table_data_frame and buttons_frame.
	"""
	root.geometry("1200x800")
	root.title("Database Manager")
	root.wm_attributes("-topmost", 1)
	
	style = ttk.Style()
	style.map('Treeview', foreground=cursor_highlight(style, "foreground"),
	          background=cursor_highlight(style, "background"))
	
	tables_frame.pack(side='right', padx=5, pady=100, fill=BOTH, expand=False)
	top_container.pack(side='top', padx=5, pady=10, fill=BOTH, expand=False, anchor=CENTER)
	buttons_frame.grid(row=1, column=1, padx=5, pady=10)
	msgs_frame.grid(row=1, column=2, padx=5, pady=10)
	table_data_frame.pack(side='top', padx=5, ipady=150, fill=BOTH, expand=False)
	low_container.pack(side='bottom', padx=5, pady=10, fill=BOTH, expand=False, anchor=CENTER)


def import_tables() -> None:
	"""
		Import and insert rows of chosen table, row by row
	"""
	global deleted_counter, total_tables
	for x in tables_tree.get_children():
		tables_tree.delete(x)
	deleted_counter=0
	all_pred_tables = controller.get_pred_table()
	total_tables = len(all_pred_tables)
	controller.cursor.execute(constants.ALL_TABLES_QUERY)
	current_tables = controller.cursor.fetchall()
	for row in all_pred_tables:
		try:
			if (row,) in current_tables:
				tables_tree.insert('', 'end', values=row, tags=('exists',))
			else:
				tables_tree.insert('', 'end', values=row, tags=('deleted',))
				deleted_counter += 1
		except Exception as error:
			messagebox.showerror("Error", error)
	if deleted_counter == total_tables:
		disable_buttons(button_disable_dict["on_table_import"])
	if deleted_counter == 0:
		disable_buttons(button_disable_dict['on_table_import_full'])
		

@msg_decorator
def fill_rows(sql: str) -> None:
	"""
			Filling the rows of rows_tree with the sql parameter
			Args:
					sql (str): the SQL query we're using
	"""
	for x in rows_tree.get_children():
		rows_tree.delete(x)
	
	controller.cursor.execute(sql)
	for row in controller.cursor:
		row = ['' if v is None else v for v in row]
		rows_tree.insert('', 'end', values=row, tags=('exists',))


@msg_decorator
def insert_table_rows(current_table: str) -> None:
	"""
		Filling the specified columns of the selected table and afterwards filling the tables' rows.
		Args:
			current_table (str): Current table's name
	"""
	columns = tuple(controller.get_all_columns(current_table))
	rows_tree["columns"] = columns
	for column in columns:
		rows_tree.heading(column, text=column)
		rows_tree.column(column, minwidth=table_data_frame.winfo_width() // len(columns), width=100)
	
	rows_tree['show'] = 'headings'
	if columns:
		fill_rows(f"SELECT * FROM {current_table};")


def clear_database():
	"""
		Drops (clears) Database
	"""
	try:
		global selected_table, selected_cell
		controller.drop_database()
		present_new_trees()
		msg_label.config(text=success_msgs["clear_db"], fg='#20B519',anchor=CENTER)
		disable_buttons(button_disable_dict["on_clear_DB"])
		enable_buttons(button_enable_dict["on_clear_DB"])
	except Exception as e:
		msg_label.config(text=f'Could not clean DB - {e}')
		

def drop_table() -> None:
	"""
			Drop the current table (clears section that presents the selected table)
	"""
	global tables_tree, selected_table, selected_cell,create_button

	if selected_table:
		controller.drop_selected_table(selected_table)
		present_new_trees()
		disable_buttons(button_disable_dict["on_drop_table"])
		enable_buttons(button_enable_dict["on_drop_table"])
		msg_label.config(text=success_msgs["drop_tbl"], fg='#20B519', anchor=CENTER)
	else:
		msg_label.config(text=err_msgs["no_tbl_selected"], fg='#D93232', anchor=CENTER)


def drop_table_popup() -> None:
	"""
			Pop up window to confirm the users action
	"""
	if not selected_table:
		msg_label.config(text=err_msgs["no_tbl_selected"], fg='#D93232', anchor=CENTER)
		return
	
	message = messagebox.askquestion(f'Drop Table {selected_table} ', warn_msgs["drop_tbl_warning"],
	                                 icon='warning')
	if message == 'yes':
		drop_table()


def drop_db_popup() -> None:
	"""
			Pop up window to confirm the users action
	"""
	if db_dropped:
		msg_label.config(text=err_msgs["db_dropped"], fg='#D93232', anchor=CENTER)
		return
	message = messagebox.askquestion('WARNING! - Drop Data Base',
	                                 warn_msgs["drop_db_warning"],
	                                 icon='warning')
	if message == 'yes':
		clear_database()


def delete_row_popup() -> None:
	"""
		Pop up window to confirm the users action
	"""
	if not check_if_db_exists():
		return

	if not selected_table:
		msg_label.config(text=err_msgs["row_dlt_no_tbl"], fg='#D93232', anchor=CENTER)
		return
	if not selected_cell:
		msg_label.config(text=err_msgs["no_row_selected"], fg='#D93232', anchor=CENTER)
		return
	message = messagebox.askquestion('Delete Row', warn_msgs["row_delete_warning"],
	                                 icon='warning')
	if message == 'yes':
		delete_entire_row()


def present_new_trees() -> None:
	"""
		Refresh and present all tables in the GUI based on updated information.
	"""
	import_tables()
	select_table()
	
	if selected_table_index:
		tables_tree.selection_set(tables_tree.get_children()[selected_table_index])
	msg_label.config(text='')


@msg_decorator
def delete_entire_row() -> None:
	"""
		Deletes the selected row
	"""
	global edit_frame
	
	if selected_table is not None and selected_cell is not None:
		if len(selected_row_id) == 2:
			cond = selected_row_id[1]
		elif len(selected_row_id) == 4:
			cond = [selected_row_id[1], selected_row_id[3]]
		controller.delete_selected_row_in_table(selected_table, cond)
		present_new_trees()
		edit_frame.grab_release()
		edit_frame.destroy()
		msg_label.config(text=success_msgs["delete_row"], fg='#20B519', anchor=CENTER)
	else:
		msg_label.config(text=err_msgs["row_dlt_no_tbl"], fg='#D93232', anchor=CENTER)


@msg_decorator
def add_new_row() -> None:
	"""
			Create an input section which enables the user to change a rows information.
	"""
	if not check_if_db_exists():
		return

	if edit_frame:
		clear_edit_frame()
	if selected_table:
		columns = controller.get_all_columns(selected_table)
		if len(columns) > 0:
			entries = bottom_frame_insert(columns)
			ButtonCustom("Insert new row", lambda: insert_new_row_to_table(entries, edit_frame), 0, frame=edit_frame)
		else:
			msg_label.config(text=err_msgs["empty_table"], fg='#D93232', anchor=CENTER)
	elif selected_cell:
		msg_label.config(text=err_msgs["uncheck_before_insret"], fg='#D93232', anchor=CENTER)
	else:
		msg_label.config(text=err_msgs["row_add_no_tbl"], fg='#D93232', anchor=CENTER)


def return_to_default() -> None:
	global selected_table
	if selected_table:
		selected_table = None
	present_new_trees()


@msg_decorator
def insert_new_row_to_table(entries: dict, close_frame) -> None:
	"""
		Gets user input to insert the relevant data to be added to the new row
		Args:
			entries: every entry that can be entered to a row in the current table
			close_frame: The frame to be closed after finished adding
	"""
	columns = []
	values = []
	for column, entry in entries.items():
		columns.append(column)
		values.append(entry())
	# remove_indexes = [index for index, value in enumerate(values) if value == '']
	for index, column in enumerate(columns):
		if controller.check_if_quotes_needed(selected_table, column):
			values[index] = f'"{values[index]}"'
		elif controller.check_if_quotes_needed(selected_table, column) == 2:
				values[index] = 0
	
	controller.add_new_row_to_table(selected_table, columns, values)
	close_frame.grab_release()
	close_frame.destroy()
	present_new_trees()
	msg_label.config(
		text=success_msgs["row_insert"], fg='#20B519', anchor=CENTER)


def create_database() -> None:
	"""
		After the database (or a specific table) has been dropped, enables the user to create the database (or table)
		from scratch
	"""
	try:
		global deleted_counter
		all_pred_tables = controller.get_pred_table()
		for table in all_pred_tables:
			controller.create_table_from_csv(table)
		present_new_trees()
		disable_buttons(button_disable_dict["on_create_DB"])
		enable_buttons(button_enable_dict["on_create_DB"])
		deleted_counter = 0
	except:
		return
	

def create_table():
	if selected_table:
		controller.create_table_from_csv(selected_table)
		enable_buttons(button_enable_dict["on_create_table"])
		disable_buttons(button_disable_dict["on_create_table"])
		present_new_trees()
		msg_label.config(text=success_msgs["creat_tbl"],fg='#20B519', anchor=CENTER)
	else:
		msg_label.config(text=warn_msgs["create_tbl_warning"],fg='#D93232', anchor=CENTER)
		pass


def disable_buttons(btns):
	global buttons
	for btn in buttons:
		if btn.text in btns:
			btn.button.state(["disabled"])


def enable_buttons(btns):
	global buttons
	for btn in buttons:
		if btn.text in btns:
			btn.button.state(["!disabled"])


def init_buttons() -> None:
	global buttons,create_button
	functions = [delete_row_popup, add_new_row, drop_table_popup,drop_db_popup, return_to_default, create_database, create_table]
	texts = ['Delete Row', 'Add New Row', 'Drop Table', 'Drop DataBase', 'Default View', 'Create DataBase', 'Create Table']
	i = 1
	for text, func in zip(texts, functions):
		btn = ButtonCustom(text, func, i, frame=buttons_frame)
		buttons.append(btn)
		i += 1


if __name__ == "__main__":
	init_frames()
	init_buttons()
	initialize_tree_rows()
	initialize_tree_table()
	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()
