"""FastAPI application for Mood Trip Postcard."""
import re
import sqlite3
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

import ai_service
import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="Mood Trip Postcard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    city: str
    mood_text: str
    language: str = "en"


class LocalizedText(BaseModel):
    en: str
    ko: str


class LocalizedTag(BaseModel):
    en: str
    ko: str


class PlaceOut(BaseModel):
    id: int
    city: str
    name: str
    description: str
    mood_tags: str
    name_i18n: LocalizedText
    description_i18n: LocalizedText
    mood_tags_i18n: LocalizedText
    image_url: str | None = None
    match_score: int = 0


class AnalyzeResponse(BaseModel):
    clue: LocalizedText
    tags: list[LocalizedTag]
    places: list[PlaceOut]


class PostcardRequest(BaseModel):
    city: str
    place_id: int
    review: str
    language: str = "en"


class PostcardOut(BaseModel):
    id: int
    city: str
    place_name: str
    place_name_i18n: LocalizedText
    title: str
    message: str
    title_i18n: LocalizedText
    message_i18n: LocalizedText
    review: str
    image_base64: str | None = None
    created_at: str


EMOTION_TAG_ALIASES = {
    "angry": {"calm", "peaceful", "restorative", "reflective"},
    "anger": {"calm", "peaceful", "restorative", "reflective"},
    "annoyed": {"calm", "quiet", "restorative"},
    "adventure": {"adventurous", "curious", "energetic", "free-spirited"},
    "adventurous": {"adventurous", "curious", "energetic", "free-spirited"},
    "anxious": {"calm", "peaceful", "grounded", "restorative"},
    "anxiety": {"calm", "peaceful", "grounded", "restorative"},
    "bored": {"curious", "inspired", "adventurous", "lively"},
    "burned-out": {"restorative", "slow-paced", "peaceful", "refreshing"},
    "confused": {"reflective", "contemplative", "grounded", "curious"},
    "creative": {"inspired", "curious", "free-spirited"},
    "depressed": {"restorative", "peaceful", "reflective", "grounded"},
    "dreamy": {"dreamy", "romantic", "peaceful"},
    "empty": {"reflective", "contemplative", "restorative"},
    "energetic": {"energetic", "joyful", "social", "lively"},
    "excited": {"energetic", "joyful", "adventurous", "social"},
    "fearful": {"peaceful", "grounded", "calm"},
    "free": {"free-spirited", "refreshing", "adventurous"},
    "happy": {"joyful", "content", "social", "refreshing"},
    "healing": {"restorative", "peaceful", "grounded"},
    "heartbroken": {"melancholy", "reflective", "restorative"},
    "hopeful": {"hopeful", "refreshing", "dreamy"},
    "lonely": {"solitary", "reflective", "contemplative", "calm"},
    "lost": {"reflective", "contemplative", "grounded"},
    "love": {"romantic", "dreamy", "hopeful"},
    "melancholy": {"melancholy", "reflective", "solitary"},
    "nervous": {"calm", "peaceful", "grounded"},
    "nostalgic": {"nostalgic", "timeless", "reflective"},
    "overwhelmed": {"calm", "quiet", "restorative", "slow-paced"},
    "peaceful": {"peaceful", "calm", "serene", "quiet"},
    "restless": {"adventurous", "refreshing", "free-spirited", "urban"},
    "romantic": {"romantic", "dreamy", "hopeful"},
    "sad": {"melancholy", "reflective", "restorative", "solitary"},
    "sadness": {"melancholy", "reflective", "restorative", "solitary"},
    "scared": {"peaceful", "grounded", "calm"},
    "stressed": {"calm", "peaceful", "restorative", "refreshing"},
    "stress": {"calm", "peaceful", "restorative", "refreshing"},
    "tired": {"restorative", "slow-paced", "peaceful", "content"},
    "worn-out": {"restorative", "slow-paced", "peaceful"},
}


def _normalize_tag(tag: str) -> str:
    return re.sub(r"[\s_]+", "-", tag.strip().lower())


def _expand_tags(tags: list[str]) -> set[str]:
    expanded = set()
    for tag in tags:
        normalized = _normalize_tag(tag)
        if not normalized:
            continue
        expanded.add(normalized)
        expanded.update(EMOTION_TAG_ALIASES.get(normalized, set()))
    return expanded


def _localized(row: sqlite3.Row, field: str, language: str) -> str:
    if language == "ko":
        localized = row[f"{field}_ko"]
        if localized:
            return localized
    return row[field]


def _localized_pair(row: sqlite3.Row, field: str) -> LocalizedText:
    return LocalizedText(
        en=row[field],
        ko=row[f"{field}_ko"] or row[field],
    )


def _row_value(row: sqlite3.Row, field: str, default: str = "") -> str:
    try:
        value = row[field]
    except (KeyError, IndexError):
        return default
    return value or default


def _row_to_place(row: sqlite3.Row, score: int = 0, language: str = "en") -> PlaceOut:
    return PlaceOut(
        id=row["id"],
        city=row["city"],
        name=_localized(row, "name", language),
        description=_localized(row, "description", language),
        mood_tags=_localized(row, "mood_tags", language),
        name_i18n=_localized_pair(row, "name"),
        description_i18n=_localized_pair(row, "description"),
        mood_tags_i18n=_localized_pair(row, "mood_tags"),
        image_url=row["image_url"],
        match_score=score,
    )


def _row_to_postcard(
    row: sqlite3.Row,
    language: str = "en",
    places_by_id: dict[int, sqlite3.Row] | None = None,
) -> PostcardOut:
    places_by_id = places_by_id or {}

    place_name = row["place_name"]
    place_name_i18n = LocalizedText(en=place_name, ko=place_name)
    if row["place_id"] in places_by_id:
        place_row = places_by_id[row["place_id"]]
        place_name_i18n = _localized_pair(place_row, "name")
        place_name = place_name_i18n.ko if language == "ko" else place_name_i18n.en

    title_en = _row_value(row, "title_en", row["title"])
    title_ko = _row_value(row, "title_ko", row["title"])
    message_en = _row_value(row, "message_en", row["message"])
    message_ko = _row_value(row, "message_ko", row["message"])

    return PostcardOut(
        id=row["id"],
        city=row["city"],
        place_name=place_name,
        place_name_i18n=place_name_i18n,
        title=title_ko if language == "ko" else title_en,
        message=message_ko if language == "ko" else message_en,
        title_i18n=LocalizedText(en=title_en, ko=title_ko),
        message_i18n=LocalizedText(en=message_en, ko=message_ko),
        review=row["review"],
        image_base64=row["image_base64"],
        created_at=row["created_at"],
    )


def _rank_places_by_tags(
    places: list[sqlite3.Row], tags: list[str], language: str = "en"
) -> list[PlaceOut]:
    tag_set = _expand_tags(tags)
    scored = []
    for place in places:
        # Matching always uses the canonical English mood_tags, regardless of
        # display language, since the AI always extracts tags in English.
        place_tags = {_normalize_tag(t) for t in place["mood_tags"].split(",")}
        score = len(tag_set & place_tags)
        scored.append((score, place))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [
        _row_to_place(place, score, language)
        for score, place in scored
        if score > 0
    ]


def _english_tags(tags: list[dict[str, str] | str]) -> list[str]:
    values = []
    for tag in tags:
        if isinstance(tag, dict):
            values.append(str(tag.get("en", "")))
        else:
            values.append(str(tag))
    return values


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    if not payload.mood_text.strip():
        raise HTTPException(status_code=400, detail="mood_text must not be empty")

    places = database.get_places_by_city(payload.city)
    if not places:
        raise HTTPException(
            status_code=404, detail=f"No places found for city '{payload.city}'"
        )

    try:
        analysis = ai_service.analyze_mood(payload.city, payload.mood_text, payload.language)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {exc}") from exc

    ranked = _rank_places_by_tags(places, _english_tags(analysis["tags"]), payload.language)
    top_places = ranked[:3]

    return AnalyzeResponse(clue=analysis["clue"], tags=analysis["tags"], places=top_places)


@app.post("/api/postcard", response_model=PostcardOut)
def create_postcard(payload: PostcardRequest) -> PostcardOut:
    if not payload.review.strip():
        raise HTTPException(status_code=400, detail="review must not be empty")

    places = database.get_places_by_city(payload.city)
    if not places:
        raise HTTPException(
            status_code=404, detail=f"No places found for city '{payload.city}'"
        )

    place = next((p for p in places if p["id"] == payload.place_id), None)
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")

    place_name = _localized(place, "name", payload.language)
    place_name_en = _localized(place, "name", "en")
    place_name_ko = _localized(place, "name", "ko")

    try:
        generated = ai_service.generate_postcard(
            city=payload.city,
            place_name=place_name,
            review=payload.review,
            language=payload.language,
            place_name_en=place_name_en,
            place_name_ko=place_name_ko,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Postcard generation failed: {exc}"
        ) from exc

    image_base64 = ai_service.generate_postcard_image(
        city=payload.city, place_name=place["name"], review=payload.review
    )

    row = database.insert_postcard(
        city=payload.city,
        place_name=place_name,
        title=generated["title"]["en"],
        message=generated["message"]["en"],
        review=payload.review,
        image_base64=image_base64,
        place_id=place["id"],
        title_en=generated["title"]["en"],
        message_en=generated["message"]["en"],
        title_ko=generated["title"]["ko"],
        message_ko=generated["message"]["ko"],
    )
    places_by_id = {p["id"]: p for p in places}
    return _row_to_postcard(row, payload.language, places_by_id)


@app.get("/api/archive", response_model=list[PostcardOut])
def archive(language: str = "en") -> list[PostcardOut]:
    rows = database.get_all_postcards()
    places_by_id = {p["id"]: p for p in database.get_all_places()}
    return [_row_to_postcard(row, language, places_by_id) for row in rows]


@app.get("/api/places", response_model=list[PlaceOut])
def list_places(city: str | None = None, language: str = "en") -> list[PlaceOut]:
    rows = database.get_places_by_city(city) if city else database.get_all_places()
    return [_row_to_place(row, language=language) for row in rows]
