#! /usr/bin/env python3

import os
import nbtbs
import filetab
import treetab
import historytab
import edittab
import fuzztab
from tkinter import *
import ttkbootstrap as tb

###################
### MAIN WINDOW ###
###################
class App(tb.Window):

	def __init__(self) -> None:
		'''Initialize Main Window'''
		super().__init__(themename="darkly")
		self.title("HARbinger")
		try:
			iconpath = os.path.join(os.path.dirname(__file__),"images/harbinger.png")
			img = PhotoImage(file=iconpath)
			self.tk.call('wm', 'iconphoto', self._w, img)
		except:
			pass
		self.minsize(1200,800)
		self._build_gui()

	def _build_gui(self) -> None:
		'''Add widgets to the window'''
		# Add a notebook
		self.nb_tbs = nbtbs.Nbtbs(self)
		# Add the file tab to the notebook
		self.file_tab = filetab.FileTab(self.nb_tbs)
		# Add the tree view tab to the notebook
		self.tree_view = treetab.TreeTab(self.nb_tbs)
		# Add the history view to the notebook
		self.history_view = historytab.HistoryTab(self.nb_tbs)
		# Add the editor tab to the notebook
		self.edit_view = edittab.EditTab(self.nb_tbs)
		# Add the fuzzer tab to the notebook
		self.fuzz_tab = fuzztab.FuzzTab(self.nb_tbs)

	def run(self) -> None:
		'''Runs the main GUI window'''
		self.mainloop()
