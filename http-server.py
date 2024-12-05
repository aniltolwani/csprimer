#In this sequence of exercises, 
# you will implement a web proxy. 
# For now, you will simply write a program which accepts a single incoming TCP connection, 
# forwards a single message to an upstream server (such as python3 -m http.server), 
# listens for a response, then forwards back the response to the client, before closing the connection. 
# importantly, it should also support persistent connections from the client.
# this will require paying attention to header contents too
# TODO:
#   1. Figure out how to determine when to break the chunk reading loop based on HTTP request length
#   2. if keep alive is true, we shouldn't need to reaccept a new connection, it should keep alive the old one when we loop back
#   3. Try to remove the "data.decode" stuff - just do it in bytes directly
# Stretch: Parse for valid HTTP request in general? headers + request type, etc.
import socket
import parser
import time
import threading


PROXY_ADDR = ('127.0.0.1', 8080)
SERVER_ADDR = ('127.0.0.1', 8000)
# create a TCP socket

print("Listening on port 8080")


def handle_client(client):
    while True:
        upstream_socket = socket.create_connection(SERVER_ADDR)
        
        new_req = parser.HTTPRequest()
        data = b""
        while not new_req.parse_request(data):
            chunk = client.recv(4096)
            if not chunk:
                upstream_socket.close()
                return
            # read the bytestream and figure out if this request is done
            print("c->*  ", len(chunk))
            upstream_socket.send(chunk)
            print("c  *->", len(chunk))
            data += chunk

        resp = b''
        while True:
            chunk = upstream_socket.recv(4096)
            if not chunk:
                break
            print("c  *<-", len(chunk))
            client.send(chunk)
            print("c<-*  ", len(chunk))
            resp += chunk

        upstream_socket.close()
        print("keep-alive: ", new_req.keep_alive)
        if not new_req.keep_alive:
            break


if __name__ == "__main__":
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # make it reusable
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind the socket to the local address
    tcp_socket.bind(PROXY_ADDR)

    # listen for incoming connections, need to hanlde multiple potential clients
    tcp_socket.listen(5)

    while True:
        try:
            client, addr = tcp_socket.accept()
            print("New connection from", addr)
            handle_client(client)
            client.close()
        except Exception as e:
            print("Error: ", e)
            continue