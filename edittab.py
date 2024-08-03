#! /usr/bin/env python3

import re
import time
import json
from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.scrolled import ScrolledFrame
import requests
import contextmenu
import contentbeautifier
import scrolledtextsearch
import harparse

################
### TREE TAB ###
################
class EditTab(tb.Frame):

	def __init__(self, notebook: tb.Notebook) -> None:
		'''Initialize the editor tab'''
		self.notebook = notebook
		super().__init__(self.notebook)
		self.notebook.add(self, text="Editor") # Add itself to the notebook
		self.session = requests.Session()
		self.cb = contentbeautifier.ContentBeautifier()
		self.sts = scrolledtextsearch.ScrolledTextSearch("#DF352E")
		self.hp = harparse.Harparse()
		self.cm = contextmenu.ContextMenu()
		self.request_id = -1
		self._add_widgets()

	def _add_widgets(self) -> None:
		'''Add widgets to the frame'''
		# Add a wire frame for request
		self._add_label_frame()
		# Add a method combo box
		self._add_method_combobox()
		# Add a method label
		self._add_method_label()
		# Add HTTP version combo box
		self._add_http_version_combobox()
		# Add an HTTP version label
		self._add_http_version_label()
		# Add a label for the URL box
		self._add_url_label()
		# Add a URL text box
		self._add_url_textbox()
		# Add a headers label
		self._add_headers_label()
		# Add a scrolling frame for headers entries
		self._add_headers_frame()
		# Add a separator to separate the request headers and body
		self._add_separator()
		# Add a label for the request body
		self._add_request_body_label()
		# Add a request body text box
		self._add_request_body_textbox()
		# Add a request send button
		self._add_request_button()
		# Add a response textbox
		self._add_response_textbox()
		# Add response search entry
		self._add_response_search_entry()
		# Add a search button
		self._add_response_search_button()
		# Add a regex toggle
		self._add_response_toggle_regex()
		# Add a case sensitivity toggle
		self._add_response_toggle_case()
		# Add a label for the matches count
		self._add_response_search_count_label()
		# Add a label for the request/response time
		self._add_response_time_label()
		# Add the right click context menu for the url text box
		self._add_url_context_menu()
		# Add the right click context menu for the headers frame
		self._add_headers_context_menu()
		# Add the right click context menu for the body text box
		self._add_body_context_menu()
		# Add the right click context menu for the response text box
		self._add_response_context_menu()

	def _add_label_frame(self) -> None:
		'''Add a label frame for the load database section'''
		self.db_label_frame = tb.Labelframe(self, text="Request", bootstyle="success")
		self.db_label_frame.place(relx=0.013, rely=0.008, relwidth=0.481, relheight=0.975)

	def _add_method_combobox(self) -> None:
		'''Add a combo box for methods'''
		self.mb_method = tb.Menubutton(self, text='Method', bootstyle='secondary')
		self.mb_method.place(relx=0.03, rely=0.045, relwidth=0.09, height=30)
		# create menu and add options
		self.method_menu = tb.Menu(self.mb_method)
		self.method_str = StringVar()
		for opt in ["GET", "POST", "HEAD", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]:
			self.method_menu.add_radiobutton(label=opt, variable=self.method_str, command=self._click_method)
		# associate menu with menubutton
		self.mb_method['menu'] = self.method_menu

	def _click_method(self) -> None:
		'''Click a method option on the menu'''
		method = self.method_str.get()
		self.method_label.config(text=method)

	def _add_method_label(self) -> None:
		'''Set label for the method combo box'''
		self.method_label = tb.Label(self, text="")
		self.method_label.place(in_=self.mb_method, relx=1.0, rely=0, x=8, width=70, height=30)

	def _add_http_version_combobox(self) -> None:
		'''Add a combo box for HTTP versions'''
		self.mb_version = tb.Menubutton(self, text='Version', bootstyle='secondary')
		self.mb_version.place(in_=self.method_label, relx=1.0, rely=0, x=6, width=100, height=30)
		# create menu and add options
		self.version_menu = tb.Menu(self.mb_version)
		self.version_str = StringVar()
		for opt in ["HTTP/1.1"]:
			self.version_menu.add_radiobutton(label=opt, variable=self.version_str, command=None)
		# associate menu with menubutton
		self.mb_version['menu'] = self.version_menu

	def _add_http_version_label(self) -> None:
		'''Set label for the method combo box'''
		self.version_label = tb.Label(self, text="HTTP/1.1")
		self.version_label.place(in_=self.mb_version, relx=1.0, rely=0, x=6, width=70, height=30)

	def _add_url_label(self) -> None:
		'''Set label for the URL box'''
		self.url_label = tb.Label(self, text="URL:")
		self.url_label.place(relx=0.03, rely=0.09, width=50, height=30)

	def _add_url_textbox(self) -> None:
		'''Add a request text box'''
		self.url_textbox = ScrolledText(self, bootstyle="success round", wrap=WORD)
		self.url_textbox.place(relx=0.0285, rely=0.12, relwidth=0.450, relheight=0.1)
		# Add a right click menu
		self.url_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_url)

	def _add_headers_label(self) -> None:
		'''Set label for the URL box'''
		self.headers_label = tb.Label(self, text="Headers:")
		self.headers_label.place(in_=self.url_textbox, relx=0, rely=1.0, width=65, height=30)

	def _add_headers_frame(self) -> None:
		'''Add a scrolling frame for the headers'''
		self.headers_frame = ScrolledFrame(self, bootstyle="dark")
		self.headers_frame.vscroll.configure(bootstyle="success round")
		self.headers_frame.place(in_=self.url_textbox, relx=0, rely=1.0, y=25, relwidth=1.0, height=200)

	def _add_separator(self) -> None:
		'''Separate headers from request body'''
		self.sep = tb.Separator(self, bootstyle="success")
		self.sep.place(in_=self.url_textbox, relx=0, rely=1.0, y=234, relwidth=1.0, relheight=0.01)

	def _add_request_body_label(self) -> None:
		'''Set label for the URL box'''
		self.body_label = tb.Label(self, text="Body:")
		self.body_label.place(in_=self.sep, relx=0, rely=1.0, width=55, height=30)

	def _add_request_body_textbox(self) -> None:
		'''Add a request body text box'''
		self.request_body_textbox = ScrolledText(self, bootstyle="success round", wrap=WORD, hbar=True)
		self.request_body_textbox.place(in_=self.url_textbox, relx=0, rely=1.0, x=-2, y=262, relwidth=1.01, relheight=3.75)
		# Add a right click menu
		self.request_body_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_body)

	def _add_request_button(self) -> None:
		'''Add a send button for the request'''
		self.send_button = tb.Button(self, text="Send", command=self._send_request, bootstyle="danger", width=20)
		self.send_button.place(in_=self.request_body_textbox, relx=0.5, rely=1.0, x=-45.5, y=9, width=95, height=30)

	def _add_response_textbox(self) -> None:
		'''Add a response text box'''
		self.response_textbox = ScrolledText(self, state="disabled", bootstyle="success round", wrap=WORD, hbar=True)
		self.response_textbox.place(relx=0.507, rely=0.0168, relwidth=0.482, relheight=0.88)
		# Add a right click menu
		self.response_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_resp)

	def _add_response_search_entry(self) -> None:
		'''Add an entry response search field'''
		self.response_search_entry = tb.Entry(self, text="")
		self.response_search_entry.place(relx=0.5085, rely=0.905, relwidth=0.39, height=30)

	def _add_response_search_button(self) -> None:
		'''Add a search button for the response search field'''
		self.response_search_button = tb.Button(self, text="Search", command=self._search_response, bootstyle="danger", width=20)
		self.response_search_button.place(relx=0.906, rely=0.905, relwidth=0.08, height=30)

	def _add_response_toggle_regex(self) -> None:
		'''Add a toggle button to enable regex'''
		self.response_regex_toggle_int = IntVar()
		self.response_search_regex = tb.Checkbutton(self, text="Regex", variable=self.response_regex_toggle_int, style="success.Roundtoggle.Toolbutton")
		self.response_search_regex.place(in_=self.response_search_entry, relx=0, rely=1.0, width=80, height=30)

	def _add_response_toggle_case(self) -> None:
		'''Add a toggle button to enable case sensitivity'''
		self.response_case_toggle_int = IntVar()
		self.response_search_case = tb.Checkbutton(self, text="Case Sensitive", variable=self.response_case_toggle_int, style="success.Roundtoggle.Toolbutton")
		self.response_search_case.place(in_=self.response_search_regex, relx=1.0, rely=0, width=134, height=30)

	def _add_response_search_count_label(self) -> None:
		'''Add a lable for the request search count'''
		self.response_search_count = tb.Label(self, text="Match: 0/0")
		self.response_search_count.place(in_=self.response_search_case, relx=1.0, rely=0, width=160, height=30)

	def _add_response_time_label(self) -> None:
		'''Add a lable for the request/response time'''
		self.response_time = tb.Label(self, text="Duration: 0.000s")
		self.response_time.place(in_=self.response_search_entry, relx=1.0, rely=1.0, x=-110, width=175, height=30)
 
	def _clear_editor(self) -> None:
		'''Delete everything in the editor prior to populating it'''
		self.method_label.config(text="")
		self.url_textbox.__dict__["children"]["!text"].delete(1.0, END)
		self._delete_table(self.headers_frame)
		self.request_body_textbox.__dict__["children"]["!text"].delete(1.0, END)
		self.response_textbox.__dict__["children"]["!text"].configure(state="normal")
		self.response_textbox.__dict__["children"]["!text"].delete(1.0, END)
		self.response_textbox.__dict__["children"]["!text"].configure(state="disabled")

	def _send_to_editor(self, rowid: int) -> None:
		'''Send a request to the editor given its row id'''
		if rowid:
			self.request_id = rowid
			self._clear_editor()
			self.notebook.cursor.execute('''SELECT request_method, request_url, request_headers, request_body FROM transactions WHERE id = ?;''',(rowid,))
			row = self.notebook.cursor.fetchone()
			if row:
				method, url, headers, body = row
				if method:
					self.method_label.config(text=method)
				if url:
					self.url_textbox.__dict__["children"]["!text"].insert(END, url)
				if body:
					content_type = self.hp.get_content_type(json.loads(headers))
					mime = self.hp.evaluate_mimetype(body, content_type)
					body = self.cb.beautify(mime, body, False)
					self.request_body_textbox.__dict__["children"]["!text"].insert(END, body)
				if headers:
					headers = [[i['name'], i['value']] for i in json.loads(headers)]
					self._build_table(self.headers_frame, headers)

	def _send_to_fuzzer(self) -> None:
		'''Send request to fuzzer'''
		if self.request_id != -1:
			self.notebook.window.fuzz_tab._send_to_fuzzer(self.request_id)
			self.notebook.select(4)

	def _send_request(self) -> None:
		'''Send the edited request'''
		self.send_button.config(bootstyle="secondary")
		self.response_textbox.__dict__["children"]["!text"].configure(state="normal")
		self.response_textbox.__dict__["children"]["!text"].delete(1.0, END)
		self.response_textbox.__dict__["children"]["!text"].configure(state="disabled")
		self.update()
		method = self.method_label.cget("text")
		url = self.url_textbox.__dict__["children"]["!text"].get(1.0,END).strip()
		headers = self._get_headers()
		body = self.request_body_textbox.__dict__["children"]["!text"].get(1.0,END)[:-1]
		if method and url and headers:
			#print(method, url, headers, body)
			try:
				t1 = time.time()
				r = self.session.request(method, headers=headers, url=url, data=body, timeout=60)
				t2 = time.time()
				rtt = round(t2-t1,3)
				raw = self.cb.rebuild_response_requests(r)
				self.response_textbox.__dict__["children"]["!text"].configure(state="normal")
				self.response_textbox.__dict__["children"]["!text"].insert(END, raw)
				self.response_textbox.__dict__["children"]["!text"].configure(state="disabled")
				self.response_time.config(text=f"Duration: {rtt}s")
			except Exception as e:
				print("Send Request Exception:",e)
		self.send_button.config(bootstyle="danger")
		# Look for search string in results
		self._search_response(True)

	def _delete_table(self, frame: tb.Frame) -> None:
		'''Delete the table'''
		children = []
		for ckey in frame.children:
			children.append(frame.children[ckey])
		for child in children:
			child.destroy()

	def _build_table(self, frame: tb.Frame, arr: list) -> None:
		'''Insert the array as an editable table grid'''
		for i in range(0,len(arr)):
			for j in range(0,len(arr[0])):
				text = Text(frame, width=30, height=1) # Entry doesn't allow text selection
				text.grid(row=i, column=j, sticky="ew")
				text.insert(END, arr[i][j])
				text.bind("<Button-3>", self._right_click_headers)

	def _add_row(self, frame: tb.Frame) -> None:
		'''Add a row to the table'''
		data = self._get_table_data()
		if data:
			lastrow = len(data)
		else:
			lastrow = 0
		cols = ["testy","tester"]
		for i, col in enumerate(cols):
			text = Entry(frame, width=31)
			text.grid(row=lastrow, column=i)
			text.insert(END, cols[i])

	def _get_headers(self) -> dict:
		'''Return a dictionary of headers'''
		headers = {}
		matrix = self._get_table_data(self.headers_frame)
		if matrix:
			for name, value in matrix:
				headers[name.lower()] = value
		return headers

	def _get_table_data(self, frame: tb.Frame) -> list:
		'''Return an array of table text'''
		children = []
		table = []
		for ckey in frame.children:
			children.append(frame.children[ckey])
		for i in range(0,len(children),2):
			row = [children[i].get(1.0,END).strip(),children[i+1].get(1.0,END).strip()]
			table.append(row)
		return table

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

	# Right click menu for the URL text box

	def _add_url_context_menu(self) -> None:
		'''Add the context menu for the url text box'''
		self.mu_url = Menu(self, tearoff=False)
		self.mu_url.add_command(label="Copy", command=lambda:self.cm.copy(self.url_textbox.__dict__["children"]["!text"]))
		self.mu_url.add_command(label="Paste", command=lambda:self.cm.paste(self.url_textbox.__dict__["children"]["!text"]))
		self.mu_url.add_command(label="URL Encode", command=lambda:self.cm.url_encode(self.url_textbox.__dict__["children"]["!text"]))
		self.mu_url.add_separator()
		self.mu_url.add_command(label="Open in Fuzzer", command=self._send_to_fuzzer)
		#self.mu_url.add_command(label="Open in Scanner", command=None)
		self.mu_url.bind("<FocusOut>", self._close_url_menu)

	def _close_url_menu(self, event=None) -> None:
		'''Close the right click menu if you left click off it'''
		self.mu_url.unpost()

	def _right_click_url(self, event) -> None:
		'''Open the right click popup window'''
		try:
			self.mu_url.tk_popup(event.x_root + 1, event.y_root + 1)
		finally:
			self.mu_url.grab_release()

	# Right click menu for the headers

	def _add_headers_context_menu(self) -> None:
		'''Add the context menu for the headers frame'''
		self.mu_headers = Menu(self, tearoff=False)
		self.mu_headers.add_command(label="Copy", command=lambda:self.cm.copy(self.focus_get()))
		self.mu_headers.add_command(label="Paste", command=lambda:self.cm.paste(self.focus_get()))
		self.mu_headers.add_command(label="URL Encode", command=lambda:self.cm.url_encode(self.focus_get()))
		self.mu_headers.add_separator()
		self.mu_headers.add_command(label="Open in Fuzzer", command=self._send_to_fuzzer)
		#self.mu_headers.add_command(label="Open in Scanner", command=None)
		self.mu_headers.bind("<FocusOut>", self._close_headers_menu)

	def _close_headers_menu(self, event=None) -> None:
		'''Close the right click menu if you left click off it'''
		self.mu_headers.unpost()

	def _right_click_headers(self, event) -> None:
		'''Open the right click popup window'''
		try:
			self.mu_headers.tk_popup(event.x_root + 1, event.y_root + 1)
		finally:
			self.mu_headers.grab_release()

	# Right click menu for the body text box

	def _add_body_context_menu(self) -> None:
		'''Add the context menu for the body text box'''
		self.mu_body = Menu(self, tearoff=False)
		self.mu_body.add_command(label="Copy", command=lambda: self.cm.copy(self.request_body_textbox.__dict__["children"]["!text"]))
		self.mu_body.add_command(label="Paste", command=lambda: self.cm.paste(self.request_body_textbox.__dict__["children"]["!text"]))
		self.mu_body.add_command(label="URL Encode", command=lambda: self.cm.url_encode(self.request_body_textbox.__dict__["children"]["!text"]))
		self.mu_body.add_separator()
		self.mu_body.add_command(label="Open in Fuzzer", command=self._send_to_fuzzer)
		#self.mu_body.add_command(label="Open in Scanner", command=None)
		self.mu_body.bind("<FocusOut>", self._close_body_menu)

	def _close_body_menu(self, event=None) -> None:
		'''Close the right click menu if you left click off it'''
		self.mu_body.unpost()

	def _right_click_body(self, event) -> None:
		'''Open the right click popup window'''
		try:
			self.mu_body.tk_popup(event.x_root + 1, event.y_root + 1)
		finally:
			self.mu_body.grab_release()

	# Right click menu for the response text box

	def _add_response_context_menu(self) -> None:
		'''Add a right click menu for the response'''
		self.mu_resp = Menu(self, tearoff=False)
		self.mu_resp.add_command(label="Copy", command=lambda:self.cm.copy(self.response_textbox.__dict__["children"]["!text"]))
		self.mu_resp.add_command(label="Save Raw", command=lambda:self.cm.save_raw(self.response_textbox.__dict__["children"]["!text"]))
		self.mu_resp.bind("<FocusOut>", self._close_resp_menu)

	def _close_resp_menu(self, event=None) -> None:
		'''Close the right click menu if you left click off it'''
		self.mu_resp.unpost()

	def _right_click_resp(self, event) -> None:
		'''Open the right click popup window'''
		try:
			self.mu_resp.tk_popup(event.x_root + 1, event.y_root + 1)
		finally:
			self.mu_resp.grab_release()

