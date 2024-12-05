import io

class HTTPRequest:
    def __init__(self):
        self.headers = {}
        self.req_type = ""
        self.file = ""
        self.http_v = ""
        self.body = b""
        self.keep_alive = None
    
    def parse_request(self, req) -> bool:
        """
        HTTP Parser.
        
        Will parse:
            1. The request type, file, and version
            2. the headers into self.headers
            3. Read the content-length, and read bytes from body
        Return true iff the request is valid.
        Return false iff the request is invalid.
        """
        bs = io.BytesIO(req)
        first_line = bs.readline().rstrip()
        if not first_line:
            return False
        self.req_type, self.file, self.http_v = first_line.decode().split(" ")

        print("req_type, file, http_v: ", self.req_type, self.file, self.http_v)

        while True:
            new_line = bs.readline()
            
            if not new_line or new_line == b"":
                # stream might still be going?
                # in any case, we'll return false and let the caller handle it
                return False
            # end of headers check
            if new_line == b"\r\n" or new_line == b"\n":
                break
            # split while being robust to :
            splits = new_line.rstrip().split(b":")
            k,v = splits[0], b''.join(splits[1:])
            self.headers[k.strip().decode().lower()] = v.strip().decode()
        
        if "content-length" in self.headers:
            # read in the bytes
            content_length = int(self.headers['content-length']) 
            self.body = bs.read(content_length)
            if not self.body or len(self.body) != content_length:
                return False
        
        # determine keep-alive status
        if "connection" in self.headers:
            self.keep_alive = self.headers["connection"] == "keep-alive"
        
        if self.keep_alive is None:
            self.keep_alive = self.http_v == "HTTP/1.1"

        # we've gotten this far, it's valid
        return True 

if __name__ == "__main__":
    new_req = HTTPRequest()
    new_req.parse_request(b"POST / HTTP/1.1\r\nContent-Length: 10\r\n\r\nheyabudddy\r\n\r\n")
    print("headers: ", new_req.headers)
    print("req_type: ", new_req.req_type)
    print("req_file: ", new_req.file)
    print("http_version: ", new_req.http_v)
    print("body: ", new_req.body)
    print("keep-alive: ", new_req.keep_alive)
    # try one with no headers
    get_req = HTTPRequest()
    get_req.parse_request(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
