import sqlite3
import os
import sys

# Resolve the DB path relative to this file's location.
# Works both from source and when loaded by server.py from BASE_DIR.
def _get_db_path():
    if getattr(sys, 'frozen', False):
        # Running inside PyInstaller bundle – DB lives next to the .exe
        return os.path.join(os.path.dirname(sys.executable), 'pixel_racer.db')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pixel_racer.db')

def save_player_name(name):
    conn = sqlite3.connect(_get_db_path())
    c = conn.cursor()
    c.execute('SELECT id FROM players WHERE name = ?', (name,))
    result = c.fetchone()

    if not result:
        c.execute('INSERT INTO players (name) VALUES (?)', (name,))
        conn.commit()
        player_id = c.lastrowid
    else:
        player_id = result[0]

    conn.close()
    return player_id
