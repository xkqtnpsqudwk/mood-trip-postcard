"""FastAPI application for MoodTrip."""
import sqlite3
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

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


app = FastAPI(title="MoodTrip API", lifespan=lifespan)

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
    style_text: str = ""


class PreferencesOut(BaseModel):
    style_text: str = ""


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
    name_i18n: LocalizedText
    description_i18n: LocalizedText
    image_url: str | None = None
    match_score: int = 0
    type: str = ""
    type_i18n: LocalizedText
    duration_labels: list[str] = []
    duration_label_i18n: LocalizedText
    reason: str = ""
    reason_i18n: LocalizedText
    avoid_warnings: list[str] = []
    avoid_warning_i18n: LocalizedText


class AnalyzeResponse(BaseModel):
    clue: LocalizedText
    tags: list[LocalizedTag]
    avoid_tags: list[LocalizedTag] = []
    places: list[PlaceOut]


class PostcardRequest(BaseModel):
    city: str
    place_id: int
    review: str
    language: str = "en"
    trip_id: str | None = None
    image_base64: str | None = None
    photo_base64_list: list[str] = []


class NextPlaceRequest(BaseModel):
    next_place_id: int


class FinalTripPostcardRequest(BaseModel):
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
    return PreferencesOut(style_text=_row_value(row, "style_text"))


@app.put("/api/preferences", response_model=PreferencesOut)
def put_preferences(
    payload: PreferencesIn, user: sqlite3.Row = Depends(require_user)
) -> PreferencesOut:
    row = database.upsert_user_preferences(user_id=user["id"], style_text=payload.style_text)
    return PreferencesOut(style_text=_row_value(row, "style_text"))


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
    avoid_conflicts = avoid_conflicts or []
    return PlaceOut(
        id=row["id"],
        city=row["city"],
        name=_localized(row, "name", language),
        description=_localized(row, "description", language),
        name_i18n=_localized_pair(row, "name"),
        description_i18n=_localized_pair(row, "description"),
        image_url=row["image_url"],
        match_score=score,
        type=_localized(row, "type", language),
        type_i18n=_localized_pair(row, "type"),
        duration_labels=tags.labels(tags.AVAILABLE_TIME, duration_codes, language),
        duration_label_i18n=LocalizedText(
            en=" / ".join(tags.labels(tags.AVAILABLE_TIME, duration_codes, "en")),
            ko=" / ".join(tags.labels(tags.AVAILABLE_TIME, duration_codes, "ko")),
        ),
        reason=_localized(row, "reason", language),
        reason_i18n=_localized_pair(row, "reason"),
        avoid_warnings=tags.labels(tags.AVOID, avoid_conflicts, language),
        avoid_warning_i18n=LocalizedText(
            en=", ".join(tags.labels(tags.AVOID, avoid_conflicts, "en")),
            ko=", ".join(tags.labels(tags.AVOID, avoid_conflicts, "ko")),
        ),
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


def _rank_places(
    places: list[sqlite3.Row],
    preference_codes: set[str],
    avoid_codes: set[str],
    language: str = "en",
) -> list[PlaceOut]:
    """Score places by saved travel style, not by the current mood sentence.

    The current mood is used to create the poetic clue and display tags. Place
    ranking stays anchored to the user's saved preferences/avoidances so the
    recommendation feels consistent rather than pretending to infer exact
    geography from a mood sentence.
    """
    user_avoid = {c.strip().lower() for c in avoid_codes if c}

    scored = []
    for index, place in enumerate(places):
        place_preferences = _code_set(_row_value(place, "preference_tags"))
        place_avoid = _code_set(_row_value(place, "avoid_tags"))

        preference_overlap = len(preference_codes & place_preferences)
        conflicts = sorted(user_avoid & place_avoid)
        score = preference_overlap * 4 - len(conflicts) * 3
        if not preference_codes:
            score = max(1, 20 - index)

        scored.append((score, place, conflicts))

    scored.sort(key=lambda triple: triple[0], reverse=True)
    return [
        _row_to_place(place, score, language, conflicts)
        for score, place, conflicts in scored
    ]


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

    # Logged-in users can save a free-text travel-style profile (My Page)
    # that is applied automatically here; guests get plain mood-text matching.
    prefs_row = database.get_user_preferences(user["id"]) if user else None
    style_text = _row_value(prefs_row, "style_text") if prefs_row else ""

    try:
        analysis = ai_service.analyze_mood(
            payload.city,
            payload.mood_text,
            payload.language,
            style_text=style_text,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {exc}") from exc

    combined_tags = [LocalizedTag(en=t["en"], ko=t["ko"]) for t in analysis["tags"]]
    avoid_tag_out = [_tag_out(tags.AVOID, code) for code in analysis["avoid"]]

    try:
        style_profile = ai_service.extract_travel_style(style_text, payload.language)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Travel style extraction failed: {exc}"
        ) from exc

    preference_codes = set(style_profile["preferences"])
    ranking_avoid_codes = set(style_profile["avoid"])

    ranked = _rank_places(
        places,
        preference_codes=preference_codes,
        avoid_codes=ranking_avoid_codes,
        language=payload.language,
    )
    # Return a larger pool than a single card grid needs so the frontend can
    # offer more stops as the user continues the same trip to nearby places.
    top_places = ranked[:6]

    return AnalyzeResponse(
        clue=analysis["clue"],
        tags=combined_tags,
        avoid_tags=avoid_tag_out,
        places=top_places,
    )


@app.post("/api/postcard", response_model=PostcardOut)
def create_postcard(
    payload: PostcardRequest, user: sqlite3.Row = Depends(require_user)
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

    source_images = payload.photo_base64_list or (
        [payload.image_base64] if payload.image_base64 else []
    )
    try:
        image_base64 = ai_service.generate_postcard_image(
            city=payload.city,
            place_name=place["name"],
            message=generated["message"]["en"],
            source_images_base64=source_images,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Postcard image generation failed: {exc}"
        ) from exc

    trip_id = payload.trip_id or str(uuid.uuid4())

    # next_place is filled in later, via update_postcard_next_place, once the
    # traveler actually visits another stop on this trip — it should never be
    # a prediction made before that stop is known.
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
        user_id=user["id"],
    )
    places_by_id = {p["id"]: p for p in places}
    return _row_to_postcard(row, payload.language, places_by_id)


@app.patch("/api/postcard/{postcard_id}/next-place", response_model=PostcardOut)
def update_postcard_next_place(
    postcard_id: int,
    payload: NextPlaceRequest,
    language: str = "en",
    user: sqlite3.Row = Depends(require_user),
) -> PostcardOut:
    postcard_row = database.get_postcard_by_id(postcard_id)
    if postcard_row is None or postcard_row["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Postcard not found")

    places = database.get_places_by_city(postcard_row["city"])
    next_place = next((p for p in places if p["id"] == payload.next_place_id), None)
    if next_place is None:
        raise HTTPException(status_code=404, detail="Place not found")

    row = database.update_postcard_next_place(
        postcard_id=postcard_id,
        next_place_id=next_place["id"],
        next_place_name_en=_localized(next_place, "name", "en"),
        next_place_name_ko=_localized(next_place, "name", "ko"),
    )
    places_by_id = {p["id"]: p for p in places}
    return _row_to_postcard(row, language, places_by_id)


@app.post("/api/trip/{trip_id}/final-postcard", response_model=PostcardOut)
def create_final_trip_postcard(
    trip_id: str,
    payload: FinalTripPostcardRequest,
    user: sqlite3.Row = Depends(require_user),
) -> PostcardOut:
    rows = database.get_postcards_by_trip(trip_id, user["id"])
    if not rows:
        raise HTTPException(status_code=404, detail="Trip postcards not found")

    city = rows[0]["city"]
    trip_items = []
    for row in rows:
        title = _row_value(row, "title_en", row["title"])
        message = _row_value(row, "message_en", row["message"])
        trip_items.append(
            {
                "place_name": row["place_name"],
                "title": title,
                "message": message,
                "review": row["review"],
                "image_base64": row["image_base64"],
            }
        )

    try:
        generated = ai_service.generate_trip_postcard(
            city=city,
            postcards=trip_items,
            language=payload.language,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Final postcard generation failed: {exc}"
        ) from exc

    place_name_i18n = LocalizedText(en=f"{city} Trip", ko=f"{city} 여정")
    return PostcardOut(
        id=0,
        city=city,
        place_name=place_name_i18n.ko if payload.language == "ko" else place_name_i18n.en,
        place_name_i18n=place_name_i18n,
        title=generated["title"]["ko"] if payload.language == "ko" else generated["title"]["en"],
        message=generated["message"]["ko"]
        if payload.language == "ko"
        else generated["message"]["en"],
        title_i18n=LocalizedText(
            en=generated["title"]["en"],
            ko=generated["title"]["ko"],
        ),
        message_i18n=LocalizedText(
            en=generated["message"]["en"],
            ko=generated["message"]["ko"],
        ),
        review="\n".join(item["review"] for item in trip_items if item["review"]),
        image_base64=generated["image_base64"],
        created_at=datetime.utcnow().isoformat(),
        trip_id=trip_id,
        next_place_id=None,
        next_place_name=None,
        next_place_name_i18n=None,
    )


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
