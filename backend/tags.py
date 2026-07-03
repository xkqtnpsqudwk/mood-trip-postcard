"""Canonical structured-input tag vocabulary.

Places are no longer stored in a local catalog - ai_service.recommend_trip
asks the model to recommend real, web-search-verified places directly. These
fixed codes are still the single source of truth for the model's structured
output (duration buckets, avoid-warning reasons) and for rendering bilingual
display labels without an extra AI call.
"""

AVAILABLE_TIME = {
    "under_30min": {"en": "30 minutes or less", "ko": "30분 이하"},
    "1h": {"en": "about 1 hour", "ko": "1시간"},
    "2_3h": {"en": "2-3 hours", "ko": "2~3시간"},
    "half_day": {"en": "half a day", "ko": "반나절"},
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
