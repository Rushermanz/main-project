# 🏎️ Pixel Racer

A top-down Formula 1-style pixel racing game with multiple tracks, game modes, and a live leaderboard — built with Python, Pygame, and Flask.

---

## 🎮 Game Modes

| Mode | Description |
|---|---|
| **Time Trial** | Race solo and post your best lap time to the leaderboard |
| **Race vs Bot** | Race against 3 ghost bots replaying real recorded runs |
| **PvP** | Split-screen 2-player race on the same keyboard |

## 🗺️ Available Tracks

- 🇧🇭 Bahrain
- 🇦🇿 Baku
- 🇬🇧 Silverstone
- 🇪🇸 Spain
- 🇺🇸 USA

---

## 🚀 How to Play (Windows — Recommended)

### Option A — Download the Release (Easiest)

1. Go to the [**Releases**](../../releases) page
2. Download `PixelRacer-Windows.zip`
3. Extract the zip anywhere on your PC
4. **Install Python** (see requirement below ⬇️)
5. Double-click `PixelRacer.exe`
6. Your browser opens automatically → enter your name → pick a track → race!

> **Controls:**
> - **Arrow keys** → steer / accelerate / brake (Player 1 / solo)
> - **WASD** → Player 2 (PvP mode)
> - **ESC** → quit game window
> - **ENTER** → retry after a race

---

## ⚠️ Requirements

### 🐍 Python Must Be Installed

The web server (`PixelRacer.exe`) is fully self-contained, but the **game windows** (Pygame) are launched as separate Python scripts. This means **Python must be installed** on your computer.

**Download Python here:** 👉 https://www.python.org/downloads/

> ✅ Check **"Add Python to PATH"** during installation — this is important!

After installing Python, also install Pygame by opening a terminal and running:

```
pip install pygame
```

### 📋 Full Requirements Summary

| Requirement | Notes |
|---|---|
| **Windows 10/11** | Only Windows is supported for the `.exe` release |
| **Python 3.10+** | Must be installed separately from python.org |
| **pygame** | Install via `pip install pygame` |
| **A browser** | Chrome, Edge, Firefox — any modern browser |
| **A keyboard** | Required for game controls |

---

## 🛠️ Running from Source (Developers)

If you want to run the project directly from the source code:

```bash
# 1. Clone the repo
git clone https://github.com/Rushermanz/main-project-bca.git
cd main-project-bca

# 2. Install dependencies
pip install flask pygame

# 3. Start the server
python server.py
```

Then open **http://127.0.0.1:5000** in your browser.

---

## 📁 Project Structure

```
main-project-bca/
├── server.py              # Flask web server (entry point)
├── db_utils.py            # Database helper
├── pixel_racer.db         # SQLite leaderboard database
├── templates/             # HTML pages (home, tracks, profile)
├── static/                # CSS, JS, images for the website
├── assets/                # Game assets (track images, sounds, car sprites)
├── pixel_racer/
│   ├── Bahrain/           # Track scripts (time_trial.py, race_bot.py, pvp.py)
│   ├── Baku/
│   ├── Silverstone/
│   ├── Spain/
│   └── USA/
└── *_bot_run.json         # Recorded ghost bot replay data
```

---

## 🏆 Leaderboard

Lap times are saved automatically after completing a Time Trial lap. The leaderboard is stored locally in `pixel_racer.db` next to the `.exe` — your scores persist between sessions.

---

## 🐛 Troubleshooting

**Game window doesn't open after clicking "Play"**
→ Make sure Python is installed and `python` is on your PATH. Open a terminal and type `python --version` to check.

**"pip is not recognized"**
→ Reinstall Python from python.org and tick **"Add Python to PATH"**.

**Browser doesn't open automatically**
→ Manually go to **http://127.0.0.1:5000** in your browser.

**Port 5000 already in use**
→ Close any other apps using port 5000, or restart your PC.
