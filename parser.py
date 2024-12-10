import io
import gzip

TO_ADD_HEADERS = ["X-Forwarded-For", "X-Via-Proxy"]
RESP_HEADERS = []
MIN_COMPRESSION_LENGTH = 100
class HTTPRequest:
    def __init__(self, client_addr):
        self.headers = {}
        self.req_type = ""
        self.file = ""
        self.http_v = ""
        self.body = b""
        self.keep_alive = None
        self.client_addr = str(client_addr).encode()
        self.via_proxy = True
        self.accept_compress = None
    
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

        self.accept_compress = False
        if "accept-encoding" in self.headers:
            if "gzip" in self.headers['accept-encoding']:
                self.accept_compress = True

        # we've gotten this far, it's good to go 

        print("Accept-encoding", self.headers.get("accept-encoding", ""))
        print("Accept flag", self.accept_compress)
        return True 


    def add_header_modification(self, key, value):
        if key in self.headers:
            self.headers[key] = value
        else:
            self.headers[key] = value
            

    def to_bytes(self):
        """
        Request headers + to_add_headers + body
        """
        first_line = f"{self.req_type} {self.file} {self.http_v}\r\n".encode()
        self.add_header_modification(TO_ADD_HEADERS[0], self.client_addr)
        self.add_header_modification(TO_ADD_HEADERS[1], self.via_proxy)
        req_headers = b""
        for key, value in self.headers.items():
            req_headers += f"{key}: {value}\r\n".encode()
        return first_line + req_headers + b"\r\n\r\n" + self.body

class HTTPResponse:
    def __init__(self, upstream_addr, compress):
        self.headers = {}
        self.body = b""
        self.http_v = b""
        self.status_code = b""
        self.status_message = b""
        self.content_length = None
        self.keep_alive = None
        self.upstream_addr = upstream_addr
        self.compress = compress
        self.min_length = MIN_COMPRESSION_LENGTH
    
    def parse_response(self, res):
        bs = io.BytesIO(res)
        first_line = bs.readline().rstrip()
        if not first_line:
            return False
        self.http_v, self.status_code, self.status_message = first_line.decode().split(" ", maxsplit = 2)

        # time for headers. read one line at a time and add to self.headers as string[k,v]
        while True:
            new_line = bs.readline()
            if not new_line or new_line == b"":
                # not valid at the moment. need a proper newline
                return False
            if new_line == b"\r\n" or new_line == b"\n":
                # this is valid, move to body
                break
            # add it to headers
            splits = new_line.split(b": ")
            k, v= splits[0], b"".join(splits[1:])
            self.headers[k.rstrip().decode().lower()] = v.rstrip().decode()

        if "content-length" not in self.headers:
            # we only are supporting this method atm
            return False
        body_len = int(self.headers['content-length'])
        self.body = bs.read(body_len)
        if body_len != len(self.body):
            # we didn't get enough bytes for some reason
            return False
        if "connection" in self.headers:
            self.keep_alive = self.headers['connection'] == 'keep-alive'
        if self.keep_alive is None:
            self.keep_alive = self.http_v == b"HTTP/1.1"

        # if client accepts compression + output is not already compressed
        if self.compress and 'content-encoding' not in self.headers:
            self.compress = True
        else:
            self.compress = False

        return True
    
    def add_modified_headers(self):
        self.headers["X-Via-Proxy"] = "true"
        self.headers["X-Proxy-Received-From"] = self.upstream_addr

    def to_bytes(self):
        first_line = f"{self.http_v} {self.status_code} {self.status_message}\r\n".encode()
        self.add_modified_headers()
        if self.compress:
            print("trying to compress")
            print("old length:", len(self.body))
            self.headers['content-encoding'] = 'gzip'
            self.body = gzip.compress(self.body)
            self.headers['content-length'] = len(self.body)
            print("new length", len(self.body))
        resp_headers = b""
        for key, value in self.headers.items():
            resp_headers += f"{key}: {value}\r\n".encode()
        return first_line + resp_headers + b"\r\n" + self.body
        
if __name__ == "__main__":
    new_req = HTTPRequest(client_addr=("127.0.0.1", 12345))
    new_req.parse_request(b"POST / HTTP/1.1\r\nContent-Length: 10\r\n\r\nheyabudddy\r\n\r\n")
    print("headers: ", new_req.headers)
    print("req_type: ", new_req.req_type)
    print("req_file: ", new_req.file)
    print("http_version: ", new_req.http_v)
    print("body: ", new_req.body)
    print("keep-alive: ", new_req.keep_alive)
    # try one with no headers
    get_req = HTTPRequest(client_addr=("127.0.0.1", 12345))
    get_req.parse_request(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
