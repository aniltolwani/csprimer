# Basic HTTP Proxy Server

A lightweight HTTP proxy server implementation in Python that demonstrates core networking concepts and provides basic caching functionality.

## Features

- HTTP request/response parsing and forwarding
- Support for persistent connections (keep-alive)
- In-memory caching with TTL
- Gzip compression support
- Concurrent connection handling using `select`
- Custom header modifications

## Installation

1. Ensure you have Python 3.10+ installed
2. Clone this repository
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Start the proxy server:
```bash
python http-server.py
```

The server will listen on `localhost:8080` by default and forward requests to `localhost:8000`.

You can test it using curl:
```bash
curl -v http://localhost:8080
```

## Project Structure

- `http-server.py`: Main proxy server implementation with connection handling and caching
- `parser.py`: HTTP request/response parsing classes
- `concurrency.py`: Example of concurrent connection handling using select

## Key Components

### HTTP Parser
The `HTTPRequest` and `HTTPResponse` classes handle parsing of HTTP messages, including:
- Header parsing
- Content-Length handling
- Keep-alive detection
- Compression support

### Caching
The proxy implements basic caching with:
- TTL-based expiration
- SHA256 hashing of request details as cache keys
- Configurable cache control headers

### Concurrent Connections
Uses Python's `select` module to handle multiple concurrent connections without threading, supporting:
- Non-blocking I/O
- Multiple client connections
- Keep-alive connections

## Requirements

See `pyproject.toml` for full dependencies:

```7:12:pyproject.toml
dependencies = [
    "ipython>=8.30.0",
    "numpy>=2.2.0",
    "pandas>=2.2.3",
    "psutil>=6.1.0",
]
```


## Contributing

Feel free to submit issues and pull requests.

## License

MIT License
