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
            name_ko TEXT,
            description_ko TEXT,
            mood_tags_ko TEXT,
            image_url TEXT
        )
        """
    )
    for column in ("name_ko", "description_ko", "mood_tags_ko"):
        try:
            cursor.execute(f"ALTER TABLE places ADD COLUMN {column} TEXT")
        except sqlite3.OperationalError:
            pass  # column already exists on a pre-existing database

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
    for column in ("image_base64 TEXT", "place_id INTEGER"):
        try:
            cursor.execute(f"ALTER TABLE postcards ADD COLUMN {column}")
        except sqlite3.OperationalError:
            pass  # column already exists on a pre-existing database

    conn.commit()

    cursor.execute(
        "SELECT COUNT(*) AS count FROM places WHERE name_ko IS NULL OR name_ko = ''"
    )
    needs_reseed = cursor.fetchone()["count"] > 0
    if needs_reseed:
        cursor.execute("DELETE FROM places")
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
            "센 강변",
            "노을 질 무렵 센 강을 따라 걷다 보면, 도시의 불빛이 물결 위에 아른거려요.",
            "차분함, 로맨틱함, 사색적임, 그리움",
            None,
        ),
        (
            "Paris",
            "Pont des Arts",
            "A pedestrian bridge famed for quiet sunset views and street musicians.",
            "romantic, hopeful, dreamy, peaceful",
            "퐁데자르 다리",
            "고요한 노을 풍경과 거리 음악가들로 유명한 보행자 다리예요.",
            "로맨틱함, 희망적임, 몽환적임, 평화로움",
            None,
        ),
        (
            "Paris",
            "Montmartre",
            "Cobblestone streets and artists' squares atop the city, full of bohemian energy.",
            "inspired, free-spirited, joyful, adventurous",
            "몽마르트르",
            "도시가 내려다보이는 언덕 위, 예술가들의 광장과 자갈길이 자유로운 에너지로 가득해요.",
            "영감을 주는, 자유로운, 즐거운, 모험적인",
            None,
        ),
        (
            "Paris",
            "Luxembourg Gardens",
            "Manicured gardens where Parisians relax among fountains and chestnut trees.",
            "serene, restorative, content, slow-paced",
            "뤽상부르 공원",
            "파리지앵들이 분수와 밤나무 사이에서 여유를 즐기는 잘 가꿔진 정원이에요.",
            "고요함, 회복되는, 만족스러운, 느긋함",
            None,
        ),
        (
            "Paris",
            "Pere Lachaise Cemetery",
            "A quiet, tree-lined cemetery resting place of legends, ideal for solitary reflection.",
            "melancholy, reflective, solitary, contemplative",
            "페르 라셰즈 공동묘지",
            "나무가 우거진 조용한 공동묘지로, 전설적인 인물들이 잠든 곳이자 홀로 사색하기 좋은 장소예요.",
            "우울함, 사색적임, 고독함, 명상적인",
            None,
        ),
        # Seoul
        (
            "Seoul",
            "Han River Park",
            "Wide green riverbanks where locals picnic and watch the sunset over the water.",
            "relaxed, hopeful, social, refreshing",
            "한강공원",
            "현지인들이 피크닉을 즐기고 노을을 바라보는 넓고 푸른 강변이에요.",
            "여유로운, 희망적인, 사교적인, 상쾌한",
            None,
        ),
        (
            "Seoul",
            "Bukchon Hanok Village",
            "Traditional hanok houses lining narrow alleys with a view over the old city.",
            "nostalgic, calm, grounded, timeless",
            "북촌 한옥마을",
            "좁은 골목을 따라 늘어선 전통 한옥과 옛 도시가 내려다보이는 풍경이에요.",
            "그리움, 차분함, 안정적인, 시간을 초월한",
            None,
        ),
        (
            "Seoul",
            "Hongdae",
            "A buzzing youth district full of street performers, music, and indie cafes.",
            "energetic, joyful, free-spirited, curious",
            "홍대",
            "거리 공연과 음악, 인디 카페로 가득한 활기찬 젊음의 거리예요.",
            "활기찬, 즐거운, 자유로운, 호기심 많은",
            None,
        ),
        (
            "Seoul",
            "Namsan Tower",
            "A hilltop tower with panoramic night views of the city skyline.",
            "romantic, hopeful, awe-struck, dreamy",
            "남산타워",
            "도시의 야경을 한눈에 담을 수 있는 언덕 위의 타워예요.",
            "로맨틱함, 희망적임, 경이로운, 몽환적인",
            None,
        ),
        (
            "Seoul",
            "Seonyudo Park",
            "A serene island park on the Han River, once a water treatment plant turned garden.",
            "peaceful, restorative, introspective, quiet",
            "선유도공원",
            "한강 위의 고요한 섬 공원으로, 정수장이었던 곳이 정원으로 탈바꿈했어요.",
            "평화로운, 회복되는, 성찰적인, 고요한",
            None,
        ),
    ]
    cursor.executemany(
        """
        INSERT INTO places (city, name, description, mood_tags, name_ko, description_ko, mood_tags_ko, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
    image_base64: str | None = None,
    place_id: int | None = None,
) -> sqlite3.Row:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO postcards (city, place_name, title, message, review, image_base64, place_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (city, place_name, title, message, review, image_base64, place_id),
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
