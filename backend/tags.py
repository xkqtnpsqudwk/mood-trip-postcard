"""Canonical structured-input tag vocabulary.

Places are no longer stored in a local catalog - ai_service.recommend_trip
asks the model to recommend real, web-search-verified places directly. This
fixed duration vocabulary is still the single source of truth for the
model's structured output and for rendering bilingual display labels
without an extra AI call.
"""

AVAILABLE_TIME = {
    "under_30min": {"en": "30 minutes or less", "ko": "30분 이하"},
    "1h": {"en": "about 1 hour", "ko": "1시간"},
    "2_3h": {"en": "2-3 hours", "ko": "2~3시간"},
    "half_day": {"en": "half a day", "ko": "반나절"},
}


def label(vocab: dict, code: str, language: str) -> str:
    entry = vocab.get(code)
    if not entry:
        return code
    return entry.get(language) or entry.get("en") or code


def labels(vocab: dict, codes: list[str], language: str) -> list[str]:
    return [label(vocab, code, language) for code in codes if code]
