import sys
import os
import sqlite3
import subprocess
import threading
import webbrowser
from flask import Flask, render_template, request, jsonify

# ── Resolve the root directory ──────────────────────────────────────────────
# When frozen by PyInstaller the extracted files land in sys._MEIPASS.
# When running from source, use the directory of this file.
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS          # PyInstaller temp-extraction folder
    # Also keep a writable dir next to the .exe for the DB & player json
    EXE_DIR  = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR  = BASE_DIR

# ── Paths ───────────────────────────────────────────────────────────────────
DB_PATH          = os.path.join(EXE_DIR, 'pixel_racer.db')
PLAYER_JSON_PATH = os.path.join(EXE_DIR, 'current_player.json')
TEMPLATES_DIR    = os.path.join(BASE_DIR, 'templates')
STATIC_DIR       = os.path.join(BASE_DIR, 'static')
PIXEL_RACER_DIR  = os.path.join(BASE_DIR, 'pixel_racer')

# Ensure the writable DB exists next to the exe (first-run copy)
_src_db = os.path.join(BASE_DIR, 'pixel_racer.db')
if not os.path.exists(DB_PATH) and os.path.exists(_src_db):
    import shutil
    shutil.copy2(_src_db, DB_PATH)

# ── Flask app ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)

# ── Import db_utils with the resolved DB path ────────────────────────────────
# We patch the module-level path before importing so db_utils uses the right DB.
import importlib, types

def _load_db_utils():
    """Load db_utils.py from BASE_DIR and inject the correct DB path."""
    spec = importlib.util.spec_from_file_location(
        "db_utils", os.path.join(BASE_DIR, "db_utils.py"))
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Monkey-patch its sqlite3.connect call to use our DB_PATH
    _orig_connect = sqlite3.connect
    def _patched_connect(path, *a, **kw):
        if path == 'pixel_racer.db':
            path = DB_PATH
        return _orig_connect(path, *a, **kw)
    mod._connect = _patched_connect   # expose for reference
    return mod

_db_utils = _load_db_utils()
save_player_name = _db_utils.save_player_name


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/tracks')
def tracks():
    return render_template('tracks.html')

@app.route('/save_name', methods=['POST'])
def save_name():
    data = request.get_json()
    name = data.get('name')
    if name:
        player_id = save_player_name(name)
        return jsonify({'status': 'success', 'id': player_id})
    return jsonify({'status': 'error', 'message': 'No name provided'}), 400

@app.route('/start_game', methods=['POST'])
def start_game():
    data  = request.get_json() or {}
    track = data.get('track')
    mode  = data.get('mode')

    if not track or not mode:
        return jsonify({'error': 'Track or mode missing'}), 400

    t = track.lower()
    folder = 'USA' if t == 'usa' else t.capitalize()

    script_path = os.path.join(PIXEL_RACER_DIR, folder, f'{mode}.py')

    if os.path.isfile(script_path):
        # Use a real Python interpreter.
        # When frozen, sys.executable is the .exe; we ship python312.dll but
        # game scripts need a plain Python – so we look for python next to exe,
        # then fall back to whatever is on PATH.
        python = sys.executable
        if getattr(sys, 'frozen', False):
            # Try pythonw.exe / python.exe in the same dir as the bundled exe
            for name in ('python.exe', 'pythonw.exe'):
                candidate = os.path.join(EXE_DIR, name)
                if os.path.isfile(candidate):
                    python = candidate
                    break
            else:
                import shutil
                python = shutil.which('python') or shutil.which('python3') or sys.executable

        subprocess.Popen(
            [python, script_path],
            cwd=BASE_DIR          # game scripts resolve "assets/" relative to BASE_DIR
        )
        return ('', 204)
    else:
        app.logger.error(f"Game file not found: {script_path}")
        return jsonify({'error': 'Game file not found'}), 404

@app.route('/submit_time', methods=['POST'])
def submit_time():
    data        = request.get_json() or {}
    track_id    = data.get('track_id')
    lap_time    = data.get('lap_time')
    player_name = data.get('player_name', 'Player 1')

    if track_id is None or lap_time is None:
        return jsonify({'error': 'track_id and lap_time required'}), 400

    db  = get_db()
    cur = db.cursor()

    cur.execute("SELECT id FROM players WHERE name = ?", (player_name,))
    row = cur.fetchone()
    if row:
        player_id = row['id']
    else:
        cur.execute("INSERT INTO players(name) VALUES (?)", (player_name,))
        player_id = cur.lastrowid

    cur.execute("""
        INSERT INTO leaderboard(track_id, player_id, lap_time)
          VALUES (?, ?, ?)
    """, (track_id, player_id, lap_time))

    db.commit()
    return jsonify({'status': 'success'}), 201

@app.route('/leaderboard/<int:track_id>')
def get_leaderboard(track_id):
    db  = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT p.name   AS player,
               l.lap_time
          FROM leaderboard l
          JOIN players    p ON p.id = l.player_id
         WHERE l.track_id = ?
         ORDER BY l.lap_time ASC
         LIMIT 10
    """, (track_id,))
    rows = cur.fetchall()
    return jsonify([{'player': r['player'], 'lap_time': r['lap_time']} for r in rows])

@app.route('/set_current_player', methods=['POST'])
def set_current_player():
    data = request.get_json() or {}
    name = data.get("name", "Player 1")
    with open(PLAYER_JSON_PATH, "w") as f:
        f.write(name)
    return jsonify({'status': 'ok'})


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Open browser automatically after a short delay
    def _open_browser():
        import time; time.sleep(1.2)
        webbrowser.open('http://127.0.0.1:5000')
    threading.Thread(target=_open_browser, daemon=True).start()

    # debug=False so Flask doesn't spawn a reloader child process
    app.run(debug=False, port=5000)
