import streamlit as st

st.set_page_config(layout="centered", page_title="Roadcraft Troubleshooting Guide", initial_sidebar_state="expanded")

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

st.markdown("---")
st.markdown("### Troubleshooting Broken Saves")
st.markdown("""
**If your save file is broken and you have no backup, you can follow these steps:**

1. **Check the Raw Save File:**  
Use [JSONLint](https://jsonlint.com) or another JSON linting tool to validate your save file.  
    - After uploading a save, scroll to the bottom of the save editor page and use the **'Show Raw JSON as Text (editable)'** option to show the raw JSON. 
    - Copy it and paste it into the validator.

2. **Validate the JSON:**  
    - If the tool says your JSON is **valid**, review the values you've changed for mistakes.
    - If the JSON is **invalid**, fix the errors reported by the tool. (You can use AI tools or ask for help if you're unsure.)

3. **Common Issues to Check:**  
    - **Numbers:** Fields like `money` should be plain numbers (no letters or decimals).
    - **Lists:** Lists like `unlockedTrucks` should only contain valid truck names (no typos or non-existent names).

4. **Reference Valid Values:**  
    - [Click here for a list of valid levels and truck names.](https://github.com/samu126-HU/roadcraft-completesave-streamlit/blob/main/valid_values.py)
        """)
st.markdown("---")
