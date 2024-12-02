# receive HTTP requests from somewhere
# parse the headers
# reformat them as json and reserve them back

# we'll use the socket library
# and we'll use the json library or jsonify

import socket
import json

# setup TCP server

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# addr is really a tuple of (IP, port)
tcp_socket.bind(("localhost", 12345))

# we gotta listen, because it's TCP
tcp_socket.listen()

while True:
    # this will be blocking until a request comes
    client, addr = tcp_socket.accept()
    data = client.recv(1024).decode()
    headers,body = data.split('\r\n\r\n')
    headers_dict = {}
    for header in headers.split('\r\n')[1:]:
        print(header)
        key, value = header.split(': ')
        headers_dict[key] = value
    # jsonify it
    json_headers = json.dumps(headers_dict)
    client.send('HTTP/1.1 200 OK\r\n\r\n'.encode())
    # this will be our body
    client.send(json_headers.encode())
    client.close()

# how do we test this program easily
# curl -v http://localhost:12345 