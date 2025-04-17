# File: migrate_leaderboard.py

import sqlite3
import sys

DB_PATH = "pixel_racer.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Disable FKs so we can do the dance
    cur.execute("PRAGMA foreign_keys = OFF;")

    # If an old migrate half‐ran, drop any leftover
    cur.execute("DROP TABLE IF EXISTS leaderboard_new;")

    # Create the new leaderboard with exactly the columns we want
    cur.execute("""
    CREATE TABLE leaderboard_new (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id    INTEGER NOT NULL,
        player_id   INTEGER NOT NULL,
        lap_time    REAL    NOT NULL,
        FOREIGN KEY(player_id) REFERENCES players(id)
    );
    """)

    # Copy old data across (old leaderboard had columns: track_id, player_id, time)
    cur.execute("""
    INSERT INTO leaderboard_new (track_id, player_id, lap_time)
    SELECT track_id,
           player_id,
           CAST(time AS REAL)
      FROM leaderboard;
    """)

    # Drop old, rename new → leaderboard
    cur.execute("DROP TABLE leaderboard;")
    cur.execute("ALTER TABLE leaderboard_new RENAME TO leaderboard;")

    # Re‐enable FKs
    cur.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()

    print("✅ Migration complete: leaderboard(track_id, player_id, lap_time)")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print("❌ Migration failed:", e, file=sys.stderr)
        sys.exit(1)
