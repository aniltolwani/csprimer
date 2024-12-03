# write a basic DNS client capable of 
# querying for A records and printing the response
# using the socket library
# The purpose is to learn another layer protocol

import socket
import struct
import random

def name_offset(answer):
    add = 0
    while True:
        x = answer[add]
        if x == 0xc0:
            return add + 2
        if x == 0x00:
            add += 1
            break
        add += 1 + x
    return add

def decode_name(response, offset):
    """Decode a DNS name from the response starting at the given offset."""
    result = []
    while True:
        length = response[offset]
        if length == 0:
            break
        if length & 0xC0:  # Compression pointer
            pointer = struct.unpack('!H', response[offset:offset+2])[0] & 0x3FFF
            result.extend(decode_name(response, pointer)[0])
            break
        else:
            offset += 1
            result.append(response[offset:offset+length].decode('ascii'))
            offset += length
    return result, offset

# create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send a query to the DNS server
DNS_SERVER_IP = "8.8.8.8"
DNS_SERVER_PORT = 53

id = random.randint(0, 65535) # 2 bytes gives us 16 bits free. So we have (0, 2^16 - 1)
flags = 0x0100 # 0100 is the standard query, with RD (recursion desired) set
header = struct.pack('!HHHHHH', id, flags, 1, 0, 0, 0)
lookup = "wikipedia.org"
qname = b""
for label in lookup.split('.'):
    qname += struct.pack('!B', len(label)) + label.encode('ascii')
# end byte
qname += struct.pack('!B', 0)

qtype = 1 # A record
qclass = 1 # IN (Internet)

question = struct.pack('!HH', qtype, qclass)

udp_socket.sendto(header + qname + question, (DNS_SERVER_IP, DNS_SERVER_PORT))
response, _ = udp_socket.recvfrom(1024)

rid, rflags, qdcount, ancount, nscount, arcount = struct.unpack('!HHHHHH', response[:12])
assert(rid == id)
assert(qdcount == 1)
assert(ancount == 1)
assert(nscount == 0)
assert(arcount == 0)
# skip the question
offset = 12 + len(qname) + 4
answer = response[offset:]
# let's parse the answer
add = name_offset(answer)
name, _ = decode_name(response, offset)  # Use the full response and our current offset
dns_type, dns_class, ttl, rdlength = struct.unpack('!HHIH', answer[add:add+10])
print(f"Name: {'.'.join(name)}")
print(f"Type: {dns_type}, Class: {dns_class}, TTL: {ttl}, Length: {rdlength}")
value = answer[add+10:add+10+rdlength]
print(f"IP Address: {'.'.join(str(x) for x in value)}")
