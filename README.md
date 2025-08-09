# QMMX Pro – Phase 1 & 2

This project is the full production build of QMMX Pro — a machine-learning-powered options trading assistant built in Python, React, and Electron.

> This `README.md` documents file structure, dependencies, how to run the app, and troubleshooting tips for development and packaging.

---

## 🚀 Project Overview

- **Backend**: Python Flask app (`app.py`) with machine learning modules and logic
- **Frontend**: React app with modular panels (SettingsPanel, MainDashboard, etc.)
- **Desktop App**: Electron wrapper with Windows installer support
- **Models**: Joblib-trained ML model used for pattern recognition
- **Features**:
  - Pattern detection, scoring, and memory
  - Live price-level interaction evaluator
  - Auto-trade simulation and portfolio tracking
  - Exit strategy engine
  - Diagnostic and performance monitor
  - Full Settings panel (API + alerts)
  - Keepalive protection for idle systems

---

## 📁 File Tree (Summary)

QMMX_Pro_Phase1/
├── app.py # Flask backend entry
├── settings_manager.py # Load/save settings
├── *.py # Modules for ML, memory, strategy, etc.
├── models/
│ └── qmmx_model_v1.joblib
├── frontend/
│ ├── src/
│ │ ├── App.js, App.css
│ │ ├── components/
│ │ │ ├── MainDashboard.js
│ │ │ ├── SettingsPanel.js
│ │ │ └── *.js (all panels)
│ ├── public/
│ │ └── index.html
│ └── package.json
├── build/ # Electron build assets
├── electron/
│ └── main.js # Electron entry point
├── dist/
│ └── QMMX Pro Setup.exe # Generated .exe from electron-builder
├── settings.json # Saved API key and phone settings
└── README.md

yaml
Copy
Edit

---

## 📦 Installing & Running

### 1. Backend (Flask + ML)
```bash
cd C:\QMMX_Pro_Phase1
python app.py
2. Frontend (React)
bash
Copy
Edit
cd frontend
npm install
npm run build
3. Electron (Desktop App)
bash
Copy
Edit
npm run electron-start      # Dev
npm run electron-pack       # Bundle for prod
⚠️ Common Errors & Fixes
🔴 "Can't resolve './App.css'" (Webpack error)
This usually means cached imports are stale:

bash
Copy
Edit
cd frontend
rmdir /s /q node_modules
del /f /q package-lock.json
npm install
npm run build
Or change the import path slightly to bust the cache:

js
Copy
Edit
import '../App.css?v=1';
🧠 Notes
All real modules are included. No stubs, mockups, or placeholders.

Duplicate SettingsPanel.js exists but only the one in src/components/ is used.

settings.json stores API key and phone numbers locally.

qmmx-icon.ico is used across frontend, Electron, and installer.

🛠️ Packaging
The .exe file for distribution is created via:

bash
Copy
Edit
npm run electron-pack
The result will appear in:

bash
Copy
Edit
frontend/dist/QMMX Pro Setup 1.0.0.exe
📅 Last Confirmed Tree Snapshot
This project tree was captured using:

bash
Copy
Edit
tree /f > file_tree.txt
Stored as:

makefile
Copy
Edit
C:\QMMX_Pro_Phase1\file_tree.txt
(You can regenerate at any time.)

vbnet
Copy
Edit

Let me know if you want me to add:
- Change log section
- Developer tips section
- Build script shortcuts
- API key setup instructions

Otherwise, you can paste that directly into `C:\QMMX_Pro_Phase1\README.md` and it’s ready to go.

Would you like a **tree-only version** of the file tree saved separately too?