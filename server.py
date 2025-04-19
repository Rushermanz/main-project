import sys
import os
import sqlite3
import subprocess
from flask import Flask, render_template, request, jsonify
from db_utils import save_player_name

app = Flask(__name__, static_folder="static", template_folder="templates")

DB_PATH = "pixel_racer.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

    # map slug to folder name
    t = track.lower()
    if t == 'usa':
        folder = 'USA'
    else:
        folder = t.capitalize()

    script_path = os.path.join(
        os.getcwd(), 'pixel_racer', folder, f'{mode}.py'
    )

    if os.path.isfile(script_path):
        subprocess.Popen([sys.executable, script_path])
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

    # upsert player
    cur.execute("SELECT id FROM players WHERE name = ?", (player_name,))
    row = cur.fetchone()
    if row:
        player_id = row['id']
    else:
        cur.execute("INSERT INTO players(name) VALUES (?)", (player_name,))
        player_id = cur.lastrowid

    # insert leaderboard entry
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
    result = [
        {'player': r['player'], 'lap_time': r['lap_time']}
        for r in rows
    ]
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

