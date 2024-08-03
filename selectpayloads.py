#! /usr/bin/env python3

import re
from tkinter import *
import random

class SelectPayloads:

	def __init__(self) -> None:
		'''Initialize Payload Selector'''
		self.selections = {}
		self.preferred_colors = [
			"#35B279","#ff0066","#2B84D2","#EE8A12","#DF352E",
			"#9900ff", "#66ff99", "#00ffff", "#ffff00", "#838991"
		]
		self.tagged_colors = []

	def _choose_random_color(self) -> str:
		'''Return a random color string'''
		r = random.randint(0,255)
		g = random.randint(0,255)
		b = random.randint(0,255)
		return "#{:02X}{:02X}{:02X}".format(r, g, b)

	def _choose_color(self) -> str:
		'''Choose a highlight color'''
		if self.preferred_colors:
			thiscolor = self.preferred_colors[0]
			self.preferred_colors.pop(0)
		else:
			while 1:
				thiscolor = self._choose_random_color()
				if thiscolor not in self.tagged_colors:
					break
		return thiscolor

	def _is_overlapping(self, highlights: dict, line: int, start_idx: int, stop_idx: int) -> bool:
		'''Make sure this selection doesn't overlap a previous one'''
		highlighted = highlights[line]
		if highlighted:
			for start, stop, filepath in highlighted:
				if start_idx > start and start_idx < stop:
					return True
				if stop_idx > start and stop_idx < stop:
					return True
				if start_idx <= start and stop_idx >= stop:
					return True
		return False

	def highlight_selection(self, text, filepath: str, valid_selection_check: bool=False) -> tuple:
		'''Highlight selections in a scrolledtext to mark for a payload'''
		try:
			sel_start, sel_end = text.tag_ranges("sel")
			selected_text = text.__dict__["children"]["!text"].selection_get()
		except:
			selected_text = ""
		if selected_text:
			line1, start_idx = sel_start.string.split(".")
			line2, stop_idx = sel_end.string.split(".")
			if line1 == line2: # No multiline selections
				line = int(line1)
				start_idx = int(start_idx)
				stop_idx = int(stop_idx)
				if line not in self.selections:
					self.selections[line] = []
				if not self._is_overlapping(self.selections, line, start_idx, stop_idx):
					if valid_selection_check:
						return (True)
					self.selections[line].append((start_idx, stop_idx, filepath))
					self.selections[line].sort(key=lambda x:x[0])
					color = self._choose_color()
					self.tagged_colors.append(color)
					text.tag_add(color, sel_start, sel_end)
					text.tag_config(color, foreground="#1A1A1A", background=color)
					return (color, filepath)
		return ()

	def clear_selections(self, text) -> None:
		'''Clear selected items'''
		self.preferred_colors = [
			"#35B279","#ff0066","#2B84D2","#EE8A12","#DF352E",
			"#9900ff", "#66ff99", "#00ffff", "#ffff00", "#838991"
		]
		for color in self.tagged_colors:
			text.tag_remove(color, '1.0', END)
		self.tagged_colors = []
		self.selections = {}

	def prepare_template(self, text) -> tuple:
		'''Return the text with format variables in it for payloads'''
		text_content = text.__dict__["children"]["!text"].get(1.0, END)[:-1]
		text_lines = re.split(r"\r?\n", text_content)
		insertion_line_numbers = sorted(self.selections.keys())
		payload_num = 0
		ordered_file_paths = []
		for line in insertion_line_numbers:
			selections = sorted(self.selections[line], reverse=True, key=lambda x:x[0])
			sel_len = len(selections)
			payload_num += sel_len
			text_line = text_lines[line-1]
			file_paths = []
			for start_idx, stop_idx, filepath in selections:
				part1 = text_line[:start_idx]
				part2 = text_line[stop_idx:]
				payload_num -= 1
				text_line = part1 + "{" + str(payload_num) + "}" + part2
				file_paths.insert(0, filepath)
			ordered_file_paths.extend(file_paths)
			payload_num += sel_len
			text_lines[line-1] = text_line
		text_content = "\n".join(text_lines)
		return (text_content, ordered_file_paths)

