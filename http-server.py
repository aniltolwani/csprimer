#In this sequence of exercises, 
# you will implement a web proxy. 
# For now, you will simply write a program which accepts a single incoming TCP connection, 
# forwards a single message to an upstream server (such as python3 -m http.server), 
# listens for a response, then forwards back the response to the client, before closing the connection. 
# You will know your proxy is working when it can sit between a browser, say, and an upstream server, 
# and log the request and response, while having the browser still display what is expected. 
# Please watch the first section of the video if this is unclear.
import socket


PROXY_ADDR = ('127.0.0.1', 8080)
SERVER_ADDR = ('127.0.0.1', 8000)
# create a TCP socket
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind the socket to the local address
tcp_socket.bind(PROXY_ADDR)

# listen for incoming connections
tcp_socket.listen(1)

print("Listening on port 8080")


while True:
    try:
        client, addr = tcp_socket.accept()
        print("New connection from", addr)
        
        # Set a reasonable timeout (e.g., 1 second)
        client.settimeout(1.0)
        
        data = b''
        while True:
            try:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
            except socket.timeout:
                # If we timeout, assume we've received all the data
                break
        print("c->*  ", len(data))

        upstream_socket = socket.create_connection(SERVER_ADDR)
        upstream_socket.settimeout(1.0)  # Also set timeout for upstream socket
        upstream_socket.sendall(data)
        print("c  *->", len(data))
        resp = b''
        while True:
            chunk = upstream_socket.recv(4096)
            if not chunk:
                break
            resp += chunk
        print("  *<-", len(resp))
        client.sendall(resp)
        print("<-*  ", len(resp))
    except Exception as e:
        print(e)
    finally:
        upstream_socket.close()
        client.close()