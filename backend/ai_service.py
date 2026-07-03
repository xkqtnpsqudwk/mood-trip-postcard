"""OpenAI-backed AI helpers for mood analysis, postcard text, and images."""
import base64
import json
import os
import re

from openai import OpenAI

import tags

OPENAI_TEXT_MODEL = os.environ.get("OPENAI_TEXT_MODEL", "gpt-5.4")
OPENAI_IMAGE_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1.5")
OPENAI_TIMEOUT_SECONDS = 90.0

LANGUAGE_NAMES = {"ko": "Korean", "en": "English"}

_client: OpenAI | None = None


def _language_name(language: str) -> str:
    return LANGUAGE_NAMES.get(language, "English")


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=api_key, timeout=OPENAI_TIMEOUT_SECONDS)
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


def _image_file_from_base64(value: str, index: int):
    match = re.match(r"^data:(image/[^;]+);base64,(.*)$", value, re.DOTALL)
    if match:
        mime_type = match.group(1)
        base64_data = match.group(2)
    else:
        mime_type = "image/jpeg"
        base64_data = value

    extension = {
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }.get(mime_type, "jpg")
    image_bytes = base64.b64decode(base64_data)
    return (f"visit-photo-{index}.{extension}", image_bytes, mime_type)


def _response_image_base64(response) -> str | None:
    if not response.data:
        return None
    first = response.data[0]
    return getattr(first, "b64_json", None)


def analyze_mood(
    city: str,
    mood_text: str,
    language: str = "en",
    *,
    style_text: str | None = None,
) -> dict:
    """Analyze only the traveler's free-text mood sentence for display.

    Place ranking is handled separately from saved travel-style preferences.
    This function creates the placebo layer: emotional display tags, avoid
    labels for user-facing context, and a poetic clue sentence.

    Returns: {"tags": [{"en": str, "ko": str}, ...], "avoid": [str, ...],
              "clue": {"en": str, "ko": str}}
    """
    client = _get_client()
    avoid_vocab = ", ".join(tags.AVOID.keys())
    preference_vocab = ", ".join(tags.PREFERENCES.keys())
    system_prompt = (
        "You are an emotionally perceptive travel companion. Given a city and "
        "a traveler's current mood, do three things. The traveler is assumed "
        "to be solo by default, so do not ask for or infer companionship "
        "style. First, extract 3-6 short emotional/vibe keywords that capture "
        "how they feel right now. When a keyword naturally matches one of "
        f"these known display tags, prefer that exact word: {preference_vocab}. Second, extract "
        "0-4 'avoid' keywords, but ONLY from this fixed list, and ONLY when "
        f"clearly implied by the mood or saved style: {avoid_vocab}. Do not "
        "invent avoid keywords outside that list; return an empty avoid list "
        "if nothing is clearly implied. Third, write one poetic metaphorical "
        "clue sentence that hints at the kind of place they should visit. "
        "Return tags with both English and Korean for display. The English "
        "tag must be lowercase and short because it is used for matching; "
        "the Korean tag must be the same meaning translated naturally for "
        "display, with no hashtag. English text must use English only. "
        "Korean text must use Korean only, except place names when needed. "
        "Respond with ONLY a JSON object in this exact shape: "
        '{"tags": [{"en": "excited", "ko": "신나는"}], '
        '"avoid": ["crowded"], '
        '"clue": {"en": "a poetic sentence", "ko": "같은 의미의 한국어 문장"}}'
    )

    context_lines = [f"City: {city}", f"Current mood: {mood_text}"]
    context_lines.append(f"Preferred UI language for tone reference: {_language_name(language)}")
    user_prompt = "\n".join(context_lines)

    completion = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=600,
        response_format={"type": "json_object"},
        timeout=OPENAI_TIMEOUT_SECONDS,
    )
    content = completion.choices[0].message.content
    data = _extract_json(content)
    valid_avoid = set(tags.AVOID.keys())
    avoid_out = [
        str(a).strip().lower() for a in data.get("avoid", []) if str(a).strip().lower() in valid_avoid
    ]
    return {
        "tags": _localized_tags(data.get("tags", [])),
        "avoid": avoid_out,
        "clue": _localized_text(data.get("clue", "")),
    }


def extract_travel_style(style_text: str, language: str = "en") -> dict[str, list[str]]:
    """Extract fixed-vocabulary travel preferences from the saved style profile.

    Returns: {"preferences": [code, ...], "avoid": [code, ...]}
    """
    if not style_text.strip():
        return {"preferences": [], "avoid": []}

    client = _get_client()
    preference_vocab = {
        code: {"en": label["en"], "ko": label["ko"]}
        for code, label in tags.PREFERENCES.items()
    }
    avoid_vocab = {
        code: {"en": label["en"], "ko": label["ko"]}
        for code, label in tags.AVOID.items()
    }
    system_prompt = (
        "You extract travel style from a user's saved free-text profile. "
        "Return only fixed vocabulary codes from the provided lists. "
        "Use preferences for things the user likes or wants more of. "
        "Use avoid for things the user explicitly dislikes, wants to avoid, "
        "or finds uncomfortable. Do not infer companionship style; the product "
        "targets solo travelers by default. Be conservative: if a preference "
        "is vague or not clearly expressed, leave it out. Respond with ONLY "
        "a JSON object in this exact shape: "
        '{"preferences": ["walking", "cafe"], "avoid": ["crowded"]}'
    )
    user_prompt = json.dumps(
        {
            "style_text": style_text,
            "language": _language_name(language),
            "allowed_preferences": preference_vocab,
            "allowed_avoid": avoid_vocab,
        },
        ensure_ascii=False,
    )

    completion = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=400,
        response_format={"type": "json_object"},
        timeout=OPENAI_TIMEOUT_SECONDS,
    )
    content = completion.choices[0].message.content
    data = _extract_json(content)
    valid_preferences = set(tags.PREFERENCES.keys())
    valid_avoid = set(tags.AVOID.keys())
    preferences = [
        str(code).strip().lower()
        for code in data.get("preferences", [])
        if str(code).strip().lower() in valid_preferences
    ]
    avoid = [
        str(code).strip().lower()
        for code in data.get("avoid", [])
        if str(code).strip().lower() in valid_avoid
    ]
    return {
        "preferences": list(dict.fromkeys(preferences)),
        "avoid": list(dict.fromkeys(avoid)),
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
        model=OPENAI_TEXT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=700,
        response_format={"type": "json_object"},
        timeout=OPENAI_TIMEOUT_SECONDS,
    )
    content = completion.choices[0].message.content
    data = _extract_json(content)
    return {
        "title": _localized_text(data.get("title", "")),
        "message": _localized_text(data.get("message", "")),
    }


def generate_postcard_image(
    city: str,
    place_name: str,
    message: str,
    source_images_base64: list[str] | None = None,
) -> str | None:
    """Generate a postcard image and return base64-encoded image data.

    When source images are provided, OpenAI edits them into a travel postcard
    collage. Otherwise, it generates a new postcard image from the AI-written
    English postcard message.

    Raises on image-generation failure so the caller can ask the user to retry
    instead of silently saving an imageless postcard.
    """
    client = _get_client()
    source_images_base64 = [image for image in (source_images_base64 or []) if image]

    if source_images_base64:
        prompt = (
            "Create a polished horizontal digital travel postcard collage "
            f"from the provided visit photos for {place_name} in {city}. "
            "Preserve the real photographed moments, arrange them like a "
            "warm modern postcard, improve light and color gently, and do "
            "not add any text, letters, captions, logos, or watermarks."
        )
        image_files = [
            _image_file_from_base64(image, index)
            for index, image in enumerate(source_images_base64[:4], start=1)
        ]
        response = client.images.edit(
            model=OPENAI_IMAGE_MODEL,
            image=image_files,
            prompt=prompt,
            size="1536x1024",
            quality="medium",
            timeout=OPENAI_TIMEOUT_SECONDS,
        )
    else:
        prompt = (
            f"A beautiful horizontal travel postcard photograph of {place_name} "
            f"in {city}, evoking this feeling: {message}. Warm natural light, "
            "cinematic but realistic travel photography, postcard aesthetic, "
            "no text, no words, no writing anywhere in the image."
        )
        response = client.images.generate(
            model=OPENAI_IMAGE_MODEL,
            prompt=prompt,
            size="1536x1024",
            quality="medium",
            timeout=OPENAI_TIMEOUT_SECONDS,
        )

    image_base64 = _response_image_base64(response)
    if not image_base64:
        raise RuntimeError("OpenAI image response did not include image data")
    return image_base64
