<<<<<<< HEAD
# bit_transfer
=======
# Binary Data Transfer Demo

This project demonstrates transferring 1 million binary digits using two different compression methods: gzip and brotli.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Servers

1. Start the gzip server (runs on port 5000):
```bash
python gzip_server.py
```

2. Start the brotli server (runs on port 5001):
```bash
python brotli_server.py
```

## Running the Clients

1. To test gzip compression:
```bash
python gzip_client.py
```

2. To test brotli compression:
```bash
python brotli_client.py
```

Each client will generate 1 million random binary digits, compress them, and send them to their respective servers. The servers will decompress the data and verify the number of bits received.
>>>>>>> 3ea1242 (init commit)
