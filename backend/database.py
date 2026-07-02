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
    for column in (
        "image_base64 TEXT",
        "place_id INTEGER",
        "title_en TEXT",
        "message_en TEXT",
        "title_ko TEXT",
        "message_ko TEXT",
    ):
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
        (
            "Paris",
            "Tuileries Garden",
            "A formal garden between the Louvre and Place de la Concorde, ideal for slow walks and people-watching.",
            "elegant, calm, reflective, leisurely",
            "튈르리 정원",
            "루브르와 콩코르드 광장 사이에 있는 정원으로, 천천히 걷고 사람들을 바라보기 좋은 곳이에요.",
            "우아한, 차분함, 사색적임, 여유로운",
            None,
        ),
        (
            "Paris",
            "Canal Saint-Martin",
            "A laid-back canal district with iron footbridges, cafes, and a local evening atmosphere.",
            "relaxed, social, curious, urban",
            "생마르탱 운하",
            "철제 다리와 카페가 이어지는 운하 거리로, 현지의 저녁 분위기를 느끼기 좋아요.",
            "여유로운, 사교적인, 호기심 많은, 도시적인",
            None,
        ),
        (
            "Paris",
            "Sainte-Chapelle",
            "A jewel-like chapel filled with stained glass light, suited to awe and quiet wonder.",
            "awe-struck, peaceful, inspired, contemplative",
            "생트샤펠",
            "스테인드글라스 빛으로 가득한 예배당으로, 조용한 경이로움을 느끼기 좋은 장소예요.",
            "경이로운, 평화로운, 영감을 주는, 명상적인",
            None,
        ),
        (
            "Paris",
            "Le Marais",
            "A historic neighborhood of galleries, boutiques, courtyards, and lively side streets.",
            "curious, stylish, lively, inspired",
            "마레 지구",
            "갤러리와 상점, 안뜰, 활기찬 골목이 어우러진 역사적인 동네예요.",
            "호기심 많은, 세련된, 활기찬, 영감을 주는",
            None,
        ),
        (
            "Paris",
            "Parc des Buttes-Chaumont",
            "A dramatic hill park with cliffs, bridges, and wide views over the city.",
            "adventurous, refreshing, free-spirited, scenic",
            "뷔트 쇼몽 공원",
            "절벽과 다리, 도시 전망이 있는 언덕 공원으로, 상쾌하게 걷기 좋은 곳이에요.",
            "모험적인, 상쾌한, 자유로운, 풍경이 좋은",
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
        (
            "Seoul",
            "Seoul Forest",
            "A spacious park with trees, lawns, and quiet paths that feel restorative inside the city.",
            "restorative, peaceful, refreshing, grounded",
            "서울숲",
            "나무와 잔디, 조용한 산책로가 있는 넓은 공원으로, 도심 속에서 회복감을 느끼기 좋아요.",
            "회복되는, 평화로운, 상쾌한, 안정적인",
            None,
        ),
        (
            "Seoul",
            "Ikseon-dong Hanok Street",
            "A compact neighborhood of old hanok alleys, small shops, and warm cafe lights.",
            "nostalgic, cozy, curious, romantic",
            "익선동 한옥거리",
            "오래된 한옥 골목과 작은 상점, 따뜻한 카페 불빛이 이어지는 아담한 동네예요.",
            "그리움, 아늑한, 호기심 많은, 로맨틱함",
            None,
        ),
        (
            "Seoul",
            "Cheonggyecheon Stream",
            "A restored stream path through downtown Seoul, good for a quiet walk between busy streets.",
            "calm, reflective, urban, refreshing",
            "청계천",
            "도심 한가운데 이어지는 복원 하천 산책로로, 바쁜 거리 사이에서 조용히 걷기 좋아요.",
            "차분함, 사색적임, 도시적인, 상쾌한",
            None,
        ),
        (
            "Seoul",
            "Gyeongui Line Forest Park",
            "A linear park built along old railway tracks, with cafes, benches, and a gentle neighborhood mood.",
            "relaxed, social, slow-paced, content",
            "경의선숲길",
            "옛 철길을 따라 조성된 공원으로, 카페와 벤치가 이어지는 느긋한 동네 분위기가 있어요.",
            "여유로운, 사교적인, 느긋함, 만족스러운",
            None,
        ),
        (
            "Seoul",
            "Dongdaemun Design Plaza",
            "A futuristic cultural landmark with sweeping curves, night lights, and design exhibitions.",
            "curious, inspired, futuristic, energetic",
            "동대문디자인플라자",
            "곡선형 건축과 야간 조명, 전시가 어우러진 미래적인 문화 공간이에요.",
            "호기심 많은, 영감을 주는, 미래적인, 활기찬",
            None,
        ),
    ]
    existing = {
        (row["city"].lower(), row["name"].lower())
        for row in cursor.execute("SELECT city, name FROM places").fetchall()
    }
    places = [
        place
        for place in places
        if (place[0].lower(), place[1].lower()) not in existing
    ]
    if not places:
        return
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
    title_en: str | None = None,
    message_en: str | None = None,
    title_ko: str | None = None,
    message_ko: str | None = None,
) -> sqlite3.Row:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO postcards (
            city, place_name, title, message, review, image_base64, place_id,
            title_en, message_en, title_ko, message_ko
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            city,
            place_name,
            title,
            message,
            review,
            image_base64,
            place_id,
            title_en or title,
            message_en or message,
            title_ko or title,
            message_ko or message,
        ),
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
