#! /usr/bin/env python3

import re
import os
import json
import sqlite3
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

class Harparse:

	def __init__(self) -> None:
		'''Initialize HAR parser'''
		pass

	def _load_har(self, fpath: str) -> dict:
		'''Return a loaded HAR file'''
		if os.path.isfile(fpath):
			f = open(fpath)
			har = json.load(f)
			f.close()
			return har
		else:
			return {}

	def _create_db(self, dbpath:str) -> None:
		'''Create the database'''
		conn = sqlite3.connect(dbpath)
		cursor = conn.cursor()
		cursor.execute('''CREATE TABLE transactions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			timestamp TEXT,
			ip_address TEXT,
			port TEXT,
			request_method TEXT,
			request_url TEXT,
			request_params TEXT,
			request_headers TEXT,
			request_has_input TEXT,
			request_body TEXT,
			request_body_type TEXT,
			request_file_extension TEXT,
			response_status_code TEXT,
			response_status_message TEXT,
			response_headers TEXT,
			response_body TEXT
		);''')
		cursor.execute('''CREATE TABLE fuzz (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			status_code TEXT,
			rtt TEXT,
			content_length TEXT,
			payloads TEXT,
			reflected TEXT,
			timeout TEXT,
			errors TEXT,
			timestamp TEXT,
			raw_request TEXT,
			raw_response TEXT
		);''')
		conn.commit()
		conn.close()

	def _has_inputs(self, request: dict) -> int:
		'''Return 1 if the request has a query string or post data'''
		if "queryString" in request:
			if request["queryString"]:
				return 1
		if "postData" in request:
			return 1
		else:
			return 0

	def _get_input_params(self, method: str, mime: str, request: dict) -> int:
		'''Return 1 if the request has a query string or post data'''
		params = "()"
		if method == "GET":
			if "queryString" in request:
				if request["queryString"]:
					params = []
					for i in request["queryString"]:
						params.append(i["name"])
					return str(tuple(params))
		elif method == "POST":
			if "postData" in request:
				if "text" in request["postData"]:
					if request["postData"]["text"]:
						if "encoding" in request["postData"]:
							return "(MIME/BINARY)"
						if mime == "URL":
							params=[]
							for match in re.finditer(r"(\w+)=", request["postData"]["text"]):
								params.append(match.group(1))
							return str(tuple(params))
						elif mime == "MULTIPART":
							return "(MIME/MULTIPART)"
						elif mime == "JSON":
							return "(MIME/JSON)"
						elif mime == "XML":
							return "(MIME/XML)"
		return params

	def evaluate_mimetype(self, data: str, content_type: str) -> str:
		'''Guess the structured request type and return it'''
		if data:
			if "javascript" in content_type:
				return "JAVASCRIPT"
			elif "form-urlencoded" in content_type:
				return "URL"
			elif "multipart/form-data" in content_type:
				return "MULTIPART"
			else:
				try:
					json.loads(data)
					return "JSON"
				except:
					try:
						ET.ElementTree(ET.fromstring(data))
						return "XML"
					except:
						return ""
		else:
			return ""

	def get_content_type(self, headers: list) -> str:
		'''Return the content-type of a request'''
		for pair in headers:
			if pair["name"].lower() == "content-type":
				return pair["value"].lower()
		return ""

	def _file_ext(self, url: str) -> str:
		'''Return the file extension'''
		urlparts = urlparse(url)
		mat = re.search(r"\x2E([a-zA-Z0-9]+$)", urlparts.path)
		if mat:
			return mat.group(1)
		else:
			return ""

	def parse(self, harfile: str, dbpath: str) -> None:
		'''Parse HAR file and insert entries into database'''
		if not os.path.isfile(dbpath):
			self._create_db(dbpath)
		har = self._load_har(harfile)
		conn = sqlite3.connect(dbpath)
		cursor = conn.cursor()
		if "log" in har:
			log = har["log"]
			if "entries" in log:
				for entry in log["entries"]:
					# Pull out basic metadata for the transaction
					timestamp = entry["startedDateTime"]
					ip_address = ""
					if "serverIPAddress" in entry:
						ip_address = entry["serverIPAddress"]
					port = ""
					if "connection" in entry:
						port = entry["connection"]
					# Pull out request info
					if "request" in entry:
						request_method = entry["request"]["method"]
						request_url = entry["request"]["url"]
						request_headers = json.dumps(entry["request"]["headers"])
						content_type = self.get_content_type(json.loads(request_headers))
						if self._has_inputs(entry["request"]):
							request_has_input = "Y"
						else:
							request_has_input = "N"
						request_body = ""
						if "postData" in entry["request"]:
							if "encoding" in entry["request"]["postData"]: # binary data (images, etc)
								request_body = "<BINARY_DATA>" + entry["request"]["postData"]["text"] + "</BINARY_DATA>"
							else:
								request_body = entry["request"]["postData"]["text"]
						request_body_type = ""
						if request_body:
							request_body_type = self.evaluate_mimetype(request_body, content_type)
						request_file_extension = self._file_ext(request_url)
						request_params = self._get_input_params(request_method, request_body_type, entry["request"])
					else:
						request_method = ""
						request_url = ""
						request_headers = ""
						request_has_input = ""
						request_body = ""
						request_body_type = ""
						request_file_extension = ""
						request_params = ""
					# Pull out response info
					if "response" in entry:
						response_status_code = str(entry["response"]["status"])
						response_status_message = entry["response"]["statusText"]
						response_headers = json.dumps(entry["response"]["headers"])
						if "text" in entry["response"]["content"]:
							if "encoding" in entry["response"]["content"]:
								response_body = "<BINARY_DATA>" + entry["response"]["content"]["text"] + "</BINARY_DATA>"
							else:
								response_body = entry["response"]["content"]["text"]
						elif "comment" in entry["response"]["content"]:
							response_body = "//" + entry["response"]["content"]["comment"]
						else:
							response_body = "//NO RESPONSE OR COMMENT CAPTURED IN HAR FILE"
					else:
						response_status_code = ""
						response_status_message = ""
						response_headers = ""
						response_body = ""
					# Insert records into database
					cursor.execute('''INSERT INTO transactions (
						timestamp,
						ip_address,
						port,
						request_method,
						request_url,
						request_params,
						request_headers,
						request_has_input,
						request_body,
						request_body_type,
						request_file_extension,
						response_status_code,
						response_status_message,
						response_headers,
						response_body
					) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);''', (
						timestamp,
						ip_address,
						port,
						request_method,
						request_url,
						request_params,
						request_headers,
						request_has_input,
						request_body,
						request_body_type,
						request_file_extension,
						response_status_code,
						response_status_message,
						response_headers,
						response_body)
					)
		conn.commit()
		conn.close()

