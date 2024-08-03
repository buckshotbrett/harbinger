#! /usr/bin/env python3

import re
from tkinter import *

class ScrolledTextSearch:

	def __init__(self, highlight_color) -> None:
		'''Initialize scrolled text search functions'''
		self.highlight_color = highlight_color
		self.scroll_indexes = []
		self.last_scroll_idx = 0
		self.last_search_str = ""
		self.last_regex = 0
		self.last_case = 0

	def search(self, regex_int, case_int, search_entry, search_target, count_label, new_click_target) -> None:
		'''Search the scrolledtext box for the specified string'''
		if regex_int.get() == 1:
			regex = True
		else:
			regex = False
		if case_int.get() == 1:
			nocase = 0
		else:
			nocase = 1
		self._search_text(search_entry, search_target, regex, nocase, new_click_target, count_label)

	def _search_regex(self, search_target, nocase, pattern):
		'''Search text with regex'''
		matches = []
		text = search_target.get("1.0", END).splitlines()
		if nocase:
			flgs = re.I
		else:
			flgs = 0
		for i, line in enumerate(text):
		    for match in re.finditer(pattern, line, flags=flgs):
		        matches.append((f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}"))
		return matches

	def _case_change(self, case_sensitive) -> bool:
		'''Return True if case sensitivity configuration has changed'''
		if self.last_case != case_sensitive:
			self.last_case = case_sensitive
			return True
		else:
			return False

	def _regex_change(self, regex) -> bool:
		'''Return True if the regex config settings have changed'''
		if self.last_regex != regex:
			self.last_regex = regex
			return True
		else:
			return False

	def _clear_existing_highlights(self, search_target) -> None:
		'''Clear tags'''
		search_target.tag_remove('found', '1.0', END)
		self.scroll_indexes = []
		self.last_scroll_idx = 0

	def _search_text(self, search_field, search_target, regex, case_sensitive, new_clicked_target, count_label):
		# Check if regex or case settings have changed
		new_case_config = self._case_change(case_sensitive)
		new_regex_config = self._regex_change(regex)
		# Get the search string
		search_str = search_field.get()
		if search_str:
			# If search string or search configuration options have changed
			if (search_str != self.last_search_str) or new_regex_config or new_case_config or new_clicked_target:
				self.last_search_str = search_str
				# remove existing highlights
				self._clear_existing_highlights(search_target)
				# Search for strings/expressions and tag them
				if regex: # search with regular expressions
					for idx, lastidx in self._search_regex(search_target, case_sensitive, search_str):
						self.scroll_indexes.append(idx)
						search_target.tag_add('found', idx, lastidx)
				else: # search with raw strings (case sensitive or not)
					idx = '1.0'
					while 1:
						# searches for desired string
						idx = search_target.search(search_str, idx, nocase=case_sensitive, stopindex=END)
						if not idx:
							break
						self.scroll_indexes.append(idx)
						lastidx = '%s+%dc' % (idx, len(search_str))
						# overwrite 'Found' at idx
						search_target.tag_add('found', idx, lastidx)
						idx = lastidx
				# mark located string
				search_target.tag_config('found', background=self.highlight_color)
				# Scroll to highlights
				if self.scroll_indexes:
					self.last_scroll_idx = 0
					search_target.see(self.scroll_indexes[self.last_scroll_idx])
				# Update the count label
				found = len(self.scroll_indexes)
				if found > 0:
					firstmatch = 1
				else:
					firstmatch = 0
				count_label.config(text=f"Match: {firstmatch}/{found}")
			else: # If search strings and config options haven't changed, scroll through selections
				idx_len = len(self.scroll_indexes)
				for i in range(0, idx_len):
					if i > self.last_scroll_idx:
						self.last_scroll_idx = i
						break
				else:
					self.last_scroll_idx = 0
				if self.scroll_indexes:
					search_target.see(self.scroll_indexes[self.last_scroll_idx])
					found = len(self.scroll_indexes)
					count_label.config(text=f"Match: {self.last_scroll_idx+1}/{found}")
		else: # Clear scroll indexes and count label
			self.scroll_indexes = []
			found = len(self.scroll_indexes)
			count_label.config(text=f"Match: 0/0")
