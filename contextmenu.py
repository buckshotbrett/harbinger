#! /usr/bin/env python3

import os
import re
import json
import urllib
from tkinter import filedialog

class ContextMenu:

	def __init__(self):
		'''Initialize functions used on multiple context menus'''
		pass

	def copy(self, widget) -> str:
		'''Return a string of selected text'''
		selected_text = ""
		try:
			selected_text = widget.selection_get()
		except:
			pass
		if selected_text:
			widget.clipboard_clear()
			widget.clipboard_append(selected_text)

	def copy_as_curl(self, widget, rowid, cursor) -> str:
		'''Copy curl command to the clipboard'''
		if rowid != -1:
			cursor.execute('''SELECT request_method, request_url, request_headers, request_body_type, request_body FROM transactions WHERE id = ?;''',(rowid,))
			results = cursor.fetchone()
			if results:
				method, url, headers, body_type, body = results
				command = f"curl -X {method}"
				headers = json.loads(headers)
				for header in headers:
					if header["name"].lower() == "accept-encoding":
						header["value"] = "identity"
					hdr = f"{header['name']}: {header['value']}"
					command += f" -H '{hdr}'"
				if body:
					if (body_type == "JSON") or (body_type == "XML"):
						body = re.sub(r"\x0d?\x0a", "", body)
					command += f" -d '{body}'"
				command += f" '{url}'"
				widget.clipboard_clear()
				widget.clipboard_append(command)

	def paste(self, widget) -> str:
		'''Paste a string of text'''
		selected_text = ""
		try:
			selected_text = widget.selection_get()
		except:
			pass
		if selected_text:
			clip = widget.clipboard_get()
			sel_start, sel_end = widget.tag_ranges("sel")
			widget.delete(sel_start, sel_end)
			widget.insert(sel_start, clip)

	def url_encode(self, widget) -> str:
		'''URL Encode the selected string'''
		selected_text = ""
		try:
			selected_text = widget.selection_get()
		except:
			pass
		if selected_text:
			sel_start, sel_end = widget.tag_ranges("sel")
			widget.delete(sel_start, sel_end)
			widget.insert(sel_start, urllib.parse.quote_plus(selected_text))

	def save_raw(self, widget) -> None:
		'''Save a raw request or response'''
		text_content = widget.get(1.0, "end")[:-1] # This operation adds a newline for some reason
		if text_content:
			text_content = re.sub(r"\x0d?\x0a","\x0d\x0a", text_content)
			desktop = os.path.expanduser("~/Desktop")
			save_path = filedialog.asksaveasfilename(initialdir=desktop, confirmoverwrite=True, filetypes=(("TXT Files","*.txt"),), defaultextension=".txt")
			if save_path:
				f = open(save_path,"w")
				f.write(text_content)
				f.close()

