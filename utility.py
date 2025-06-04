import hashlib
import zlib
import streamlit as st

# --- Constants ---
WBITS_VALUE = -15
HEADER_LENGTH = 53
ZLIB_HEADER = b'\x78\x9c'

# --- Utility Functions ---
def compute_md5(data):
    """Compute the MD5 hash of the given data."""
    md5_hash = hashlib.md5(data).hexdigest()
    return md5_hash

def try_decompress_zlib_block(data, start_offset=0):
    """Try different decompression methods on the data starting at offset."""
    result = {}
    zlib_block = data[start_offset:]
    uncompressed_size = int.from_bytes(zlib_block[:4], byteorder='little')
    compressed_size = int.from_bytes(zlib_block[4:8], byteorder='little')

    # Confirm next 2 bytes are zlib header (or expected for raw deflate)
    # The original WBITS_VALUE = -15 means raw deflate, so there's no zlib header
    # But it's good to keep the check if the game sometimes uses standard zlib
    if zlib_block[8:10] == ZLIB_HEADER:
        st.warning("Warning: Standard zlib header found. Ensure WBITS_VALUE=-15 is correct for raw deflate.")
    
    # Decompress from here
    decompressed = zlib.decompress(zlib_block[10:], wbits=WBITS_VALUE)

    result['uncompressed_size'] = uncompressed_size
    result['compressed_size'] = compressed_size
    result['decompressed_bytes'] = decompressed
    return result

def decode_file(file_content_bytes):
    """Decode a file by decompressing its zlib blocks and return a single byte array."""
    if not file_content_bytes:
        return None, None

    # st.write(f"File size: {len(file_content_bytes)} bytes") # Commented out to avoid cluttering UI

    md5 = compute_md5(file_content_bytes[HEADER_LENGTH:])
    # st.write(f"Original MD5 hash of compressed data from offset {HEADER_LENGTH}: {md5}")

    offset = HEADER_LENGTH
    decompressed_data = bytearray()

    try:
        while offset < len(file_content_bytes):
            result = try_decompress_zlib_block(file_content_bytes, start_offset=offset)
            decompressed_data.extend(result['decompressed_bytes'])
            offset += result['compressed_size'] + 8 # 8 bytes for the 2 int32s
    except zlib.error as e:
        st.error(f"Zlib decompression error: {e}. The file might be corrupted or not a valid save file.")
        return None, None
    except Exception as e:
        st.error(f"Error during file decoding: {e}")
        return None, None
    
    # st.write(f"Total decompressed data size: {len(decompressed_data)} bytes")
    return file_content_bytes, decompressed_data

def encode_file(original_file_content, decompressed_data_edited):
    """Encode a file by compressing the decompressed data into chunks."""
    try:
        st.info("Rebuilding the file with the new compressed data...")

        new_zlib_data = b''
        chunk_size = 1024**2 # 1 MB (1MB chunks for compression)
        offset = 0

        while offset < len(decompressed_data_edited):
            chunk = decompressed_data_edited[offset:offset + chunk_size]
            offset += chunk_size

            new_block_uncompressed_size_bytes = len(chunk).to_bytes(4, 'little')
            
            # Using WBITS_VALUE=-15 for raw deflate stream, as per original code's design
            new_compressed_data = zlib.compress(chunk, level=-1, wbits=WBITS_VALUE) 
            
            adler32 = zlib.adler32(chunk)
            adler32_bytes = adler32.to_bytes(4, 'big')

            new_block_compressed_size = len(new_compressed_data) + 6
            new_block_compressed_size_bytes = new_block_compressed_size.to_bytes(4, 'little')

            # Append the new block to the new data
            new_zlib_data += new_block_uncompressed_size_bytes + new_block_compressed_size_bytes + ZLIB_HEADER + new_compressed_data + adler32_bytes

        # Rebuild header components
        original_filetype = original_file_content[:4]
        zero_bytes = b'\x00\x00\x00\x00'
        three_byte = b'\x03' # Constant byte from original header logic
        new_total_compressed_size_bytes = len(new_zlib_data).to_bytes(4, 'little')
        new_total_uncompressed_size_bytes = len(decompressed_data_edited).to_bytes(4, 'little')
        new_md5 = compute_md5(new_zlib_data)
        st.info(f"New MD5 hash of compressed data: {new_md5}")
        new_md5_bytes = new_md5.encode('utf-8')

        final_data = original_filetype + new_total_compressed_size_bytes + zero_bytes + new_total_uncompressed_size_bytes + zero_bytes + new_md5_bytes + three_byte + new_zlib_data

        # In Streamlit, we offer the file for download directly
        st.download_button(
            label="Download CompleteSave",
            data=final_data,
            file_name="CompleteSave",
            mime="application/octet-stream",
            help="Replace the original file in your save directory. **DID YOU BACK UP YOUR ORIGINAL?**"
        )
        st.success("File rebuilt and ready for download!")
        return True
    except Exception as e:
        st.error(f"Error during encoding: {e}. Please check the console/logs.")
        return False