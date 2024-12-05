# implement a basic proxy
# that gets HTTP requests
# and sends back a simple 200 OK response
# without a body
# importantly, use select to handle multiple connections simultaneously
import select
import socket


SOCKET_ADDR = ('127.0.0.1', 8080)
RESP = b"HTTP/1.1 200 OK\r\n\r\n"

def handle_client(client_socket):
    while True:
        # impt: is blocking
        data = client_socket.recv(4096)
        if not data:
            return
        print("c->*  ", len(data))
        # first, check for whether the client is write-ready
        client_socket.sendall(RESP)
        print("c<-*  ", len(RESP))
def main():
    # open a TCP socket and accept 5 concurrent connections
    # use select to wait for any of the connections to have data available
    # when data is available, parse the request
    # send a response back to the client
    # close the connection
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # make it reusable
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.setblocking(False)
    tcp_socket.bind(SOCKET_ADDR)
    # this queues up to 5 connections, but we need to explicitly handle them
    # in a select loop to make sure we can handle multiple connections simultaneously
    tcp_socket.listen(5)
    all_sockets = [tcp_socket]
    write_sockets = []
    while True:
        # wait for any of the connections to have data available
        r_ready, w_ready, exceptional_ready = select.select(all_sockets, write_sockets, [])
        for current_socket in r_ready:
            if current_socket == tcp_socket:
                # tcp socket is ready to accept a new connection
                client, addr = current_socket.accept()
                client.setblocking(False)
                print("new client from:", addr)
                all_sockets.append(client)
            else:
                # client socket is ready to be read from
                data = current_socket.recv(4096)
                if not data:
                    current_socket.close()
                    all_sockets.remove(current_socket)
                else:
                    print("c->*  ", len(data))
                    write_sockets.append(current_socket)
        for current_socket in w_ready:
            print("c<-*  ", len(RESP))
            current_socket.sendall(RESP)
            to_send.remove(current_socket)
            write_sockets.remove(current_socket)
if __name__ == "__main__":
    main()
