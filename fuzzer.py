#! /usr/bin/env python3

import re
import json
import time
import queue
import urllib
import sqlite3
import requests
import datetime
import itertools
import threading
import contentbeautifier

class Fuzzer:

	def __init__(self) -> None:
		'''Initalize a fuzzer object'''
		self.encoder = None
		self.timeout = 90
		self.threads = 4
		self.delay = 0
		self.request_queue = queue.Queue(maxsize=100)
		self.session = requests.Session()
		self.lock = threading.Lock()
		self.cb = contentbeautifier.ContentBeautifier()
		self.num_of_payloads = 1
		self.payload_idx = 0
		self.is_running = False
		self.encoders = {
			"url": self._format_url,
			"json": self._format_json,
			"cookie": self._format_cookie,
			"xml": self._format_xml,
			"base64": self._format_base64,
			"base64url": self._format_base64_url,
			"None": self._format_none
		}

	def kill_fuzzer(self, conn) -> None:
		'''Stop the current fuzzing'''
		if self.is_running:
			self.is_running = False
			while 1:
				try:
					entry = self.request_queue.get(block=True, timeout=2)
				except queue.Empty:
					break
		conn.commit()

	def _update_progress_bar(self, progress_bar) -> None:
		'''Update the progress bar status'''
		status = self.payload_idx / self.num_of_payloads
		if status < 1.0:
			progress_bar["value"] = status

	def _load_payloads(self, file_paths: list) -> list:
		'''Return a list of lists'''
		self.num_of_payloads = 1
		self.payload_idx = 0
		payloads = []
		for path in file_paths:
			payload_set = []
			f = open(path,"r")
			for line in f:
				p = line.strip()
				payload_set.append(p)
			f.close()
			self.num_of_payloads *= len(payload_set)
			payloads.append(payload_set)
		return payloads

	def _iter_format_payloads(self, template: str, payloads: list, encoding: str) -> str:
		'''Load the queue with request data formatted with payloads'''
		for payload_set in itertools.product(*payloads):
			if not self.is_running:
				break
			formatted_payloads = self._format_payloads(payload_set, encoding)
			formatted_request = template.format(*formatted_payloads)
			lines = re.split(r"\r?\n", formatted_request)
			if lines:
				request_line = lines[0]
				method, url, version = re.split(r"\s+", request_line)
				headers = {}
				for i in range(1, len(lines)):
					if re.search(r":\s", lines[i]):
						name, value = re.split(r":\s+", lines[i])
						headers[name] = value
					else:
						break
				body_lines = lines[i+1:]
				body = ""
				if body_lines:
					body = "\n".join(body_lines)
				self.request_queue.put(
					{
						"method": method,
						"url": url,
						"headers": headers,
						"data": body,
						"payloads": payload_set,
						"raw_request": formatted_request
					}
				)

	def _format_payloads(self, payloads: tuple, encoding: str) -> list:
		'''Return a list of formatted payloads'''
		if encoding in self.encoders:
			encoder = self.encoders[encoding]
		else:
			encoder = self.encoders["None"]
		return [encoder(i) for i in payloads]

	def _format_url(self, payload: str) -> str:
		'''Return string encoded to be URL parameter compatible'''
		return urllib.parse.quote_plus(payload)

	def _format_json(self, payload: str) -> str:
		'''Return string encoded to be JSON compatible'''
		return json.dumps(payload)

	def _format_cookie(self, payload: str) -> str:
		'''Return string encoded to be cookie format compatible'''
		return urllib.parse.quote_plus(payload).replace("+","%20")

	def _format_base64(self, payload: str) -> str:
		'''Return a base64 encoded payload'''
		return str(base64.b64encode(bytes(payload,"utf-8")),"utf-8")

	def _format_base64_url(self, payload: str) -> str:
		'''Return a url-safe base64 encoded payload'''
		return str(base64.urlsafe_b64encode(bytes(payload,"utf-8")),"utf-8")

	def _format_xml(self, payload: str) -> str:
		'''Return string encoded to be in an xml document'''
		payload = payload.replace("&", "&amp;")
		payload = payload.replace("<", "&lt;")
		payload = payload.replace(">", "&gt;")
		payload = payload.replace('"', "&quot;")
		payload = payload.replace("'", "&apos;")
		return payload

	def _format_none(self, payload: str) -> str:
		'''Return the original payload without encoding'''
		return payload

	def _send_request(self, cursor: sqlite3.Cursor, progress_bar, fuzz_table) -> None:
		'''Get request data from the queue and send it'''
		queue_timeout = 2
		while self.is_running:
			try:
				# Prepare variables for results
				error = ""
				req_data = self.request_queue.get(block=True, timeout=queue_timeout)
				status_code = "000"
				rtt = "0.0"
				timestamp = "0000-00-00 00:00:00"
				content_length = "0"
				reflected = "N"
				payloads = str(req_data["payloads"])
				timeout = "N"
				raw_request = req_data["raw_request"]
				raw_response = ""
				success = False
				# Make and time the request
				try:
					t1 = time.time()
					r = self.session.request(
						req_data["method"],
						req_data["url"],
						headers=req_data["headers"],
						data=req_data["data"],
						timeout=self.timeout,
						allow_redirects=False,
						verify=False
					)
					t2 = time.time()
					success = True
				except requests.ConnectionError:
					error = "Connection Error"
				except requests.Timeout:
					error = "Timeout Error"
					timeout = "Y"
				except requests.HTTPError:
					error = "HTTP Error"
				except requests.URLRequired:
					error = "URL Error"
				except:
					error = "Generic Request Error"
				# Post processing after the request if successful
				if success:
					timestamp = datetime.datetime.fromtimestamp(t1).strftime("%Y-%m-%d %H:%M:%S")
					rtt = str(round(t2 - t1, 3))
					status_code = str(r.status_code)
					content_length = str(len(r.content))
					for payload in req_data["payloads"]:
						if bytes(payload,"utf-8") in r.content:
							reflected = "Y"
							break
					raw_response = self.cb.rebuild_response_requests(r)
				# Add request results to the database
				results = (
					status_code,
					rtt,
					content_length,
					payloads,
					reflected,
					timeout,
					error,
					timestamp,
					raw_request,
					raw_response
				)
				self._add_to_db(cursor, results, progress_bar, fuzz_table)
				time.sleep(self.delay)
			except queue.Empty:
				break

	def _add_to_db(self, cursor: sqlite3.Cursor, results: tuple, progress_bar, fuzz_table) -> None:
		'''Add results to the database. Update status bar and fuzz table.'''
		self.lock.acquire()
		self.payload_idx += 1
		cursor.execute('''INSERT INTO fuzz 
			(status_code,
			rtt,
			content_length,
			payloads,
			reflected,
			timeout,
			errors,
			timestamp,
			raw_request,
			raw_response) VALUES (?,?,?,?,?,?,?,?,?,?);''', results)
		self._update_progress_bar(progress_bar)
		table_results = [self.payload_idx]
		table_results.extend(results)
		iid = fuzz_table.view.insert("", "end", values=table_results) # Enables better updating, but not clicking/filtering
		fuzz_table.view.update()
		#fuzz_table.insert_row("end", values=table_results) # Enables clicking/filtering, but does not update cleanly with load_table_data()
		#fuzz_table.load_table_data() # not good to call often
		self.lock.release()

	def _clear_fuzz_table(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
		'''Clear the fuzz results table'''
		cursor.execute('''DELETE FROM fuzz;''')
		cursor.execute('''UPDATE SQLITE_SEQUENCE SET seq=0 WHERE name='fuzz';''')
		conn.commit()

	def fuzz(self, template: str, file_paths: list, encoder: str, timeout: int, threads: int, delay: int, conn: sqlite3.Connection, cursor: sqlite3.Cursor, progress_bar, fuzz_table) -> None:
		'''Fuzz the target application and add results to the database'''
		self._clear_fuzz_table(cursor, conn)
		self.is_running = True
		self.encoder = encoder
		self.timeout = timeout
		self.threads = threads
		self.delay = delay
		payloads = self._load_payloads(file_paths)
		threads = []
		# Create thread that loads the queue for requests to pull on the fly
		t = threading.Thread(target=self._iter_format_payloads, args=(template, payloads, self.encoder))
		t.daemon = True
		t.start()
		threads.append(t)
		# Create threads to make requests
		for i in range(0,self.threads):
			t = threading.Thread(target=self._send_request, args=(cursor, progress_bar, fuzz_table))
			t.daemon = True
			t.start()
			threads.append(t)
		# Wait for all threads to finish
		for t in threads:
			t.join()
		progress_bar["value"] = 1.0
		progress_bar.config(bootstyle="danger")
		self.is_running = False
		# Commit database writes made by request threads
		conn.commit()


