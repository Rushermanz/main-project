import sqlite3

def save_player_name(name):
    conn = sqlite3.connect('pixel_racer.db')
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
