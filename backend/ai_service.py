"""OpenAI-backed AI helpers for mood analysis, recommendations, and images."""
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


def _image_file_from_base64(value: str, index: int):
    match = re.match(r"^data:(image/[^;]+);base64,(.*)$", value, re.DOTALL)
    if match:
        mime_type = match.group(1)
        base64_data = match.group(2)
    else:
        mime_type = ""
        base64_data = value

    image_bytes = base64.b64decode(base64_data)
    if not mime_type:
        if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            mime_type = "image/png"
        elif image_bytes.startswith(b"\xff\xd8\xff"):
            mime_type = "image/jpeg"
        elif image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"

    extension = {
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }.get(mime_type, "jpg")
    return (f"visit-photo-{index}.{extension}", image_bytes, mime_type)


def _response_image_base64(response) -> str | None:
    if not response.data:
        return None
    first = response.data[0]
    return getattr(first, "b64_json", None)


def _strip_markdown_links(text: str) -> str:
    """Drop inline source citations the web-searching model tends to leave in
    free-text fields, e.g. '... ([site.com](https://site.com/x))'."""
    return re.sub(r"\s*\(\[[^\]]*\]\([^)]*\)\)", "", text).strip()


def _normalize_place_name(value: str) -> str:
    return re.sub(r"[\W_]+", "", value or "", flags=re.UNICODE).casefold()


_PLACE_SCHEMA = {
    "type": "object",
    "properties": {
        "name_en": {"type": "string"},
        "name_ko": {"type": "string"},
        "type_en": {"type": "string"},
        "type_ko": {"type": "string"},
        "description_en": {"type": "string"},
        "description_ko": {"type": "string"},
        "duration": {"type": "string", "enum": list(tags.AVAILABLE_TIME.keys())},
        "reason_en": {"type": "string"},
        "reason_ko": {"type": "string"},
        "intensity_level": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
        "map_x": {"type": "number"},
        "map_y": {"type": "number"},
        "latitude": {"type": "number"},
        "longitude": {"type": "number"},
    },
    "required": [
        "name_en", "name_ko", "type_en", "type_ko", "description_en",
        "description_ko", "duration", "reason_en", "reason_ko",
        "intensity_level", "map_x", "map_y", "latitude", "longitude",
    ],
    "additionalProperties": False,
}

_RECOMMEND_TRIP_SCHEMA = {
    "type": "object",
    "properties": {
        "clue_en": {"type": "string"},
        "clue_ko": {"type": "string"},
        "places": {"type": "array", "items": _PLACE_SCHEMA},
    },
    "required": ["clue_en", "clue_ko", "places"],
    "additionalProperties": False,
}


def recommend_trip(
    city: str,
    mood_text: str,
    language: str = "en",
    *,
    style_text: str | None = None,
    excluded_place_names: list[str] | None = None,
) -> dict:
    """Ask the model to recommend real places, grounded with web search.

    Replaces the old fixed-catalog lookup: the model proposes one real place
    in `city` that fits the traveler's saved personality profile and current
    mood tone. It's required to use the web_search tool to confirm the place
    actually exists and is currently operating, rather than recommending from
    parametric memory alone.

    Returns: {"clue": {"en", "ko"}, "places": [{"name": {...}, "type": {...},
              "description": {...}, "duration": str, "reason": {...},
              "intensity_level": "LOW"|"MEDIUM"|"HIGH", "map_position": {"x", "y"},
              "coordinates": {"lat", "lng"}}]}
    """
    client = _get_client()
    duration_vocab = ", ".join(tags.AVAILABLE_TIME.keys())
    excluded_place_names = [
        name.strip() for name in (excluded_place_names or []) if name and name.strip()
    ]
    instructions = (
        "You are an emotionally perceptive solo-travel companion. Given a city, "
        "the traveler's current mood, and (optionally) a free-text profile "
        "they saved about themselves, recommend exactly 1 real, currently-operating "
        "place in that exact city. The saved profile describes who the "
        "traveler is broadly - personality, general likes/dislikes, how they "
        "tend to feel in different situations - not a literal list of travel "
        "preferences, so read it for the kind of person they are and infer "
        "what would suit them, rather than pattern-matching keywords. When "
        "the current mood and the saved profile point in different "
        "directions, use the saved profile as the primary basis for the place "
        "choice, and use the current mood mainly to tune emotional framing, "
        "pace, intensity, and social exposure. Avoid shallow keyword matching: if they feel low "
        "but their profile says they're extroverted, don't default to a "
        "quiet cafe - consider energetic but accessible places where they "
        "can borrow energy from a crowd; if they feel overstimulated but "
        "usually enjoy nightlife, prioritize the current need to decompress "
        "over their usual taste; if they feel lonely, favor places where "
        "being alone doesn't feel isolating (markets, riversides, "
        "bookstores, museums, parks); if they feel anxious, avoid chaotic "
        "picks unless their profile strongly suggests crowds feel like "
        "comfort to them. Since you are choosing only one place, make the "
        "reason for that one choice specific and grounded in the saved profile. "
        "If excluded_place_names is provided, do not recommend any listed place "
        "or the same place under a translated, abbreviated, or slightly varied "
        "name. Treat the excluded list as places the traveler has already "
        "recorded during this trip. Choose a meaningfully different place, "
        "preferably in a different micro-area or with a different texture, "
        "while still fitting the saved profile. "
        "The traveler is solo by default. You MUST use the web_search "
        "tool to verify each place actually exists and is currently operating "
        "before including it - never rely on memory alone, and prefer "
        "well-known, easily verifiable places over obscure ones. Only "
        "recommend places actually inside the named city itself, not "
        "neighboring towns or the wider metro area, unless the city name "
        "given explicitly refers to that broader region. "
        "For the place, give a bilingual name/type/description/reason "
        "(natural English and Korean), a duration code from this fixed list: "
        f"{duration_vocab}, an intensity_level of LOW, MEDIUM, or HIGH for "
        "how stimulating/energetic the place is, an approximate map_x/map_y "
        "(0-100) representing where the place roughly sits within the city, "
        "with 0,0 as northwest and 100,100 as southeast, and the place's "
        "real latitude/longitude (use web_search to find its actual current "
        "coordinates - do not estimate from memory). After choosing the "
        "place, also write one poetic metaphorical clue sentence (English "
        "and Korean) that hints at today's mood AND subtly resonates with a "
        "texture, color, or feeling of the selected place - it should read like a preview of what's "
        "ahead, not a generic mood note disconnected from the actual "
        "recommendation. Vary the sentence's opening and structure every "
        "time; do not default to a fixed template like always starting "
        "with 'Today feels like...' or 'Follow...' - surprise with the "
        "phrasing itself. English text must use English only; Korean text "
        "must use Korean only, except place names when needed."
    )
    user_prompt = json.dumps(
        {
            "city": city,
            "mood_text": mood_text,
            "saved_personality_profile": style_text or "",
            "excluded_place_names": excluded_place_names,
            "preferred_ui_language_for_tone": _language_name(language),
        },
        ensure_ascii=False,
    )

    response = client.responses.create(
        model=OPENAI_TEXT_MODEL,
        instructions=instructions,
        input=user_prompt,
        tools=[{"type": "web_search"}],
        text={
            "format": {
                "type": "json_schema",
                "name": "trip_recommendation",
                "schema": _RECOMMEND_TRIP_SCHEMA,
                "strict": True,
            }
        },
        timeout=OPENAI_TIMEOUT_SECONDS,
    )
    data = json.loads(response.output_text)
    excluded_normalized = {_normalize_place_name(name) for name in excluded_place_names}

    valid_duration = set(tags.AVAILABLE_TIME.keys())
    valid_intensity = {"LOW", "MEDIUM", "HIGH"}
    places = []
    for place in data.get("places", []):
        place_names = [
            _normalize_place_name(place.get("name_en", "")),
            _normalize_place_name(place.get("name_ko", "")),
        ]
        if excluded_normalized.intersection(place_names):
            raise RuntimeError(
                f"AI recommendation duplicated an excluded place: {place.get('name_en')}"
            )
        duration = place.get("duration")
        if duration not in valid_duration:
            duration = next(iter(valid_duration))
        intensity_level = place.get("intensity_level")
        if intensity_level not in valid_intensity:
            intensity_level = "MEDIUM"
        places.append(
            {
                "name": {"en": place["name_en"], "ko": place["name_ko"]},
                "type": {"en": place["type_en"], "ko": place["type_ko"]},
                "description": {
                    "en": _strip_markdown_links(place["description_en"]),
                    "ko": _strip_markdown_links(place["description_ko"]),
                },
                "duration": duration,
                "reason": {
                    "en": _strip_markdown_links(place["reason_en"]),
                    "ko": _strip_markdown_links(place["reason_ko"]),
                },
                "intensity_level": intensity_level,
                "map_position": {
                    "x": max(0.0, min(100.0, float(place["map_x"]))),
                    "y": max(0.0, min(100.0, float(place["map_y"]))),
                },
                "coordinates": {
                    "lat": float(place["latitude"]),
                    "lng": float(place["longitude"]),
                },
            }
        )

    return {
        "clue": {"en": data["clue_en"], "ko": data["clue_ko"]},
        "places": places,
    }


def generate_postcard_image(
    city: str,
    place_name: str,
    message: str,
    source_images_base64: list[str] | None = None,
) -> str | None:
    """Generate a visit-moment image and return base64-encoded image data.

    When source images are provided, OpenAI edits them into a travel-memory
    collage. Otherwise, it generates a new image from the user's note.

    Raises on image-generation failure so the caller can ask the user to retry
    instead of silently saving an imageless postcard.
    """
    client = _get_client()
    source_images_base64 = [image for image in (source_images_base64 or []) if image]

    if source_images_base64:
        prompt = (
            "Create a polished horizontal digital travel memory collage "
            f"from the provided visit photos for {place_name} in {city}. "
            "Preserve the real photographed moments, arrange them like a "
            "warm modern travel record, improve light and color gently, and do "
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
            size="auto",
            quality="medium",
            timeout=OPENAI_TIMEOUT_SECONDS,
        )
    else:
        prompt = (
            f"A beautiful horizontal travel memory photograph of {place_name} "
            f"in {city}, inspired by this traveler's note: {message}. Warm natural light, "
            "cinematic but realistic travel photography, personal travel-record aesthetic, "
            "no text, no words, no writing anywhere in the image."
        )
        response = client.images.generate(
            model=OPENAI_IMAGE_MODEL,
            prompt=prompt,
            size="auto",
            quality="medium",
            timeout=OPENAI_TIMEOUT_SECONDS,
        )

    image_base64 = _response_image_base64(response)
    if not image_base64:
        raise RuntimeError("OpenAI image response did not include image data")
    return image_base64


_TRIP_CLOSING_SCHEMA = {
    "type": "object",
    "properties": {
        "closing_en": {"type": "string"},
        "closing_ko": {"type": "string"},
    },
    "required": ["closing_en", "closing_ko"],
    "additionalProperties": False,
}


def generate_trip_closing_note(city: str, clues: list[dict]) -> dict:
    """Weave a finished trip's per-place clues into one closing line.

    Each clue was already written as a poetic one-line mood note for a
    single recommended place, in visit order. This blends their shared
    feeling, texture, or arc into one new sentence rather than just
    concatenating them.

    Returns: {"en": str, "ko": str}
    """
    if not clues:
        return {"en": "", "ko": ""}

    client = _get_client()
    clue_lines = "\n".join(
        f"{index}. EN: {clue.get('en', '')} / KO: {clue.get('ko', '')}"
        for index, clue in enumerate(clues, start=1)
    )
    instructions = (
        "You are weaving together the emotional clues from a finished solo "
        f"trip in {city} into one closing line for a travel postcard. Each "
        "clue below was written as a poetic one-line mood note for a single "
        "place the traveler visited, in the order visited. Blend their "
        "shared feeling, texture, or arc into ONE new closing sentence that "
        "reads like a natural conclusion to the journey - do not just "
        "concatenate or list them, and do not mention place names. Write it "
        "in both natural English and Korean, one sentence each."
    )
    response = client.responses.create(
        model=OPENAI_TEXT_MODEL,
        instructions=instructions,
        input=clue_lines,
        text={
            "format": {
                "type": "json_schema",
                "name": "trip_closing_note",
                "schema": _TRIP_CLOSING_SCHEMA,
                "strict": True,
            }
        },
        timeout=OPENAI_TIMEOUT_SECONDS,
    )
    data = json.loads(response.output_text)
    return {"en": data["closing_en"], "ko": data["closing_ko"]}


def generate_trip_postcard(
    city: str,
    postcards: list[dict],
    language: str = "en",
    closing_note: str = "",
) -> dict:
    """Create one final postcard-style image from every record in a finished trip.

    Returns: {"title": {"en": "", "ko": ""}, "message": {"en": "", "ko": ""},
              "image_base64": str}
    """
    if not postcards:
        raise ValueError("postcards must not be empty")

    client = _get_client()
    trip_notes = [
        {
            "place_name": item.get("place_name") or "",
            "title": item.get("title") or "",
            "message": item.get("message") or "",
            "review": item.get("review") or "",
        }
        for item in postcards
    ]
    image_sources = [
        item.get("image_base64")
        for item in postcards
        if item.get("image_base64")
    ][:8]
    # A finished trip always has at least one record, and a record can only
    # exist once its own image was generated successfully - so this should
    # never be empty. Fail loudly rather than quietly falling back to a
    # generic generated image if that invariant is ever violated.
    if not image_sources:
        raise RuntimeError("No record images available to build the final postcard")

    image_context = "\n".join(
        f"{index}. {item.get('place_name', '')}: "
        f"{item.get('title', '')} / {item.get('message', '')} / {item.get('review', '')}"
        for index, item in enumerate(trip_notes, start=1)
    )
    closing_note_line = (
        f"\nThe emotional threads running through this whole trip: {closing_note}"
        if closing_note
        else ""
    )
    prompt = (
        "Create one polished horizontal image of a finished travel postcard "
        f"for a completed solo trip in {city}.\n\n"
        "Use only the attached input photos as the photographic elements. Do "
        "not invent, generate, or add any new travel photos, landmarks, "
        "people, scenery, or background scenes. The attached photos must "
        "remain individually recognizable, with their real photographed "
        "details preserved.\n\n"
        "Treat this explicitly as a postcard, not a generic photo blend. "
        "Arrange the provided real trip photos as if they were physically "
        "cut out and pasted onto a vintage travel postcard template, like a "
        "scrapbook page of collected moments. Do not melt, morph, or blend "
        "the photos into one seamless scene.\n\n"
        "Tie the collage together with a warm cohesive color grade and "
        "small decorative postcard touches such as abstract postmark "
        "shapes, washi tape, paper texture, stamp-like stickers, rounded "
        "photo corners, subtle shadows, and vintage postcard framing.\n\n"
        f"Use {city} only as visual context for the overall mood. Do not "
        "write the city name anywhere.\n\n"
        "Use the trip notes only to guide the mood, visual rhythm, and "
        "emotional tone of the postcard. Do not render the notes as "
        "visible text.\n\n"
        f"Trip notes:\n{image_context}{closing_note_line}\n\n"
        "Strict restrictions:\n"
        "- No readable text\n"
        "- No letters\n"
        "- No captions\n"
        "- No logos\n"
        "- No watermarks\n"
        "- No generated extra photos\n"
        "- No new people or objects that were not in the attached photos\n"
        "- No seamless fantasy scene\n"
        "- The result must look like a finished physical travel postcard "
        "collage made from the attached photos"
    )
    response = client.images.edit(
        model=OPENAI_IMAGE_MODEL,
        image=[
            _image_file_from_base64(image, index)
            for index, image in enumerate(image_sources, start=1)
        ],
        prompt=prompt,
        size="auto",
        quality="medium",
        timeout=OPENAI_TIMEOUT_SECONDS,
    )

    image_base64 = _response_image_base64(response)
    if not image_base64:
        raise RuntimeError("OpenAI trip image response did not include image data")
    return {
        "title": {"en": "", "ko": ""},
        "message": {"en": "", "ko": ""},
        "image_base64": image_base64,
    }
