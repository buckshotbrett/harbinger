#! /usr/bin/env python3

import base64
import json
import harparse
import jsbeautifier
from bs4 import BeautifulSoup

class ContentBeautifier:

	def __init__(self) -> None:
		'''Initialize content beautifier'''
		self.hp = harparse.Harparse()

	def beautify(self, mime: str, content: str, binary: bool) -> str:
		'''Try to beautify content before returning'''
		if binary:
			bin_body = "<BINARY_DATA>" + base64.b64encode(content).decode("utf-8") + "</BINARY_DATA>"
			return bin_body
		else:
			try:
				if mime == "JAVASCRIPT":
					pretty_js = jsbeautifier.beautify(content)
					return pretty_js.replace("\r","")
				elif mime == "XML":
					soup = BeautifulSoup(content, 'xml')
					pretty_xml = soup.prettify()
					return pretty_xml.replace("\r","")
				elif mime == "JSON":
					pretty_json = json.loads(content)
					pretty_json = json.dumps(pretty_json, indent=4)
					return pretty_json.replace("\r","")
				else:
					return content
			except Exception as e:
				print("Beautification Error:", e)
		return content

	def rebuild_request(self, method: str, url: str, headers: str, body: str) -> str:
		'''Rebuild the raw request'''
		request = f"{method} {url} HTTP/1.1\n"
		headers = json.loads(headers)
		for i in headers:
			request += f"{i['name']}: {i['value']}\n"
		request += "\n"
		if body:
			# Attempt beautification
			content_type = self.hp.get_content_type(headers)
			mime = self.hp.evaluate_mimetype(body, content_type)
			body = self.beautify(mime, body, False)
			request += body
		return request

	def rebuild_response(self, status_code: str, msg: str, headers: str, body: str) -> str:
		'''Rebuild the raw response'''
		response = f"HTTP/1.1 {status_code} {msg}\n"
		headers = json.loads(headers)
		for i in headers:
			response += f"{i['name']}: {i['value']}\n"
		response += "\n"
		if body:
			# Attempt beautification
			content_type = self.hp.get_content_type(headers)
			mime = self.hp.evaluate_mimetype(body, content_type)
			body = self.beautify(mime, body, False)
			response += body
		return response

	def rebuild_response_requests(self, response) -> str:
		'''Return a string formatted to look like a raw response using response object from requests'''
		# Build response headers
		text = f"HTTP/1.1 {response.status_code} {response.reason}\n"
		for name in response.headers:
			text += name + ": " + response.headers[name] + "\n"
		text += "\n"
		# Get content type
		content_type = ""
		for header_name in response.headers:
			if header_name.lower() == "content-type":
				content_type = response.headers[header_name]
		# Get body and beaufity
		body = ""
		if response.raw:
			try:
				body = response.content.decode("utf-8")
				binary = False
			except:
				body = response.content
				binary = True
			if content_type:
				mime = self.hp.evaluate_mimetype(body, content_type)
				body = self.beautify(mime, body, binary)
		text += body
		return text
