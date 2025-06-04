import streamlit as st

st.set_page_config(layout="centered", page_title="Troubleshooting Guide", initial_sidebar_state="expanded")

# --- Sidebar Navigation Menu ---
page = st.sidebar.selectbox(
    "Navigation",
    ["Save Editor", "Troubleshooting Guide"]
)

if page == "Save Editor":
    st.switch_page("roadcraft_streamlit.py")

st.title("Troubleshooting Guide")

st.markdown("---")
st.markdown("### Troubleshooting Broken Saves")
st.markdown("""
**If your save file is broken and you have no backup, you can follow these steps:**

1. **Check the Raw Save File:**  
   Use [JSONLint](https://jsonlint.com) or another JSON linting tool to validate your save file.  
   - After uploading a save, scroll to the bottom of this page and use the **'Show Raw JSON as Text (editable)'** option to copy the raw JSON.

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
