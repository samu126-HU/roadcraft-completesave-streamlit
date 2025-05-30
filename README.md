# roadcraft-completesave-streamlit
An online tool for editing your roadcraft save. Forked from Roadcraft completesave editor by NakedDave. 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://roadcraft-save-edit.streamlit.app/)

## what it does:
* Add/Edit XP
* Add/Edit Cash
* Add/Edit Inventory
  * Recovery Coins (gas)
  * Logs
  * Steel Beams
  * Pipes
  * Concrete
* Unlock all maps
* Unlock all trucks
* Update company name

## how to use it:
* BACKUP YOUR SAVE BEFORE STARTING
* Upload your CompleteSave file
* Edit as desired
* Download updated file and save it back to your directory

to run locally, if you don't want to upload your save file: 
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install streamlit
streamlit run roadcraft_streamlit.py
```
