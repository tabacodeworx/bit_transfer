import requests
import brotli
import random
import os

def generate_binary_data(size=1_000_000):
    """Generate random binary data of specified size"""
    return bytes([random.randint(0, 1) for _ in range(size)])

def send_compressed_data(data, url='http://localhost:5001/upload'):
    """Compress and send the binary data"""
    # Compress the data using brotli
    compressed_data = brotli.compress(data)
    
    # Send the compressed data
    response = requests.post(
        url,
        data=compressed_data,
        headers={'Content-Type': 'application/octet-stream'}
    )
    
    return response.json()

if __name__ == '__main__':
    # Generate 1 million random binary digits
    binary_data = generate_binary_data()
    
    # Send the data
    try:
        result = send_compressed_data(binary_data)
        print("Server response:", result)
    except Exception as e:
        print(f"Error: {e}")
