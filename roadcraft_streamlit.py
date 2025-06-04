import json
import streamlit as st
from valid_values import ALL_LEVELS_LIST, ALL_TRUCKS_LIST
from utility import encode_file
from file_loading import load_and_init_session_state
import os # For checking default file path existence

# --- Streamlit App Layout and Logic ---
st.set_page_config(layout="centered", page_title="Roadcraft Save Editor", initial_sidebar_state="expanded")

with st.sidebar:
    st.page_link('roadcraft_streamlit.py', label='Save Editor')
    st.page_link('pages/troubleshooting_guide.py', label='Troubleshooting Guide')
    st.markdown("Save files are usually found at:")
    st.markdown("***1. STEAM*** `%AppData%/Local/Saber/RoadCraftGame/storage/steam/user/<YOUR_STEAM_USER_ID>/Main/save`")
    st.markdown("***2. STEAM DECK*** `/home/deck/.local/share/Steam/steamapps/compatdata/2104890/pfx/drive_c/users/steamuser/AppData/Local/Saber/RoadCraftGame/storage/steam/user/<YOUR_STEAM_USER_ID>/Main/save`")
    st.markdown("---")
    st.markdown("The source code for this app is available on [github](https://github.com/samu126-HU/roadcraft-completesave-streamlit) if you prefer to run locally.")
    st.markdown("---")
    st.markdown("Thanks to cgpavlakos for his [fork](https://github.com/cgpavlakos/roadcraft-completesave-streamlit) of NakedDevA's [Roadcraft completesave editor](https://github.com/NakedDevA/roadcraft-completesave) (the original save editor author).")
    st.markdown("This app is a version of that editor, with some additional features.")
    st.markdown("---")

# Initialize session state variables if they don't exist
if 'json_data' not in st.session_state:
    st.session_state.json_data = None
if 'original_file_content_bytes' not in st.session_state:
    st.session_state.original_file_content_bytes = None
if 'initial_values' not in st.session_state:
    st.session_state.initial_values = {}
if 'initial_unlocked_levels_checkbox_state' not in st.session_state:
    st.session_state.initial_unlocked_levels_checkbox_state = False
if 'initial_unlocked_trucks_checkbox_state' not in st.session_state:
    st.session_state.initial_unlocked_trucks_checkbox_state = False
if 'initial_lift_fog_checkbox_state' not in st.session_state: # New state for fog of war
    st.session_state.initial_lift_fog_checkbox_state = False
if 'initial_remove_rusty_trucks_checkbox_state' not in st.session_state: # New state for removing rusty trucks
    st.session_state.initial_remove_rusty_trucks_checkbox_state = False

# --- File Uploader and Default Path Check ---
st.warning("***BACK UP YOUR SAVES FIRST!*** This tool is **unofficial, unsupported.** If it's too late you can check the troubleshooting page in the sidebar but there's no guarantee it will work. If your save breaks I have no way of helping you.")
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
    
    # Helper for status indicator and string input
    def create_string_input_with_status(label, widget_key, initial_value_key, parent_column):
        current_value_from_json = st.session_state.json_data.get('SslValue', {}).get(initial_value_key, "")

        input_sub_col, status_sub_col = parent_column.columns([0.85, 0.15])

        with input_sub_col:
            new_value = st.text_input(
                label=label,
                value=current_value_from_json,
                key=widget_key,
                help=f"Original: {st.session_state.initial_values.get(initial_value_key, 'N/A')}"
            )

        with status_sub_col:
            is_modified = (new_value != st.session_state.initial_values.get(initial_value_key, ""))
            color = "red" if is_modified else "green"
            status_icon = f"<span style='color: {color}; font-size: 1.5em;'>&#x25CF;</span>"
            st.markdown(f"<div style='margin-top: 25px;'>{status_icon}</div>", unsafe_allow_html=True)
        
        return new_value

    # --- XP and Cash ---
    col1, col2 = st.columns(2) # Parent columns for XP and Cash sections
    xp_value = create_number_input_with_status("Experience Points (max = 605990)", "xp_input", "xp", parent_column=col1)
    cash_value = create_number_input_with_status("Cash", "money_input", "money", parent_column=col2)

    # --- Company Name ---
    company_name_col = st.columns(1)[0] # Single column for company name
    company_name_value = create_string_input_with_status("Company Name", "companyName_input", "companyName", parent_column=company_name_col)


    # --- Unlock All Levels Checkbox ---
    unlock_levels = st.checkbox(
        "Unlock All Levels",
        value=st.session_state.initial_unlocked_levels_checkbox_state, # Set default state based on loaded file
        key="unlock_all_levels_checkbox",
        help="Checking this will unlock all known levels in the game. If unchecked, no changes will be made to your available levels."
    )

    # --- Unlock All Trucks Checkbox ---
    unlock_trucks = st.checkbox(
        "Unlock All Trucks",
        value=st.session_state.initial_unlocked_trucks_checkbox_state, # Set default state based on loaded file
        key="unlock_all_trucks_checkbox",
        help="Checking this will unlock all known trucks in the game. If unchecked, no changes will be made to your available trucks. Aramatsu Bowhead added."
    )

    # --- Remove Rusty Trucks Checkbox ---
    remove_rusty_trucks = st.checkbox(
        "Remove Rusty Trucks from Garage",
        value=st.session_state.initial_remove_rusty_trucks_checkbox_state, # Set default state based on loaded file
        key="remove_rusty_trucks_checkbox",
        help="Checking this will set the inventory count of all trucks ending in '_old' to zero, EXCEPT 'khan_lo_strannik_mob_old'. Trucks on maps will remain."
    )

    # --- Per-Truck Unlock Dropdown ---
    st.markdown("**Select Unlocked Trucks:**")
    current_unlocked_trucks = st.session_state.json_data.get('SslValue', {}).get('newUnlockedTrucks', [])
    # Deduplicate trucks while preserving order
    seen_trucks = set()
    unique_trucks = []
    for truck in ALL_TRUCKS_LIST:
        if truck not in seen_trucks:
            unique_trucks.append(truck)
            seen_trucks.add(truck)
    # Filter current_unlocked_trucks to only those present in unique_trucks to avoid Streamlit errors
    filtered_unlocked_trucks = [truck for truck in current_unlocked_trucks if truck in unique_trucks]
    # Multi-select dropdown for unlocked trucks
    selected_trucks = st.multiselect(
        "Unlocked Trucks",
        options=unique_trucks,
        default=filtered_unlocked_trucks,
        key="unlocked_trucks_multiselect",
        help="Select which trucks should be unlocked."
    )
    # For compatibility with the rest of the code, create a dict of truck:bool
    truck_checkbox_states = {truck: (truck in selected_trucks) for truck in unique_trucks}

    # # --- Lift all fog checkbox ---
    # lift_fog = st.checkbox(
    #     "Lift All Fog of War",
    #     value=st.session_state.initial_lift_fog_checkbox_state, # Set default state based on loaded file
    #     key="lift_fog_checkbox",
    #     help="Checking this will reveal all fog of war on all maps to 100%."
    # )


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
            
            # Apply Company Name change
            if company_name_value != st.session_state.initial_values['companyName']:
                ssl_value_to_modify['companyName'] = company_name_value


            # --- Apply Recovery Coins change using ALL_LEVELS_LIST ---
            if recovery_coins_value != st.session_state.initial_values['recovery_coins']:
                if 'recoveryCoins' not in ssl_value_to_modify:
                    ssl_value_to_modify['recoveryCoins'] = {}
                for map_name in ALL_LEVELS_LIST: # Iterate through all known levels
                    ssl_value_to_modify['recoveryCoins'][map_name] = recovery_coins_value


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

            # --- Apply Unlock All Trucks change (updated logic) ---
            if unlock_trucks: # If checkbox is currently checked
                ssl_value_to_modify["newUnlockedTrucks"] = ALL_TRUCKS_LIST
                ssl_value_to_modify['lockedTrucks'] = [] # Set it to an empty list
            else:
                # Use the per-truck checkboxes to determine which trucks to unlock
                selected_trucks = [truck for truck, checked in truck_checkbox_states.items() if checked]
                ssl_value_to_modify["newUnlockedTrucks"] = selected_trucks
                # Optionally, update lockedTrucks as well
                ssl_value_to_modify['lockedTrucks'] = [truck for truck in ALL_TRUCKS_LIST if truck not in selected_trucks]

            # --- Apply Remove Rusty Trucks change ---
            if remove_rusty_trucks:
                if 'storedTrucks' in ssl_value_to_modify:
                    for truck_name in list(ssl_value_to_modify['storedTrucks'].keys()): # Iterate over a copy to allow modification
                        if truck_name.endswith("_old") and truck_name != "khan_lo_strannik_mob_old": # Added exception
                            ssl_value_to_modify['storedTrucks'][truck_name] = [] # Set to empty list

            # # --- Apply Lift All Fog of War change ---
            # if lift_fog:
            #     if 'fogOfWarProgress' not in ssl_value_to_modify:
            #         ssl_value_to_modify['fogOfWarProgress'] = {}
            #     for map_name in ALL_LEVELS_LIST: # Use ALL_LEVELS_LIST as a reference for map names
            #         ssl_value_to_modify['fogOfWarProgress'][map_name] = 100.0

            # --- Resources (Logs, Steel Beams, Concrete, Steel Pipes) using ALL_LEVELS_LIST ---
            resource_updates_map = { # Maps initial_key to (current_value, index)
                'logs_4_idx': (logs_value, 4),
                'steel_beams_5_idx': (steel_beams_value, 5),
                'concrete_6_idx': (concrete_value, 6),
                'steel_pipes_7_idx': (steel_pipes_value, 7)
            }

            if 'fobsResources' not in ssl_value_to_modify:
                ssl_value_to_modify['fobsResources'] = {}

            for map_name in ALL_LEVELS_LIST: # Iterate through all known levels
                # Ensure the map entry exists in fobsResources
                if map_name not in ssl_value_to_modify['fobsResources']:
                    ssl_value_to_modify['fobsResources'][map_name] = {"resources": [0]*8} # Initialize with 8 zeros if not present

                resources = ssl_value_to_modify['fobsResources'][map_name]['resources']
                for initial_key, (current_val, idx) in resource_updates_map.items():
                    if current_val != st.session_state.initial_values[initial_key]:
                        # Ensure list is long enough, extend with zeros if needed
                        while len(resources) <= idx:
                            resources.append(0)
                        resources[idx] = current_val

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

    # Show raw JSON as editable text
    if st.checkbox("Show Raw JSON as Text (editable)", value=False, help="Edit the full JSON content directly."):
        if st.session_state.json_data:
            raw_json_str = json.dumps(st.session_state.json_data, indent=3, ensure_ascii=False)
            edited_json_str = st.text_area(
                "Edit Raw JSON",
                value=raw_json_str,
                height=400,
                key="editable_json_text_area",
                help="Edit the JSON directly. Be careful: invalid JSON will cause errors.",
                label_visibility="visible"
            )
            if st.button("Apply Edited JSON", key="apply_edited_json_button"):
                try:
                    new_json = json.loads(edited_json_str)
                    st.session_state.json_data = new_json
                    st.success("JSON applied successfully.")
                except Exception as e:
                    st.error(f"Invalid JSON: {e}")
        else:
            st.info("Upload a file to view and edit raw JSON.")
