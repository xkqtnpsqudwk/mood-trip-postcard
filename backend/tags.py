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

# 하나로 통합된 취향 목록. 예전에는 활동/분위기/선호장소 3개 카테고리, 22개
# 항목으로 나뉘어 있었는데, 실제로 places 시드 데이터의 preference_tags에
# 쓰이는 코드는 이 10개뿐이었음 - 나머지 절반은 어떤 장소와도 매칭되지 않는
# 죽은 옵션이라 애매하게 느껴졌음. 실사용 코드만 남겨 하나의 목록으로 정리.
PREFERENCES = {
    "walking": {"en": "walking", "ko": "산책"},
    "riverside": {"en": "riverside", "ko": "강변"},
    "photo": {"en": "photography", "ko": "사진"},
    "quiet": {"en": "quiet", "ko": "조용한"},
    "night_view": {"en": "night views", "ko": "야경"},
    "exhibition": {"en": "exhibitions", "ko": "전시"},
    "shopping": {"en": "shopping", "ko": "쇼핑"},
    "reading": {"en": "reading", "ko": "독서"},
    "cafe": {"en": "cafes", "ko": "카페"},
    "history": {"en": "history", "ko": "역사 탐방"},
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
