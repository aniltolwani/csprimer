# write a basic DNS client capable of 
# using the socket library
# The purpose is to learn another layer protocol

import socket
import struct
import random

DNS_SERVER_IP = "8.8.8.8"
DNS_SERVER_PORT = 53

RECORD_TYPES = {
    'A': 1,
    'NS': 2,
    'CNAME': 5,
    'SOA': 6,
    'MX': 15,
    'TXT': 16,
}

def decode_name(response, offset):
    """Decode a DNS name from the response starting at the given offset."""
    result = []
    while True:
        length = response[offset] # converts from bytes to int automatically
        # empty byte indicates the end
        if length == 0:
            offset += 1
            break
        if length & 0xC0: # Check whether this is a compression pointer
            full_ptr = response[offset: offset+2]
            offset_compress = struct.unpack('!H', full_ptr)[0] & 0x3FFF
            res, _ = decode_name(response, offset_compress)
            result.extend(res)
            offset += 2
            # we have the name so let's break
            break
        else:
            # just keep going one by one and add it to the response (this is in the case where we are just)
            # skip to the next byte (i.e. after the length)
            offset += 1
            result.append(response[offset:offset+length].decode('ascii'))
            offset += length
    return result, offset

def get_query(domain, record_type) -> bytes:
    # 1. create the header
    # randomly generate an id
    id = random.randint(0, 0xFFFF) # 2 bytes gives us 16 bits free. So we have (0, 2^16 - 1)
    # set the flags to 0100, which is the standard query, with RD (recursion desired) set
    flags = 0x0100 
    # set the header, QDCOUNT is 1, ANCOUNT, NSCOUNT, and ARCOUNT are 0
    header = struct.pack('!HHHHHH', id, flags, 1, 0, 0, 0)
    # 2. create the question
    qname = b""
    for label in domain.split('.'):
        qname += struct.pack('!B', len(label)) + label.encode('ascii')
    # add a zero to indicate the end of the name
    qname += struct.pack('!B', 0)
    # add the type of the record
    qtype = RECORD_TYPES[record_type]
    # add the class of the record
    qclass = 1 # IN (Internet)
    question = qname + struct.pack('!HH', qtype, qclass)
    return header + question, id

def decode_response(response, id):
    # unpack the response
    rid, rflags, qdcount, ancount, nscount, arcount = struct.unpack('!HHHHHH', response[:12])
    # TODO: some parsing on rflags.
    assert(rid == id)
    assert qdcount == 1
    # we are querying an authoritative server, so nscount should be 0
    assert nscount == 0
    assert arcount == 0
    assert ancount > 0

    # let's just skip the question, since it should be the same as the query
    # start with just the headers, which are 12 bytes (above)
    offset = 12
    # decode + skip the name
    parts, offset = decode_name(response, offset)
    name = '.'.join(parts)
    print("first name from resp: ", name)
    # skip QTYPE and QCLASS
    offset += 4
    # in practice, this is just ancount, but this is more general
    num_resource_records = ancount + nscount + arcount
    for _ in range(num_resource_records):
        # decode the rest
        parts, offset = decode_name(response, offset)
        name = '.'.join(parts)
        dns_type, dns_class, ttl, rdlength = struct.unpack('!HHIH', response[offset:offset+10])
        offset += 10 # (type (2) + class (2) + ttl (4) + rdlength (2))
        print(f"Name from request: {name}")
        print(f"Type: {dns_type}, Class: {dns_class}, TTL: {ttl}, Length: {rdlength}")
        if dns_type == RECORD_TYPES['NS']:
            ns_parts, _ = decode_name(response, offset)
            ns_name = '.'.join(ns_parts)
            print(f"NS Name: {ns_name}")
        elif dns_type == RECORD_TYPES['A']:
            value = response[offset:offset+rdlength]
            ip_address = '.'.join(str(x) for x in value)
            print(f"IP Address: {ip_address}")
        offset += rdlength

    return name, dns_type, dns_class, ttl, rdlength

def main():
    # create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    query, id = get_query("wikipedia.org", "A")
    udp_socket.sendto(query, (DNS_SERVER_IP, DNS_SERVER_PORT))
    response, _ = udp_socket.recvfrom(1024)
    resp_decoded = decode_response(response, id)
if __name__ == "__main__":
    main()
