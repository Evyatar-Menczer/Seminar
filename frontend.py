from tkinter import *
from tkinter import ttk
from dataclasses import dataclass
import backend


def sort_command():
	set_titles(titles)
	tv.delete(*tv.get_children())
	for row in backend.sort_by_name():
		tv.insert(parent='', index='end', text="", values=[data for data in row])
	

def sort_type_command():
	# set_titles(titles)
	title1=('sadsadas','sadasda', 'asdsad')
	set_titles(title1)
	tv.delete(*tv.get_children())
	for row in backend.sort_by_type():
		tv.insert(parent='', index='end', text="", values=[data for data in row])


def sort_top_seller_command():
	tv.delete(*tv.get_children())
	titles = ('CustomerId', 'FirstName', 'LastName', 'Company', 'Address', 'City', 'State', 'Country', 'PostalCode',
			  'Phone', 'Fax', 'Email', 'SupportRepId')
	set_titles(titles)
	for row in backend.sort_by_best_seller():
		tv.insert(parent='', index='end', text="", values=[data for data in row])


def view_command():
	rows_tree.delete(*rows_tree.get_children())
	set_titles()
	for row in backend.view():
		rows_tree.insert(parent='', index='end', text="", values=[data for data in row])


def set_titles():
	columnns = controller.get_all_table_column('Employees')
	rows_tree['columns'] = tuple(columnns)
	for column in columnns:
		rows_tree.heading(column, text=column)
		rows_tree.column(column, minwidth=10, width=500//len(column))
	rows_tree['show'] = 'headings'


def init_rows_tree():
	global rows_tree
	rows_tree.tag_configure('exists', background='cyan')
	# rows_tree.tag_configure('deleted', background='red')
	rows_tree.grid(row=0, column=2, rowspan=3, columnspan=5)
	# rows_tree_label.pack(side='top')

	# rows_tree.pack(side='top', fill='x')

	# rows_tree.bind('<ButtonRelease-1>',
	#               lambda e: selectTableCell(e))  # used to give e

	# Horizontal Scroll Bar
	horscrlbar = ttk.Scrollbar(
		rows_frame, orient="horizontal", command=rows_tree.xview)

	# horscrlbar.pack(side='bottom', fill='x')

	rows_tree.configure(xscrollcommand=horscrlbar.set)



def init_table_tree():
	global tables_tree
	tables_tree.tag_configure('exists', background='cyan')
	tables_tree.tag_configure('deleted', background='red')
	tables_tree.grid(row=0, column=0, rowspan=3, columnspan=3)
	# tables_tree.pack(side='top')

	tables_tree.heading('Tables', text="Tables")

	tables_tree.column('Tables', width=100)

	# tables_tree.bind('<ButtonRelease-1>',
	#                 lambda e: selectTable())  # used to give e

	# fillTablesTree()




window = Tk()
window.title("My Data")
window.geometry("500x500")
window.resizable(True, True)
style = ttk.Style()
style.configure("BW.TLabel", foreground="black", background="white")

tables_frame = Frame(window)
rows_frame = Frame(window)

tables_tree = ttk.Treeview(tables_frame, columns=(
    'Tables'), height=20, show="headings")

rows_tree_label = Label(rows_frame)
rows_tree = ttk.Treeview(rows_frame, height=20, selectmode='browse')

selcted_table = None
current_row = None
selected_cell = None


# l1 = Label(window, text="Chinook")
# l1.grid(row=0, column=0)

# tv = ttk.Treeview(window, show="headings", height="15", selectmode='browse', style='BW.TLabel')
# tv.grid(row=1, column=0, rowspan=3, columnspan=1)



def init_window():
	window.geometry("800x500")
	window.title("DataBase - Management")
	window.wm_attributes("-topmost", 1)

	style = ttk.Style()
	style.configure("BW.TLabel", foreground="black", background="white")

	# tables_frame.pack(side='left', padx=5)
	tables_frame.grid(row=0, column=0, rowspan=3, columnspan=1)
	rows_frame.grid(row=0, column=2, rowspan=3, columnspan=5)
	# rows_frame.pack(side='left', padx=5, fill='x', expand=True)



if __name__ == '__main__':
	init_window()
	controller = backend.Database()
	# y_scrollbar = ttk.Scrollbar(window, orient=VERTICAL, command=rows_tree.yview)
	# y_scrollbar.grid(row=1, column=1, rowspan=30, sticky='ns')
	init_rows_tree()
	init_table_tree()
	# x_scrollbar = ttk.Scrollbar(window, orient=HORIZONTAL, command=rows_tree.xview)
	# x_scrollbar.grid(row=5, column=0, sticky='ew')
	# tv.configure(xscroll=x_scrollbar.set, yscroll=y_scrollbar.set)

	# b1 = Button(window, text="Sort By Name", width=12, command=sort_command)
	# b1.grid(row=11, column=0)
	#
	# b2 = Button(window, text="Purchased Track", width=12, command=sort_type_command)
	# b2.grid(row=12, column=0)
	#
	# b4 = Button(window, text="View Top Seller", width=12, command=sort_top_seller_command)
	# b4.grid(row=13, column=0)

	b3 = Button(window, text="View All", width=12, command=view_command)
	b3.grid(row=14, column=0)

	window.mainloop()
