#! /usr/bin/env python3

import re
from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tableview import Tableview
import contextmenu
import contentbeautifier
import scrolledtextsearch

################
### TREE TAB ###
################
class HistoryTab(tb.Frame):

	def __init__(self, notebook: tb.Notebook) -> None:
		'''Initialize the history tab'''
		self.notebook = notebook
		super().__init__(self.notebook)
		self.notebook.add(self, text="History") # Add itself to the notebook
		self.cb = contentbeautifier.ContentBeautifier()
		self.sts = scrolledtextsearch.ScrolledTextSearch("#35B279")
		self.cm = contextmenu.ContextMenu()
		self.last_clicked = -1
		self._add_widgets()

	def _add_widgets(self) -> None:
		'''Add UI widgets to the tab'''
		# Add a table to show metadata
		self._add_table()
		# Add a request textbox
		self._add_request_textbox()
		# Add a request search entry
		self._add_request_search_entry()
		# Add a button for the request search
		self._add_request_search_button()
		# Add a toggle for request search regex
		self._add_request_toggle_regex()
		# Add a toggle for request search case sensitivity
		self._add_request_toggle_case()
		# Add a text label for search result count
		self._add_request_search_count_label()
		# Add a response textbox
		self._add_response_textbox()
		# Add a response search entry
		self._add_response_search_entry()
		# Add a button for the response search
		self._add_response_search_button()
		# Add a toggle for response search regex
		self._add_response_toggle_regex()
		# Add a toggle for response search case sensitivity
		self._add_response_toggle_case()
		# Add a text label for search response result count
		self._add_response_search_count_label()
		# Add right click request context menu
		self._add_request_context_menu()
		# Add a right click response context menu
		self._add_response_context_menu()

	def _add_table(self) -> None:
		'''Add a table to the tab'''
		self.cols = [
			{"text": "id", "stretch": False},
			{"text":"method","stretch":False},
			{"text":"url","stretch":True},
			{"text":"status_code","stretch":False},
			{"text":"input","stretch":False},
			{"text":"type","stretch":False},
			{"text":"extension","stretch":False},
			{"text":"ip addr","stretch":False},
			{"text":"port","stretch":False},
			{"text":"timestamp","stretch":False}
		]
		self.history_table = Tableview(self, paginated=False, autofit=True, bootstyle="warning", coldata=self.cols, rowdata=(), searchable=True)
		self.history_table.place(relx=0.015, rely=0.009, relwidth=0.971, relheight=0.463)
		self.history_table.view.bind("<Double-1>", self._double_click_row)

	def _add_request_textbox(self) -> None:
		'''Add a request text box'''
		self.request_textbox = ScrolledText(self, state="disabled", bootstyle="warning round", wrap=WORD, hbar=True)
		self.request_textbox.place(relx=0.0135, rely=0.498, relwidth=0.48, relheight=0.398)
		# Add a right click menu
		self.request_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_request)

	def _add_request_search_entry(self) -> None:
		'''Add an entry request search field'''
		self.request_search_entry = tb.Entry(self, text="")
		self.request_search_entry.place(relx=0.015, rely=0.905, relwidth=0.39, height=30)

	def _add_request_search_button(self) -> None:
		'''Add a search button for the search field'''
		self.request_search_button = tb.Button(self, text="Search", command=self._search_request, bootstyle="success", width=20)
		self.request_search_button.place(relx=0.411, rely=0.905, relwidth=0.08, height=30)

	def _add_request_toggle_regex(self) -> None:
		'''Add a toggle button to enable regex'''
		self.request_regex_toggle_int = IntVar()
		self.request_search_regex = tb.Checkbutton(self, text="Regex", variable=self.request_regex_toggle_int, style="warning.Roundtoggle.Toolbutton")
		self.request_search_regex.place(in_=self.request_search_entry, relx=0, rely=1.0, width=80, height=30)

	def _add_request_toggle_case(self) -> None:
		'''Add a toggle button to enable case sensitivity'''
		self.request_case_toggle_int = IntVar()
		self.request_search_case = tb.Checkbutton(self, text="Case Sensitive", variable=self.request_case_toggle_int, style="warning.Roundtoggle.Toolbutton")
		self.request_search_case.place(in_=self.request_search_regex, relx=1.0, rely=0, width=134, height=30)

	def _add_request_search_count_label(self) -> None:
		'''Add a lable for the request search count'''
		self.request_search_count = tb.Label(self, text="Match: 0/0")
		self.request_search_count.place(in_=self.request_search_case, relx=1.0, rely=0, width=160, height=30)

	def _add_response_textbox(self) -> None:
		'''Add a request text box'''
		self.response_textbox = ScrolledText(self, state="disabled", bootstyle="warning round", wrap=WORD, hbar=True)
		self.response_textbox.place(relx=0.507, rely=0.498, relwidth=0.48, relheight=0.398)
		# Add a right click menu to send it to other tools
		self.response_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_response)

	def _add_response_search_entry(self) -> None:
		'''Add an entry response search field'''
		self.response_search_entry = tb.Entry(self, text="")
		self.response_search_entry.place(relx=0.5085, rely=0.905, relwidth=0.39, height=30)

	def _add_response_search_button(self) -> None:
		'''Add a search button for the response search field'''
		self.response_search_button = tb.Button(self, text="Search", command=self._search_response, bootstyle="success", width=20)
		self.response_search_button.place(relx=0.9045, rely=0.905, relwidth=0.08, height=30)

	def _add_response_toggle_regex(self) -> None:
		'''Add a toggle button to enable regex'''
		self.response_regex_toggle_int = IntVar()
		self.response_search_regex = tb.Checkbutton(self, text="Regex", variable=self.response_regex_toggle_int, style="warning.Roundtoggle.Toolbutton")
		self.response_search_regex.place(in_=self.response_search_entry, relx=0, rely=1.0, width=80, height=30)

	def _add_response_toggle_case(self) -> None:
		'''Add a toggle button to enable case sensitivity'''
		self.response_case_toggle_int = IntVar()
		self.response_search_case = tb.Checkbutton(self, text="Case Sensitive", variable=self.response_case_toggle_int, style="warning.Roundtoggle.Toolbutton")
		self.response_search_case.place(in_=self.response_search_regex, relx=1.0, rely=0, width=134, height=30)

	def _add_response_search_count_label(self) -> None:
		'''Add a lable for the request search count'''
		self.response_search_count = tb.Label(self, text="Match: 0/0")
		self.response_search_count.place(in_=self.response_search_case, relx=1.0, rely=0, width=160, height=30)

	# Create a right click menu for the request box

	def _add_request_context_menu(self) -> None:
		'''Add a right click menu on a target to show a menu'''
		self.mu_request = Menu(self, tearoff=False)
		self.mu_request.add_command(label="Copy", command=lambda:self.cm.copy(self.request_textbox.__dict__["children"]["!text"]))
		self.mu_request.add_command(label="Copy as curl", command=lambda:self.cm.copy_as_curl(self.request_textbox.__dict__["children"]["!text"], self.last_clicked, self.notebook.cursor))
		self.mu_request.add_command(label="Save Raw", command=lambda:self.cm.save_raw(self.request_textbox.__dict__["children"]["!text"]))
		self.mu_request.add_separator()
		self.mu_request.add_command(label="Open in Editor", command=self._send_to_editor)
		self.mu_request.add_command(label="Open in Fuzzer", command=self._send_to_fuzzer)
		#self.mu_request.add_command(label="Open in Scanner", command=None)
		self.mu_request.bind("<FocusOut>", self._close_request_menu)

	def _close_request_menu(self, event=None) -> None:
		'''Close the right click menu if you left click off it'''
		self.mu_request.unpost()

	def _right_click_request(self, event) -> None:
		'''Open the right click popup window'''
		try:
			self.mu_request.tk_popup(event.x_root + 1, event.y_root + 1)
		finally:
			self.mu_request.grab_release()

	# Create a right click menu for the response box

	def _add_response_context_menu(self) -> None:
		'''Add a right click menu on a target to show a menu'''
		self.mu_response = Menu(self, tearoff=False)
		self.mu_response.add_command(label="Copy", command=lambda:self.cm.copy(self.response_textbox.__dict__["children"]["!text"]))
		self.mu_response.add_command(label="Save Raw", command=lambda:self.cm.save_raw(self.response_textbox.__dict__["children"]["!text"]))
		self.mu_response.bind("<FocusOut>", self._close_response_menu)

	def _close_response_menu(self, event=None) -> None:
		'''Close the right click menu if you left click off it'''
		self.mu_response.unpost()

	def _right_click_response(self, event) -> None:
		'''Open the right click popup window'''
		try:
			self.mu_response.tk_popup(event.x_root + 1, event.y_root + 1)
		finally:
			self.mu_response.grab_release()

	def _send_to_editor(self) -> None:
		'''Send request to editor'''
		if self.last_clicked != -1:
			self.notebook.window.edit_view._send_to_editor(self.last_clicked)
			self.notebook.select(3)

	def _send_to_fuzzer(self) -> None:
		'''Send request to fuzzer'''
		if self.last_clicked != -1:
			self.notebook.window.fuzz_tab._send_to_fuzzer(self.last_clicked)
			self.notebook.select(4)

	def _load_table(self) -> None:
		'''Load table rows from the database'''
		self.history_table.delete_rows()
		self.notebook.cursor.execute('''SELECT id, request_method, request_url, response_status_code, request_has_input, request_body_type, request_file_extension, ip_address, port, timestamp FROM transactions;''')
		rows = self.notebook.cursor.fetchall()
		if rows:
			self.history_table.build_table_data(coldata=self.cols, rowdata=rows)

	def _double_click_row(self, event) -> None:
		'''Click a row'''
		try:
			iid = self.history_table.view.focus()
			row = self.history_table.get_row(iid=iid)
		except:
			row = None
		if row:
			if row.values:
				request_id = row.values[0]
				if request_id != self.last_clicked:
					self.last_clicked = request_id
					self.notebook.cursor.execute('''SELECT request_method, request_url, request_headers, request_body FROM transactions WHERE id = ?;''',(request_id,))
					request_info = self.notebook.cursor.fetchone()
					self.notebook.cursor.execute('''SELECT response_status_code, response_status_message, response_headers, response_body FROM transactions WHERE id = ?;''',(request_id,))
					response_info = self.notebook.cursor.fetchone()
					raw_request = self.cb.rebuild_request(*request_info)
					raw_response = self.cb.rebuild_response(*response_info)
					# Set the text in each pane.
					### ENABLE DISABLED ScrolledText PANE - !!! Its insane it had to be done this way !!!
					self.request_textbox.__dict__["children"]["!text"].configure(state="normal")
					self.response_textbox.__dict__["children"]["!text"].configure(state="normal")
					self.request_textbox.delete(1.0, END)
					self.response_textbox.delete(1.0, END)
					self.request_textbox.insert(END, raw_request)
					self.response_textbox.insert(END, raw_response)
					### DISABLE ENABLED ScrolledText PANE - !!! Its insane it had to be done this way !!!
					self.request_textbox.__dict__["children"]["!text"].configure(state="disabled")
					self.response_textbox.__dict__["children"]["!text"].configure(state="disabled")
					# Perform searches
					self._search_request(True)
					self._search_response(True)

	def _search_request(self, new_click_target: bool=False):
		'''Search the request'''
		self.sts.search(
			self.request_regex_toggle_int,
			self.request_case_toggle_int,
			self.request_search_entry,
			self.request_textbox.__dict__["children"]["!text"],
			self.request_search_count,
			new_click_target
		)

	def _search_response(self, new_click_target: bool=False):
		'''Search the response'''
		self.sts.search(
			self.response_regex_toggle_int,
			self.response_case_toggle_int,
			self.response_search_entry,
			self.response_textbox.__dict__["children"]["!text"],
			self.response_search_count,
			new_click_target
		)
