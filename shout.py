import socket

# write a short program that lets you send data to it
# using UDP from a telnet/nc call
# and SHOUTs it back (put it in all caps lol)

# we'll use the socket library

# sockets are:
# - IP addresses + ports for local + remote
# - protocol (TCP/UDP)
# - state (listening, connected, etc.)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
server.bind(("localhost", 12345))

# since we are usng UDP, we DON't need to listen wait for client connection
# we can just wait from data using recv or recvfrom

while True:
    data, addr = server.recvfrom(1024)
    upper_data = data.decode().upper()
    server.sendto(upper_data.encode(), addr)