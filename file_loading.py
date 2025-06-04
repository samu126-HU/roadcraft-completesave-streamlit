import json
import streamlit as st
from valid_values import ALL_LEVELS_LIST, ALL_TRUCKS_LIST
from utility import decode_file

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
                'companyName': json_data.get('SslValue', {}).get('companyName', ""), 
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

            # --- Set initial state of unlock_trucks checkbox ---
            current_unlocked_trucks = json_data.get('SslValue', {}).get('newUnlockedTrucks', [])
            st.session_state.initial_unlocked_trucks_checkbox_state = all(truck in current_unlocked_trucks for truck in ALL_TRUCKS_LIST)

            # --- Set initial state of lift_fog checkbox ---
            current_fog_progress = json_data.get('SslValue', {}).get('fogOfWarProgress', {})
            # Assume fog is lifted if all maps present have 100% progress
            st.session_state.initial_lift_fog_checkbox_state = all(progress == 100.0 for progress in current_fog_progress.values()) and bool(current_fog_progress)

            # --- Set initial state of remove_rusty_trucks checkbox ---
            # Check if any "old" trucks exist in storedTrucks, excluding "khan_lo_strannik_mob_old"
            current_stored_trucks = json_data.get('SslValue', {}).get('storedTrucks', {})
            has_rusty_trucks_to_remove = False
            for truck_name, truck_data in current_stored_trucks.items():
                if truck_name.endswith("_old") and truck_name != "khan_lo_strannik_mob_old" and len(truck_data) > 0:
                    has_rusty_trucks_to_remove = True
                    break
            st.session_state.initial_remove_rusty_trucks_checkbox_state = not has_rusty_trucks_to_remove # Checked if no removable rusty trucks are present

            st.success("File loaded successfully! Ready for editing.")
            st.rerun()
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON from file: {e}. File might be corrupted.")
            # Reset session state on error
            st.session_state.json_data = None
            st.session_state.original_file_content_bytes = None
            st.session_state.initial_values = {}
        except Exception as e:
            st.error(f"An unexpected error occurred during file loading: {e}")
            st.session_state.json_data = None
            st.session_state.original_file_content_bytes = None
            st.session_state.initial_values = {}
    else:
        st.error("Failed to decode the file. It might not be a valid CompleteSave.")
        st.session_state.json_data = None
        st.session_state.original_file_content_bytes = None
        st.session_state.initial_values = {}
