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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            available_time TEXT,
            mobility TEXT,
            environment TEXT,
            avoid TEXT,
            preferences TEXT,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

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


def _seed_places(cursor: sqlite3.Cursor) -> None:
    existing = {
        (row["city"].lower(), row["name"].lower())
        for row in cursor.execute("SELECT city, name FROM places").fetchall()
    }
    rows = [
        tuple(place.get(column, "") or ("" if column != "image_url" else None) for column in _PLACE_COLUMNS)
        for place in _PLACES
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


def upsert_user_preferences(
    user_id: int,
    available_time: str,
    mobility: str,
    environment: str,
    avoid: str,
    preferences: str,
) -> sqlite3.Row:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO user_preferences (
            user_id, available_time, mobility, environment, avoid, preferences, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            available_time = excluded.available_time,
            mobility = excluded.mobility,
            environment = excluded.environment,
            avoid = excluded.avoid,
            preferences = excluded.preferences,
            updated_at = excluded.updated_at
        """,
        (user_id, available_time, mobility, environment, avoid, preferences),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row
