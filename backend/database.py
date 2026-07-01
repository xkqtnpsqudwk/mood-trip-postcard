"""SQLite database setup and seeding for Mood Trip Postcard."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            mood_tags TEXT NOT NULL,
            image_url TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS postcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            place_name TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            review TEXT NOT NULL,
            next_recommendation TEXT,
            image_base64 TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    try:
        cursor.execute("ALTER TABLE postcards ADD COLUMN image_base64 TEXT")
    except sqlite3.OperationalError:
        pass  # column already exists on a pre-existing database

    conn.commit()

    cursor.execute("SELECT COUNT(*) AS count FROM places")
    if cursor.fetchone()["count"] == 0:
        _seed_places(cursor)
        conn.commit()

    conn.close()


def _seed_places(cursor: sqlite3.Cursor) -> None:
    places = [
        # Paris
        (
            "Paris",
            "Seine Riverside",
            "A gentle walk along the Seine at dusk, where the city's lights shimmer on the water.",
            "calm, romantic, reflective, nostalgic",
            None,
        ),
        (
            "Paris",
            "Pont des Arts",
            "A pedestrian bridge famed for quiet sunset views and street musicians.",
            "romantic, hopeful, dreamy, peaceful",
            None,
        ),
        (
            "Paris",
            "Montmartre",
            "Cobblestone streets and artists' squares atop the city, full of bohemian energy.",
            "inspired, free-spirited, joyful, adventurous",
            None,
        ),
        (
            "Paris",
            "Luxembourg Gardens",
            "Manicured gardens where Parisians relax among fountains and chestnut trees.",
            "serene, restorative, content, slow-paced",
            None,
        ),
        (
            "Paris",
            "Pere Lachaise Cemetery",
            "A quiet, tree-lined cemetery resting place of legends, ideal for solitary reflection.",
            "melancholy, reflective, solitary, contemplative",
            None,
        ),
        # Seoul
        (
            "Seoul",
            "Han River Park",
            "Wide green riverbanks where locals picnic and watch the sunset over the water.",
            "relaxed, hopeful, social, refreshing",
            None,
        ),
        (
            "Seoul",
            "Bukchon Hanok Village",
            "Traditional hanok houses lining narrow alleys with a view over the old city.",
            "nostalgic, calm, grounded, timeless",
            None,
        ),
        (
            "Seoul",
            "Hongdae",
            "A buzzing youth district full of street performers, music, and indie cafes.",
            "energetic, joyful, free-spirited, curious",
            None,
        ),
        (
            "Seoul",
            "Namsan Tower",
            "A hilltop tower with panoramic night views of the city skyline.",
            "romantic, hopeful, awe-struck, dreamy",
            None,
        ),
        (
            "Seoul",
            "Seonyudo Park",
            "A serene island park on the Han River, once a water treatment plant turned garden.",
            "peaceful, restorative, introspective, quiet",
            None,
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO places (city, name, description, mood_tags, image_url)
        VALUES (?, ?, ?, ?, ?)
        """,
        places,
    )


def get_places_by_city(city: str) -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM places WHERE city = ? COLLATE NOCASE", (city,)
    ).fetchall()
    conn.close()
    return rows


def get_all_places() -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM places").fetchall()
    conn.close()
    return rows


def insert_postcard(
    city: str,
    place_name: str,
    title: str,
    message: str,
    review: str,
    next_recommendation: str,
    image_base64: str | None = None,
) -> sqlite3.Row:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO postcards (city, place_name, title, message, review, next_recommendation, image_base64)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (city, place_name, title, message, review, next_recommendation, image_base64),
    )
    conn.commit()
    postcard_id = cursor.lastrowid
    row = conn.execute(
        "SELECT * FROM postcards WHERE id = ?", (postcard_id,)
    ).fetchone()
    conn.close()
    return row


def get_all_postcards() -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM postcards ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return rows
