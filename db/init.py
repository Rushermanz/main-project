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
    c.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            track_id TEXT NOT NULL,
            player_id INTEGER NOT NULL,
            time REAL NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id)
        ) 
    ''')
    conn.commit()
    conn.close()

create_database()