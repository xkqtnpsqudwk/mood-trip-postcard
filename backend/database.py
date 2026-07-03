"""SQLite database setup and seeding for MoodTrip."""
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
    for column in (
        "name_ko TEXT",
        "description_ko TEXT",
        "mood_tags_ko TEXT",
        "type TEXT",
        "type_ko TEXT",
        "duration TEXT",
        "preference_tags TEXT",
        "preference_tags_ko TEXT",
        "situation_tags TEXT",
        "situation_tags_ko TEXT",
        "avoid_tags TEXT",
        "avoid_tags_ko TEXT",
        "reason TEXT",
        "reason_ko TEXT",
    ):
        try:
            cursor.execute(f"ALTER TABLE places ADD COLUMN {column}")
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
        "next_place_id INTEGER",
        "next_place_name_en TEXT",
        "next_place_name_ko TEXT",
        "trip_id TEXT",
        "user_id INTEGER",
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
    # Sessions are cleared every time the app starts up, so a server restart
    # always logs everyone out rather than leaving stale tokens around.
    cursor.execute("DELETE FROM sessions")

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

    conn.commit()

    cursor.execute(
        "SELECT COUNT(*) AS count FROM places "
        "WHERE name_ko IS NULL OR name_ko = '' OR type IS NULL OR type = ''"
    )
    needs_reseed = cursor.fetchone()["count"] > 0
    if needs_reseed:
        cursor.execute("DELETE FROM places")
    _seed_places(cursor)
    conn.commit()

    conn.close()


# Tag vocabulary shared with the frontend's structured input options:
#
# situation_tags: solo, friends, couple, family (companions),
#                 near, moderate_walk, far_walk (mobility),
#                 indoor, outdoor (environment)
# preference_tags: walking, photo, cafe, exhibition, shopping, reading,
#                   night_view, history (activities); quiet, sentimental,
#                   lively, exotic, natural, local, artistic (atmosphere);
#                   riverside, park, alley, bookstore, gallery, market,
#                   viewpoint (preferred place types)
# avoid_tags: crowded, far, expensive, complex_route, long_wait,
#             long_distance, too_touristy
# duration: under_30min, 1h, 2_3h, half_day

_PLACES = [
    {
        "city": "Paris",
        "name": "Seine Riverside",
        "description": "A gentle walk along the Seine at dusk, where the city's lights shimmer on the water.",
        "description_ko": "노을 질 무렵 센 강을 따라 걷다 보면, 도시의 불빛이 물결 위에 아른거려요.",
        "mood_tags": "calm, romantic, reflective, nostalgic",
        "mood_tags_ko": "차분함, 로맨틱함, 사색적임, 그리움",
        "name_ko": "센 강변",
        "type": "Riverside walk",
        "type_ko": "강변 산책로",
        "duration": "1h,2_3h",
        "preference_tags": "walking,riverside,photo,quiet",
        "preference_tags_ko": "산책,강변,사진,조용한",
        "situation_tags": "solo,couple,moderate_walk,outdoor",
        "situation_tags_ko": "혼자,연인과,조금 걸어도 괜찮음,야외 선호",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A quiet riverside path perfect for slow walking and untangling your thoughts, without the crowds of indoor tourist sites.",
        "reason_ko": "복잡한 실내 관광지보다 천천히 걸으며 생각을 정리하기 좋은 조용한 강변길이에요.",
    },
    {
        "city": "Paris",
        "name": "Pont des Arts",
        "description": "A pedestrian bridge famed for quiet sunset views and street musicians.",
        "description_ko": "고요한 노을 풍경과 거리 음악가들로 유명한 보행자 다리예요.",
        "mood_tags": "romantic, hopeful, dreamy, peaceful",
        "mood_tags_ko": "로맨틱함, 희망적임, 몽환적임, 평화로움",
        "name_ko": "퐁데자르 다리",
        "type": "Bridge",
        "type_ko": "다리",
        "duration": "under_30min,1h",
        "preference_tags": "photo,night_view,riverside,quiet",
        "preference_tags_ko": "사진,야경,강변,조용한",
        "situation_tags": "couple,solo,near,outdoor",
        "situation_tags_ko": "연인과,혼자,가까운 곳 위주,야외 선호",
        "avoid_tags": "crowded",
        "avoid_tags_ko": "사람 많은 곳",
        "reason": "A pedestrian bridge known for quiet sunset views and street musicians, ideal for a short romantic pause.",
        "reason_ko": "고요한 노을 풍경과 거리 음악가로 유명한 다리로, 짧게 들르기 좋은 로맨틱한 장소예요.",
    },
    {
        "city": "Paris",
        "name": "Montmartre",
        "description": "Cobblestone streets and artists' squares atop the city, full of bohemian energy.",
        "description_ko": "도시가 내려다보이는 언덕 위, 예술가들의 광장과 자갈길이 자유로운 에너지로 가득해요.",
        "mood_tags": "inspired, free-spirited, joyful, adventurous",
        "mood_tags_ko": "영감을 주는, 자유로운, 즐거운, 모험적인",
        "name_ko": "몽마르트르",
        "type": "Historic hill district",
        "type_ko": "예술가 언덕 마을",
        "duration": "2_3h,half_day",
        "preference_tags": "walking,photo,exhibition,shopping",
        "preference_tags_ko": "산책,사진,전시,쇼핑",
        "situation_tags": "friends,family,far_walk,outdoor",
        "situation_tags_ko": "친구와,가족과,오래 걸어도 괜찮음,야외 선호",
        "avoid_tags": "crowded,too_touristy",
        "avoid_tags_ko": "사람 많은 곳,너무 관광지스러운 곳",
        "reason": "Cobblestone streets and artists' squares full of bohemian energy, great when you want lively inspiration rather than quiet.",
        "reason_ko": "자갈길과 예술가 광장이 자유로운 에너지로 가득한 곳으로, 조용함보다 활기찬 영감을 원할 때 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Luxembourg Gardens",
        "description": "Manicured gardens where Parisians relax among fountains and chestnut trees.",
        "description_ko": "파리지앵들이 분수와 밤나무 사이에서 여유를 즐기는 잘 가꿔진 정원이에요.",
        "mood_tags": "serene, restorative, content, slow-paced",
        "mood_tags_ko": "고요함, 회복되는, 만족스러운, 느긋함",
        "name_ko": "뤽상부르 공원",
        "type": "Garden",
        "type_ko": "정원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,reading,cafe",
        "preference_tags_ko": "산책,독서,카페",
        "situation_tags": "solo,friends,family,near,outdoor",
        "situation_tags_ko": "혼자,친구와,가족과,가까운 곳 위주,야외 선호",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "Manicured gardens where locals relax among fountains and chestnut trees, easy to enjoy solo or with company.",
        "reason_ko": "파리지앵들이 분수와 밤나무 사이에서 쉬어가는 정원으로, 혼자든 함께든 부담 없이 즐기기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Pere Lachaise Cemetery",
        "description": "A quiet, tree-lined cemetery resting place of legends, ideal for solitary reflection.",
        "description_ko": "나무가 우거진 조용한 공동묘지로, 전설적인 인물들이 잠든 곳이자 홀로 사색하기 좋은 장소예요.",
        "mood_tags": "melancholy, reflective, solitary, contemplative",
        "mood_tags_ko": "우울함, 사색적임, 고독함, 명상적인",
        "name_ko": "페르 라셰즈 공동묘지",
        "type": "Historic cemetery",
        "type_ko": "역사적인 묘지",
        "duration": "1h,2_3h",
        "preference_tags": "walking,history,reading",
        "preference_tags_ko": "산책,역사 탐방,독서",
        "situation_tags": "solo,moderate_walk,outdoor",
        "situation_tags_ko": "혼자,조금 걸어도 괜찮음,야외 선호",
        "avoid_tags": "complex_route",
        "avoid_tags_ko": "복잡한 동선",
        "reason": "A quiet, tree-lined resting place of legends, ideal for solitary reflection away from busy streets.",
        "reason_ko": "나무가 우거진 조용한 곳으로, 번잡한 거리에서 벗어나 홀로 사색하기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Tuileries Garden",
        "description": "A formal garden between the Louvre and Place de la Concorde, ideal for slow walks and people-watching.",
        "description_ko": "루브르와 콩코르드 광장 사이에 있는 정원으로, 천천히 걷고 사람들을 바라보기 좋은 곳이에요.",
        "mood_tags": "elegant, calm, reflective, leisurely",
        "mood_tags_ko": "우아한, 차분함, 사색적임, 여유로운",
        "name_ko": "튈르리 정원",
        "type": "Garden",
        "type_ko": "정원",
        "duration": "under_30min,1h",
        "preference_tags": "walking,photo",
        "preference_tags_ko": "산책,사진",
        "situation_tags": "solo,couple,family,near,outdoor",
        "situation_tags_ko": "혼자,연인과,가족과,가까운 곳 위주,야외 선호",
        "avoid_tags": "crowded",
        "avoid_tags_ko": "사람 많은 곳",
        "reason": "A formal garden between the Louvre and Place de la Concorde, good for slow walks and people-watching.",
        "reason_ko": "루브르와 콩코르드 광장 사이의 정원으로, 천천히 걷고 사람 구경하기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Canal Saint-Martin",
        "description": "A laid-back canal district with iron footbridges, cafes, and a local evening atmosphere.",
        "description_ko": "철제 다리와 카페가 이어지는 운하 거리로, 현지의 저녁 분위기를 느끼기 좋아요.",
        "mood_tags": "relaxed, social, curious, urban",
        "mood_tags_ko": "여유로운, 사교적인, 호기심 많은, 도시적인",
        "name_ko": "생마르탱 운하",
        "type": "Canal district",
        "type_ko": "운하 거리",
        "duration": "1h,2_3h",
        "preference_tags": "walking,cafe,shopping",
        "preference_tags_ko": "산책,카페,쇼핑",
        "situation_tags": "friends,couple,moderate_walk,outdoor",
        "situation_tags_ko": "친구와,연인과,조금 걸어도 괜찮음,야외 선호",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A laid-back canal district with iron footbridges and cafes, great for feeling the local evening mood with company.",
        "reason_ko": "철제 다리와 카페가 이어지는 운하 거리로, 친구나 연인과 현지 저녁 분위기를 느끼기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Sainte-Chapelle",
        "description": "A jewel-like chapel filled with stained glass light, suited to awe and quiet wonder.",
        "description_ko": "스테인드글라스 빛으로 가득한 예배당으로, 조용한 경이로움을 느끼기 좋은 장소예요.",
        "mood_tags": "awe-struck, peaceful, inspired, contemplative",
        "mood_tags_ko": "경이로운, 평화로운, 영감을 주는, 명상적인",
        "name_ko": "생트샤펠",
        "type": "Chapel",
        "type_ko": "예배당",
        "duration": "under_30min,1h",
        "preference_tags": "exhibition,photo,quiet",
        "preference_tags_ko": "전시,사진,조용한",
        "situation_tags": "solo,couple,indoor,near",
        "situation_tags_ko": "혼자,연인과,실내 선호,가까운 곳 위주",
        "avoid_tags": "crowded,long_wait",
        "avoid_tags_ko": "사람 많은 곳,긴 대기",
        "reason": "A jewel-like chapel filled with stained glass light, suited to quiet awe rather than a quick glance.",
        "reason_ko": "스테인드글라스 빛으로 가득한 예배당으로, 잠깐 스치기보다 조용히 경이로움을 느끼기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Le Marais",
        "description": "A historic neighborhood of galleries, boutiques, courtyards, and lively side streets.",
        "description_ko": "갤러리와 상점, 안뜰, 활기찬 골목이 어우러진 역사적인 동네예요.",
        "mood_tags": "curious, stylish, lively, inspired",
        "mood_tags_ko": "호기심 많은, 세련된, 활기찬, 영감을 주는",
        "name_ko": "마레 지구",
        "type": "Historic district",
        "type_ko": "역사적인 동네",
        "duration": "2_3h,half_day",
        "preference_tags": "shopping,exhibition,cafe,photo",
        "preference_tags_ko": "쇼핑,전시,카페,사진",
        "situation_tags": "friends,couple,moderate_walk,outdoor",
        "situation_tags_ko": "친구와,연인과,조금 걸어도 괜찮음,야외 선호",
        "avoid_tags": "crowded,expensive",
        "avoid_tags_ko": "사람 많은 곳,비싼 곳",
        "reason": "A historic neighborhood of galleries and boutiques, lively enough for curious wandering with friends.",
        "reason_ko": "갤러리와 상점이 어우러진 역사적인 동네로, 친구와 호기심 어린 산책을 하기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Parc des Buttes-Chaumont",
        "description": "A dramatic hill park with cliffs, bridges, and wide views over the city.",
        "description_ko": "절벽과 다리, 도시 전망이 있는 언덕 공원으로, 상쾌하게 걷기 좋은 곳이에요.",
        "mood_tags": "adventurous, refreshing, free-spirited, scenic",
        "mood_tags_ko": "모험적인, 상쾌한, 자유로운, 풍경이 좋은",
        "name_ko": "뷔트 쇼몽 공원",
        "type": "Hill park",
        "type_ko": "언덕 공원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,photo,night_view",
        "preference_tags_ko": "산책,사진,야경",
        "situation_tags": "solo,friends,far_walk,outdoor",
        "situation_tags_ko": "혼자,친구와,오래 걸어도 괜찮음,야외 선호",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A dramatic hill park with cliffs and wide views, refreshing when you want a bit of adventurous walking.",
        "reason_ko": "절벽과 도시 전망이 있는 언덕 공원으로, 조금 모험적으로 걷고 싶을 때 상쾌해요.",
    },
    {
        "city": "Paris",
        "name": "Musee d'Orsay",
        "description": "A grand former railway station turned museum, filled with Impressionist masterpieces under a glass ceiling.",
        "description_ko": "인상주의 걸작들로 가득한, 기차역을 개조한 웅장한 미술관이에요. 유리 천장 아래로 빛이 스며들어요.",
        "mood_tags": "inspired, awe-struck, contemplative, elegant",
        "mood_tags_ko": "영감을 주는, 경이로운, 명상적인, 우아한",
        "name_ko": "오르세 미술관",
        "type": "Art museum",
        "type_ko": "미술관",
        "duration": "1h,2_3h",
        "preference_tags": "exhibition,photo",
        "preference_tags_ko": "전시,사진",
        "avoid_tags": "crowded,long_wait,expensive",
        "avoid_tags_ko": "사람 많은 곳,긴 대기,비싼 곳",
        "reason": "A grand former railway station full of Impressionist masterpieces, worth the wait for a dose of quiet awe.",
        "reason_ko": "인상주의 걸작으로 가득한 웅장한 미술관으로, 조용한 경이로움을 느끼고 싶을 때 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Place des Vosges",
        "description": "The oldest planned square in Paris, a symmetrical garden ringed by arcaded townhouses.",
        "description_ko": "파리에서 가장 오래된 계획 광장으로, 아케이드 저택들에 둘러싸인 대칭적인 정원이에요.",
        "mood_tags": "elegant, calm, nostalgic, leisurely",
        "mood_tags_ko": "우아한, 차분함, 그리움, 여유로운",
        "name_ko": "보주 광장",
        "type": "Historic square",
        "type_ko": "역사적인 광장",
        "duration": "under_30min,1h",
        "preference_tags": "walking,photo",
        "preference_tags_ko": "산책,사진",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "Paris's oldest planned square, a symmetrical garden that feels like a quiet pause in the middle of the Marais.",
        "reason_ko": "파리에서 가장 오래된 계획 광장으로, 마레 지구 한가운데서 조용히 쉬어가기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Jardin des Plantes",
        "description": "A historic botanical garden with greenhouses, a small zoo, and quiet tree-lined paths.",
        "description_ko": "온실과 작은 동물원, 조용한 가로수길이 있는 역사적인 식물원이에요.",
        "mood_tags": "calm, natural, curious, restorative",
        "mood_tags_ko": "차분함, 자연적인, 호기심 많은, 회복되는",
        "name_ko": "식물원",
        "type": "Botanical garden",
        "type_ko": "식물원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,photo",
        "preference_tags_ko": "산책,사진",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A historic botanical garden with greenhouses and quiet paths, restorative when you want nature without leaving the city.",
        "reason_ko": "온실과 조용한 산책로가 있는 식물원으로, 도시를 벗어나지 않고도 자연 속에서 회복감을 느끼기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Rue Cremieux",
        "description": "A short pastel-colored residential street that feels like a postcard from another era.",
        "description_ko": "다른 시대에서 온 엽서 같은, 파스텔톤 집들이 늘어선 짧은 주택가 골목이에요.",
        "mood_tags": "cozy, playful, nostalgic, cheerful",
        "mood_tags_ko": "아늑한, 장난스러운, 그리움, 명랑한",
        "name_ko": "크레미외 거리",
        "type": "Photogenic alley",
        "type_ko": "포토제닉 골목",
        "duration": "under_30min",
        "preference_tags": "photo,walking",
        "preference_tags_ko": "사진,산책",
        "avoid_tags": "crowded",
        "avoid_tags_ko": "사람 많은 곳",
        "reason": "A short pastel-colored street that feels like a postcard, perfect for a quick, playful photo walk.",
        "reason_ko": "엽서 같은 파스텔톤 골목으로, 짧고 경쾌한 사진 산책에 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Passage des Panoramas",
        "description": "One of Paris's oldest covered arcades, lined with old shops, stamp dealers, and vintage restaurants.",
        "description_ko": "오래된 상점과 우표상, 빈티지 레스토랑이 늘어선 파리에서 가장 오래된 아케이드 중 하나예요.",
        "mood_tags": "nostalgic, curious, cozy, timeless",
        "mood_tags_ko": "그리움, 호기심 많은, 아늑한, 시간을 초월한",
        "name_ko": "파노라마 파사주",
        "type": "Covered arcade",
        "type_ko": "아케이드",
        "duration": "under_30min,1h",
        "preference_tags": "shopping,walking",
        "preference_tags_ko": "쇼핑,산책",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "One of Paris's oldest covered arcades, full of old shops - a rainy-day wander that feels like stepping back in time.",
        "reason_ko": "오래된 상점들이 늘어선 파리에서 가장 오래된 아케이드로, 시간을 거슬러 걷는 듯한 기분을 느끼기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Shakespeare and Company",
        "description": "A legendary English-language bookshop by Notre-Dame, crammed with books and literary history.",
        "description_ko": "노트르담 옆에 자리한 전설적인 영어 서점으로, 책과 문학의 역사로 가득해요.",
        "mood_tags": "cozy, inspired, nostalgic, curious",
        "mood_tags_ko": "아늑한, 영감을 주는, 그리움, 호기심 많은",
        "name_ko": "셰익스피어 앤 컴퍼니",
        "type": "Bookstore",
        "type_ko": "서점",
        "duration": "under_30min,1h",
        "preference_tags": "reading,photo",
        "preference_tags_ko": "독서,사진",
        "avoid_tags": "crowded,long_wait",
        "avoid_tags_ko": "사람 많은 곳,긴 대기",
        "reason": "A legendary bookshop packed with literary history, cozy for browsing when you want to slow down.",
        "reason_ko": "문학의 역사로 가득한 전설적인 서점으로, 천천히 둘러보며 마음을 가라앉히기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Butte aux Cailles",
        "description": "A hidden hillside village of narrow lanes, street art, and neighborhood bistros away from the tourist crowds.",
        "description_ko": "관광객이 적은, 좁은 골목과 거리 예술, 동네 비스트로가 있는 숨은 언덕 마을이에요.",
        "mood_tags": "local, relaxed, curious, urban",
        "mood_tags_ko": "로컬한, 여유로운, 호기심 많은, 도시적인",
        "name_ko": "뷔트 오 카이유",
        "type": "Local neighborhood",
        "type_ko": "로컬 동네",
        "duration": "1h,2_3h",
        "preference_tags": "walking,cafe,photo",
        "preference_tags_ko": "산책,카페,사진",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A hidden hillside village away from the crowds, full of street art and neighborhood charm.",
        "reason_ko": "관광객이 적은 숨은 언덕 마을로, 거리 예술과 동네 분위기를 느끼기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Parc Monceau",
        "description": "An elegant English-style park with follies, statues, and manicured lawns favored by locals.",
        "description_ko": "기암 조형물과 조각상, 잘 가꿔진 잔디밭이 있는 우아한 영국식 공원으로, 현지인들이 즐겨 찾아요.",
        "mood_tags": "elegant, peaceful, refreshing, leisurely",
        "mood_tags_ko": "우아한, 평화로운, 상쾌한, 여유로운",
        "name_ko": "몽소 공원",
        "type": "Park",
        "type_ko": "공원",
        "duration": "under_30min,1h",
        "preference_tags": "walking,photo",
        "preference_tags_ko": "산책,사진",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "An elegant English-style park with follies and lawns, a favorite quiet escape for locals.",
        "reason_ko": "기암 조형물과 잔디밭이 있는 우아한 공원으로, 현지인들이 조용히 쉬어가는 곳이에요.",
    },
    {
        "city": "Paris",
        "name": "Parc Montsouris",
        "description": "A large hillside park in the south of Paris with a lake, wide lawns, and a laid-back local feel.",
        "description_ko": "호수와 넓은 잔디밭이 있는 파리 남쪽의 큰 언덕 공원으로, 느긋한 동네 분위기가 있어요.",
        "mood_tags": "relaxed, natural, refreshing, social",
        "mood_tags_ko": "여유로운, 자연적인, 상쾌한, 사교적인",
        "name_ko": "몽수리 공원",
        "type": "Park",
        "type_ko": "공원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,photo",
        "preference_tags_ko": "산책,사진",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A large hillside park with a lake and wide lawns, laid-back and local rather than touristy.",
        "reason_ko": "호수와 넓은 잔디밭이 있는 큰 공원으로, 관광지보다는 동네 분위기를 느끼기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Belleville",
        "description": "A hilly, multicultural neighborhood with street art, a park view over the city, and an artsy edge.",
        "description_ko": "거리 예술과 도시 전망이 있는 언덕 위 다문화 동네로, 예술적인 매력이 있어요.",
        "mood_tags": "artistic, curious, local, energetic",
        "mood_tags_ko": "예술적인, 호기심 많은, 로컬한, 활기찬",
        "name_ko": "벨빌",
        "type": "Local neighborhood",
        "type_ko": "로컬 동네",
        "duration": "1h,2_3h",
        "preference_tags": "walking,photo,cafe",
        "preference_tags_ko": "산책,사진,카페",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A hilly, multicultural neighborhood with street art and a skyline view, full of artsy energy.",
        "reason_ko": "거리 예술과 도시 전망이 있는 언덕 위 동네로, 예술적인 에너지가 가득해요.",
    },
    {
        "city": "Paris",
        "name": "Ile Saint-Louis",
        "description": "A tranquil island in the Seine with quiet streets, ice cream shops, and river views on both sides.",
        "description_ko": "조용한 거리와 아이스크림 가게, 양쪽으로 강 전망이 펼쳐지는 센 강의 고요한 섬이에요.",
        "mood_tags": "calm, romantic, quiet, timeless",
        "mood_tags_ko": "차분함, 로맨틱함, 조용한, 시간을 초월한",
        "name_ko": "생루이 섬",
        "type": "River island",
        "type_ko": "강 위의 섬",
        "duration": "under_30min,1h",
        "preference_tags": "walking,riverside,photo",
        "preference_tags_ko": "산책,강변,사진",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A tranquil island with quiet streets and river views on both sides, calm just steps from Notre-Dame.",
        "reason_ko": "노트르담에서 몇 걸음만 걸으면 닿는 고요한 섬으로, 양쪽으로 강 전망을 즐기며 차분히 걷기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Trocadero Gardens",
        "description": "Terraced gardens facing the Eiffel Tower across the river, best known for its postcard skyline view.",
        "description_ko": "강 건너 에펠탑을 마주보는 계단식 정원으로, 엽서 같은 스카이라인 전망으로 유명해요.",
        "mood_tags": "awe-struck, romantic, scenic, joyful",
        "mood_tags_ko": "경이로운, 로맨틱함, 풍경이 좋은, 즐거운",
        "name_ko": "트로카데로 정원",
        "type": "Viewpoint garden",
        "type_ko": "전망 정원",
        "duration": "under_30min,1h",
        "preference_tags": "photo,walking",
        "preference_tags_ko": "사진,산책",
        "avoid_tags": "crowded,too_touristy",
        "avoid_tags_ko": "사람 많은 곳,너무 관광지스러운 곳",
        "reason": "Terraced gardens with the classic postcard view of the Eiffel Tower, worth it for a moment of awe.",
        "reason_ko": "에펠탑을 마주보는 엽서 같은 전망으로 유명한 정원으로, 잠깐의 경이로움을 느끼기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Village Saint-Paul",
        "description": "A maze of quiet courtyards packed with antique dealers, tucked away from the busy Marais streets.",
        "description_ko": "번잡한 마레 거리에서 벗어난, 골동품 상점들로 가득한 조용한 안뜰들의 미로예요.",
        "mood_tags": "quiet, nostalgic, curious, cozy",
        "mood_tags_ko": "조용한, 그리움, 호기심 많은, 아늑한",
        "name_ko": "빌라주 생폴",
        "type": "Antique courtyards",
        "type_ko": "골동품 안뜰",
        "duration": "under_30min,1h",
        "preference_tags": "walking,shopping",
        "preference_tags_ko": "산책,쇼핑",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A maze of quiet courtyards full of antiques, tucked away from the busy Marais streets.",
        "reason_ko": "번잡한 마레 거리에서 벗어난 조용한 안뜰의 미로로, 골동품을 구경하며 여유를 즐기기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Marche des Enfants Rouges",
        "description": "Paris's oldest covered market, a lively mix of food stalls from around the world.",
        "description_ko": "파리에서 가장 오래된 실내 시장으로, 세계 각국의 음식 노점이 활기차게 모여 있어요.",
        "mood_tags": "lively, social, curious, local",
        "mood_tags_ko": "활기찬, 사교적인, 호기심 많은, 로컬한",
        "name_ko": "앙팡 루주 시장",
        "type": "Food market",
        "type_ko": "식료품 시장",
        "duration": "under_30min,1h",
        "preference_tags": "shopping,cafe",
        "preference_tags_ko": "쇼핑,카페",
        "avoid_tags": "crowded,long_wait",
        "avoid_tags_ko": "사람 많은 곳,긴 대기",
        "reason": "Paris's oldest covered market, lively with food stalls from around the world - great for a social bite.",
        "reason_ko": "파리에서 가장 오래된 실내 시장으로, 세계 각국 음식을 활기차게 즐기며 사람들과 어울리기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Coulee Verte Rene-Dumont",
        "description": "An elevated park built on a disused railway viaduct, lined with roses and quiet city views.",
        "description_ko": "사용하지 않는 철도 고가 위에 조성된 공중 공원으로, 장미와 조용한 도시 전망이 이어져요.",
        "mood_tags": "peaceful, refreshing, romantic, slow-paced",
        "mood_tags_ko": "평화로운, 상쾌한, 로맨틱함, 느긋함",
        "name_ko": "쿨레 베르트 (고가 산책로)",
        "type": "Elevated park",
        "type_ko": "공중 공원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,photo",
        "preference_tags_ko": "산책,사진",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "An elevated park on an old railway viaduct, peaceful and above the noise of the streets below.",
        "reason_ko": "옛 철도 고가 위에 만들어진 공중 공원으로, 아래 거리의 소음에서 벗어나 평화롭게 걷기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Musee Rodin Garden",
        "description": "A sculpture garden around a grand townhouse, where Rodin's bronze works sit among roses.",
        "description_ko": "로댕의 청동 작품들이 장미 사이에 자리한, 웅장한 저택을 둘러싼 조각 정원이에요.",
        "mood_tags": "artistic, contemplative, serene, elegant",
        "mood_tags_ko": "예술적인, 명상적인, 고요함, 우아한",
        "name_ko": "로댕 미술관 정원",
        "type": "Sculpture garden",
        "type_ko": "조각 정원",
        "duration": "under_30min,1h",
        "preference_tags": "exhibition,walking,photo",
        "preference_tags_ko": "전시,산책,사진",
        "avoid_tags": "expensive",
        "avoid_tags_ko": "비싼 곳",
        "reason": "A sculpture garden where Rodin's bronze works sit among roses, contemplative and unhurried.",
        "reason_ko": "로댕의 청동 작품들이 장미 사이에 놓인 조각 정원으로, 여유롭게 명상하듯 거닐기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Parc de la Villette",
        "description": "A vast, futuristic park with a giant silver sphere, canal paths, and open lawns for wandering.",
        "description_ko": "거대한 은빛 구형 건축물과 운하 산책로, 넓은 잔디밭이 있는 거대하고 미래적인 공원이에요.",
        "mood_tags": "futuristic, free-spirited, energetic, curious",
        "mood_tags_ko": "미래적인, 자유로운, 활기찬, 호기심 많은",
        "name_ko": "라 빌레트 공원",
        "type": "Park",
        "type_ko": "공원",
        "duration": "1h,2_3h,half_day",
        "preference_tags": "walking,photo",
        "preference_tags_ko": "산책,사진",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A vast, futuristic park with a giant silver sphere and canal paths, great for free-spirited wandering.",
        "reason_ko": "거대한 은빛 구형 건축물과 운하 산책로가 있는 공원으로, 자유롭게 거닐기 좋아요.",
    },
    {
        "city": "Paris",
        "name": "Batignolles",
        "description": "A quiet, village-like neighborhood with an English-style park and a Saturday organic market.",
        "description_ko": "영국식 공원과 토요 유기농 시장이 있는, 마을처럼 조용한 동네예요.",
        "mood_tags": "quiet, local, cozy, relaxed",
        "mood_tags_ko": "조용한, 로컬한, 아늑한, 여유로운",
        "name_ko": "바티뇰",
        "type": "Local neighborhood",
        "type_ko": "로컬 동네",
        "duration": "1h,2_3h",
        "preference_tags": "walking,cafe",
        "preference_tags_ko": "산책,카페",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A quiet, village-like neighborhood with a park and market, far from the tourist trail.",
        "reason_ko": "관광객이 적은, 마을처럼 조용한 동네로, 공원과 시장에서 현지 분위기를 느끼기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Han River Park",
        "description": "Wide green riverbanks where locals picnic and watch the sunset over the water.",
        "description_ko": "현지인들이 피크닉을 즐기고 노을을 바라보는 넓고 푸른 강변이에요.",
        "mood_tags": "relaxed, hopeful, social, refreshing",
        "mood_tags_ko": "여유로운, 희망적인, 사교적인, 상쾌한",
        "name_ko": "한강공원",
        "type": "Riverside park",
        "type_ko": "강변 공원",
        "duration": "1h,2_3h,half_day",
        "preference_tags": "walking,photo,cafe",
        "preference_tags_ko": "산책,사진,카페",
        "situation_tags": "friends,family,couple,near,outdoor",
        "situation_tags_ko": "친구와,가족과,연인과,가까운 곳 위주,야외 선호",
        "avoid_tags": "crowded",
        "avoid_tags_ko": "사람 많은 곳",
        "reason": "Wide green riverbanks where locals picnic and watch the sunset, easy to enjoy with any company.",
        "reason_ko": "현지인들이 피크닉을 즐기고 노을을 바라보는 넓은 강변으로, 누구와 가도 부담 없어요.",
    },
    {
        "city": "Seoul",
        "name": "Bukchon Hanok Village",
        "description": "Traditional hanok houses lining narrow alleys with a view over the old city.",
        "description_ko": "좁은 골목을 따라 늘어선 전통 한옥과 옛 도시가 내려다보이는 풍경이에요.",
        "mood_tags": "nostalgic, calm, grounded, timeless",
        "mood_tags_ko": "그리움, 차분함, 안정적인, 시간을 초월한",
        "name_ko": "북촌 한옥마을",
        "type": "Historic alley",
        "type_ko": "전통 골목",
        "duration": "1h,2_3h",
        "preference_tags": "walking,photo,history",
        "preference_tags_ko": "산책,사진,역사 탐방",
        "situation_tags": "solo,couple,moderate_walk,outdoor",
        "situation_tags_ko": "혼자,연인과,조금 걸어도 괜찮음,야외 선호",
        "avoid_tags": "crowded,complex_route",
        "avoid_tags_ko": "사람 많은 곳,복잡한 동선",
        "reason": "Traditional hanok houses lining narrow alleys with a view over the old city, best at an unhurried pace.",
        "reason_ko": "좁은 골목을 따라 늘어선 전통 한옥과 옛 도시 풍경으로, 여유롭게 걸을 때 가장 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Hongdae",
        "description": "A buzzing youth district full of street performers, music, and indie cafes.",
        "description_ko": "거리 공연과 음악, 인디 카페로 가득한 활기찬 젊음의 거리예요.",
        "mood_tags": "energetic, joyful, free-spirited, curious",
        "mood_tags_ko": "활기찬, 즐거운, 자유로운, 호기심 많은",
        "name_ko": "홍대",
        "type": "Youth district",
        "type_ko": "젊음의 거리",
        "duration": "2_3h,half_day",
        "preference_tags": "shopping,cafe,night_view",
        "preference_tags_ko": "쇼핑,카페,야경",
        "situation_tags": "friends,moderate_walk,outdoor",
        "situation_tags_ko": "친구와,조금 걸어도 괜찮음,야외 선호",
        "avoid_tags": "crowded,long_wait",
        "avoid_tags_ko": "사람 많은 곳,긴 대기",
        "reason": "A buzzing youth district full of street performers and indie cafes, great for lively energy with friends.",
        "reason_ko": "거리 공연과 인디 카페로 가득한 활기찬 거리로, 친구와 에너지를 느끼기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Namsan Tower",
        "description": "A hilltop tower with panoramic night views of the city skyline.",
        "description_ko": "도시의 야경을 한눈에 담을 수 있는 언덕 위의 타워예요.",
        "mood_tags": "romantic, hopeful, awe-struck, dreamy",
        "mood_tags_ko": "로맨틱함, 희망적임, 경이로운, 몽환적인",
        "name_ko": "남산타워",
        "type": "Viewpoint tower",
        "type_ko": "전망대",
        "duration": "1h,2_3h",
        "preference_tags": "night_view,photo",
        "preference_tags_ko": "야경,사진",
        "situation_tags": "couple,friends,far_walk,outdoor",
        "situation_tags_ko": "연인과,친구와,오래 걸어도 괜찮음,야외 선호",
        "avoid_tags": "crowded,expensive",
        "avoid_tags_ko": "사람 많은 곳,비싼 곳",
        "reason": "A hilltop tower with panoramic night views, worth the climb for a romantic skyline moment.",
        "reason_ko": "도시 야경을 한눈에 담을 수 있는 언덕 위 타워로, 로맨틱한 순간을 위해 오를 만해요.",
    },
    {
        "city": "Seoul",
        "name": "Seonyudo Park",
        "description": "A serene island park on the Han River, once a water treatment plant turned garden.",
        "description_ko": "한강 위의 고요한 섬 공원으로, 정수장이었던 곳이 정원으로 탈바꿈했어요.",
        "mood_tags": "peaceful, restorative, introspective, quiet",
        "mood_tags_ko": "평화로운, 회복되는, 성찰적인, 고요한",
        "name_ko": "선유도공원",
        "type": "Island park",
        "type_ko": "섬 공원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,reading,photo",
        "preference_tags_ko": "산책,독서,사진",
        "situation_tags": "solo,near,outdoor",
        "situation_tags_ko": "혼자,가까운 곳 위주,야외 선호",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A serene island park on the Han River, once a water plant turned garden, quiet enough for solo reflection.",
        "reason_ko": "한강 위의 고요한 섬 공원으로, 혼자 사색하기 좋을 만큼 조용해요.",
    },
    {
        "city": "Seoul",
        "name": "Seoul Forest",
        "description": "A spacious park with trees, lawns, and quiet paths that feel restorative inside the city.",
        "description_ko": "나무와 잔디, 조용한 산책로가 있는 넓은 공원으로, 도심 속에서 회복감을 느끼기 좋아요.",
        "mood_tags": "restorative, peaceful, refreshing, grounded",
        "mood_tags_ko": "회복되는, 평화로운, 상쾌한, 안정적인",
        "name_ko": "서울숲",
        "type": "Urban park",
        "type_ko": "도심 공원",
        "duration": "1h,2_3h,half_day",
        "preference_tags": "walking,photo,cafe",
        "preference_tags_ko": "산책,사진,카페",
        "situation_tags": "solo,friends,family,moderate_walk,outdoor",
        "situation_tags_ko": "혼자,친구와,가족과,조금 걸어도 괜찮음,야외 선호",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A spacious park with trees and quiet paths that feel restorative even inside the city.",
        "reason_ko": "나무와 조용한 산책로가 있는 넓은 공원으로, 도심 속에서도 회복감을 느끼기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Ikseon-dong Hanok Street",
        "description": "A compact neighborhood of old hanok alleys, small shops, and warm cafe lights.",
        "description_ko": "오래된 한옥 골목과 작은 상점, 따뜻한 카페 불빛이 이어지는 아담한 동네예요.",
        "mood_tags": "nostalgic, cozy, curious, romantic",
        "mood_tags_ko": "그리움, 아늑한, 호기심 많은, 로맨틱함",
        "name_ko": "익선동 한옥거리",
        "type": "Historic alley",
        "type_ko": "전통 골목",
        "duration": "under_30min,1h",
        "preference_tags": "cafe,shopping,photo",
        "preference_tags_ko": "카페,쇼핑,사진",
        "situation_tags": "couple,friends,near,indoor",
        "situation_tags_ko": "연인과,친구와,가까운 곳 위주,실내 선호",
        "avoid_tags": "crowded,long_wait",
        "avoid_tags_ko": "사람 많은 곳,긴 대기",
        "reason": "A compact neighborhood of old hanok alleys and warm cafe lights, cozy for a short cafe-hopping visit.",
        "reason_ko": "오래된 한옥 골목과 따뜻한 카페 불빛이 이어지는 아담한 동네로, 짧게 카페 투어하기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Cheonggyecheon Stream",
        "description": "A restored stream path through downtown Seoul, good for a quiet walk between busy streets.",
        "description_ko": "도심 한가운데 이어지는 복원 하천 산책로로, 바쁜 거리 사이에서 조용히 걷기 좋아요.",
        "mood_tags": "calm, reflective, urban, refreshing",
        "mood_tags_ko": "차분함, 사색적임, 도시적인, 상쾌한",
        "name_ko": "청계천",
        "type": "Stream walk",
        "type_ko": "하천 산책로",
        "duration": "under_30min,1h",
        "preference_tags": "walking,photo",
        "preference_tags_ko": "산책,사진",
        "situation_tags": "solo,near,outdoor",
        "situation_tags_ko": "혼자,가까운 곳 위주,야외 선호",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A restored stream path through downtown Seoul, good for a quiet walk between busy streets.",
        "reason_ko": "도심 한가운데 이어지는 하천 산책로로, 바쁜 거리 사이에서 조용히 걷기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Gyeongui Line Forest Park",
        "description": "A linear park built along old railway tracks, with cafes, benches, and a gentle neighborhood mood.",
        "description_ko": "옛 철길을 따라 조성된 공원으로, 카페와 벤치가 이어지는 느긋한 동네 분위기가 있어요.",
        "mood_tags": "relaxed, social, slow-paced, content",
        "mood_tags_ko": "여유로운, 사교적인, 느긋함, 만족스러운",
        "name_ko": "경의선숲길",
        "type": "Linear park",
        "type_ko": "선형 공원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,cafe",
        "preference_tags_ko": "산책,카페",
        "situation_tags": "friends,couple,moderate_walk,outdoor",
        "situation_tags_ko": "친구와,연인과,조금 걸어도 괜찮음,야외 선호",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A linear park along old railway tracks with cafes and benches, a gentle neighborhood mood to share.",
        "reason_ko": "옛 철길을 따라 조성된 공원으로, 카페와 벤치가 이어지는 느긋한 동네 분위기를 함께 즐기기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Dongdaemun Design Plaza",
        "description": "A futuristic cultural landmark with sweeping curves, night lights, and design exhibitions.",
        "description_ko": "곡선형 건축과 야간 조명, 전시가 어우러진 미래적인 문화 공간이에요.",
        "mood_tags": "curious, inspired, futuristic, energetic",
        "mood_tags_ko": "호기심 많은, 영감을 주는, 미래적인, 활기찬",
        "name_ko": "동대문디자인플라자",
        "type": "Cultural landmark",
        "type_ko": "문화 랜드마크",
        "duration": "1h,2_3h",
        "preference_tags": "exhibition,night_view,photo",
        "preference_tags_ko": "전시,야경,사진",
        "situation_tags": "friends,family,indoor,outdoor",
        "situation_tags_ko": "친구와,가족과,실내 선호,야외 선호",
        "avoid_tags": "crowded,expensive",
        "avoid_tags_ko": "사람 많은 곳,비싼 곳",
        "reason": "A futuristic cultural landmark with sweeping curves and design exhibitions, good for curious exploring.",
        "reason_ko": "곡선형 건축과 전시가 어우러진 미래적인 문화 공간으로, 호기심 어린 탐방에 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Insadong",
        "description": "A cultural street lined with traditional teahouses, galleries, and craft shops.",
        "description_ko": "전통 찻집과 갤러리, 공예품 상점이 늘어선 문화 거리예요.",
        "mood_tags": "curious, nostalgic, artistic, local",
        "mood_tags_ko": "호기심 많은, 그리움, 예술적인, 로컬한",
        "name_ko": "인사동",
        "type": "Cultural street",
        "type_ko": "문화 거리",
        "duration": "1h,2_3h",
        "preference_tags": "shopping,cafe,exhibition",
        "preference_tags_ko": "쇼핑,카페,전시",
        "avoid_tags": "crowded,too_touristy",
        "avoid_tags_ko": "사람 많은 곳,너무 관광지스러운 곳",
        "reason": "A cultural street of teahouses and galleries, good for slow browsing and traditional craft-hunting.",
        "reason_ko": "전통 찻집과 갤러리가 늘어선 문화 거리로, 천천히 둘러보며 공예품을 구경하기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Gwangjang Market",
        "description": "A century-old market famous for street food stalls, silk fabrics, and a lively local buzz.",
        "description_ko": "길거리 음식 노점과 비단 원단, 활기찬 현지 분위기로 유명한 100년 넘은 시장이에요.",
        "mood_tags": "lively, social, curious, energetic",
        "mood_tags_ko": "활기찬, 사교적인, 호기심 많은, 활력 있는",
        "name_ko": "광장시장",
        "type": "Traditional market",
        "type_ko": "전통 시장",
        "duration": "1h,2_3h",
        "preference_tags": "shopping,cafe",
        "preference_tags_ko": "쇼핑,카페",
        "avoid_tags": "crowded,long_wait",
        "avoid_tags_ko": "사람 많은 곳,긴 대기",
        "reason": "A century-old market famous for street food, buzzing with local energy and easy to fall into for hours.",
        "reason_ko": "길거리 음식으로 유명한 100년 넘은 시장으로, 현지의 활기를 느끼며 시간 가는 줄 모르고 둘러보기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Myeongdong",
        "description": "A bustling shopping district packed with cosmetics stores, street food carts, and neon signs.",
        "description_ko": "화장품 매장과 길거리 음식 카트, 네온사인으로 가득한 번화한 쇼핑 거리예요.",
        "mood_tags": "energetic, lively, urban, joyful",
        "mood_tags_ko": "활기찬, 활력 있는, 도시적인, 즐거운",
        "name_ko": "명동",
        "type": "Shopping district",
        "type_ko": "쇼핑 거리",
        "duration": "1h,2_3h,half_day",
        "preference_tags": "shopping,cafe,night_view",
        "preference_tags_ko": "쇼핑,카페,야경",
        "avoid_tags": "crowded,too_touristy,expensive",
        "avoid_tags_ko": "사람 많은 곳,너무 관광지스러운 곳,비싼 곳",
        "reason": "A bustling shopping district full of neon and street food, best when you want maximum energy.",
        "reason_ko": "네온사인과 길거리 음식으로 가득한 번화한 쇼핑 거리로, 가장 활기찬 에너지를 원할 때 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Ihwa Mural Village",
        "description": "A hillside village with colorful murals and stairways, offering wide views over old Seoul.",
        "description_ko": "형형색색의 벽화와 계단이 있는 언덕 마을로, 옛 서울의 전망을 넓게 담을 수 있어요.",
        "mood_tags": "artistic, playful, nostalgic, scenic",
        "mood_tags_ko": "예술적인, 장난스러운, 그리움, 풍경이 좋은",
        "name_ko": "이화 벽화마을",
        "type": "Mural village",
        "type_ko": "벽화 마을",
        "duration": "1h,2_3h",
        "preference_tags": "photo,walking",
        "preference_tags_ko": "사진,산책",
        "avoid_tags": "crowded,complex_route",
        "avoid_tags_ko": "사람 많은 곳,복잡한 동선",
        "reason": "A hillside village of colorful murals and stairways, playful and photogenic with wide city views.",
        "reason_ko": "형형색색의 벽화와 계단이 있는 언덕 마을로, 도시 전망을 보며 경쾌하게 사진 찍기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Seochon Village",
        "description": "A quiet hanok neighborhood beside Gyeongbokgung, full of small galleries and low-key cafes.",
        "description_ko": "경복궁 옆의 조용한 한옥 동네로, 작은 갤러리와 아늑한 카페들이 자리해요.",
        "mood_tags": "quiet, artistic, cozy, local",
        "mood_tags_ko": "조용한, 예술적인, 아늑한, 로컬한",
        "name_ko": "서촌",
        "type": "Historic alley",
        "type_ko": "전통 골목",
        "duration": "1h,2_3h",
        "preference_tags": "walking,cafe,exhibition",
        "preference_tags_ko": "산책,카페,전시",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A quiet hanok neighborhood beside the palace, with small galleries and cafes away from the crowds.",
        "reason_ko": "경복궁 옆의 조용한 한옥 동네로, 인파를 피해 작은 갤러리와 카페를 즐기기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Gyeongbokgung Palace",
        "description": "Seoul's grandest royal palace, with sweeping courtyards, guard ceremonies, and mountain backdrops.",
        "description_ko": "넓은 마당과 수문장 교대식, 산을 배경으로 한 서울에서 가장 웅장한 궁궐이에요.",
        "mood_tags": "awe-struck, historic, grounded, elegant",
        "mood_tags_ko": "경이로운, 역사적인, 안정적인, 우아한",
        "name_ko": "경복궁",
        "type": "Royal palace",
        "type_ko": "궁궐",
        "duration": "1h,2_3h",
        "preference_tags": "walking,history,photo",
        "preference_tags_ko": "산책,역사 탐방,사진",
        "avoid_tags": "crowded,too_touristy,long_wait",
        "avoid_tags_ko": "사람 많은 곳,너무 관광지스러운 곳,긴 대기",
        "reason": "Seoul's grandest palace, with sweeping courtyards and mountain views - awe-inspiring if you don't mind the crowds.",
        "reason_ko": "산을 배경으로 한 웅장한 궁궐로, 인파만 감수하면 경이로운 풍경을 즐길 수 있어요.",
    },
    {
        "city": "Seoul",
        "name": "Changdeokgung Secret Garden",
        "description": "A palace garden of ponds, pavilions, and old trees, quieter and wilder than the main palaces.",
        "description_ko": "연못과 정자, 고목이 어우러진 궁궐 정원으로, 다른 궁궐보다 조용하고 자연스러워요.",
        "mood_tags": "serene, contemplative, natural, timeless",
        "mood_tags_ko": "고요함, 명상적인, 자연적인, 시간을 초월한",
        "name_ko": "창덕궁 후원",
        "type": "Palace garden",
        "type_ko": "궁궐 정원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,history,photo",
        "preference_tags_ko": "산책,역사 탐방,사진",
        "avoid_tags": "long_wait",
        "avoid_tags_ko": "긴 대기",
        "reason": "A palace garden of ponds and old trees, quieter and wilder than the main palace courtyards.",
        "reason_ko": "연못과 고목이 어우러진 궁궐 정원으로, 다른 궁궐보다 조용하고 자연스러운 분위기예요.",
    },
    {
        "city": "Seoul",
        "name": "Deoksugung Stone Wall Road",
        "description": "A tree-lined path beside an old stone palace wall, a favorite quiet stroll in downtown Seoul.",
        "description_ko": "오래된 돌담을 따라 이어지는 가로수길로, 서울 도심 속 조용한 산책으로 사랑받아요.",
        "mood_tags": "romantic, calm, nostalgic, quiet",
        "mood_tags_ko": "로맨틱함, 차분함, 그리움, 조용한",
        "name_ko": "덕수궁 돌담길",
        "type": "Historic walking path",
        "type_ko": "돌담길",
        "duration": "under_30min,1h",
        "preference_tags": "walking,photo,history",
        "preference_tags_ko": "산책,사진,역사 탐방",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A tree-lined path beside an old stone wall, a favorite quiet stroll right in the middle of downtown.",
        "reason_ko": "오래된 돌담을 따라 걷는 가로수길로, 도심 한복판에서도 조용히 걷기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Naksan Park",
        "description": "A hillside park along the old city wall, with open views over the rooftops of Seoul.",
        "description_ko": "옛 도성벽을 따라 이어지는 언덕 공원으로, 서울 지붕들 너머로 탁 트인 전망이 펼쳐져요.",
        "mood_tags": "refreshing, free-spirited, scenic, reflective",
        "mood_tags_ko": "상쾌한, 자유로운, 풍경이 좋은, 사색적인",
        "name_ko": "낙산공원",
        "type": "Hillside park",
        "type_ko": "언덕 공원",
        "duration": "1h,2_3h",
        "preference_tags": "walking,photo,history",
        "preference_tags_ko": "산책,사진,역사 탐방",
        "avoid_tags": "far,long_distance",
        "avoid_tags_ko": "너무 먼 곳,긴 이동",
        "reason": "A hillside park along the old city wall, refreshing for a walk with open rooftop views.",
        "reason_ko": "옛 도성벽을 따라 걷는 언덕 공원으로, 탁 트인 전망을 보며 상쾌하게 걷기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Yeouido Hangang Park",
        "description": "A riverside park famous for cherry blossoms in spring and wide lawns for picnics year-round.",
        "description_ko": "봄에는 벚꽃으로 유명하고, 사계절 내내 넓은 잔디밭에서 피크닉을 즐길 수 있는 강변 공원이에요.",
        "mood_tags": "refreshing, joyful, social, relaxed",
        "mood_tags_ko": "상쾌한, 즐거운, 사교적인, 여유로운",
        "name_ko": "여의도 한강공원",
        "type": "Riverside park",
        "type_ko": "강변 공원",
        "duration": "1h,2_3h,half_day",
        "preference_tags": "walking,riverside,photo",
        "preference_tags_ko": "산책,강변,사진",
        "avoid_tags": "crowded",
        "avoid_tags_ko": "사람 많은 곳",
        "reason": "A riverside park famous for cherry blossoms and wide lawns, refreshing for a picnic with friends.",
        "reason_ko": "벚꽃으로 유명하고 넓은 잔디밭이 있는 강변 공원으로, 친구들과 피크닉하기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Banpo Hangang Park",
        "description": "A riverside park known for a bridge fountain show that lights up the water after dark.",
        "description_ko": "해가 진 뒤 물줄기가 다리에서 불을 밝히는 분수쇼로 유명한 강변 공원이에요.",
        "mood_tags": "romantic, awe-struck, joyful, dreamy",
        "mood_tags_ko": "로맨틱함, 경이로운, 즐거운, 몽환적인",
        "name_ko": "반포 한강공원",
        "type": "Riverside park",
        "type_ko": "강변 공원",
        "duration": "1h,2_3h",
        "preference_tags": "riverside,night_view,photo",
        "preference_tags_ko": "강변,야경,사진",
        "avoid_tags": "crowded",
        "avoid_tags_ko": "사람 많은 곳",
        "reason": "A riverside park known for its glowing bridge fountain show, romantic once the sun goes down.",
        "reason_ko": "해가 진 뒤 다리에서 펼쳐지는 분수쇼로 유명한 강변 공원으로, 로맨틱한 밤을 보내기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Seongsu-dong Cafe Street",
        "description": "A former industrial district turned trendy cafe and design neighborhood with exposed-brick charm.",
        "description_ko": "옛 공장 지대가 트렌디한 카페와 디자인 동네로 변신한 곳으로, 노출 벽돌의 매력이 있어요.",
        "mood_tags": "stylish, artistic, lively, curious",
        "mood_tags_ko": "세련된, 예술적인, 활기찬, 호기심 많은",
        "name_ko": "성수동 카페거리",
        "type": "Cafe district",
        "type_ko": "카페 거리",
        "duration": "1h,2_3h",
        "preference_tags": "cafe,shopping,photo",
        "preference_tags_ko": "카페,쇼핑,사진",
        "avoid_tags": "crowded,expensive",
        "avoid_tags_ko": "사람 많은 곳,비싼 곳",
        "reason": "A former industrial district turned trendy cafe neighborhood, stylish for an afternoon of cafe-hopping.",
        "reason_ko": "공장 지대가 트렌디한 카페 동네로 변신한 곳으로, 세련된 카페 투어를 즐기기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Mangwon Market",
        "description": "A traditional neighborhood market known for affordable street food and an unpolished local feel.",
        "description_ko": "저렴한 길거리 음식과 꾸밈없는 동네 분위기로 유명한 전통 시장이에요.",
        "mood_tags": "local, lively, cozy, social",
        "mood_tags_ko": "로컬한, 활기찬, 아늑한, 사교적인",
        "name_ko": "망원시장",
        "type": "Traditional market",
        "type_ko": "전통 시장",
        "duration": "under_30min,1h",
        "preference_tags": "shopping,cafe",
        "preference_tags_ko": "쇼핑,카페",
        "avoid_tags": "crowded",
        "avoid_tags_ko": "사람 많은 곳",
        "reason": "A traditional market known for cheap street food and an unpolished local feel, far from the tourist trail.",
        "reason_ko": "저렴한 길거리 음식으로 유명한 전통 시장으로, 관광객보다 현지인들의 일상을 느끼기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Jongmyo Shrine",
        "description": "A solemn Confucian shrine set among old trees, one of the quietest historic sites in the city.",
        "description_ko": "고목들 사이에 자리한 엄숙한 유교 사당으로, 도시에서 가장 고요한 역사 유적 중 하나예요.",
        "mood_tags": "solemn, quiet, contemplative, grounded",
        "mood_tags_ko": "엄숙한, 조용한, 명상적인, 안정적인",
        "name_ko": "종묘",
        "type": "Historic shrine",
        "type_ko": "역사 사당",
        "duration": "1h,2_3h",
        "preference_tags": "walking,history",
        "preference_tags_ko": "산책,역사 탐방",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A solemn Confucian shrine among old trees, one of the quietest, most grounding historic sites in the city.",
        "reason_ko": "고목 사이의 엄숙한 사당으로, 도시에서 가장 고요하고 마음을 다잡기 좋은 역사 유적이에요.",
    },
    {
        "city": "Seoul",
        "name": "National Museum of Korea",
        "description": "A vast museum of Korean history and art, with a reflecting pool and open lawns outside.",
        "description_ko": "한국의 역사와 예술을 아우르는 방대한 박물관으로, 야외에는 반영 연못과 넓은 잔디밭이 있어요.",
        "mood_tags": "inspired, contemplative, curious, grounded",
        "mood_tags_ko": "영감을 주는, 명상적인, 호기심 많은, 안정적인",
        "name_ko": "국립중앙박물관",
        "type": "History museum",
        "type_ko": "역사 박물관",
        "duration": "2_3h,half_day",
        "preference_tags": "exhibition,history,walking",
        "preference_tags_ko": "전시,역사 탐방,산책",
        "avoid_tags": "",
        "avoid_tags_ko": "",
        "reason": "A vast museum of Korean history and art, with a peaceful reflecting pool outside for afterward.",
        "reason_ko": "한국의 역사와 예술을 담은 방대한 박물관으로, 관람 후 반영 연못에서 여유를 즐기기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Leeum Museum of Art",
        "description": "A striking contemporary art museum blending traditional Korean and modern international works.",
        "description_ko": "전통 한국 미술과 현대 국제 미술이 어우러진 인상적인 현대 미술관이에요.",
        "mood_tags": "artistic, inspired, stylish, contemplative",
        "mood_tags_ko": "예술적인, 영감을 주는, 세련된, 명상적인",
        "name_ko": "리움미술관",
        "type": "Art museum",
        "type_ko": "미술관",
        "duration": "1h,2_3h",
        "preference_tags": "exhibition,photo",
        "preference_tags_ko": "전시,사진",
        "avoid_tags": "expensive,long_wait",
        "avoid_tags_ko": "비싼 곳,긴 대기",
        "reason": "A striking museum blending traditional Korean and modern art, inspiring for a slow, thoughtful visit.",
        "reason_ko": "전통과 현대 미술이 어우러진 인상적인 미술관으로, 천천히 사색하며 둘러보기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Gyeongridan-gil",
        "description": "A hillside street of small cafes, boutiques, and international restaurants near Itaewon.",
        "description_ko": "이태원 근처 언덕길에 자리한, 작은 카페와 부티크, 세계 각국의 레스토랑이 늘어선 거리예요.",
        "mood_tags": "exotic, stylish, lively, curious",
        "mood_tags_ko": "이국적인, 세련된, 활기찬, 호기심 많은",
        "name_ko": "경리단길",
        "type": "Cafe street",
        "type_ko": "카페 거리",
        "duration": "1h,2_3h",
        "preference_tags": "cafe,shopping",
        "preference_tags_ko": "카페,쇼핑",
        "avoid_tags": "expensive",
        "avoid_tags_ko": "비싼 곳",
        "reason": "A hillside street of small cafes and international restaurants, exotic and lively near Itaewon.",
        "reason_ko": "작은 카페와 세계 각국 레스토랑이 늘어선 언덕길로, 이국적이고 활기찬 분위기를 느끼기 좋아요.",
    },
    {
        "city": "Seoul",
        "name": "Ttukseom Hangang Park",
        "description": "A riverside park with a music fountain, camping-style lawns, and views of the Seoul skyline.",
        "description_ko": "음악 분수와 캠핑 느낌의 잔디밭, 서울 스카이라인 전망이 있는 강변 공원이에요.",
        "mood_tags": "relaxed, refreshing, social, scenic",
        "mood_tags_ko": "여유로운, 상쾌한, 사교적인, 풍경이 좋은",
        "name_ko": "뚝섬한강공원",
        "type": "Riverside park",
        "type_ko": "강변 공원",
        "duration": "1h,2_3h,half_day",
        "preference_tags": "riverside,walking,photo",
        "preference_tags_ko": "강변,산책,사진",
        "avoid_tags": "crowded",
        "avoid_tags_ko": "사람 많은 곳",
        "reason": "A riverside park with a music fountain and skyline views, relaxed for lounging on the grass.",
        "reason_ko": "음악 분수와 스카이라인 전망이 있는 강변 공원으로, 잔디밭에 누워 여유를 즐기기 좋아요.",
    },
]

_PLACE_COLUMNS = [
    "city",
    "name",
    "description",
    "mood_tags",
    "name_ko",
    "description_ko",
    "mood_tags_ko",
    "image_url",
    "type",
    "type_ko",
    "duration",
    "preference_tags",
    "preference_tags_ko",
    "situation_tags",
    "situation_tags_ko",
    "avoid_tags",
    "avoid_tags_ko",
    "reason",
    "reason_ko",
]

_PLACE_COPY_OVERRIDES = {
    ("Paris", "Seine Riverside"): {
        "reason": "The path stays close to the water, so the city feels present but softened. It works well when you need movement without noise.",
        "reason_ko": "물가를 따라 걷다 보면 도시는 곁에 있지만 한결 부드럽게 느껴져요. 소란보다 움직임이 필요한 날에 잘 맞아요.",
    },
    ("Paris", "Pont des Arts"): {
        "reason": "This is less a destination than a small pause over the river. Sunset, footsteps, and stray music can shift the mood in just a few minutes.",
        "reason_ko": "목적지라기보다 강 위에서 잠깐 멈추는 장소에 가까워요. 노을과 발걸음, 가끔 들리는 음악이 기분을 가볍게 바꿔줘요.",
    },
    ("Paris", "Montmartre"): {
        "reason": "The hill has a slightly messy rhythm: stairs, sketch artists, viewpoints, and side streets. It suits a mood that wants sparks rather than silence.",
        "reason_ko": "계단과 화가들, 전망과 골목이 뒤섞인 리듬이 있어요. 조용함보다 작은 자극과 영감이 필요한 기분에 어울려요.",
    },
    ("Paris", "Luxembourg Gardens"): {
        "reason": "Chairs, fountains, tree shade, and the slow pace of locals make the garden feel settled. It is a good place to sit before deciding what you feel next.",
        "reason_ko": "의자와 분수, 나무 그늘, 현지인의 느린 속도가 안정감을 줘요. 다음 기분을 정하기 전에 잠시 앉아 있기 좋아요.",
    },
    ("Paris", "Canal Saint-Martin"): {
        "reason": "The canal has a casual evening texture: footbridges, cafe fronts, and water moving through the neighborhood. It feels local without becoming too quiet.",
        "reason_ko": "철제 다리와 카페, 동네 사이로 흐르는 물길이 편안한 저녁 결을 만들어요. 너무 조용하지 않으면서도 로컬한 분위기가 있어요.",
    },
    ("Paris", "Le Marais"): {
        "reason": "The appeal is in drifting between contrasts: old courtyards, small galleries, busy corners, and quiet lanes. Curiosity has plenty of room here.",
        "reason_ko": "오래된 안뜰, 작은 갤러리, 붐비는 모퉁이와 조용한 골목이 번갈아 나와요. 호기심이 머물 여지가 많은 동네예요.",
    },
    ("Paris", "Rue Cremieux"): {
        "reason": "The street is brief, colorful, and almost unreal. It is best treated as a small visual lift rather than a place to spend a long afternoon.",
        "reason_ko": "짧고 색감이 또렷해서 현실보다 살짝 엽서처럼 느껴지는 골목이에요. 오래 머물기보다 기분을 가볍게 들어 올리는 장면에 가까워요.",
    },
    ("Paris", "Ile Saint-Louis"): {
        "reason": "Water frames the island on both sides, and the streets keep their voice low. It gives central Paris a surprisingly private pace.",
        "reason_ko": "양쪽으로 강이 감싸고 거리의 목소리가 낮게 유지돼요. 파리 한복판에서도 의외로 사적인 속도를 느낄 수 있어요.",
    },
    ("Paris", "Pere Lachaise Cemetery"): {
        "reason": "Tree shade, old stone, and long paths make the cemetery feel removed from ordinary traffic. The silence here has weight, not emptiness.",
        "reason_ko": "나무 그늘과 오래된 비석, 긴 길들이 일상의 흐름에서 한 발 떨어진 감각을 줘요. 이곳의 침묵은 비어 있다기보다 묵직해요.",
    },
    ("Paris", "Tuileries Garden"): {
        "reason": "The garden is formal, but the people passing through keep it alive. It gives you symmetry without making the walk feel stiff.",
        "reason_ko": "정돈된 정원이지만 오가는 사람들이 있어 살아 있는 느낌이 있어요. 반듯한 풍경 속에서도 산책이 딱딱하게 굳지 않아요.",
    },
    ("Paris", "Marche des Enfants Rouges"): {
        "reason": "The market folds many smells and languages into a small covered space. It feels lively in a grounded, everyday way.",
        "reason_ko": "작은 실내 공간 안에 여러 냄새와 언어가 겹쳐져요. 들뜬 관광지라기보다 일상에 가까운 활기가 느껴져요.",
    },
    ("Paris", "Parc de la Villette"): {
        "reason": "The park feels wide and slightly strange, with open lawns, canals, and futuristic shapes. It leaves room for wandering without a fixed route.",
        "reason_ko": "넓은 잔디와 운하, 미래적인 구조물이 있어 조금 낯선 여백이 느껴져요. 정해진 동선 없이 돌아다니기 좋아요.",
    },
    ("Seoul", "Han River Park"): {
        "reason": "The scale of the river gives your mood somewhere to spread out. Even a short stop can feel open, airy, and less crowded inside your head.",
        "reason_ko": "강의 스케일이 커서 마음이 넓게 풀리는 느낌이 있어요. 짧게 머물러도 머릿속이 조금 덜 복잡해지는 장소예요.",
    },
    ("Seoul", "Bukchon Hanok Village"): {
        "reason": "The narrow alleys ask you to slow down. Rooflines, stone walls, and glimpses of the city make the walk feel careful rather than rushed.",
        "reason_ko": "좁은 골목이 자연스럽게 속도를 늦추게 해요. 지붕선과 돌담, 도시가 스치는 풍경 덕분에 서두르기보다 조심히 걷게 됩니다.",
    },
    ("Seoul", "Hongdae"): {
        "reason": "Hongdae is loud in a useful way when you need outside energy. Music, signs, and passing crowds keep the mood moving.",
        "reason_ko": "밖에서 에너지를 받아야 하는 날에는 홍대의 소란이 오히려 도움이 돼요. 음악과 간판, 지나가는 사람들이 기분을 계속 움직이게 해요.",
    },
    ("Seoul", "Seonyudo Park"): {
        "reason": "Old industrial traces sit quietly inside the garden, so the place feels calm without being plain. It is gentle enough for a low-energy day.",
        "reason_ko": "옛 정수장의 흔적이 정원 안에 조용히 남아 있어 밋밋하지 않은 고요함이 있어요. 에너지가 낮은 날에도 부담이 적어요.",
    },
    ("Seoul", "Cheonggyecheon Stream"): {
        "reason": "The stream cuts a quieter line through downtown. It lets you stay in the city while stepping slightly below its speed.",
        "reason_ko": "청계천은 도심 사이로 조용한 선을 하나 내줘요. 도시 안에 있으면서도 그 속도에서 살짝 내려올 수 있어요.",
    },
    ("Seoul", "Dongdaemun Design Plaza"): {
        "reason": "The curves, lights, and open plaza make the area feel almost unreal at night. It sharpens the mood rather than calming it down.",
        "reason_ko": "곡선 건축과 조명, 넓은 광장이 밤에는 살짝 비현실적으로 느껴져요. 마음을 가라앉히기보다 감각을 또렷하게 깨워줘요.",
    },
    ("Seoul", "Insadong"): {
        "reason": "Tea houses, craft shops, and gallery signs slow the street into small stops. It has enough detail to reward unhurried looking.",
        "reason_ko": "찻집과 공예품 상점, 갤러리 간판들이 거리를 작은 정거장들로 나눠줘요. 천천히 볼수록 디테일이 살아나는 곳이에요.",
    },
    ("Seoul", "Gwangjang Market"): {
        "reason": "This place is all texture: steam, voices, steel counters, quick plates of food. It fits a mood that wants the city to feel vivid again.",
        "reason_ko": "김이 오르는 음식, 목소리, 금속 식탁, 빠르게 오가는 접시들까지 감각이 선명해요. 도시가 다시 생생하게 느껴지길 바랄 때 어울려요.",
    },
    ("Seoul", "Myeongdong"): {
        "reason": "Neon, food carts, cosmetics shops, and crossing crowds make the district almost overstimulating. That intensity is exactly its character.",
        "reason_ko": "네온사인과 길거리 음식, 화장품 매장, 오가는 인파가 감각을 꽉 채워요. 조금 과할 정도의 강도가 이 거리의 성격이에요.",
    },
    ("Seoul", "Seochon Village"): {
        "reason": "Small galleries, low buildings, and cafe windows keep the neighborhood at a human scale. Wandering here feels unhurried rather than directed.",
        "reason_ko": "작은 갤러리와 낮은 건물, 카페 창들이 동네의 스케일을 사람 가까이에 둬요. 끌려다니지 않고 천천히 헤매기 좋아요.",
    },
    ("Seoul", "Yeouido Hangang Park"): {
        "reason": "The lawns and river views give the park a broad, open rhythm. It feels especially light when the season changes around the water.",
        "reason_ko": "넓은 잔디와 강 전망이 크고 열린 리듬을 만들어줘요. 물가 주변으로 계절이 바뀔 때 특히 가볍게 느껴지는 공원이에요.",
    },
    ("Seoul", "Deoksugung Stone Wall Road"): {
        "reason": "The stone wall gives the walk a steady edge, while trees soften the city around it. It is simple, but that simplicity is the point.",
        "reason_ko": "돌담이 산책의 선을 잡아주고, 가로수가 주변 도시를 부드럽게 눌러줘요. 단순하지만 바로 그 단순함이 좋은 길이에요.",
    },
    ("Seoul", "Seongsu-dong Cafe Street"): {
        "reason": "Old factory surfaces and polished cafes sit side by side. The area feels useful when you want something current without losing rough edges.",
        "reason_ko": "오래된 공장 표면과 세련된 카페가 나란히 있어요. 거칠고 현재적인 분위기를 동시에 느끼고 싶을 때 잘 맞아요.",
    },
    ("Seoul", "Ttukseom Hangang Park"): {
        "reason": "Grass, river wind, and skyline views make the park feel relaxed but not empty. It gives you space without asking for a full plan.",
        "reason_ko": "잔디와 강바람, 스카이라인이 있어 느슨하지만 비어 보이지 않아요. 큰 계획 없이도 머물 공간을 내어주는 곳이에요.",
    },
}


def _place_with_overrides(place: dict) -> dict:
    merged = dict(place)
    merged.update(_PLACE_COPY_OVERRIDES.get((place["city"], place["name"]), {}))
    return merged


def _seed_places(cursor: sqlite3.Cursor) -> None:
    existing = {
        (row["city"].lower(), row["name"].lower())
        for row in cursor.execute("SELECT city, name FROM places").fetchall()
    }
    update_columns = [column for column in _PLACE_COLUMNS if column not in ("city", "name")]
    update_sql = ", ".join(f"{column} = ?" for column in update_columns)
    for raw_place in _PLACES:
        place = _place_with_overrides(raw_place)
        if (place["city"].lower(), place["name"].lower()) not in existing:
            continue
        cursor.execute(
            f"UPDATE places SET {update_sql} WHERE city = ? COLLATE NOCASE AND name = ? COLLATE NOCASE",
            tuple(place.get(column, "") or ("" if column != "image_url" else None) for column in update_columns)
            + (place["city"], place["name"]),
        )
    rows = [
        tuple(place.get(column, "") or ("" if column != "image_url" else None) for column in _PLACE_COLUMNS)
        for place in (_place_with_overrides(place) for place in _PLACES)
        if (place["city"].lower(), place["name"].lower()) not in existing
    ]
    if not rows:
        return
    placeholders = ", ".join("?" for _ in _PLACE_COLUMNS)
    cursor.executemany(
        f"INSERT INTO places ({', '.join(_PLACE_COLUMNS)}) VALUES ({placeholders})",
        rows,
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
    trip_id: str,
    image_base64: str | None = None,
    place_id: int | None = None,
    title_en: str | None = None,
    message_en: str | None = None,
    title_ko: str | None = None,
    message_ko: str | None = None,
    next_place_id: int | None = None,
    next_place_name_en: str | None = None,
    next_place_name_ko: str | None = None,
    user_id: int | None = None,
) -> sqlite3.Row:
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO postcards (
            city, place_name, title, message, review, image_base64, place_id,
            title_en, message_en, title_ko, message_ko,
            next_place_id, next_place_name_en, next_place_name_ko, trip_id,
            user_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            next_place_id,
            next_place_name_en,
            next_place_name_ko,
            trip_id,
            user_id,
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


def update_postcard_next_place(
    postcard_id: int,
    next_place_id: int,
    next_place_name_en: str,
    next_place_name_ko: str,
) -> sqlite3.Row:
    conn = get_connection()
    conn.execute(
        """
        UPDATE postcards
        SET next_place_id = ?, next_place_name_en = ?, next_place_name_ko = ?
        WHERE id = ?
        """,
        (next_place_id, next_place_name_en, next_place_name_ko, postcard_id),
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
        """
        SELECT users.* FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
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
