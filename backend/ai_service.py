"""Wrapper around the NVIDIA NIM API for mood analysis, postcard generation,
and postcard image generation (via NVIDIA's hosted FLUX.1-dev NIM)."""
import json
import os
import re

import httpx
from openai import OpenAI

import tags

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
NIM_MODEL = "meta/llama-4-maverick-17b-128e-instruct"
NIM_TIMEOUT_SECONDS = 90.0

NIM_IMAGE_URL = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"

LANGUAGE_NAMES = {"ko": "Korean", "en": "English"}

_client: OpenAI | None = None


def _language_name(language: str) -> str:
    return LANGUAGE_NAMES.get(language, "English")


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("NVIDIA_NIM_API_KEY")
        if not api_key:
            raise RuntimeError("NVIDIA_NIM_API_KEY is not set")
        _client = OpenAI(
            base_url=NIM_BASE_URL,
            api_key=api_key,
            timeout=NIM_TIMEOUT_SECONDS,
        )
    return _client


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response, tolerating code fences."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model response: {text!r}")
    return json.loads(match.group(0))


def _localized_text(value, fallback: str = "") -> dict[str, str]:
    if isinstance(value, dict):
        en = str(value.get("en") or value.get("english") or fallback).strip()
        ko = str(value.get("ko") or value.get("korean") or fallback).strip()
        return {"en": en, "ko": ko}
    text = str(value or fallback).strip()
    return {"en": text, "ko": text}


def _localized_tags(value) -> list[dict[str, str]]:
    tags = []
    for item in value or []:
        if isinstance(item, dict):
            en = str(item.get("en") or item.get("english") or "").strip().lower()
            ko = str(item.get("ko") or item.get("korean") or en).strip()
        else:
            en = str(item).strip().lower()
            ko = en
        if en:
            tags.append({"en": en, "ko": ko})
    return tags


def analyze_mood(
    city: str,
    mood_text: str,
    language: str = "en",
    *,
    companions: str | None = None,
    available_time: str | None = None,
    mobility: str | None = None,
    environment: str | None = None,
    emotions: list[str] | None = None,
    emotion_intensity: str | None = None,
    preferences: list[str] | None = None,
    avoid: list[str] | None = None,
) -> dict:
    """Analyze the traveler's structured selections plus an optional free-text
    mood sentence, and return bilingual supplementary tags plus a bilingual clue.

    The structured selections (companions/available_time/mobility/environment/
    emotions/preferences/avoid) are already canonical codes from a fixed
    vocabulary (see tags.py) and are matched against place tags directly by
    the caller without going through the AI. This call only asks the AI to
    (a) read the free-text mood_text, if any, and surface a few SHORT
    supplementary emotion/preference keywords not already covered by the
    selections, and (b) write one poetic clue sentence that weaves the whole
    context together.

    Returns: {"tags": [{"en": str, "ko": str}, ...], "clue": {"en": str, "ko": str}}
    """
    client = _get_client()
    system_prompt = (
        "You are an emotionally perceptive travel companion. You are given a "
        "traveler's already-selected trip context (companions, available "
        "time, mobility preference, indoor/outdoor preference, emotions, "
        "emotion intensity, preferences, things to avoid) and an optional "
        "free-text mood sentence. First, read the free-text sentence, if "
        "any, and extract 0-5 short supplementary emotional/vibe/preference "
        "keywords that are implied by it but not already covered by the "
        "selected context; return an empty list if there is no free text or "
        "it adds nothing new. Second, write one poetic metaphorical clue "
        "sentence that hints at the kind of place they should visit, "
        "weaving together the full context. Return both English and Korean "
        "for display. The English tag must be lowercase and short because it "
        "is used for matching; the Korean tag must be the same meaning "
        "translated naturally for display, with no hashtag. English text "
        "must use English only. Korean text must use Korean only, except "
        "place names when needed. "
        "Respond with ONLY a JSON object in this exact shape: "
        '{"tags": [{"en": "excited", "ko": "신나는"}], '
        '"clue": {"en": "a poetic sentence", "ko": "같은 의미의 한국어 문장"}}'
    )

    context_lines = [f"City: {city}"]
    if companions:
        context_lines.append(f"Companions: {tags.label(tags.COMPANIONS, companions, 'en')}")
    if available_time:
        context_lines.append(
            f"Available time: {tags.label(tags.AVAILABLE_TIME, available_time, 'en')}"
        )
    if mobility:
        context_lines.append(f"Mobility preference: {tags.label(tags.MOBILITY, mobility, 'en')}")
    if environment:
        context_lines.append(
            f"Environment preference: {tags.label(tags.ENVIRONMENT, environment, 'en')}"
        )
    if emotions:
        context_lines.append(
            f"Selected emotions: {', '.join(tags.labels(tags.EMOTIONS, emotions, 'en'))}"
        )
    if emotion_intensity:
        context_lines.append(
            f"Emotion intensity: {tags.label(tags.EMOTION_INTENSITY, emotion_intensity, 'en')}"
        )
    if preferences:
        context_lines.append(
            f"Selected preferences: {', '.join(tags.labels(tags.PREFERENCES, preferences, 'en'))}"
        )
    if avoid:
        context_lines.append(f"Wants to avoid: {', '.join(tags.labels(tags.AVOID, avoid, 'en'))}")
    context_lines.append(f"Preferred UI language for tone reference: {_language_name(language)}")
    context_lines.append(f"Free-text mood (may be empty): {mood_text or '(none)'}")
    user_prompt = "\n".join(context_lines)

    completion = client.chat.completions.create(
        model=NIM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=600,
    )
    content = completion.choices[0].message.content
    data = _extract_json(content)
    return {
        "tags": _localized_tags(data.get("tags", [])),
        "clue": _localized_text(data.get("clue", "")),
    }


def generate_postcard(
    city: str,
    place_name: str,
    review: str,
    language: str = "en",
    place_name_en: str | None = None,
    place_name_ko: str | None = None,
) -> dict:
    """Generate a bilingual poetic postcard title and message.

    Returns: {"title": {"en": str, "ko": str}, "message": {"en": str, "ko": str}}
    """
    client = _get_client()
    place_name_en = place_name_en or place_name
    place_name_ko = place_name_ko or place_name
    system_prompt = (
        "You are a poet who writes short, heartfelt digital travel postcards. "
        "Given the city, the place visited, and the traveler's review, write a "
        "short poetic postcard title (under 8 words) and an emotional postcard "
        "message (2-4 sentences). Return both English and Korean. English text "
        "must use English only. Korean text must use Korean only, except place "
        "names. Keep each place name exactly as provided for that language. "
        "Respond with ONLY a JSON object in this exact shape: "
        '{"title": {"en": "a poetic title", "ko": "같은 의미의 한국어 제목"}, '
        '"message": {"en": "a short emotional message", '
        '"ko": "같은 의미의 한국어 메시지"}}'
    )
    user_prompt = (
        f"City: {city}\n"
        f"Place visited, English name: {place_name_en}\n"
        f"Place visited, Korean name: {place_name_ko}\n"
        f"Preferred UI language for tone reference: {_language_name(language)}\n"
        f"Traveler's review: {review}"
    )

    completion = client.chat.completions.create(
        model=NIM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=700,
    )
    content = completion.choices[0].message.content
    data = _extract_json(content)
    return {
        "title": _localized_text(data.get("title", "")),
        "message": _localized_text(data.get("message", "")),
    }


def generate_postcard_image(city: str, place_name: str, review: str) -> str | None:
    """Generate a postcard photo via NVIDIA's hosted FLUX.1-dev NIM and return
    base64-encoded JPEG data.

    Returns None (rather than raising) on any failure, so a missing key or a
    slow/failing image provider never blocks postcard creation.
    """
    api_key = os.environ.get("NVIDIA_NIM_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"A beautiful travel postcard photograph of {place_name} in {city}, "
        f"evoking this feeling: {review}. Warm painterly light, postcard "
        "aesthetic, no text, no words, no writing anywhere in the image."
    )

    try:
        response = httpx.post(
            NIM_IMAGE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
            json={
                "prompt": prompt,
                "width": 1152,
                "height": 768,
                "steps": 25,
            },
            timeout=NIM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        artifacts = response.json().get("artifacts", [])
        if not artifacts:
            return None
        return artifacts[0].get("base64")
    except Exception:
        return None
