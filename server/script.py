import http.server
import socket
import threading

import file


# https://stackoverflow.com/questions/166506
# Finding local IP addresses using Python's stdlib
with socket.socket(type=socket.SOCK_DGRAM) as _socket:
	_socket.connect((r'255.255.255.255', 0))
	address, _ = _socket.getsockname()  # address, port

with http.server.ThreadingHTTPServer(server_address=(r'', 0), RequestHandlerClass=file.File.load(directory=r'client')) as server:
	print(f'http://{address}:{server.server_port}/')
	print(r'...')

	thread = threading.Thread(target=server.serve_forever)
	thread.start()

	print(input())

	server.shutdown()
	thread.join()
