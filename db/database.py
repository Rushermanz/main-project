# db/database.py
import sqlite3

def create_database():
    conn = sqlite3.connect('pixel_racer.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_player(name):
    conn = sqlite3.connect('pixel_racer.db')
    c = conn.cursor()
    c.execute('INSERT INTO players (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def get_player_name():
    conn = sqlite3.connect('pixel_racer.db')
    c = conn.cursor()
    c.execute('SELECT name FROM players ORDER BY id DESC LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result[0] if result else 'Player 1'