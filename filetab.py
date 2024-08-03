#! /usr/bin/env python3

import os
import sqlite3
from tkinter import *
import ttkbootstrap as tb
from tkinter import filedialog
import harparse

################
### FILE TAB ###
################
class FileTab(tb.Frame):

	def __init__(self, notebook: tb.Notebook) -> None:
		'''Initialize the configuration tab'''
		self.notebook = notebook
		super().__init__(self.notebook)
		self.notebook.add(self, text="File") # Add itself to the notebook
		self.import_load = StringVar(value="import")
		self._add_widgets()
		self.hp = harparse.Harparse()

	def _add_widgets(self) -> None:
		'''Add widgets to the frame'''
		### IMPORT HAR FILE WIDGETS ###
		# Create the label frame around the import HAR section
		self._add_har_label_frame()
		# Add import har radio button
		self._add_har_radio()
		# Add a har text box label for the har file path entry
		self._add_har_text_label()
		# Add a har text entry for the file path
		self._add_har_text_entry()
		# Add a button to select a har file with a file dialog
		self._add_har_button()
		# Add a text label for the database file path entry
		self._add_database_label()
		# Add a text entry for the database file path
		self._add_database_text_entry()
		# Add a button to select a database file to save
		self._add_database_save_button()
		### LOAD DATABASE WIDGETS ###
		# Add a label frame for the load database section
		self._add_label_frame()
		# Add add a radio button to enable the load database section
		self._add_load_db_radio()
		# Add a text label for the load db text entry
		self._add_load_db_text_label()
		# Add a text entry for the load DB file path
		self._add_load_db_text_entry()
		# Add the DB load button to select a file to load
		self._add_load_db_button()
		# Add the main yellow button to perform the main form action
		self._add_main_action_button()

	########################
	### IMPORT HAR FRAME ###
	########################

	def _add_har_label_frame(self) -> None:
		'''Create the label frame for importing a HAR file'''
		self.har_label_frame = tb.Labelframe(self, text="Import New", bootstyle="info")
		self.har_label_frame.place(relx=0.013, rely=0.01, relwidth=0.974, relheight=0.284)

	def _add_har_radio(self) -> None:
		'''Radio button to ename HAR import'''
		self.load_har = tb.Radiobutton(self, variable=self.import_load, text="Import a HAR file to a new or existing database", value="import", command=self._enable_load_import_buttons, bootstyle="info")
		self.load_har.place(relx=0.037, rely=0.05, relwidth=0.5, height=30)

	def _add_har_text_label(self) -> None:
		'''Add a text label above the har file path text box'''
		self.har_text_label = tb.Label(self, text="HAR File:")
		self.har_text_label.place(relx=0.037, rely=0.09, relwidth=0.1, height=30)

	def _add_har_text_entry(self) -> None:
		'''Add the text box for the har file path'''
		self.har_text_entry = tb.Entry(self, text="", state="disabled", bootstyle="readonly")
		self.har_text_entry.config(foreground="white")
		self.har_text_entry.place(relx=0.037, rely=0.125, relwidth=0.755, height=30)

	def _add_har_button(self) -> None:
		'''Add a button to select a har file to import'''
		self.har_button = tb.Button(self, text="Select HAR", command=self._select_har, bootstyle="info", width=20)
		self.har_button.place(relx=0.804, rely=0.125, relwidth=0.16, height=30)

	def _add_database_label(self) -> None:
		'''Add a text label above the database file path text box'''
		self.db_text_label = tb.Label(self, text="Database File:")
		self.db_text_label.place(relx=0.037, rely=0.175, relwidth=0.1, height=30)

	def _add_database_text_entry(self) -> None:
		'''Add a text entry for the database file path'''		
		self.db_text_entry = tb.Entry(self, text="", state="disabled", bootstyle="readonly")
		self.db_text_entry.config(foreground="white")
		self.db_text_entry.place(relx=0.037, rely=0.211, relwidth=0.755, height=30)

	def _add_database_save_button(self) -> None:
		'''Add a button to select a database file to save'''
		self.db_button = tb.Button(self, text="Choose Database Name", command=self._select_db, bootstyle="info", width=20)
		self.db_button.place(relx=0.804, rely=0.211, relwidth=0.16, height=30)

	def _enable_load_import_buttons(self) -> None:
		'''Radio button click action to enable/disable form fields'''
		radio_value = self.import_load.get()
		if radio_value == "load":
			self.db_label_frame.config(style="success.TLabelframe")
			self.har_label_frame.config(style="default.TLabelframe")
			self.db_load_button.config(state="enabled")
			self.har_button.config(state="disabled")
			self.db_button.config(state="disabled")
			self.db_load_text_entry.config(foreground="white")
			self.har_text_entry.config(foreground="gray")
			self.db_text_entry.config(foreground="gray")
		elif radio_value == "import":
			self.har_label_frame.config(style="info.TLabelframe")
			self.db_label_frame.config(style="default.TLabelframe")
			self.har_button.config(state="enabled")
			self.db_button.config(state="enabled")
			self.db_load_button.config(state="disabled")
			self.db_load_text_entry.config(foreground="gray")
			self.har_text_entry.config(foreground="white")
			self.db_text_entry.config(foreground="white")

	def _select_har(self) -> None:
		'''Use a file dialog to choose a har file to import'''
		desktop = os.path.expanduser("~/Desktop")
		harfile = filedialog.askopenfilename(initialdir=desktop, title="Select HAR file", filetypes=(("HAR files","*.har"),("All Files","*.*")))
		if harfile:
			self.har_text_entry.configure(state="normal")
			self.har_text_entry.delete(0, 'end')
			self.har_text_entry.insert(END, harfile)
			self.har_text_entry.configure(state="disabled")

	def _select_db(self) -> None:
		'''Use a file dialog to choose a database file name to save'''
		desktop = os.path.expanduser("~/Desktop")
		dbfpath = filedialog.asksaveasfilename(initialdir=desktop, confirmoverwrite=False, filetypes=(("DB files","*.db"),), defaultextension=".db")
		if dbfpath:
			self.db_text_entry.configure(state="normal")
			self.db_text_entry.delete(0, 'end')
			self.db_text_entry.insert(END, dbfpath)
			self.db_text_entry.configure(state="disabled")

	#################################
	### LOAD DATABASE LABEL FRAME ###
	#################################

	def _add_label_frame(self) -> None:
		'''Add a label frame for the load database section'''
		self.db_label_frame = tb.Labelframe(self, text="Load Existing", bootstyle="default")
		self.db_label_frame.place(relx=0.013, rely=0.31, relwidth=0.974, relheight=0.197)

	def _add_load_db_radio(self) -> None:
		'''Radio button to enable database import'''
		self.load_db = tb.Radiobutton(self, variable=self.import_load, text="Load an existing database", value="load", command=self._enable_load_import_buttons, bootstyle="success")
		self.load_db.place(relx=0.037, rely=0.35, relwidth=0.5, height=30)

	def _add_load_db_text_label(self) -> None:
		'''Add a label for the load db text entry'''
		self.db_load_text_label = tb.Label(self, text="Database File:")
		self.db_load_text_label.place(relx=0.037, rely=0.388, relwidth=0.1, height=30)

	def _add_load_db_text_entry(self) -> None:
		'''Add a text entry for the load db file path'''
		self.db_load_text_entry = tb.Entry(self, text="", state="disabled", bootstyle="readonly")
		self.db_load_text_entry.config(foreground="gray")
		self.db_load_text_entry.place(relx=0.037, rely=0.425, relwidth=0.755, height=30)

	def _add_load_db_button(self) -> None:
		'''Add a button to choose a database file to load'''
		self.db_load_button = tb.Button(self, text="Select Database", command=self._select_db_load, bootstyle="success", width=20, state="disabled")
		self.db_load_button.place(relx=0.804, rely=0.425, relwidth=0.16, height=30)

	def _add_main_action_button(self) -> None:
		'''Add the yellow button to perform the selected form action'''
		self.load_button = tb.Button(self, text="Proceed", bootstyle="warning", command=self._load_file, width=20)
		self.load_button.place(relx=0.5-0.08, rely=0.532, relwidth=0.16, height=30)

	def _select_db_load(self) -> None:
		'''Use a file dialog to select a database to load'''
		db_load = filedialog.askopenfilename(initialdir="~/Desktop", title="Select Database", filetypes=(("DB files","*.db"),))
		if db_load:
			self.db_load_text_entry.configure(state="normal")
			self.db_load_text_entry.delete(0, 'end')
			self.db_load_text_entry.insert(END, db_load)
			self.db_load_text_entry.configure(state="disabled")

	def _load_file(self) -> None:
		'''Load the selected file'''
		ready = False
		radio_value = self.import_load.get()
		if radio_value == "load":
			path = self.db_load_text_entry.get()
			if path:
				for i in self.notebook.window.tree_view.tree.get_children():
					self.notebook.window.tree_view.tree.delete(i)
				self.notebook.conn = sqlite3.connect(path, check_same_thread=False)
				self.notebook.cursor = self.notebook.conn.cursor()
				ready = True
		else:
			harfile = self.har_text_entry.get()
			dbfile = self.db_text_entry.get()
			if harfile and dbfile:
				self.hp.parse(harfile, dbfile)
				self.notebook.conn = sqlite3.connect(dbfile, check_same_thread=False)
				self.notebook.cursor = self.notebook.conn.cursor()
				ready = True
		if ready:
			# Load the fuzz table
			self.notebook.window.fuzz_tab._load_table()
			# Load the table view
			self.notebook.window.history_view._load_table()
			# Load the tree view
			self.notebook.window.tree_view._populate_treeview()
			self.notebook.select(1)

