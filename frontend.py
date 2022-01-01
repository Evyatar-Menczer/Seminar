from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import backend
import constants
from constants import error_messages as err_msgs
from constants import success_messages as success_msgs
from constants import warning_messages as warn_msgs


root = Tk()
root.minsize(1200, 800)

# Frames Definition:
tables_frame = Frame(root, width=120)
rows_frame = Frame(root, width=400)
top_container = Frame(root, width=800)
low_container = Frame(root, width=400,)
buttons_frame = Frame(top_container, width=400)
error_frame = Frame(top_container, width=1000)
edit_frame = None

# Labels Definition
error_label = Label(error_frame, font=("Arial", 15), wraplength=300)
error_label.pack(side='top', padx=20)
rows_tree_label = Label(rows_frame)

# Trees Definition:
tables_tree = ttk.Treeview(
    tables_frame, columns='Tables', height=11, show="headings")
rows_tree = ttk.Treeview(rows_frame, height=20, selectmode='browse')

selected_table = None
selected_table_index = None
selected_row_id = None
selected_cell = None

controller = backend.DataController('./chinook.db')


class ButtonCustom:
    def __init__(self, text: str, command: str, i: int, frame=root) -> None:
        """
                Initialize a button object

                Args:
                        text (str): text to appear on button
                        command (str): command to be executed upon click
                        frame (str, optional): which frame the button will be placed. Defaults to root.
        """
        self.button = ttk.Button(frame, text=text, command=command)
        self.button.grid(
            row=1, column=i, padx=constants.BUTTON_PADX, ipady=3, ipadx=10)


def init_tables_tree() -> None:
    """
            Initialize table tree
    """

    tables_tree.heading('Tables', text="Tables")
    tables_tree.column('Tables', width=100, anchor=CENTER)

    tables_tree.tag_configure('exists', font=(
        'Helvetica', 10), background='#1a6600', foreground='white')
    tables_tree.tag_configure('deleted', font=(
        'Helvetica', 10), background='#ff6666', foreground='white')

    tables_tree.pack(side='top', fill=BOTH)
    tables_tree.bind('<ButtonRelease-1>', lambda e: select_table())

    import_tables()


def init_rows_tree() -> None:
    """
            Initialize rows tree
    """

    # Vertical Scrool Bar
    vertical_scroll = ttk.Scrollbar(
        rows_tree, orient="vertical", command=rows_tree.yview)
    vertical_scroll.pack(side='right', fill='y')

    # Horizontal Scroll Bar
    horizontal_scroll = ttk.Scrollbar(
        rows_tree, orient="horizontal", command=rows_tree.xview)
    horizontal_scroll.pack(side='bottom', fill='x')

    rows_tree.tag_configure('exists', background='#80ffcc')
    rows_tree.tag_configure('deleted', background='#ff6666')

    rows_tree_label.pack(side='top', anchor='nw')
    rows_tree.pack(side='top', fill=BOTH, expand=True)
    rows_tree.bind('<ButtonRelease-1>',
                   lambda e: select_table_row(e))  # used to give e

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
    edit_frame.pack(side='top', padx=4, ipady=150)

    entries = {}
    row = 1

    for index, column in enumerate(columns):
        if index % 6 == 0:
            row += 4
        l = Label(edit_frame, text=column)
        l.grid(row=row, column=index %
               6, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)
        edit_entry = Entry(edit_frame)
        edit_entry.grid(row=row + 1, column=index %
                        6, padx=constants.BUTTON_PADX, ipady=3, ipadx=20)

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
            Creation of a new window which allows the user to change values of a selected row.
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
                entries = bottom_frame_insert(
                    columns, current_row=current_item, disable_flag=1)
                ButtonCustom("Accept Changes", lambda: update_cell_value(
                    entries), 0, frame=edit_frame)
                ButtonCustom("Ignore Changes", on_ignore, 2, frame=edit_frame)

            else:
                error_label.config(text=err_msgs["empty_table"], anchor=CENTER)
        else:
            error_label.config(text=err_msgs["no_tbl_selected"], anchor=CENTER)
    except Exception as error:
        messagebox.showerror("Error", error)


def update_cell_value(entries: dict) -> None:
    """
            Updates the selected value of a cell of a specific row.
            Raises: Error if selected table is None/length of columns is 0 or smaller
    """
    columns = []
    values = []
    for column, entry in entries.items():
        columns.append(column)
        values.append(entry())
    remove_indexes = [index for index,
                      value in enumerate(values) if value == '']
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

    error_label.config(
        text=success_msgs["edit_completed"], fg='#20B519', anchor=CENTER)
    clear_edit_frame()
    present_new_trees()


def msg_decorator(func):
    """
            Decorator for functions clicks.
            Args:
                    func (function): the function we're decorating
            Returns: function
    """

    def inner_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_label.config(text=e, fg='#D93232', anchor=CENTER)

    return inner_func


def on_closing():
    controller.stop_connection()
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


@msg_decorator
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
            insert_table_rows(current_item[0])
            rows_tree_label.config(
                text=f'{selected_table.capitalize()} Table', font=("Arial", 18))
        elif selected_table:
            current_item = selected_table
            insert_table_rows(current_item)
            print('hi')
            rows_tree_label.config(
                text=f'{selected_table.capitalize()} Table', font=("Arial", 18))
        else:
            insert_table_rows('')
            print("hi3")
            rows_tree_label.config(text='')
    except Exception as error:
        messagebox.showerror("Error", error)


@msg_decorator
def select_table_row(event) -> None:
    """
            Select a cell when pressed in the table tree

            Args:
                    event (event): the event when pressing on a row in the table
    """
    global selected_cell, selected_row_id
    if selected_cell:
        clear_edit_frame()
    current_item = rows_tree.item(rows_tree.focus())['values']
    if current_item == '':
        return
    col = int(rows_tree.identify_column(event.x)[1:]) - 1
    if selected_table != 'playlist_track' and selected_table != 'invoices':
        selected_row_id = [rows_tree.column(0)["id"], current_item[0]]
    else:
        selected_row_id = [rows_tree.column(
            0)["id"], current_item[0], rows_tree.column(1)["id"], current_item[1]]

    selected_cell = [rows_tree.column(col)["id"], str(
        current_item[col]).replace("'", "\'").replace('"', '\"')]
    edit_input_frame(event)


def init_frames():
    """
            Initiates key variables such as root, style, tables_frame, rows_frame and buttons_frame.
    """
    root.geometry("1200x800")
    root.title("Database Manager")
    root.wm_attributes("-topmost", 1)

    style = ttk.Style()
    style.map('Treeview', foreground=fixed_map(style, "foreground"),
              background=fixed_map(style, "background"))

    tables_frame.pack(side='right', padx=5, pady=100, fill=BOTH, expand=False)
    top_container.pack(side='top', padx=5, pady=10,
                       fill=BOTH, expand=False, anchor=CENTER)
    buttons_frame.grid(row=1, column=1, padx=5, pady=10)
    error_frame.grid(row=1, column=2, padx=5, pady=10)
    rows_frame.pack(side='top', padx=5, ipady=150, fill=BOTH, expand=False)
    low_container.pack(side='bottom', padx=5, pady=10,
                       fill=BOTH, expand=False, anchor=CENTER)


def import_tables() -> None:
    """
            Import and insert rows of chosen table, row by row
    """
    for x in tables_tree.get_children():
        tables_tree.delete(x)

    all_pred_tables = controller.get_pred_table()
    controller.cursor.execute(constants.ALL_TABLES_QUERY)
    current_tables = controller.cursor.fetchall()
    for row in all_pred_tables:
        try:
            if (row,) in current_tables:
                tables_tree.insert('', 'end', values=row, tags=('exists',))
            else:
                tables_tree.insert('', 'end', values=row, tags=('deleted',))
        except Exception as error:
            messagebox.showerror("Error", error)


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
        rows_tree.column(column, minwidth=rows_frame.winfo_width() // len(columns), width=100)

    rows_tree['show'] = 'headings'
    if columns:
        fill_rows(f"SELECT * FROM {current_table};")


def clear_DB():
    """
    	Drops (clears) Database
    """
    controller.clear_DB()
    present_new_trees()
    error_label.config(text=success_msgs["clear_db"], anchor=CENTER)


def drop_table() -> None:
    """
            Drop the current table (clears window of table)
    """
    global tables_tree
    if selected_table:
        controller.drop_selected_table(selected_table)
        present_new_trees()
        error_label.config(
            text=success_msgs["drop_tbl"], fg='#20B519', anchor=CENTER)
    else:
        error_label.config(
            text=err_msgs["no_tbl_selected"], fg='#D93232', anchor=CENTER)


def drop_table_popup() -> None:
    """
            Pop up window to confirm the users action
    """

    if not selected_table:
        error_label.config(
            text=err_msgs["no_tbl_selected"], fg='#D93232', anchor=CENTER)
        return

    message = messagebox.askquestion(f'Drop Table {selected_table} ', warn_msgs["drop_tbl_warning"],
                                     icon='warning')
    if message == 'yes':
        drop_table()


def drop_db_popup() -> None:
    """
            Pop up window to confirm the users action
    """
    message = messagebox.askquestion('WARNING! - Drop Data Base',
                                     warn_msgs["drop_db_warning"],
                                     icon='warning')
    if message == 'yes':
        clear_DB()


def delete_row_popup() -> None:
    """
        Pop up window to confirm the users action
    """
    if not selected_table:
        error_label.config(
            text=err_msgs["row_dlt_no_tbl"], fg='#D93232', anchor=CENTER)
        return
    if not selected_cell:
        error_label.config(
            text=err_msgs["no_row_selected"], fg='#D93232', anchor=CENTER)
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
    error_label.config(text='')


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
        controller.delete_row_in_table(selected_table, cond)
        present_new_trees()
        edit_frame.grab_release()
        edit_frame.destroy()
        error_label.config(
            text=success_msgs["delete_row"], fg='#20B519', anchor=CENTER)
    else:
        error_label.config(
            text=err_msgs["row_dlt_no_tbl"], fg='#D93232', anchor=CENTER)


@msg_decorator
def add_new_row() -> None:
    """
            Create an input window which enables the user to change rows information.
    """
    if edit_frame:
        clear_edit_frame()
    if selected_table:
        columns = controller.get_all_columns(selected_table)
        if len(columns) > 0:
            entries = bottom_frame_insert(columns)
            ButtonCustom("Insert new row", lambda: insert_new_row_to_table(entries, edit_frame), 0, frame=edit_frame)
        else:
            error_label.config(
                text=err_msgs["empty_table"], fg='#D93232', anchor=CENTER)
    elif selected_cell:
        error_label.config(
            text=err_msgs["uncheck_before_insret"], fg='#D93232', anchor=CENTER)
    else:
        error_label.config(
            text=err_msgs["row_add_no_tbl"], fg='#D93232', anchor=CENTER)


def return_to_default() -> None:
    global selected_table
    if selected_table:
        selected_table = None
    present_new_trees()


@msg_decorator
def insert_new_row_to_table(entries: dict, window_to_close) -> None:
    """
        Collect information to add a new row to the current table.

        Args:
            entries: every entry that can be entered to a row in the current table
            window_to_close: The window that we'll destroy after adding the new row
    """
    columns = []
    values = []
    for column, entry in entries.items():
        columns.append(column)
        values.append(entry())
    remove_indexes = [index for index,
                    value in enumerate(values) if value == '']
    for index in sorted(remove_indexes, reverse=True):
        del columns[index]
        del values[index]
    for index, column in enumerate(columns):
        if controller.check_if_quotes_needed(selected_table, column):
            values[index] = f'"{values[index]}"'
    
    controller.insert_new_row_to_table(selected_table, columns, values)
    window_to_close.grab_release()
    window_to_close.destroy()
    present_new_trees()
    error_label.config(
        text=success_msgs["row_insert"], fg='#20B519', anchor=CENTER)


def init_buttons() -> None:
    functions = [delete_row_popup, add_new_row, drop_db_popup, drop_table_popup,
                 return_to_default]
    texts = ["Delete Row", "Add New Row",
             "Drop DataBase", "Drop Table", 'Default View']
    i = 1
    for text, func in zip(texts, functions):
        ButtonCustom(text, func, i, frame=buttons_frame)
        i += 1


if __name__ == "__main__":
    init_frames()
    init_buttons()
    init_rows_tree()
    init_tables_tree()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
