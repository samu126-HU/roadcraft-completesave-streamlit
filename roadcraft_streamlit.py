import zlib
import hashlib
import json
import streamlit as st
import os # For checking default file path existence

# --- Constants ---
WBITS_VALUE = -15
HEADER_LENGTH = 53
ZLIB_HEADER = b'\x78\x9c'

# List of all levels to unlock
ALL_LEVELS_LIST = [
    "rb_map_01_storm_preparation",
    "rb_map_07_rail_failure",
    "rb_map_08_contamination",
    "rb_map_02_storm_aftermath",
    "rb_map_03_incommunicado",
    "rb_map_04_salt_mines",
    "rb_map_05_dam_break",
    "rb_map_06_sinkholes",
    "rb_map_09_sand_storm",
    "rb_map_10_geothermal"
]

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

# --- Streamlit App Layout and Logic ---

st.set_page_config(layout="centered", page_title="Roadcraft Save Editor", initial_sidebar_state="expanded")

st.title("Roadcraft Save Editor")
with st.sidebar:
    st.markdown("Upload and edit your CompleteSave file, usually found at: `%AppData%/Local/Saber/RoadCraftGame/storage/steam/user/<YOUR_STEAM_USER_ID>/Main/save`")
    st.markdown("The default steam deck location is: `/home/deck/.local/share/Steam/steamapps/compatdata/2104890/pfx/drive_c/users/steamuser/AppData/Local/Saber/RoadCraftGame/storage/steam/user/<YOUR_STEAM_USER_ID>/Main/save`")
    st.markdown("---")
    st.markdown("The source code for this app is available on [github](https://github.com/cgpavlakos/roadcraft-completesave-streamlit) if you prefer to run locally.")
    st.markdown("---") # Add a horizontal rule for visual separation
    st.markdown("If you find this useful, consider a small donation to my beer fund!")
    st.markdown(
        '<a href="https://coindrop.to/cgpavlakos" target="_blank">'
        '<img src="https://coindrop.to/embed-button.png" '
        'style="border-radius: 10px; height: 57px !important; width: 229px !important;" '
        'alt="Coindrop.to me">'
        '</a>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("Thanks to NakedDevA for his [Roadcraft completesave editor](https://github.com/NakedDevA/roadcraft-completesave) which this is forked from.")

# Initialize session state variables if they don't exist
if 'json_data' not in st.session_state:
    st.session_state.json_data = None
if 'original_file_content_bytes' not in st.session_state:
    st.session_state.original_file_content_bytes = None
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'initial_unlocked_levels_checkbox_state' not in st.session_state:
    st.session_state.initial_unlocked_levels_checkbox_state = False

# --- File Loading Logic ---
# Define a function to load and initialize session state, to avoid repetition
def load_and_init_session_state(file_content):
    original_file_content_bytes, decompressed_data = decode_file(file_content)

    if original_file_content_bytes and decompressed_data:
        try:
            json_data = json.loads(decompressed_data.decode('utf-8'))
            st.session_state.json_data = json_data
            st.session_state.original_file_content_bytes = original_file_content_bytes
            
            # Initialize initial_values for the session
            st.session_state.initial_values = {
                'xp': json_data.get('SslValue', {}).get('xp', 0),
                'money': json_data.get('SslValue', {}).get('money', 0),
                'recovery_coins': json_data.get('SslValue', {}).get('recoveryCoins', {}).get(next(iter(json_data.get('SslValue', {}).get('recoveryCoins', {})), ''), 0),
                'logs_4_idx': 0,
                'steel_beams_5_idx': 0,
                'concrete_6_idx': 0,
                'steel_pipes_7_idx': 0
            }
            # Populate initial_values for resources (using the correct keys)
            if 'fobsResources' in json_data.get('SslValue', {}):
                for map_data in json_data['SslValue']['fobsResources'].values():
                    if 'resources' in map_data and isinstance(map_data['resources'], list):
                        resources = map_data['resources']
                        if len(resources) > 4: st.session_state.initial_values['logs_4_idx'] = resources[4]
                        if len(resources) > 5: st.session_state.initial_values['steel_beams_5_idx'] = resources[5]
                        if len(resources) > 6: st.session_state.initial_values['concrete_6_idx'] = resources[6]
                        if len(resources) > 7: st.session_state.initial_values['steel_pipes_7_idx'] = resources[7]
                        break

            # --- Set initial state of unlock_levels checkbox ---
            current_unlocked_levels = json_data.get('SslValue', {}).get('unlockedLevels', [])
            st.session_state.initial_unlocked_levels_checkbox_state = all(level in current_unlocked_levels for level in ALL_LEVELS_LIST)

            st.success("File loaded successfully! Ready for editing.")
            st.rerun()
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON from file: {e}. File might be corrupted.")
            # Reset session state on error
            st.session_state.json_data = None
            st.session_state.original_file_content_bytes = None
            st.session_state.initial_values = {}
    else:
        st.error("Failed to decode the file. It might not be a valid CompleteSave.")
        st.session_state.json_data = None
        st.session_state.original_file_content_bytes = None
        st.session_state.initial_values = {}


# --- File Uploader and Default Path Check ---
st.warning("BACK UP YOUR SAVES FIRST!!! This tool is unofficial, unsupported, and I have no way to help you if something breaks.")
st.markdown("---")
uploaded_file = st.file_uploader(
    "Upload your CompleteSave file:",
    type=None, # Allow any file type
    help="Browse for your CompleteSave file. Or, place 'CompleteSave' in the same directory as this script and restart."
)

default_file_path = "CompleteSave"

# 1. Check for default file if no file uploaded and no data loaded yet
if os.path.exists(default_file_path) and uploaded_file is None and st.session_state.json_data is None:
    try:
        with open(default_file_path, 'rb') as f:
            default_file_content = f.read()
        st.info(f"Attempting to load 'CompleteSave' from default path: '{default_file_path}'...")
        load_and_init_session_state(default_file_content)
    except Exception as e:
        st.error(f"Error loading default 'CompleteSave' file: {e}")

# 2. Process uploaded file if available and not already loaded
elif uploaded_file is not None and st.session_state.json_data is None:
    file_content_bytes = uploaded_file.read()
    st.info(f"Attempting to load uploaded file: '{uploaded_file.name}'...")
    load_and_init_session_state(file_content_bytes)


# --- Quick Edits Section (only show if data is loaded) ---
if st.session_state.json_data:
    st.subheader("Quick Edits")

    # Helper for status indicator and number input
    # This helper function now correctly retrieves the *current* value from json_data
    # and compares it against the *initial* value for the indicator.
    # It also handles the column layout for the input and its indicator.
    def create_number_input_with_status(label, widget_key, initial_value_key, parent_column, min_value=0, step=1):
        current_value_from_json = min_value # Default fallback

        # Logic to get the current value from st.session_state.json_data
        if initial_value_key == "xp":
            current_value_from_json = st.session_state.json_data.get('SslValue', {}).get('xp', min_value)
        elif initial_value_key == "money":
            current_value_from_json = st.session_state.json_data.get('SslValue', {}).get('money', min_value)
        elif initial_value_key == "recovery_coins":
            map_data_vals = st.session_state.json_data.get('SslValue', {}).get('recoveryCoins', {}).values()
            current_value_from_json = next(iter(map_data_vals), min_value)
        elif '_idx' in initial_value_key: # For resource indices
            resource_idx = int(initial_value_key.split('_')[-2])
            map_data_vals = st.session_state.json_data.get('SslValue', {}).get('fobsResources', {}).values()
            for map_data in map_data_vals:
                if 'resources' in map_data and isinstance(map_data['resources'], list) and len(map_data['resources']) > resource_idx:
                    current_value_from_json = map_data['resources'][resource_idx]
                    break
        
        # Create sub-columns within the parent_column for the input and its indicator
        # Adjust ratios to give enough space for label and input, plus a small space for icon
        input_sub_col, status_sub_col = parent_column.columns([0.85, 0.15]) 

        with input_sub_col:
            new_value = st.number_input(
                label=label,
                value=current_value_from_json,
                min_value=min_value,
                step=step,
                key=widget_key,
                help=f"Original: {st.session_state.initial_values.get(initial_value_key, 'N/A')}"
            )

        with status_sub_col:
            is_modified = (new_value != st.session_state.initial_values.get(initial_value_key, min_value))
            color = "red" if is_modified else "green"
            status_icon = f"<span style='color: {color}; font-size: 1.5em;'>&#x25CF;</span>"
            
            # Use st.markdown with a div to align the icon vertically with the input box
            # You might need to tweak margin-top based on exact browser/OS rendering
            st.markdown(f"<div style='margin-top: 25px;'>{status_icon}</div>", unsafe_allow_html=True) 

        return new_value # Only return the value, as rendering is handled internally
    

    # --- XP and Cash ---
    col1, col2 = st.columns(2) # Parent columns for XP and Cash sections
    xp_value = create_number_input_with_status("Experience Points (max = 605990)", "xp_input", "xp", parent_column=col1)
    cash_value = create_number_input_with_status("Cash", "money_input", "money", parent_column=col2)

    # --- Unlock All Levels Checkbox ---
    unlock_levels = st.checkbox(
        "Unlock All Levels",
        value=st.session_state.initial_unlocked_levels_checkbox_state, # Set default state based on loaded file
        key="unlock_all_levels_checkbox",
        help="Checking this will unlock all known levels in the game. If unchecked, no changes will be made to your available levels."
    )

    st.subheader("Global Resources (applies to all maps)")

    # --- Recovery Coins ---
    rc_col_input, rc_col_status = st.columns([0.93, 0.07]) # Adjusted ratio for nearly full width input

    with rc_col_input:
        current_rc_value_from_json = st.session_state.json_data.get('SslValue', {}).get('recoveryCoins', {}).get(next(iter(st.session_state.json_data.get('SslValue', {}).get('recoveryCoins', {})), ''), 0)
        recovery_coins_value = st.number_input(
            label="Recovery Coins (Gas)",
            value=current_rc_value_from_json,
            min_value=0,
            step=1,
            key="recoveryCoins_input",
            help=f"Original: {st.session_state.initial_values.get('recovery_coins', 'N/A')}"
        )
    with rc_col_status:
        is_modified = (recovery_coins_value != st.session_state.initial_values.get('recovery_coins', 0))
        color = "red" if is_modified else "green"
        status_icon = f"<span style='color: {color}; font-size: 1.5em;'>&#x25CF;</span>"
        st.markdown(f"<div style='margin-top: 25px;'>{status_icon}</div>", unsafe_allow_html=True)

    # # --- Recovery Coins ---
    # rc_col_main = st.columns(1)[0] # Create a single column for RC, its own sub-columns will be inside
    # recovery_coins_value = create_number_input_with_status("Recovery Coins (Gas)", "recoveryCoins_input", "recovery_coins", parent_column=rc_col_main)

    
    # --- Logs, Steel Beams ---
    col3, col4 = st.columns(2) # Parent columns for Logs/SB sections
    logs_value = create_number_input_with_status("Logs", "logs_input", "logs_4_idx", parent_column=col3)
    steel_beams_value = create_number_input_with_status("Steel Beams", "steelBeams_input", "steel_beams_5_idx", parent_column=col4)

    # --- Concrete, Steel Pipes ---
    col5, col6 = st.columns(2) # Parent columns for Concrete/SP sections
    concrete_value = create_number_input_with_status("Concrete", "concrete_input", "concrete_6_idx", parent_column=col5)
    steel_pipes_value = create_number_input_with_status("Steel Pipes", "steelPipes_input", "steel_pipes_7_idx", parent_column=col6)



    # --- Save Button Logic ---
    if st.button("Save Changes to New File", help="Click to apply changes and download the new save file."):
        if st.session_state.json_data and st.session_state.original_file_content_bytes:
            # Create a deep copy of the JSON data to modify, avoiding direct modification of session_state.json_data
            # until the very end, to prevent unexpected Streamlit rerender issues or stale state.
            modified_json_data = json.loads(json.dumps(st.session_state.json_data)) 
            ssl_value_to_modify = modified_json_data.get('SslValue', {})
            if not ssl_value_to_modify:
                modified_json_data['SslValue'] = {}
                ssl_value_to_modify = modified_json_data['SslValue']

            # Apply changes only if values differ from initial_values
            if xp_value != st.session_state.initial_values['xp']:
                ssl_value_to_modify['xp'] = xp_value

            if cash_value != st.session_state.initial_values['money']:
                ssl_value_to_modify['money'] = cash_value

            if recovery_coins_value != st.session_state.initial_values['recovery_coins']:
                if 'recoveryCoins' in ssl_value_to_modify:
                    for map_name in ssl_value_to_modify['recoveryCoins']:
                        ssl_value_to_modify['recoveryCoins'][map_name] = recovery_coins_value
                else: # If 'recoveryCoins' didn't exist, create it as an empty dict (cautiously)
                    ssl_value_to_modify['recoveryCoins'] = {}

             # --- Apply Unlock All Levels change (updated logic) ---
            if unlock_levels: # If checkbox is currently checked
                ssl_value_to_modify["unlockedLevels"] = ALL_LEVELS_LIST
            # # Only delete if it was initially fully unlocked and now explicitly unchecked
            # elif not unlock_levels and st.session_state.initial_unlocked_levels_checkbox_state:
            #     if 'unlockedLevels' in ssl_value_to_modify: # Ensure it exists before deleting
            #         del ssl_value_to_modify['unlockedLevels']
            # ELSE (if not unlock_levels AND not initial_unlocked_levels_checkbox_state):
            # The user did nothing, and it wasn't fully unlocked initially.
            # So, the 'unlockedLevels' entry remains exactly as it was loaded.
            
            # Resources (Logs, Steel Beams, Concrete, Steel Pipes)
            resource_updates_map = { # Maps initial_key to (current_value, index)
                'logs_4_idx': (logs_value, 4),
                'steel_beams_5_idx': (steel_beams_value, 5),
                'concrete_6_idx': (concrete_value, 6),
                'steel_pipes_7_idx': (steel_pipes_value, 7)
            }

            if 'fobsResources' in ssl_value_to_modify:
                for map_name, map_data in ssl_value_to_modify['fobsResources'].items():
                    if 'resources' in map_data and isinstance(map_data['resources'], list):
                        resources = map_data['resources']
                        for initial_key, (current_val, idx) in resource_updates_map.items():
                            if current_val != st.session_state.initial_values[initial_key]:
                                # Ensure list is long enough, extend with zeros if needed
                                while len(resources) <= idx:
                                    resources.append(0)
                                resources[idx] = current_val
            # else: # If 'fobsResources' didn't exist, create it if resources were modified
            #     # This logic would be more complex as it would need to add default map entries
            #     # For simplicity, we assume 'fobsResources' exists if any resources are present.

            # Convert modified JSON back to bytes
            decompressed_data_edited = json.dumps(
                modified_json_data,
                indent=3, # Pretty print for readability
                ensure_ascii=False, # Allow non-ASCII characters
                separators=(',', ': ') # Compact separators for smaller output
            ).encode('utf-8')

            # Encode and provide for download
            encode_file(st.session_state.original_file_content_bytes, decompressed_data_edited)
        else:
            st.warning("Please upload a file first to save changes.")

    st.markdown("---")
    # Optional: Display raw JSON for debugging/advanced users
    if st.checkbox("Show Raw JSON (for advanced users)", value=False, help="Displays the full JSON content of the loaded save file."):
        if st.session_state.json_data:
            st.json(st.session_state.json_data)
        else:
            st.info("Upload a file to view raw JSON.")
