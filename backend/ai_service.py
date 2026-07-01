"""Wrapper around the NVIDIA NIM API for mood analysis, postcard generation,
and postcard image generation (via NVIDIA's hosted FLUX.1-dev NIM)."""
import json
import os
import re

import httpx
from openai import OpenAI

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
NIM_MODEL = "deepseek-ai/deepseek-v4-pro"

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
        _client = OpenAI(base_url=NIM_BASE_URL, api_key=api_key)
    return _client


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response, tolerating code fences."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model response: {text!r}")
    return json.loads(match.group(0))


def analyze_mood(city: str, mood_text: str, language: str = "en") -> dict:
    """Analyze the user's mood text and return tags plus a metaphorical clue.

    Returns: {"tags": [str, ...], "clue": str}
    """
    client = _get_client()
    language_name = _language_name(language)
    system_prompt = (
        "You are an emotionally perceptive travel companion. Given a city and a "
        "traveler's mood description, extract 3-5 short emotional/vibe keywords "
        "(single words or short phrases, in English, lowercase, for internal "
        "matching) that capture their feeling, and write one poetic 'metaphorical "
        f"clue' sentence that hints at the kind of place they should visit. "
        f"Write the clue entirely in {language_name}, using only the "
        f"{language_name} script — never mix in Chinese, Japanese, Cyrillic, "
        "Greek, or any other language's characters. "
        "Respond with ONLY a JSON object in this exact shape: "
        '{"tags": ["tag1", "tag2", "tag3"], "clue": "a poetic sentence"}'
    )
    user_prompt = f"City: {city}\nMood: {mood_text}"

    completion = client.chat.completions.create(
        model=NIM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=400,
    )
    content = completion.choices[0].message.content
    data = _extract_json(content)
    return {
        "tags": [str(t).strip().lower() for t in data.get("tags", [])],
        "clue": str(data.get("clue", "")).strip(),
    }


def generate_postcard(
    city: str,
    place_name: str,
    review: str,
    next_place_name: str,
    language: str = "en",
) -> dict:
    """Generate a poetic postcard title and message from a visit review.

    Returns: {"title": str, "message": str}
    """
    client = _get_client()
    language_name = _language_name(language)
    system_prompt = (
        "You are a poet who writes short, heartfelt digital travel postcards. "
        "Given the city, the place visited, and the traveler's review, write a "
        "short poetic postcard title (under 8 words) and an emotional postcard "
        "message (2-4 sentences), weaving in the next recommended spot as a "
        f"gentle invitation. Write both entirely in {language_name}, using only "
        f"the {language_name} script — never mix in Chinese, Japanese, Cyrillic, "
        "Greek, or any other language's characters. Keep place names exactly as "
        "given, in their original spelling, rather than transliterating or "
        "translating them. "
        "Respond with ONLY a JSON object in this exact shape: "
        '{"title": "a poetic title", "message": "a short emotional message"}'
    )
    user_prompt = (
        f"City: {city}\n"
        f"Place visited: {place_name}\n"
        f"Traveler's review: {review}\n"
        f"Next recommended spot: {next_place_name}"
    )

    completion = client.chat.completions.create(
        model=NIM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=400,
    )
    content = completion.choices[0].message.content
    data = _extract_json(content)
    return {
        "title": str(data.get("title", "")).strip(),
        "message": str(data.get("message", "")).strip(),
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
            timeout=90,
        )
        response.raise_for_status()
        artifacts = response.json().get("artifacts", [])
        if not artifacts:
            return None
        return artifacts[0].get("base64")
    except Exception:
        return None
