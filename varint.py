"""

Implementing the variable integer from protobuf.
"""

def decode(b: bytes) -> int:
    # drop the msb from each byte
    res, shift = 0, 0 
    for byte in b:
        # get the msb and part
        msb, part = byte & 128, byte & 0x7F
        # add it to res, shift the current result and add the new one
        res = res | part << shift
        if msb == 0:
            break
        shift += 7 
    return res

def encode(a: int) -> bytes:
    # convert to bytes / binary repr
    out = []
    while a > 0:
        # get last 7 bits
        part = a & 0x7F
        # shift out those 7 bits
        a = a >> 7
        if a:
            # if we aren't done, add a 1 to it
            part = part | 128
        out.append(part)
    return bytes(out)

def test_varint():
    test_cases = [
        # Basic cases
        0,                      # Zero
        127,                    # Max single byte
        128,                    # Min two byte
        
        # Powers of 2 edge cases
        2**7 - 1,              # 127  (Max 1 byte)
        2**7,                  # 128  (Min 2 bytes)
        2**14 - 1,             # 16383 (Max 2 bytes)
        2**14,                 # 16384 (Min 3 bytes)
        
        # 64-bit unsigned max
        2**64 - 1,             # Max unsigned int64 (0xFFFFFFFFFFFFFFFF)
    ]

    for test_value in test_cases:
        encoded = encode(test_value)
        decoded = decode(encoded)
        if test_value != decoded:
            print(f"FAILED: {test_value} -> {[bin(b) for b in encoded]} -> {decoded}")
            return False
        print(f"PASSED: {test_value} -> {[bin(b) for b in encoded]} -> {decoded}")
    return True

def main():
    print("---NEW RUN---")
    print("hi")
    test_varint()
    for n in range(1 << 30):
        assert decode(encode(n)) == n
if __name__ == "__main__":
    main()