"""

Implementing the variable integer from protobuf.
"""

def decode(b: bytes) -> int:
    # drop the msb from each byte
    res, shift = 0, 0 
    for byte in b:
        msb, part = byte & 0b10000000, byte & 0b01111111
        res = res | part << shift
        if msb == 0:
            break
        shift += 7 
    return res

def encode(a: int) -> bytes:
    # convert to bytes / binary repr
    b = format(a, '08b')
    pos = 0
    # go 7 bits at a time, and add it to a finalized repr
    new_str = "" 
    while True:
        if pos + 7 > len(b):
            # this will be our last iter
            msb = 0
        else:
            msb = 1
        start = len(b)-pos - 7
        end = start + 7
        start = max(start,0)
        new_part = b[start:end]
        diff = 7 - len(new_part)
        if diff > 0:
            new_part = "0"*diff + new_part
        new_str = new_str + str(msb) + new_part
        pos += 7
        if pos > len(b):
            break
    return int(new_str, pos // 7).to_bytes(pos // 7, byteorder="big")

def main():
    print("---NEW RUN---")
    for i in range(0xFFFFFFFF):
        if (i != decode(encode(i))):
            print(i, "is wrong")
if __name__ == "__main__":
    main()