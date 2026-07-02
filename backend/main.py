"""FastAPI application for Mood Trip Postcard."""
import re
import sqlite3
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

import ai_service
import auth
import database
import tags


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


class SignupRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthOut(BaseModel):
    token: str
    username: str


class UserOut(BaseModel):
    username: str


class PreferencesIn(BaseModel):
    available_time: str | None = None
    mobility: str | None = None
    environment: str | None = None
    avoid: list[str] = []
    preferences: list[str] = []


class PreferencesOut(BaseModel):
    available_time: str | None = None
    mobility: str | None = None
    environment: str | None = None
    avoid: list[str] = []
    preferences: list[str] = []


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
    type: str = ""
    type_i18n: LocalizedText
    duration_labels: list[str] = []
    reason: str = ""
    reason_i18n: LocalizedText
    avoid_warnings: list[str] = []


class AnalyzeResponse(BaseModel):
    clue: LocalizedText
    tags: list[LocalizedTag]
    situation_tags: list[LocalizedTag] = []
    avoid_tags: list[LocalizedTag] = []
    places: list[PlaceOut]


class PostcardRequest(BaseModel):
    city: str
    place_id: int
    review: str
    language: str = "en"
    trip_id: str | None = None
    next_place_id: int | None = None


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
    trip_id: str
    next_place_id: int | None = None
    next_place_name: str | None = None
    next_place_name_i18n: LocalizedText | None = None


def get_current_user(authorization: str | None = Header(default=None)) -> sqlite3.Row | None:
    """Optional auth: returns the user row for a valid bearer token, else None.
    Endpoints that work for both guests and logged-in users depend on this."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        return None
    return database.get_user_by_token(token)


def require_user(user: sqlite3.Row | None = Depends(get_current_user)) -> sqlite3.Row:
    """Required auth: raises 401 when no valid session is presented."""
    if user is None:
        raise HTTPException(status_code=401, detail="Login required")
    return user


@app.post("/api/auth/signup", response_model=AuthOut)
def signup(payload: SignupRequest) -> AuthOut:
    username = payload.username.strip()
    if not username or not payload.password:
        raise HTTPException(status_code=400, detail="username and password are required")
    if len(payload.password) < 4:
        raise HTTPException(status_code=400, detail="password must be at least 4 characters")
    if database.get_user_by_username(username):
        raise HTTPException(status_code=409, detail="username is already taken")

    user = database.create_user(username, auth.hash_password(payload.password))
    token = auth.generate_token()
    database.create_session(token, user["id"])
    return AuthOut(token=token, username=user["username"])


@app.post("/api/auth/login", response_model=AuthOut)
def login(payload: LoginRequest) -> AuthOut:
    user = database.get_user_by_username(payload.username.strip())
    if not user or not auth.verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = auth.generate_token()
    database.create_session(token, user["id"])
    return AuthOut(token=token, username=user["username"])


@app.post("/api/auth/logout")
def logout(authorization: str | None = Header(default=None)) -> dict:
    if authorization and authorization.startswith("Bearer "):
        database.delete_session(authorization.removeprefix("Bearer ").strip())
    return {"ok": True}


@app.get("/api/auth/me", response_model=UserOut)
def me(user: sqlite3.Row = Depends(require_user)) -> UserOut:
    return UserOut(username=user["username"])


@app.get("/api/preferences", response_model=PreferencesOut)
def get_preferences(user: sqlite3.Row = Depends(require_user)) -> PreferencesOut:
    row = database.get_user_preferences(user["id"])
    if row is None:
        return PreferencesOut()
    return PreferencesOut(
        available_time=row["available_time"] or None,
        mobility=row["mobility"] or None,
        environment=row["environment"] or None,
        avoid=[v for v in (row["avoid"] or "").split(",") if v],
        preferences=[v for v in (row["preferences"] or "").split(",") if v],
    )


@app.put("/api/preferences", response_model=PreferencesOut)
def put_preferences(
    payload: PreferencesIn, user: sqlite3.Row = Depends(require_user)
) -> PreferencesOut:
    row = database.upsert_user_preferences(
        user_id=user["id"],
        available_time=payload.available_time or "",
        mobility=payload.mobility or "",
        environment=payload.environment or "",
        avoid=",".join(payload.avoid),
        preferences=",".join(payload.preferences),
    )
    return PreferencesOut(
        available_time=row["available_time"] or None,
        mobility=row["mobility"] or None,
        environment=row["environment"] or None,
        avoid=[v for v in (row["avoid"] or "").split(",") if v],
        preferences=[v for v in (row["preferences"] or "").split(",") if v],
    )


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
    "stuffy": {"refreshing", "riverside", "scenic"},
    "tired": {"restorative", "slow-paced", "peaceful", "content"},
    "worn-out": {"restorative", "slow-paced", "peaceful"},
}


def _normalize_tag(tag: str) -> str:
    return re.sub(r"[\s_]+", "-", tag.strip().lower())


def _expand_tags(tag_list: list[str]) -> set[str]:
    expanded = set()
    for tag in tag_list:
        normalized = _normalize_tag(tag)
        if not normalized:
            continue
        expanded.add(normalized)
        expanded.update(EMOTION_TAG_ALIASES.get(normalized, set()))
    return expanded


def _tag_set(value: str) -> set[str]:
    """Normalized (hyphenated) tag set, for fuzzy vibe/mood matching."""
    return {_normalize_tag(t) for t in (value or "").split(",") if t.strip()}


def _code_set(value: str) -> set[str]:
    """Exact fixed-vocabulary codes (see tags.py), for situation/avoid matching."""
    return {c.strip().lower() for c in (value or "").split(",") if c.strip()}


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


def _row_to_place(
    row: sqlite3.Row,
    score: int = 0,
    language: str = "en",
    avoid_conflicts: list[str] | None = None,
) -> PlaceOut:
    duration_codes = [c for c in _row_value(row, "duration").split(",") if c]
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
        type=_localized(row, "type", language),
        type_i18n=_localized_pair(row, "type"),
        duration_labels=tags.labels(tags.AVAILABLE_TIME, duration_codes, language),
        reason=_localized(row, "reason", language),
        reason_i18n=_localized_pair(row, "reason"),
        avoid_warnings=tags.labels(tags.AVOID, avoid_conflicts or [], language),
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

    next_place_name_en = _row_value(row, "next_place_name_en")
    next_place_name_ko = _row_value(row, "next_place_name_ko")
    next_place_name_i18n = None
    next_place_name = None
    if next_place_name_en:
        next_place_name_i18n = LocalizedText(
            en=next_place_name_en, ko=next_place_name_ko or next_place_name_en
        )
        next_place_name = (
            next_place_name_i18n.ko if language == "ko" else next_place_name_i18n.en
        )

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
        trip_id=_row_value(row, "trip_id"),
        next_place_id=row["next_place_id"],
        next_place_name=next_place_name,
        next_place_name_i18n=next_place_name_i18n,
    )


def _tag_out(vocab: dict, code: str) -> LocalizedTag:
    entry = vocab.get(code, {"en": code, "ko": code})
    return LocalizedTag(en=entry.get("en", code), ko=entry.get("ko", code))


def _combine_tags(*groups: list[LocalizedTag]) -> list[LocalizedTag]:
    seen: set[str] = set()
    combined: list[LocalizedTag] = []
    for group in groups:
        for tag in group:
            key = tag.en.strip().lower()
            if key and key not in seen:
                seen.add(key)
                combined.append(tag)
    return combined


def _rank_places(
    places: list[sqlite3.Row],
    vibe_tags: list[str],
    situation_codes: list[str],
    avoid_codes: list[str],
    available_time: str | None = None,
    language: str = "en",
) -> list[PlaceOut]:
    """Score places by overlap across three axes and penalize avoid conflicts.

    - vibe: user's emotions + preferences + AI-extracted free-text tags,
      matched (with alias expansion) against a place's mood_tags + preference_tags.
    - situation: companions/mobility/environment matched against situation_tags.
    - avoid: user's avoid selections matched against a place's avoid_tags,
      which lowers (not eliminates) that place's ranking.
    """
    user_vibe = _expand_tags(vibe_tags)
    user_situation = {c.strip().lower() for c in situation_codes if c}
    user_avoid = {c.strip().lower() for c in avoid_codes if c}

    scored = []
    for place in places:
        place_vibe = _tag_set(place["mood_tags"]) | _tag_set(_row_value(place, "preference_tags"))
        place_situation = _code_set(_row_value(place, "situation_tags"))
        place_avoid = _code_set(_row_value(place, "avoid_tags"))
        place_duration = [c for c in _row_value(place, "duration").split(",") if c]

        vibe_overlap = len(user_vibe & place_vibe)
        if vibe_overlap == 0:
            continue

        situation_overlap = len(user_situation & place_situation)
        duration_match = 1 if available_time and available_time in place_duration else 0
        conflicts = sorted(user_avoid & place_avoid)

        score = vibe_overlap * 2 + situation_overlap + duration_match - len(conflicts) * 2
        scored.append((score, place, conflicts))

    scored.sort(key=lambda triple: triple[0], reverse=True)
    return [
        _row_to_place(place, score, language, conflicts)
        for score, place, conflicts in scored
    ]


def _english_tags(tag_list: list[dict[str, str] | str]) -> list[str]:
    values = []
    for tag in tag_list:
        if isinstance(tag, dict):
            values.append(str(tag.get("en", "")))
        else:
            values.append(str(tag))
    return values


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(
    payload: AnalyzeRequest, user: sqlite3.Row | None = Depends(get_current_user)
) -> AnalyzeResponse:
    if not payload.mood_text.strip():
        raise HTTPException(status_code=400, detail="mood_text must not be empty")

    places = database.get_places_by_city(payload.city)
    if not places:
        raise HTTPException(
            status_code=404, detail=f"No places found for city '{payload.city}'"
        )

    # Logged-in users can save a personalization profile (My Page) that is
    # applied automatically here; guests get plain mood-text matching.
    prefs_row = database.get_user_preferences(user["id"]) if user else None
    available_time = prefs_row["available_time"] if prefs_row else None
    mobility = prefs_row["mobility"] if prefs_row else None
    environment = prefs_row["environment"] if prefs_row else None
    saved_avoid = [v for v in (prefs_row["avoid"] or "").split(",") if v] if prefs_row else []
    saved_preferences = (
        [v for v in (prefs_row["preferences"] or "").split(",") if v] if prefs_row else []
    )

    try:
        analysis = ai_service.analyze_mood(
            payload.city,
            payload.mood_text,
            payload.language,
            available_time=available_time,
            mobility=mobility,
            environment=environment,
            preferences=saved_preferences,
            avoid=saved_avoid,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {exc}") from exc

    ai_tag_out = [LocalizedTag(en=t["en"], ko=t["ko"]) for t in analysis["tags"]]
    preference_tag_out = [_tag_out(tags.PREFERENCES, code) for code in saved_preferences]
    combined_tags = _combine_tags(preference_tag_out, ai_tag_out)

    situation_tag_out = []
    if available_time:
        situation_tag_out.append(_tag_out(tags.AVAILABLE_TIME, available_time))
    if mobility:
        situation_tag_out.append(_tag_out(tags.MOBILITY, mobility))
    if environment:
        situation_tag_out.append(_tag_out(tags.ENVIRONMENT, environment))
    avoid_tag_out = [_tag_out(tags.AVOID, code) for code in saved_avoid]

    vibe_matching_tags = _english_tags(saved_preferences) + _english_tags(analysis["tags"])
    situation_codes = [c for c in (mobility, environment) if c]

    ranked = _rank_places(
        places,
        vibe_tags=vibe_matching_tags,
        situation_codes=situation_codes,
        avoid_codes=saved_avoid,
        available_time=available_time,
        language=payload.language,
    )
    # Return a larger pool than a single card grid needs so the frontend can
    # offer more stops as the user continues the same trip to nearby places.
    top_places = ranked[:6]

    return AnalyzeResponse(
        clue=analysis["clue"],
        tags=combined_tags,
        situation_tags=situation_tag_out,
        avoid_tags=avoid_tag_out,
        places=top_places,
    )


@app.post("/api/postcard", response_model=PostcardOut)
def create_postcard(
    payload: PostcardRequest, user: sqlite3.Row | None = Depends(get_current_user)
) -> PostcardOut:
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

    next_place = None
    if payload.next_place_id is not None:
        next_place = next((p for p in places if p["id"] == payload.next_place_id), None)
    next_place_id = next_place["id"] if next_place else None
    next_place_name_en = _localized(next_place, "name", "en") if next_place else None
    next_place_name_ko = _localized(next_place, "name", "ko") if next_place else None

    trip_id = payload.trip_id or str(uuid.uuid4())

    row = database.insert_postcard(
        city=payload.city,
        place_name=place_name,
        title=generated["title"]["en"],
        message=generated["message"]["en"],
        review=payload.review,
        trip_id=trip_id,
        image_base64=image_base64,
        place_id=place["id"],
        title_en=generated["title"]["en"],
        message_en=generated["message"]["en"],
        title_ko=generated["title"]["ko"],
        message_ko=generated["message"]["ko"],
        next_place_id=next_place_id,
        next_place_name_en=next_place_name_en,
        next_place_name_ko=next_place_name_ko,
        user_id=user["id"] if user else None,
    )
    places_by_id = {p["id"]: p for p in places}
    return _row_to_postcard(row, payload.language, places_by_id)


@app.get("/api/archive", response_model=list[PostcardOut])
def archive(
    language: str = "en", user: sqlite3.Row | None = Depends(get_current_user)
) -> list[PostcardOut]:
    rows = database.get_all_postcards(user["id"] if user else None)
    places_by_id = {p["id"]: p for p in database.get_all_places()}
    return [_row_to_postcard(row, language, places_by_id) for row in rows]


@app.get("/api/places", response_model=list[PlaceOut])
def list_places(city: str | None = None, language: str = "en") -> list[PlaceOut]:
    rows = database.get_places_by_city(city) if city else database.get_all_places()
    return [_row_to_place(row, language=language) for row in rows]
