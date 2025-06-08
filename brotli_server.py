from flask import Flask, request, jsonify
import brotli

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Get the brotli compressed data
        compressed_data = request.data
        
        # Decompress the data
        decompressed_data = brotli.decompress(compressed_data)
        
        # The decompressed data should already be a string of '0' and '1' characters
        binary_data = decompressed_data.decode('ascii')
        
        # Verify length
        if len(binary_data) != 1_000_000:
            print(f'Expected 1,000,000 bits, got {len(binary_data)}')
            return jsonify({'error': f'Expected 1,000,000 bits, got {len(binary_data)}'}), 400
            
        print(f'{__file__} Successfully received and decompressed data')
        return jsonify({
            'message': 'Successfully received and decompressed data',
            'bits_count': len(binary_data),
            'first_100_bits': binary_data[:100]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5001)
