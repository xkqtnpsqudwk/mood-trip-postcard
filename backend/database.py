"""SQLite database setup and seeding for MoodTrip."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"

SESSION_TTL_DAYS = 30


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
        CREATE TABLE IF NOT EXISTS postcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            place_name TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            review TEXT NOT NULL,
            image_base64 TEXT,
            place_id INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    for column in (
        "image_base64 TEXT",
        "image_path TEXT",
        "place_id INTEGER",
        "place_name_en TEXT",
        "place_name_ko TEXT",
        "title_en TEXT",
        "message_en TEXT",
        "title_ko TEXT",
        "message_ko TEXT",
        "next_place_id INTEGER",
        "next_place_name_en TEXT",
        "next_place_name_ko TEXT",
        "trip_id TEXT",
        "user_id INTEGER",
        "mood_text TEXT",
        "clue_en TEXT",
        "clue_ko TEXT",
    ):
        try:
            cursor.execute(f"ALTER TABLE postcards ADD COLUMN {column}")
        except sqlite3.OperationalError:
            pass  # column already exists on a pre-existing database

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    # Only prune sessions past their expiry on startup; a server restart no
    # longer logs everyone out (see SESSION_TTL_DAYS / get_user_by_token).
    cursor.execute(
        f"DELETE FROM sessions WHERE created_at <= datetime('now', '-{SESSION_TTL_DAYS} days')"
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            style_text TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    for column in ("style_text TEXT",):
        try:
            cursor.execute(f"ALTER TABLE user_preferences ADD COLUMN {column}")
        except sqlite3.OperationalError:
            pass  # column already exists on a pre-existing database

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_postcards_user_created "
        "ON postcards(user_id, created_at)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_postcards_trip_id ON postcards(trip_id)"
    )

    conn.commit()
    conn.close()


def insert_postcard(
    city: str,
    place_name: str,
    title: str,
    message: str,
    review: str,
    trip_id: str,
    image_base64: str | None = None,
    image_path: str | None = None,
    place_name_en: str | None = None,
    place_name_ko: str | None = None,
    title_en: str | None = None,
    message_en: str | None = None,
    title_ko: str | None = None,
    message_ko: str | None = None,
    next_place_name_en: str | None = None,
    next_place_name_ko: str | None = None,
    user_id: int | None = None,
    mood_text: str | None = None,
    clue_en: str | None = None,
    clue_ko: str | None = None,
) -> sqlite3.Row:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO postcards (
            city, place_name, title, message, review, image_base64, image_path,
            place_name_en, place_name_ko, title_en, message_en, title_ko, message_ko,
            next_place_name_en, next_place_name_ko, trip_id,
            user_id, mood_text, clue_en, clue_ko
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            city,
            place_name,
            title,
            message,
            review,
            image_base64,
            image_path,
            place_name_en or place_name,
            place_name_ko or place_name,
            title_en or title,
            message_en or message,
            title_ko or title,
            message_ko or message,
            next_place_name_en,
            next_place_name_ko,
            trip_id,
            user_id,
            mood_text,
            clue_en,
            clue_ko,
        ),
    )
    conn.commit()
    postcard_id = cursor.lastrowid
    row = conn.execute(
        "SELECT * FROM postcards WHERE id = ?", (postcard_id,)
    ).fetchone()
    conn.close()
    return row


def get_postcard_by_id(postcard_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM postcards WHERE id = ?", (postcard_id,)).fetchone()
    conn.close()
    return row


def set_postcard_image_path(postcard_id: int, image_path: str) -> sqlite3.Row:
    """Point a postcard at its on-disk image file, clearing any legacy inline blob."""
    conn = get_connection()
    conn.execute(
        "UPDATE postcards SET image_path = ?, image_base64 = NULL WHERE id = ?",
        (image_path, postcard_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM postcards WHERE id = ?", (postcard_id,)).fetchone()
    conn.close()
    return row


def update_postcard_next_place(
    postcard_id: int,
    next_place_name_en: str,
    next_place_name_ko: str,
) -> sqlite3.Row:
    conn = get_connection()
    conn.execute(
        """
        UPDATE postcards
        SET next_place_name_en = ?, next_place_name_ko = ?
        WHERE id = ?
        """,
        (next_place_name_en, next_place_name_ko, postcard_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM postcards WHERE id = ?", (postcard_id,)).fetchone()
    conn.close()
    return row


def get_all_postcards(user_id: int | None = None) -> list[sqlite3.Row]:
    conn = get_connection()
    if user_id is None:
        rows = conn.execute(
            "SELECT * FROM postcards WHERE user_id IS NULL ORDER BY created_at DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM postcards WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    conn.close()
    return rows


def get_postcards_by_trip(trip_id: str, user_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM postcards
        WHERE trip_id = ? AND user_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (trip_id, user_id),
    ).fetchall()
    conn.close()
    return rows


def get_all_postcard_image_paths() -> set[str]:
    """Every image_path still referenced by a postcard row, for orphan cleanup."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT image_path FROM postcards WHERE image_path IS NOT NULL"
    ).fetchall()
    conn.close()
    return {row["image_path"] for row in rows}


def create_user(username: str, password_hash: str) -> sqlite3.Row:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def get_user_by_username(username: str) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,)
    ).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def create_session(token: str, user_id: int) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id)
    )
    conn.commit()
    conn.close()


def get_user_by_token(token: str) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        f"""
        SELECT users.* FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
          AND sessions.created_at > datetime('now', '-{SESSION_TTL_DAYS} days')
        """,
        (token,),
    ).fetchone()
    conn.close()
    return row


def delete_session(token: str) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def get_user_preferences(user_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row


def upsert_user_preferences(user_id: int, style_text: str) -> sqlite3.Row:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO user_preferences (user_id, style_text, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            style_text = excluded.style_text,
            updated_at = excluded.updated_at
        """,
        (user_id, style_text),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row
