# Roadcraft Save Editor (Streamlit)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://roadcraft-save-editor.streamlit.app)

A modern, user-friendly web and local tool for editing your **Roadcraft** game save files. Forked from the original Roadcraft completesave editor by NakedDevA, with major UI and feature improvements.

---

## 🚀 Features

- **Edit Player Progress**
  - Add or edit XP
  - Add or edit Cash
  - Update company name

- **Inventory Management**
  - Add or edit Recovery Coins
  - Add or edit Logs
  - Add or edit Steel Beams
  - Add or edit Concrete
  - Add or edit Steel Pipes

- **Trucks & Maps**
  - Unlock all trucks (or select/unlock trucks individually)
  - Unlock all maps/levels
  - Remove rusty trucks from garage (with exceptions)

- **Advanced Editing**
  - View and edit raw JSON
  - Download the updated save file for use in your game

---

## 📝 How to Use

1. **Back up your save file!**
2. [Open the Streamlit App](https://roadcraft-save-edit.streamlit.app/) *(or run locally, see below)*
3. Upload your `CompleteSave` file (see below for file locations)
4. Make your desired edits using the intuitive UI
5. Download the updated file and replace your original (after backing it up!)
6. If you run into issues, use Troubleshooting Guide page found in the sidebar of the UI app

---

## 📂 Save File Locations

- **Steam (Windows):**
  - `%AppData%/Local/Saber/RoadCraftGame/storage/steam/user/<YOUR_STEAM_USER_ID>/Main/save`
- **Steam Deck (Linux):**
  - `/home/deck/.local/share/Steam/steamapps/compatdata/2104890/pfx/drive_c/users/steamuser/AppData/Local/Saber/RoadCraftGame/storage/steam/user/<YOUR_STEAM_USER_ID>/Main/save`

---

## 🖥️ Run Locally

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # or just: pip install streamlit
streamlit run roadcraft_streamlit.py
```

- Place your `CompleteSave` file in the same directory or upload it via the UI.
- Use the sidebar to navigate between the Main Editor and Troubleshooting Guide.

---

## 🛠️ Troubleshooting & Help

- Use the **Troubleshooting Guide** page in the sidebar for step-by-step help if your save doesn't work after editing.
- Validate your save file's JSON using [JSONLint](https://jsonlint.com) if you encounter errors.
- Always keep a backup of your original save file!

---

## 🙏 Credits & Acknowledgements

- Forked from [NakedDevA's Roadcraft completesave editor](https://github.com/NakedDevA/roadcraft-completesave)
- UI and feature improvements by [cgpavlakos](https://github.com/cgpavlakos) and [samu126-HU](https://github.com/samu126-HU)

---

## 📢 Disclaimer

This tool is **unofficial** and **unsupported**. Use at your own risk. Always back up your saves before making changes. The authors are not responsible for lost or corrupted save files.
