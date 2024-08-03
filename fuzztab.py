#! /usr/bin/env python3

import os
import fuzzer
import threading
import selectpayloads
import contentbeautifier
import scrolledtextsearch
import contextmenu
from tkinter import *
import ttkbootstrap as tb
from tkinter import filedialog
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tableview import Tableview

# To make Meter widgets compatibility with newer PIL versions
from PIL import Image
Image.CUBIC = Image.BICUBIC

################
### FUZZ TAB ###
################
class FuzzTab(tb.Frame):

	def __init__(self, notebook: tb.Notebook) -> None:
		'''Initialize the configuration tab'''
		self.notebook = notebook
		super().__init__(self.notebook)
		self.notebook.add(self, text="Fuzzer") # Add itself to the notebook
		self.fzr = fuzzer.Fuzzer()
		self.cb = contentbeautifier.ContentBeautifier()
		self.sp = selectpayloads.SelectPayloads()
		self.sts = scrolledtextsearch.ScrolledTextSearch("#35B279")
		self.selected_pane = 0
		self.selected_request_id = -1
		self.last_clicked = -1
		self.cols = [
			{"text": "id", "stretch": False},
			{"text":"status_code","stretch":False},
			{"text":"rtt (s)","stretch":False},
			{"text":"content_length","stretch":False},
			{"text":"payloads","stretch":True},
			{"text":"reflected","stretch":False},
			{"text":"timeout","stretch":False},
			{"text":"errors","stretch":False},
			{"text":"timestamp","stretch":False}
		]
		self.cm = contextmenu.ContextMenu()
		self.request_id = -1
		self._add_widgets()

	def _add_widgets(self) -> None:
		'''Add widgets to the frame'''
		# Add the label frame to the fuzzer tab
		self._add_label_frame()
		# Add the config button for the config pane
		self._add_config_button()
		# Add the results button for the results pane
		self._add_results_button()
		# Add the config frame
		self._add_config_frame()
		# Add the results frame
		self._add_results_frame()
		# Add a progress bar to the bottom
		self._add_progress_bar()
		# Add a config request context menu
		self._add_request_context_menu()
		# Add a fuzz request context menu
		self._add_request_fuzz_context_menu()
		# Add a fuzz response context menu
		self._add_response_fuzz_context_menu()

	def _add_label_frame(self) -> None:
		'''Create the label frame for the fuzzer'''
		self.label_frame = tb.Labelframe(self, bootstyle="info")
		self.label_frame.place(relx=0.013, rely=0.03, relwidth=0.974, relheight=0.925)

	def _add_config_button(self) -> None:
		'''Add a button to select the config pane'''
		self.config_button = tb.Button(self, text="Configure", command=lambda:self._switch_pane(0), bootstyle="info")
		self.config_button.place(relx=0.0175, rely=0.025, width=118, height=30)

	def _add_results_button(self) -> None:
		'''Add a button to select the config pane'''
		self.results_button = tb.Button(self, text="Results", command=lambda:self._switch_pane(1), bootstyle="info outline")
		self.results_button.place(in_=self.config_button, relx=0, rely=0, x=118, width=118, height=30)

	####################
	### CONFIG FRAME ###
	####################
	def _add_config_frame(self) -> None:
		'''Add a config frame to the label frame'''
		self.config_frame = tb.Frame(self)
		### Add widgets to the config pane ###
		# Add the request text box
		self._add_request_textbox(self.config_frame)
		# Add the button to clear selections
		self._add_clear_button(self.config_frame)
		# Add the button to select text
		self._add_selection_button(self.config_frame)
		# Add a label for the combobox encoders
		self._add_encoder_label(self.config_frame)
		# Add a selection combobox for encoders
		self._add_encoder_combobox(self.config_frame)
		# Add a meter to control the delay between requests
		self._add_delay_meter(self.config_frame)
		# Add a meter to control the number of threads
		self._add_threads_meter(self.config_frame)
		# Add a meter to control request timeout
		self._add_timeout_meter(self.config_frame)
		# Add the file payload tree
		self._add_files_tree(self.config_frame)
		# Add the button to start fuzzing
		self._add_fuzz_button(self.config_frame)
		# Add the button to stop fuzzing
		self._add_stop_button(self.config_frame)
		# Place the frame
		self.config_frame.place(relx=0.018, rely=0.07, relwidth=0.9635, relheight=0.876)

	def _add_request_textbox(self, parent_frame) -> None:
		'''Add a request text box'''
		self.request_textbox = ScrolledText(parent_frame, bootstyle="info round", wrap=WORD, hbar=True)
		self.request_textbox.place(relx=0.0135, rely=0.008, relwidth=0.485, relheight=0.925)
		# Add a right click menu
		self.request_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_request)

	def _add_clear_button(self, parent_frame) -> None:
		'''Add a send button for the request'''
		self.clear_button = tb.Button(parent_frame, text="Clear", command=self._clear_payload_positions, bootstyle="success", width=20)
		self.clear_button.place(in_=self.request_textbox, relx=0.5, rely=1.0, x=-85, y=10, width=80, height=30)

	def _add_selection_button(self, parent_frame) -> None:
		'''Add a send button for the request'''
		self.select_button = tb.Button(parent_frame, text="Select", command=self._select_payload_positions, bootstyle="warning", width=20)
		self.select_button.place(in_=self.request_textbox, relx=0.5, rely=1.0, x=5, y=10, width=80, height=30)

	def _add_encoder_label(self, parent_frame) -> None:
		'''Add the encoder label'''
		self.enc_label = tb.Label(parent_frame, text="Encoder:")
		self.enc_label.place(relx=0.51, rely=0.0, relwidth=0.052, height=30)

	def _add_encoder_combobox(self, parent_frame) -> None:
		'''Add a combo box for encoders'''
		self.mb_encoders = tb.Menubutton(parent_frame, text='None', bootstyle='secondary')
		self.mb_encoders.place(relx=0.51, rely=0.036, relwidth=0.48, relheight=0.045)
		# create menu and add options
		self.enc_menu = tb.Menu(self.mb_encoders)
		self.enc_str = StringVar()
		self.enc_str.set("None") # Setting menu default value
		for opt in self.fzr.encoders.keys():
			self.enc_menu.add_radiobutton(label=opt, variable=self.enc_str, command=self._click_encoder)
		# associate menu with menubutton
		self.mb_encoders['menu'] = self.enc_menu

	def _click_encoder(self) -> None:
		'''Click a method option on the menu'''
		enc = self.enc_str.get()
		self.mb_encoders.config(text=enc)

	def _add_threads_meter(self, parent_frame) -> None:
		'''Add a meter for the number of fuzzing threads'''
		self.thread_meter = tb.Meter(parent_frame, bootstyle="danger", subtext="Threads", metertype="semi", amountused=4, amounttotal=100, metersize=150, interactive=True)
		self.thread_meter.place(in_=self.delay_meter, relx=-1.0, rely=0.0, x=-45, bordermode="outside")

	def _add_delay_meter(self, parent_frame) -> None:
		'''Add a meter for the number of fuzzing threads'''
		self.delay_meter = tb.Meter(parent_frame, bootstyle="warning", subtext="Delay", metertype="semi", textright="s", amountused=0, amounttotal=300, metersize=150, interactive=True)
		self.delay_meter.place(in_=self.mb_encoders, relx=0.5, rely=1.0, x=-75, y=12, bordermode="outside")

	def _add_timeout_meter(self, parent_frame) -> None:
		'''Add a meter for the number of fuzzing threads'''
		self.timeout_meter = tb.Meter(parent_frame, bootstyle="success", subtext="Timeout", metertype="semi", textright="s", amountused=90, amounttotal=300, metersize=150, interactive=True)
		self.timeout_meter.place(in_=self.delay_meter, relx=1.0, rely=0.0, x=45, bordermode="outside")

	def _add_files_tree(self, parent_frame) -> None:
		'''Add a tree for payload file paths'''
		self.file_tree = tb.Treeview(parent_frame, bootstyle="info")
		self.file_tree.heading('#0', text="Payload Files")
		self.file_tree.place(in_=self.mb_encoders, relx=0, rely=1.0, relwidth=1.0, relheight=13.67, y=152)

	def _add_fuzz_button(self, parent_frame) -> None:
		'''Add a send button for the request'''
		self.fuzz_button = tb.Button(parent_frame, text="Fuzz", command=self._start_fuzzer_thread, bootstyle="danger", width=20)
		self.fuzz_button.place(in_=self.file_tree, relx=0.5, rely=1.0, x=-85, y=10, width=80, height=30, bordermode="outside")

	def _add_stop_button(self, parent_frame) -> None:
		'''Add a send button for the request'''
		self.stop_button = tb.Button(parent_frame, text="Stop", command=self._stop_fuzzer, bootstyle="secondary", state="disabled", width=20)
		self.stop_button.place(in_=self.file_tree, relx=0.5, rely=1.0, x=5, y=10, width=80, height=30, bordermode="outside")

	#####################
	### RESULTS FRAME ###
	#####################
	def _add_results_frame(self) -> None:
		'''Add a results frame to the label frame'''
		self.results_frame = tb.Frame(self)
		# Commented out placement since this pane is now shown yet
		#self.results_frame.place(relx=0.018, rely=0.07, relwidth=0.9635, relheight=0.876)
		# Add a table to the results frame
		self._add_table(self.results_frame)
		# Add a request text box
		self._add_fuzz_req_textbox(self.results_frame)
		# Add a request search entry
		self._add_fuzz_req_search_entry(self.results_frame)
		# Add a search button for the fuzz request
		self._add_fuzz_req_search_button(self.results_frame)
		# Add the fuzz request regex toggle
		self._add_request_toggle_regex(self.results_frame)
		# Add the fuzz request case toggle
		self._add_request_toggle_case(self.results_frame)
		# Add the request search count label
		self._add_request_search_count_label(self.results_frame)
		# Add a response text box
		self._add_fuzz_res_textbox(self.results_frame)
		# Add a response search entry
		self._add_fuzz_res_search_entry(self.results_frame)
		# Add a response search button
		self._add_fuzz_res_search_button(self.results_frame)
		# Add the fuzz response regex toggle
		self._add_response_toggle_regex(self.results_frame)
		# Add the fuzz response case toggle
		self._add_response_toggle_case(self.results_frame)
		# Add the response search count label
		self._add_response_search_count_label(self.results_frame)

	def _add_table(self, parent_frame) -> None:
		'''Add a table to the tab'''
		self.fuzz_table = Tableview(parent_frame, paginated=False, autofit=True, bootstyle="secondary", coldata=self.cols, rowdata=(), searchable=False)
		self.fuzz_table.place(relx=0.01, rely=0.001, relwidth=0.98, relheight=0.48)
		self.fuzz_table.view.bind("<Double-1>", self._double_click_row)

	### FUZZ REQUEST ###

	def _add_fuzz_req_textbox(self, parent_frame) -> None:
		'''Add a request text box'''
		self.fuzz_req_textbox = ScrolledText(parent_frame, state="normal", bootstyle="info round", wrap=WORD, hbar=True)
		self.fuzz_req_textbox.place(relx=0.008, rely=0.50, relwidth=0.485, relheight=0.40)
		# Add a right click menu
		self.fuzz_req_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_fuzz_request)

	def _add_fuzz_req_search_entry(self, parent_frame) -> None:
		'''Add an entry request search field'''
		self.fuzz_req_search_entry = tb.Entry(parent_frame, text="")
		self.fuzz_req_search_entry.place(in_=self.fuzz_req_textbox, relx=0, rely=1.0, y=13, relwidth=0.80, height=30)

	def _add_fuzz_req_search_button(self, parent_frame) -> None:
		'''Add a search button for the request search field'''
		self.fuzz_req_search_button = tb.Button(parent_frame, text="Search", command=self._search_request, bootstyle="success", width=20)
		self.fuzz_req_search_button.place(in_=self.fuzz_req_textbox, relx=0.82, rely=1.0, y=13, relwidth=0.18, height=30)

	def _add_request_toggle_regex(self, parent_frame) -> None:
		'''Add a toggle button to enable regex'''
		self.request_regex_toggle_int = IntVar()
		self.request_search_regex = tb.Checkbutton(parent_frame, text="Regex", variable=self.request_regex_toggle_int, style="info.Roundtoggle.Toolbutton")
		self.request_search_regex.place(in_=self.fuzz_req_search_entry, relx=0, rely=1.0, width=80, height=30)

	def _add_request_toggle_case(self, parent_frame) -> None:
		'''Add a toggle button to enable case sensitivity'''
		self.request_case_toggle_int = IntVar()
		self.request_search_case = tb.Checkbutton(parent_frame, text="Case Sensitive", variable=self.request_case_toggle_int, style="info.Roundtoggle.Toolbutton")
		self.request_search_case.place(in_=self.request_search_regex, relx=1.0, rely=0, width=134, height=30)

	def _add_request_search_count_label(self, parent_frame) -> None:
		'''Add a lable for the request search count'''
		self.request_search_count = tb.Label(parent_frame, text="Match: 0/0")
		self.request_search_count.place(in_=self.request_search_case, relx=1.0, rely=0, width=160, height=30)

	### FUZZ RESPONSE ###

	def _add_fuzz_res_textbox(self, parent_frame) -> None:
		'''Add a response text box'''
		self.fuzz_res_textbox = ScrolledText(parent_frame, state="normal", bootstyle="info round", wrap=WORD, hbar=True)
		self.fuzz_res_textbox.place(relx=0.503, rely=0.50, relwidth=0.49, relheight=0.40)
		# Add a right click menu
		self.fuzz_res_textbox.__dict__["children"]["!text"].bind("<Button-3>", self._right_click_fuzz_response)

	def _add_fuzz_res_search_entry(self, parent_frame) -> None:
		'''Add an entry response search field'''
		self.fuzz_res_search_entry = tb.Entry(parent_frame, text="")
		self.fuzz_res_search_entry.place(in_=self.fuzz_res_textbox, relx=0, rely=1.0, y=13, relwidth=0.80, height=30)

	def _add_fuzz_res_search_button(self, parent_frame) -> None:
		'''Add a search button for the response search field'''
		self.fuzz_res_search_button = tb.Button(parent_frame, text="Search", command=self._search_response, bootstyle="success", width=20)
		self.fuzz_res_search_button.place(in_=self.fuzz_res_textbox, relx=0.82, rely=1.0, y=13, relwidth=0.18, height=30)

	def _add_response_toggle_regex(self, parent_frame) -> None:
		'''Add a toggle button to enable regex'''
		self.response_regex_toggle_int = IntVar()
		self.response_search_regex = tb.Checkbutton(parent_frame, text="Regex", variable=self.response_regex_toggle_int, style="info.Roundtoggle.Toolbutton")
		self.response_search_regex.place(in_=self.fuzz_res_search_entry, relx=0, rely=1.0, width=80, height=30)

	def _add_response_toggle_case(self, parent_frame) -> None:
		'''Add a toggle button to enable case sensitivity'''
		self.response_case_toggle_int = IntVar()
		self.response_search_case = tb.Checkbutton(parent_frame, text="Case Sensitive", variable=self.response_case_toggle_int, style="info.Roundtoggle.Toolbutton")
		self.response_search_case.place(in_=self.response_search_regex, relx=1.0, rely=0, width=134, height=30)

	def _add_response_search_count_label(self, parent_frame) -> None:
		'''Add a lable for the request search count'''
		self.response_search_count = tb.Label(parent_frame, text="Match: 0/0")
		self.response_search_count.place(in_=self.response_search_case, relx=1.0, rely=0, width=160, height=30)

	def _add_progress_bar(self) -> None:
		'''Add a progress bar to the bottom'''
		self.progress_bar = tb.Progressbar(self, bootstyle="success", maximum=1.0, value=0)
		self.progress_bar.place(relx=0.013, rely=0.97, relwidth=0.974, height=10)

	###########################
	### OTHER FUNCTIONALITY ###
	###########################
	def _switch_pane(self, clicked: int=1) -> None:
		'''Switch between the config and results pane'''
		# Results pane is selected
		if clicked == 0:
			if self.selected_pane == 1:
				self.results_button.config(bootstyle="info outline")
				self.config_button.config(bootstyle="info")
				self.results_frame.place_forget()
				self.config_frame.place(relx=0.018, rely=0.07, relwidth=0.9635, relheight=0.876)
				self.selected_pane = 0
		# Config pane is selected
		if clicked == 1:
			if self.selected_pane == 0:
				self.results_button.config(bootstyle="info")
				self.config_button.config(bootstyle="info outline")
				self.config_frame.place_forget()
				self.results_frame.place(relx=0.018, rely=0.07, relwidth=0.9635, relheight=0.876)
				self.selected_pane = 1


	def _clear_fuzzer(self) -> None:
		'''Delete everything in the editor prior to populating it'''
		for item in self.file_tree.get_children():
			self.file_tree.delete(item)
		self.sp.clear_selections(self.request_textbox)
		self.request_textbox.__dict__["children"]["!text"].delete(1.0, END)
		self.fuzz_req_textbox.__dict__["children"]["!text"].configure(state="normal")
		self.fuzz_res_textbox.__dict__["children"]["!text"].configure(state="normal")
		self.fuzz_req_textbox.delete(1.0, END)
		self.fuzz_res_textbox.delete(1.0, END)
		self.fuzz_req_textbox.__dict__["children"]["!text"].configure(state="disabled")
		self.fuzz_res_textbox.__dict__["children"]["!text"].configure(state="disabled")

	def _send_to_fuzzer(self, rowid: int) -> None:
		'''Send raw request to the fuzzer'''
		if rowid:
			self.request_id = rowid
			self._clear_fuzzer()
			self._switch_pane(0)
			self.notebook.cursor.execute('''SELECT request_method, request_url, request_headers, request_body FROM transactions WHERE id = ?;''',(rowid,))
			row = self.notebook.cursor.fetchone()
			if row:
				self.selected_request_id = rowid
				method, url, headers, body = row
				raw_request = self.cb.rebuild_request(method, url, headers, body)
				self.request_textbox.__dict__["children"]["!text"].insert(END, raw_request)

	def _clear_payload_positions(self) -> None:
		'''Clear all payload positions and files tree'''
		for item in self.file_tree.get_children():
			self.file_tree.delete(item)
		self.sp.clear_selections(self.request_textbox)

	def _select_payload_positions(self) -> None:
		'''Action that occurs when the select button is clicked'''
		is_valid_selection = self.sp.highlight_selection(self.request_textbox, "", valid_selection_check=True)
		if is_valid_selection:
			init_dir = os.path.join(os.path.dirname(__file__), "fuzz_payloads")
			payload_filepath = filedialog.askopenfilename(initialdir=init_dir, title="Select payload file", filetypes=(("TXT files","*.txt"),("All Files","*.*")))
			if payload_filepath:
				selected = self.sp.highlight_selection(self.request_textbox, payload_filepath)
				if selected:
					color, filepath = selected
					self.file_tree.insert("", index="end", iid=None, text=payload_filepath, tags=(color,))
					self.file_tree.tag_configure(color, foreground="#1A1A1A", background=color)

	def _start_fuzzer_thread(self) -> None:
		'''Start fuzzer'''
		if self.sp.selections:
			t = threading.Thread(target=self._start_fuzzer, args=())
			t.daemon = True
			t.start()

	def _start_fuzzer(self) -> None:
		'''Start the fuzzer'''
		self.progress_bar["value"] = 0
		self.fuzz_table.delete_rows()
		self.fuzz_req_textbox.__dict__["children"]["!text"].configure(state="normal")
		self.fuzz_res_textbox.__dict__["children"]["!text"].configure(state="normal")
		self.fuzz_req_textbox.delete(1.0, END)
		self.fuzz_res_textbox.delete(1.0, END)
		self.fuzz_req_textbox.__dict__["children"]["!text"].configure(state="disabled")
		self.fuzz_res_textbox.__dict__["children"]["!text"].configure(state="disabled")
		self.fuzz_button.config(bootstyle="secondary", state="disabled")
		self.clear_button.config(state="disabled")
		self.select_button.config(state="disabled")
		self.stop_button.config(bootstyle="danger", state="normal")
		self.update()
		self._switch_pane(1)
		encoder = self.enc_str.get()
		thread_count = int(self.thread_meter.amountusedvar.get())
		delay_time = int(self.delay_meter.amountusedvar.get())
		timeout_length = int(self.timeout_meter.amountusedvar.get())
		template_info = self.sp.prepare_template(self.request_textbox)
		if template_info:
			template, ordered_file_paths = template_info
			self.fzr.fuzz(template, ordered_file_paths, encoder, timeout_length, thread_count, delay_time, self.notebook.conn, self.notebook.cursor, self.progress_bar, self.fuzz_table)
		self._load_table()
		self.progress_bar.config(bootstyle="success")
		self.progress_bar["value"] = 0
		self.stop_button.config(bootstyle="secondary", state="disabled")
		self.clear_button.config(state="normal")
		self.select_button.config(state="normal")
		self.fuzz_button.config(bootstyle="danger", state="normal")

	def _stop_fuzzer(self) -> None:
		'''Stop the fuzzer'''
		self.stop_button.config(bootstyle="secondary", state="disabled")
		self.update()
		self.fzr.kill_fuzzer(self.notebook.conn)
		self.clear_button.config(state="normal")
		self.select_button.config(state="normal")
		self.fuzz_button.config(bootstyle="danger", state="normal")
		self.fuzz_table.load_table_data()

	def _load_table(self) -> None:
		'''Load table rows from the database'''
		self.fuzz_table.delete_rows()
		self.notebook.cursor.execute('''SELECT id, status_code, rtt, content_length, payloads, reflected, timeout, errors, timestamp FROM fuzz;''')
		rows = self.notebook.cursor.fetchall()
		if rows:
			self.fuzz_table.build_table_data(coldata=self.cols, rowdata=rows)

	def _double_click_row(self, event) -> None:
		'''Click a row'''
		try:
			iid = self.fuzz_table.view.focus()
			row = self.fuzz_table.get_row(iid=iid)
		except:
			row = None
		if row:
			if row.values:
				request_id = row.values[0]
				if request_id != self.last_clicked:
					self.last_clicked = request_id
					self.notebook.cursor.execute('''SELECT raw_request, raw_response FROM fuzz WHERE id = ?;''',(request_id,))
					fuzz_request_info = self.notebook.cursor.fetchone()
					if fuzz_request_info:
						raw_request, raw_response = fuzz_request_info
						# Set the text in each pane.
						### ENABLE DISABLED ScrolledText PANE - !!! Its insane it had to be done this way !!!
						self.fuzz_req_textbox.__dict__["children"]["!text"].configure(state="normal")
						self.fuzz_res_textbox.__dict__["children"]["!text"].configure(state="normal")
						self.fuzz_req_textbox.delete(1.0, END)
						self.fuzz_res_textbox.delete(1.0, END)
						self.fuzz_req_textbox.insert(END, raw_request)
						self.fuzz_res_textbox.insert(END, raw_response)
						### DISABLE ENABLED ScrolledText PANE - !!! Its insane it had to be done this way !!!
						self.fuzz_req_textbox.__dict__["children"]["!text"].configure(state="disabled")
						self.fuzz_res_textbox.__dict__["children"]["!text"].configure(state="disabled")
						# Perform searches
						self._search_request(True)
						self._search_response(True)

	def _search_request(self, new_click_target: bool=False):
		'''Search the request'''
		self.sts.search(
			self.request_regex_toggle_int,
			self.request_case_toggle_int,
			self.fuzz_req_search_entry,
			self.fuzz_req_textbox.__dict__["children"]["!text"],
			self.request_search_count,
			new_click_target
		)

	def _search_response(self, new_click_target: bool=False):
		'''Search the response'''
		self.sts.search(
			self.response_regex_toggle_int,
			self.response_case_toggle_int,
			self.fuzz_res_search_entry,
			self.fuzz_res_textbox.__dict__["children"]["!text"],
			self.response_search_count,
			new_click_target
		)

	def _send_to_editor(self) -> None:
		'''Send request to editor'''
		if self.request_id != -1:
			self.notebook.window.edit_view._send_to_editor(self.request_id)
			self.notebook.select(3)

	# Create a right click menu for the config request box

	def _add_request_context_menu(self) -> None:
		'''Add a right click menu on a target to show a menu'''
		self.mu_request = Menu(self, tearoff=False)
		self.mu_request.add_command(label="Copy", command=lambda:self.cm.copy(self.request_textbox.__dict__["children"]["!text"]))
		self.mu_request.add_command(label="Paste", command=lambda: self.cm.paste(self.request_textbox.__dict__["children"]["!text"]))
		self.mu_request.add_command(label="URL Encode", command=lambda: self.cm.url_encode(self.request_textbox.__dict__["children"]["!text"]))
		self.mu_request.add_command(label="Save Raw", command=lambda:self.cm.save_raw(self.request_textbox.__dict__["children"]["!text"]))
		self.mu_request.add_separator()
		self.mu_request.add_command(label="Open in Editor", command=self._send_to_editor)
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

	# Create a right click menu for the fuzz request box

	def _add_request_fuzz_context_menu(self) -> None:
		'''Add a right click menu on a target to show a menu'''
		self.mu_fuzz_request = Menu(self, tearoff=False)
		self.mu_fuzz_request.add_command(label="Copy", command=lambda:self.cm.copy(self.fuzz_req_textbox.__dict__["children"]["!text"]))
		self.mu_fuzz_request.add_command(label="Save Raw", command=lambda:self.cm.save_raw(self.fuzz_req_textbox.__dict__["children"]["!text"]))
		self.mu_fuzz_request.bind("<FocusOut>", self._close_request_fuzz_menu)

	def _close_request_fuzz_menu(self, event=None) -> None:
		'''Close the right click menu if you left click off it'''
		self.mu_fuzz_request.unpost()

	def _right_click_fuzz_request(self, event) -> None:
		'''Open the right click popup window'''
		try:
			self.mu_fuzz_request.tk_popup(event.x_root + 1, event.y_root + 1)
		finally:
			self.mu_fuzz_request.grab_release()

	# Create a right click menu for the fuzz response box

	def _add_response_fuzz_context_menu(self) -> None:
		'''Add a right click menu on a target to show a menu'''
		self.mu_fuzz_response = Menu(self, tearoff=False)
		self.mu_fuzz_response.add_command(label="Copy", command=lambda:self.cm.copy(self.fuzz_res_textbox.__dict__["children"]["!text"]))
		self.mu_fuzz_response.add_command(label="Save Raw", command=lambda:self.cm.save_raw(self.fuzz_res_textbox.__dict__["children"]["!text"]))
		self.mu_fuzz_response.bind("<FocusOut>", self._close_response_fuzz_menu)

	def _close_response_fuzz_menu(self, event=None) -> None:
		'''Close the right click menu if you left click off it'''
		self.mu_fuzz_response.unpost()

	def _right_click_fuzz_response(self, event) -> None:
		'''Open the right click popup window'''
		try:
			self.mu_fuzz_response.tk_popup(event.x_root + 1, event.y_root + 1)
		finally:
			self.mu_fuzz_response.grab_release()
