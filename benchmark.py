import gzip
import brotli
import random
import time
import requests
import psutil
import os
import statistics
from prettytable import PrettyTable

def generate_binary_data(num_bits=1_000_000):
    """Generate random binary data with specified number of bits"""
    # Calculate how many bytes we need (8 bits per byte)
    num_bytes = (num_bits + 7) // 8
    # Generate random bytes
    random_bytes = bytes([random.randint(0, 255) for _ in range(num_bytes)])
    # Convert to binary string
    binary_str = ''.join(format(b, '08b') for b in random_bytes)
    # Truncate to exact number of bits needed
    binary_str = binary_str[:num_bits]
    # Convert back to bytes
    return binary_str.encode('ascii')

class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.get_memory()
        self.peak_memory = self.initial_memory
    
    def get_memory(self):
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def measure(self):
        """Update peak memory usage"""
        current = self.get_memory()
        self.peak_memory = max(self.peak_memory, current)
        return current
    
    def peak_usage(self):
        """Get peak memory usage relative to initial memory"""
        return self.peak_memory - self.initial_memory

def benchmark_compression(data, num_trials=5):
    results = {
        'gzip': {'compression_times': [], 'decompression_times': [], 'compressed_sizes': [], 'memory_usage': []},
        'brotli': {'compression_times': [], 'decompression_times': [], 'compressed_sizes': [], 'memory_usage': []}
    }
    
    for _ in range(num_trials):
        # GZIP
        monitor = MemoryMonitor()
        start_time = time.time()
        gzip_compressed = gzip.compress(data)
        monitor.measure()  # Measure after compression
        compression_time = time.time() - start_time
        
        start_time = time.time()
        gzip.decompress(gzip_compressed)
        monitor.measure()  # Measure after decompression
        decompression_time = time.time() - start_time
        
        results['gzip']['compression_times'].append(compression_time)
        results['gzip']['decompression_times'].append(decompression_time)
        results['gzip']['compressed_sizes'].append(len(gzip_compressed))
        results['gzip']['memory_usage'].append(monitor.peak_usage())
        
        # Brotli
        monitor = MemoryMonitor()
        start_time = time.time()
        brotli_compressed = brotli.compress(data)
        monitor.measure()  # Measure after compression
        compression_time = time.time() - start_time
        
        start_time = time.time()
        brotli.decompress(brotli_compressed)
        monitor.measure()  # Measure after decompression
        decompression_time = time.time() - start_time
        
        results['brotli']['compression_times'].append(compression_time)
        results['brotli']['decompression_times'].append(decompression_time)
        results['brotli']['compressed_sizes'].append(len(brotli_compressed))
        results['brotli']['memory_usage'].append(monitor.peak_usage())
    
    return results

def benchmark_transfer(data, num_trials=5):
    results = {
        'gzip': {'transfer_times': []},
        'brotli': {'transfer_times': []}
    }
    
    for _ in range(num_trials):
        # GZIP
        compressed_data = gzip.compress(data)
        start_time = time.time()
        response = requests.post(
            'http://localhost:5000/upload',
            data=compressed_data,
            headers={'Content-Type': 'application/octet-stream'}
        )
        transfer_time = time.time() - start_time
        results['gzip']['transfer_times'].append(transfer_time)
        
        # Brotli
        compressed_data = brotli.compress(data)
        start_time = time.time()
        response = requests.post(
            'http://localhost:5001/upload',
            data=compressed_data,
            headers={'Content-Type': 'application/octet-stream'}
        )
        transfer_time = time.time() - start_time
        results['brotli']['transfer_times'].append(transfer_time)
    
    return results

def calculate_statistics(results):
    stats = {}
    
    for method in ['gzip', 'brotli']:
        stats[method] = {
            'avg_compression_time': statistics.mean(results[method]['compression_times']),
            'avg_decompression_time': statistics.mean(results[method]['decompression_times']),
            'avg_compressed_size': statistics.mean(results[method]['compressed_sizes']),
            'avg_memory_usage': statistics.mean(results[method]['memory_usage'])
        }
    
    return stats

def print_results(compression_results, transfer_results, original_size):
    table = PrettyTable()
    table.field_names = ["Metric", "GZIP", "Brotli"]
    
    stats = calculate_statistics(compression_results)
    
    # Add compression ratio (original size / compressed size)
    table.add_row([
        "Compression Ratio",
        f"{original_size / stats['gzip']['avg_compressed_size']:.2f}x",
        f"{original_size / stats['brotli']['avg_compressed_size']:.2f}x"
    ])
    
    # Add compressed size
    table.add_row([
        "Compressed Size (bytes)",
        f"{stats['gzip']['avg_compressed_size']:.0f}",
        f"{stats['brotli']['avg_compressed_size']:.0f}"
    ])
    
    # Add compression time
    table.add_row([
        "Compression Time (ms)",
        f"{stats['gzip']['avg_compression_time'] * 1000:.2f}",
        f"{stats['brotli']['avg_compression_time'] * 1000:.2f}"
    ])
    
    # Add decompression time
    table.add_row([
        "Decompression Time (ms)",
        f"{stats['gzip']['avg_decompression_time'] * 1000:.2f}",
        f"{stats['brotli']['avg_decompression_time'] * 1000:.2f}"
    ])
    
    # Add memory usage
    table.add_row([
        "Memory Usage (MB)",
        f"{stats['gzip']['avg_memory_usage']:.2f}",
        f"{stats['brotli']['avg_memory_usage']:.2f}"
    ])
    
    # Add transfer time
    table.add_row([
        "Transfer Time (ms)",
        f"{statistics.mean(transfer_results['gzip']['transfer_times']) * 1000:.2f}",
        f"{statistics.mean(transfer_results['brotli']['transfer_times']) * 1000:.2f}"
    ])
    
    print("\nBenchmark Results:")
    print(table)

if __name__ == '__main__':
    print("Starting benchmark test...")
    print("Generating test data...")
    
    # Generate test data
    test_data = generate_binary_data()
    original_size = len(test_data)
    
    print(f"Original data size: {original_size} bytes")
    print("\nRunning compression benchmarks...")
    compression_results = benchmark_compression(test_data)
    
    print("Running transfer benchmarks...")
    print("Make sure both servers are running first!")
    try:
        transfer_results = benchmark_transfer(test_data)
        print_results(compression_results, transfer_results, original_size)
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to servers. Make sure both servers are running:")
        print("- GZIP server should be running on http://localhost:5000")
        print("- Brotli server should be running on http://localhost:5001")
