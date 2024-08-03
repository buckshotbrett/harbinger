#! /usr/bin/env python3

import re
import contextmenu
from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledText
from urllib.parse import urlparse
import contentbeautifier
import scrolledtextsearch

################
### TREE TAB ###
################
class TreeTab(tb.Frame):

	def __init__(self, notebook: tb.Notebook) -> None:
		'''Initialize the tree tab'''
		self.notebook = notebook
		super().__init__(self.notebook)
		self.notebook.add(self, text="Site Map") # Add itself to the notebook
		self.cb = contentbeautifier.ContentBeautifier()
		self.sts = scrolledtextsearch.ScrolledTextSearch("#EE8A12")
		self.cm = contextmenu.ContextMenu()
		self.last_clicked = -1
		self._add_widgets()

	def _add_widgets(self) -> None:
		'''Add widgets to the frame'''
		# Add the tree view for the sites
		self._add_treeview()
		# Add the text box for the request
		self._add_request_textbox()
		# Add the entry search for the request textbox
		self._add_request_search_entry()
		# Add a button to search the request box
		self._add_request_search_button()
		# Add a toggle to enable regex on the request search box
		self._add_request_toggle_regex()
		# Add a toggle to enable case sensitivity on the request search box
		self._add_request_toggle_case()
		# Add a label for the number of matches
		self._add_request_search_count_label()
		# Add the text box for the response
		self._add_response_textbox()
		# Add the entry search for the response textbox
		self._add_response_search_entry()
		# Add a button to search the response box
		self._add_response_search_button()
		# Add a toggle to enable regex on the response search box
		self._add_response_toggle_regex()
		# Add a toggle to enable case sensitivity on the response search box
		self._add_response_toggle_case()
		# Add a label for the number of matches
		self._add_response_search_count_label()
		# Add the right click context menu for the requestbox
		self._add_request_context_menu()
		# Add the right click menu for the response text box
		self._add_response_context_menu()

	def _add_treeview(self) -> None:
		'''Add site tree view'''
		self.tree = tb.Treeview(self, bootstyle="primary")
		self.tree.heading('#0', text="Sites")
		self.tree.place(relx=0.009, rely=0.015, relwidth=0.48, relheight=0.97)
		self.tree.bind("<Button-1>", self._fetch_transaction)

	def _add_request_textbox(self) -> None:
		'''Add the text box for a request'''
		self.request_textbox = ScrolledText(self, state="disabled", bootstyle="primary round", wrap=WORD, hbar=True)
		self.request_textbox.place(relx=0.5, rely=0.012, relwidth=0.49, relheight=0.39)
		# Add a right click menu
		self.request_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_request)

	def _add_request_search_entry(self) -> None:
		'''Add an entry request search field'''
		self.request_search_entry = tb.Entry(self, text="")
		self.request_search_entry.place(relx=0.502, rely=0.41, relwidth=0.40, height=30)

	def _add_request_search_button(self) -> None:
		'''Add a search button for the search field'''
		self.request_search_button = tb.Button(self, text="Search", command=self._search_request, bootstyle="warning", width=20)
		self.request_search_button.place(relx=0.908, rely=0.41, relwidth=0.08, height=30)

	def _add_request_toggle_regex(self) -> None:
		'''Add a toggle button to enable regex'''
		self.request_regex_toggle_int = IntVar()
		self.request_search_regex = tb.Checkbutton(self, text="Regex", variable=self.request_regex_toggle_int, bootstyle="primary", style="primary.Roundtoggle.Toolbutton")
		self.request_search_regex.place(in_=self.request_search_entry, relx=0, rely=1.0, width=80, height=30)

	def _add_request_toggle_case(self) -> None:
		'''Add a toggle button to enable case sensitivity'''
		self.request_case_toggle_int = IntVar()
		self.request_search_case = tb.Checkbutton(self, text="Case Sensitive", variable=self.request_case_toggle_int, bootstyle="primary", style="primary.Roundtoggle.Toolbutton")
		self.request_search_case.place(in_=self.request_search_regex, relx=1.0, rely=0, width=134, height=30)

	def _add_request_search_count_label(self) -> None:
		'''Add a lable for the request search count'''
		self.request_search_count = tb.Label(self, text="Match: 0/0")
		self.request_search_count.place(in_=self.request_search_case, relx=1.0, rely=0, width=160, height=30)

	def _add_response_textbox(self) -> None:
		'''Add the text box for a response'''
		self.response_textbox = ScrolledText(self, state="disabled", bootstyle="primary round", wrap=WORD, hbar=True)
		self.response_textbox.place(relx=0.50, rely=0.507, relwidth=0.49, relheight=0.39)
		# Add a right click menu
		self.response_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_response)

	def _add_response_search_entry(self) -> None:
		'''Add an entry response search field'''
		self.response_search_entry = tb.Entry(self, text="")
		self.response_search_entry.place(relx=0.502, rely=0.903, relwidth=0.40, height=30)

	def _add_response_search_button(self) -> None:
		'''Add a search button for the response search field'''
		self.response_search_button = tb.Button(self, text="Search", command=self._search_response, bootstyle="warning", width=20)
		self.response_search_button.place(relx=0.908, rely=0.903, relwidth=0.08, height=30)

	def _add_response_toggle_regex(self) -> None:
		'''Add a toggle button to enable regex'''
		self.response_regex_toggle_int = IntVar()
		self.response_search_regex = tb.Checkbutton(self, text="Regex", variable=self.response_regex_toggle_int, bootstyle="primary", style="primary.Roundtoggle.Toolbutton")
		self.response_search_regex.place(in_=self.response_search_entry, relx=0, rely=1.0, width=80, height=30)

	def _add_response_toggle_case(self) -> None:
		'''Add a toggle button to enable case sensitivity'''
		self.response_case_toggle_int = IntVar()
		self.response_search_case = tb.Checkbutton(self, text="Case Sensitive", variable=self.response_case_toggle_int, bootstyle="primary", style="primary.Roundtoggle.Toolbutton")
		self.response_search_case.place(in_=self.response_search_regex, relx=1.0, rely=0, width=134, height=30)

	def _add_response_search_count_label(self) -> None:
		'''Add a lable for the request search count'''
		self.response_search_count = tb.Label(self, text="Match: 0/0")
		self.response_search_count.place(in_=self.response_search_case, relx=1.0, rely=0, width=160, height=30)

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

	def _populate_treeview(self) -> None:
		'''Add website tree data to the widget'''
		self.tree_map = {}
		for item in self.tree.get_children():
			self.tree.delete(item)
		self.notebook.cursor.execute('''SELECT id, request_method, request_params, request_url FROM transactions;''')
		rows = self.notebook.cursor.fetchall()
		for row in rows:
			self._add_url(*row)

	def _add_url(self, request_id: int, method: str, request_params: str, url: str) -> None:
		'''Add a URL to the tree'''
		# parse URL for interesting parts
		urlparts = urlparse(url)
		folders = [i for i in urlparts.path.split("/") if i]
		query = method + request_params
		# Finalize list
		folders.insert(0, urlparts.scheme + "://" + urlparts.netloc)
		folders.append(query)
		# Insert path
		self._add_url_path(request_id, folders)

	def _add_url_path(self, request_id: int, folders: list, parent_id="", urlstr: str="") -> None:
		'''Recursive mapping'''
		if folders:
			label = folders.pop(0)
			if folders:
				last = False
			else:
				last = True
			if urlstr:
				level = urlstr + "/" + label
			else:
				level = label
			if level not in self.tree_map:
				l_id = self.tree.insert(parent_id, index="end", iid=None, text=label, values=(level,))
				self.tree_map[level] = {"parent_id": parent_id, "level_id": l_id, "request_id": request_id, "last": last}
				self._add_url_path(request_id, folders, l_id, level)
			else:
				parent_id = self.tree_map[level]["level_id"]
				self._add_url_path(request_id, folders, parent_id, level)

	def _fetch_transaction(self, event):
		'''Retrieve the relevant transaction request and response data'''
		try:
			row = self.tree.identify_row(event.y)
			url = self.tree.item(row, "values")[0]
		except:
			url = ""
		if url:
			if self.tree_map[url]["last"] == True:
				_id = self.tree_map[url]["request_id"]
				if _id != self.last_clicked:
					self.last_clicked = _id
					self.notebook.cursor.execute('''SELECT request_method, request_url, request_headers, request_body FROM transactions WHERE id = ?;''',(_id,))
					request_info = self.notebook.cursor.fetchone()
					self.notebook.cursor.execute('''SELECT response_status_code, response_status_message, response_headers, response_body FROM transactions WHERE id = ?;''',(_id,))
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
