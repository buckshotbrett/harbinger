#! /usr/bin/env python3

from tkinter import *
import ttkbootstrap as tb

################
### NOTEBOOK ###
################
class Nbtbs(tb.Notebook):

	def __init__(self, window: tb.Window) -> None:
		'''Create a notebook (set of tabs)'''
		self.window = window
		super().__init__(self.window, bootstyle="dark")
		self.pack(fill="both", expand="True", padx=5, pady=5)
		self.conn = None
		self.cursor = None

	def __del__(self):
		'''Destructor'''
		try:
			self.conn.close()
		except:
			pass
