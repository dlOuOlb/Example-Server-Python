import http
import http.server
import mimetypes
import os
import typing


class File(object):
	@staticmethod
	def load(*, directory: str) -> type[http.server.BaseHTTPRequestHandler]:
		class Handler(http.server.BaseHTTPRequestHandler):
			server_version = r'Server'
			sys_version = r'Python'

			__client = File._load(cache={}, root=directory, stem=r'')

			def do_GET(self: typing.Self) -> None:
				if os.path.sep == (path:=File._normalize(path=self.path)):
					self.send_response(code=http.HTTPStatus.MOVED_PERMANENTLY)
					self.send_header(keyword=r'Location', value=os.path.join(path, r'index.html'))
					self.end_headers()
					return
				elif None is (file:=self.__client.get(path)):
					return self.send_error(code=http.HTTPStatus.NOT_FOUND)
				else:
					self.send_response(code=http.HTTPStatus.OK)
					for keyword, value in file.parameters.items():
						self.send_header(keyword=keyword, value=value)
						continue
					self.end_headers()
					count = self.wfile.write(file.contents)
					return

		return Handler

	@staticmethod
	def _load(*, cache: dict[str, 'File'], root: str, stem: str) -> dict[str, 'File']:
		with os.scandir(path=os.path.join(root, stem)) as entries:
			for entry in entries:
				if entry.is_dir(follow_symlinks=False):
					cache = File._load(cache=cache, root=root, stem=os.path.join(stem, entry.name))
					continue
				elif entry.is_file(follow_symlinks=False):
					cache[File._normalize(path=os.path.join(os.path.sep, stem, entry.name))] = File(path=entry.path)
					continue
				else:
					raise NotImplementedError

		return cache

	def __init__(self: typing.Self, /, *, path: str) -> None:
		mimetype, encoding = mimetypes.guess_type(url=path)  # 'text/html', None

		if mimetype is None:
			raise NotImplementedError(f'Failed to find out the mime type of the file: "{path}".')
		elif encoding is not None:
			raise NotImplementedError
		else:
			type, _, subtype = mimetype.partition(r'/')  # 'text', '/', 'html'

			self.parameters = {r'X-Content-Type-Options': r'nosniff'}
			self.parameters[r'Cache-Control'] = r'no-cache' if r'html' == subtype else r'immutable, private, max-age=31536000'

			if r'text' == type:
				encoding = r'utf-8-sig'
				with open(file=path, encoding=encoding) as file:
					self.contents = file.read().encode(encoding=encoding)
				self.parameters[r'Content-Type'] = f'{mimetype}; charset=utf-8'
			else:
				with open(file=path, mode=r'rb') as file:
					self.contents = file.read()
				self.parameters[r'Content-Type'] = mimetype

			return

	@staticmethod
	def _normalize(*, path: str) -> str:
		path = os.path.normpath(path=path)
		path = os.path.normcase(path)
		return path
