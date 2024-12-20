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
import select
import hashlib
from datetime import datetime

PROXY_ADDR = ('127.0.0.1', 8080)
SERVER_ADDR = ('127.0.0.1', 8000)
# create a TCP socket

# cache will be key, value pairs of hashed (first_line) -> (res, ttl)

DEFAULT_TTL = 3000
cache = {}

print("Listening on port 8080")

if __name__ == "__main__":
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # make it reusable
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.setblocking(False)

    # bind the socket to the local address
    tcp_socket.bind(PROXY_ADDR)

    # listen for incoming connections, need to hanlde multiple potential clients
    tcp_socket.listen(5)
    input_sockets = [tcp_socket]
    output_sockets = []
    requests = {}

    while True:
        r_ready, w_ready, exceptional_ready = select.select(input_sockets, output_sockets, [])
        for current_socket in r_ready:
            if current_socket == tcp_socket:
                # tcp socket is ready to accept a new connection
                client, addr = current_socket.accept()
                print("New connection from", addr)
                client.setblocking(False)
                input_sockets.append(client)
                requests[client] = (b"", parser.HTTPRequest(client_addr=addr))
            else:
                # we are getting a read request to a client socket
                # we will assume that the request is < 4096 bytes, but may come in multiple parts
                partial_data, req = requests[current_socket]
                data = current_socket.recv(4096)
                print("c->*  ", len(data))
                if not data:
                    # client closed the connection
                    input_sockets.remove(current_socket)
                    requests.pop(current_socket)
                    current_socket.close()

                partial_data += data
                # check if the request is complete
                if req.parse_request(partial_data):
                    # check if it's cached, if so we can skip the rest of this path
                    key = hashlib.sha256("".join([req.req_type, req.file, req.http_v]).encode()).hexdigest()
                    curr_time = datetime.now().timestamp()
                    if key in cache and curr_time <= cache[key][1]:
                        print(f"Cached response. Curr time {curr_time}, expiry time: {cache[key][1]}")
                        current_socket.sendall(cache[key][0])
                    # request is complete, send it upstream
                    else:
                        requests[current_socket] = (partial_data, req)
                        output_sockets.append(current_socket)
                else:
                    # we need to wait for more data, which we can do on the next loop
                    requests[current_socket] = (partial_data, req)

        for current_socket in w_ready:
            # 1. forward to upstream server
            upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            upstream_socket.connect(SERVER_ADDR)
            req = requests[current_socket][1]
            new_req = req.to_bytes()
            print("c  *->", len(data))
            upstream_socket.sendall(new_req)
            # 2. get response back
            resp = parser.HTTPResponse(upstream_addr=SERVER_ADDR, compress=req.accept_compress)
            data = b""
            while True:
                chunk = upstream_socket.recv(4096)
                if not chunk:
                    break
                print("c  *<-", len(chunk))
                data += chunk
                if resp.parse_response(data):
                    break
            # 3. forward response back to client
            resp_encoded = resp.to_bytes()
            current_socket.sendall(resp_encoded)
            # choose whether or not to cache it
            if resp.status_code == "200" and req.req_type == "GET":
                # cache it if the status was good
                key = hashlib.sha256("".join([req.req_type, req.file, req.http_v]).encode()).hexdigest()
                curr_time = datetime.now().timestamp()
                ttl = DEFAULT_TTL if not resp.get_ttl() else resp.get_ttl()
                print(f"Caching response with TTL: {ttl/60} minutes.")
                cache[key] = (resp_encoded, curr_time + ttl)
            # 4. close connection if not keep alive
            if not req.keep_alive or not resp.keep_alive:
                input_sockets.remove(current_socket)
                current_socket.close()
                del requests[current_socket]
            else:
                # this request is processed, but we are keep alive
                # replace the request with a blank one, but keep the client address
                requests[current_socket] = (b"", parser.HTTPRequest(client_addr=requests[current_socket][1].client_addr))
            # close the upstream socket (wasteful but much easier to manage)
            upstream_socket.close()
            # remove from output and requests, since we have fully proceessed this
            output_sockets.remove(current_socket)