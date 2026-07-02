"""Canonical structured-input tag vocabulary.

These codes are the single source of truth for matching against place tags
(see database.py's _PLACES). The bilingual label maps let the backend render
display text for the user's explicit selections without an AI call; only
free-text mood input goes through the AI (see ai_service.analyze_mood).
"""

AVAILABLE_TIME = {
    "under_30min": {"en": "30 minutes or less", "ko": "30분 이하"},
    "1h": {"en": "about 1 hour", "ko": "1시간"},
    "2_3h": {"en": "2-3 hours", "ko": "2~3시간"},
    "half_day": {"en": "half a day", "ko": "반나절"},
}

MOBILITY = {
    "near": {"en": "prefers nearby spots", "ko": "가까운 곳 위주"},
    "moderate_walk": {"en": "okay with some walking", "ko": "조금 걸어도 괜찮음"},
    "far_walk": {"en": "okay with a lot of walking", "ko": "오래 걸어도 괜찮음"},
}

ENVIRONMENT = {
    "indoor": {"en": "prefers indoors", "ko": "실내 선호"},
    "outdoor": {"en": "prefers outdoors", "ko": "야외 선호"},
    "any": {"en": "no preference", "ko": "상관없음"},
}

# 활동 취향 + 분위기 취향 + 선호 장소 (카페는 두 목록에 겹쳐 등장하므로 코드 하나로 통합)
PREFERENCES = {
    "walking": {"en": "walking", "ko": "산책"},
    "photo": {"en": "photography", "ko": "사진"},
    "cafe": {"en": "cafes", "ko": "카페"},
    "exhibition": {"en": "exhibitions", "ko": "전시"},
    "shopping": {"en": "shopping", "ko": "쇼핑"},
    "reading": {"en": "reading", "ko": "독서"},
    "night_view": {"en": "night views", "ko": "야경"},
    "history": {"en": "history", "ko": "역사 탐방"},
    "quiet": {"en": "quiet", "ko": "조용한"},
    "sentimental": {"en": "sentimental", "ko": "감성적인"},
    "lively": {"en": "lively", "ko": "활기찬"},
    "exotic": {"en": "exotic", "ko": "이국적인"},
    "natural": {"en": "natural", "ko": "자연적인"},
    "local": {"en": "local", "ko": "로컬한"},
    "artistic": {"en": "artistic", "ko": "예술적인"},
    "riverside": {"en": "riverside", "ko": "강변"},
    "park": {"en": "park", "ko": "공원"},
    "alley": {"en": "alleyways", "ko": "골목"},
    "bookstore": {"en": "bookstores", "ko": "서점"},
    "gallery": {"en": "galleries", "ko": "미술관"},
    "market": {"en": "markets", "ko": "시장"},
    "viewpoint": {"en": "viewpoints", "ko": "전망대"},
}

# 하나로 통합된 회피 요소 목록 (예전에는 "여행 상황"과 "취향" 두 곳에서 겹치는
# 항목을 따로 물어봤는데, 여기 하나로 합쳐 중복 질문을 없앰)
AVOID = {
    "crowded": {"en": "crowded places", "ko": "사람 많은 곳"},
    "far": {"en": "places that are too far", "ko": "너무 먼 곳"},
    "expensive": {"en": "expensive places", "ko": "비싼 곳"},
    "complex_route": {"en": "complicated routes", "ko": "복잡한 동선"},
    "long_wait": {"en": "long waits", "ko": "긴 대기"},
    "long_distance": {"en": "long travel distances", "ko": "긴 이동"},
    "too_touristy": {"en": "overly touristy spots", "ko": "너무 관광지스러운 곳"},
}


def label(vocab: dict, code: str, language: str) -> str:
    entry = vocab.get(code)
    if not entry:
        return code
    return entry.get(language) or entry.get("en") or code


def labels(vocab: dict, codes: list[str], language: str) -> list[str]:
    return [label(vocab, code, language) for code in codes if code]
