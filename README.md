# 🍒 Takeout Extractor

> A beautiful, cherry-red desktop app to merge and extract all your **Google Takeout ZIP files** into one folder — with a single click.

![Python](https://img.shields.io/badge/Python-3.9%2B-crimson?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-darkred?style=flat-square)

---
<img width="1216" height="846" alt="image" src="https://github.com/user-attachments/assets/bafb28d4-1f75-4572-b636-5e6e50422779" />

## ✨ Features

- 📂 **Browse** for your source folder containing `takeout-*.zip` files
- 🔍 **Scan** to auto-discover all matching ZIPs and display them in a list
- 📁 **Pick** any destination folder to extract everything into
- ⚡ **Extract All** with one click — files merge seamlessly
- 📊 Live **progress bar** with percentage and ETA
- 📋 Color-coded **extraction log** (green = success, red = error, orange = warning)
- ⏹ **Stop** mid-extraction at any time
- 🛡️ Full **error handling** — corrupted ZIPs, permission errors, disk errors
- 📦 **Auto-installs** any missing Python packages on first run

---

## 📋 Requirements

| Requirement | Version |
|---|---|
| Python | **3.9 or newer** |
| tkinter | Included with Python (see notes below) |
| pip | Included with Python |

> All other dependencies are installed **automatically** on first run via `requirements.txt`.

---

## 🪟 Windows

### 1. Install Python
Download from [python.org](https://www.python.org/downloads/) and run the installer.

> ⚠️ **Important:** During install, check **"Add Python to PATH"**

Verify in a terminal:
```cmd
python --version
```

### 2. Run the app

**Option A — Double-click launcher (easiest)**
```
Double-click  Launch.bat
```

**Option B — Command Prompt**
```cmd
cd path\to\TakeoutExtractorGUI
python app.py
```

**Option C — PowerShell**
```powershell
cd path\to\TakeoutExtractorGUI
python app.py
```

> tkinter is bundled with the official Python Windows installer — no extra steps needed.

---

## 🍎 macOS

### 1. Install Python

**Option A — Official installer (recommended)**
Download from [python.org](https://www.python.org/downloads/macos/) and install the `.pkg`.

**Option B — Homebrew**
```bash
brew install python
```

Verify:
```bash
python3 --version
```

### 2. Install tkinter (if missing)

The official python.org installer includes tkinter. If you used Homebrew:
```bash
brew install python-tk
```

Or for a specific version (e.g. 3.12):
```bash
brew install python-tk@3.12
```

### 3. Run the app
```bash
cd path/to/TakeoutExtractorGUI
python3 app.py
```

> 💡 On macOS you may see a pop-up asking to allow network access for pip — click **Allow** so dependencies can install.

---

## 🐧 Linux

### 1. Install Python & tkinter

**Ubuntu / Debian / Linux Mint**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

**Fedora / RHEL / CentOS**
```bash
sudo dnf install python3 python3-pip python3-tkinter
```

**Arch Linux / Manjaro**
```bash
sudo pacman -S python python-pip tk
```

**openSUSE**
```bash
sudo zypper install python3 python3-pip python3-tk
```

Verify:
```bash
python3 --version
python3 -c "import tkinter; print('tkinter OK')"
```

### 2. Run the app
```bash
cd path/to/TakeoutExtractorGUI
python3 app.py
```

To make it executable directly:
```bash
chmod +x app.py
./app.py
```

---

## 🚀 First-Run Behavior

On the **very first launch**, if any packages in `requirements.txt` are missing, the app will:

1. Show a small cherry-red **installer splash window**
2. Install each missing package via `pip` automatically
3. Close the splash and open the **main app**

This only ever happens **once** per machine. All subsequent launches open instantly.

---

## 🗂️ How to Use

```
1.  Click  "Browse 📁"  next to Source Folder
    → Select the folder containing your  takeout-*.zip  files

2.  Click  "🔍 Scan for ZIPs"
    → The file list fills with all discovered archives

3.  Click  "Browse 📁"  next to Destination Folder
    → Select (or create) where you want the files extracted

4.  Click  "⚡ Extract All"
    → Watch the progress bar and log as files extract

5.  A summary popup appears when done ✓
```

---

## ➕ Adding More Python Dependencies

Edit [`requirements.txt`](./requirements.txt) and add packages (one per line):

```txt
Pillow>=10.0.0
requests>=2.31.0
```

They will be auto-installed the next time the app is launched.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `python: command not found` | Use `python3` instead, or add Python to PATH |
| `No module named tkinter` | Install `python3-tk` (Linux) or `python-tk` (Homebrew) |
| `Permission denied` on destination | Choose a folder you own, or run with elevated permissions |
| App window doesn't appear | Ensure a display is available (not SSH without `-X`) |
| Pip install fails at splash | Check internet connection; install manually: `pip install -r requirements.txt` |

---

## 📁 File Structure

```
TakeoutExtractorGUI/
├── app.py            ← Main application (run this)
├── requirements.txt  ← Auto-installed dependencies
├── Launch.bat        ← Windows one-click launcher
└── README.md         ← This file
```

---

## 📄 License

MIT — free to use, modify, and distribute.
