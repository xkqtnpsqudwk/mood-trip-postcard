"""FastAPI application for MoodTrip."""
import base64
import math
import sqlite3
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

import ai_service
import auth
import database
import tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    _cleanup_orphaned_postcard_images()
    yield


app = FastAPI(title="MoodTrip API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR = Path(__file__).parent / "uploads"
POSTCARD_IMAGES_DIR = UPLOADS_DIR / "postcards"
POSTCARD_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


def _save_postcard_image(image_base64: str) -> str:
    """Write a base64-encoded image to disk and return its /uploads-relative path."""
    filename = f"{uuid.uuid4().hex}.jpg"
    (POSTCARD_IMAGES_DIR / filename).write_bytes(base64.b64decode(image_base64))
    return f"postcards/{filename}"


def _ensure_postcard_image_file(row: sqlite3.Row) -> sqlite3.Row:
    """Lazily migrate a legacy inline-base64 postcard image onto disk."""
    if row["image_path"] or not row["image_base64"]:
        return row
    image_path = _save_postcard_image(row["image_base64"])
    return database.set_postcard_image_path(row["id"], image_path)


def _read_postcard_image_base64(row: sqlite3.Row) -> str | None:
    """Read a postcard's image as base64, from disk or the legacy DB blob."""
    if row["image_path"]:
        return base64.b64encode((UPLOADS_DIR / row["image_path"]).read_bytes()).decode()
    return row["image_base64"]


def _cleanup_orphaned_postcard_images() -> None:
    """Delete postcard image files no longer referenced by any DB row.

    Runs once at startup. Files can go orphaned when a request fails between
    saving the image and recording it (e.g. a final-trip-postcard call that's
    never persisted), or after a legacy row gets migrated onto a new file.
    """
    referenced = database.get_all_postcard_image_paths()
    for file_path in POSTCARD_IMAGES_DIR.glob("*"):
        if not file_path.is_file():
            continue
        if f"postcards/{file_path.name}" not in referenced:
            file_path.unlink(missing_ok=True)


class AnalyzeRequest(BaseModel):
    city: str
    mood_text: str
    language: str = "en"
    latitude: float | None = None
    longitude: float | None = None
    excluded_place_names: list[str] = []


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


class MapPosition(BaseModel):
    x: float
    y: float


class Coordinates(BaseModel):
    lat: float
    lng: float


class PlaceOut(BaseModel):
    id: int
    city: str
    name: str
    description: str
    name_i18n: LocalizedText
    description_i18n: LocalizedText
    type: str = ""
    type_i18n: LocalizedText
    duration_labels: list[str] = []
    duration_label_i18n: LocalizedText
    reason: str = ""
    reason_i18n: LocalizedText
    intensity_level: str = "MEDIUM"
    map_position: MapPosition
    coordinates: Coordinates
    distance_km: float | None = None


class AnalyzeResponse(BaseModel):
    clue: LocalizedText
    places: list[PlaceOut]


class ChatMessage(BaseModel):
    role: str
    content: str


class PlaceChatRequest(BaseModel):
    city: str
    place_name: str
    place_name_en: str = ""
    place_name_ko: str = ""
    place_type: str = ""
    place_description: str = ""
    place_reason: str = ""
    mood_text: str = ""
    clue: str = ""
    messages: list[ChatMessage] = []
    language: str = "en"


class PlaceChatResponse(BaseModel):
    reply: str


class PostcardRequest(BaseModel):
    city: str
    place_name: str
    place_name_en: str
    place_name_ko: str
    review: str
    language: str = "en"
    trip_id: str | None = None
    image_base64: str | None = None
    photo_base64_list: list[str] = []
    mood_text: str = ""
    clue_en: str = ""
    clue_ko: str = ""


class NextPlaceRequest(BaseModel):
    next_place_name_en: str
    next_place_name_ko: str


class FinalTripPostcardRequest(BaseModel):
    language: str = "en"


class PostcardOut(BaseModel):
    id: int
    artifact_type: str = "record"
    city: str
    place_name: str
    place_name_i18n: LocalizedText
    title: str
    message: str
    title_i18n: LocalizedText
    message_i18n: LocalizedText
    review: str
    image_url: str | None = None
    created_at: str
    trip_id: str
    next_place_name: str | None = None
    next_place_name_i18n: LocalizedText | None = None
    mood_text: str = ""
    clue_i18n: LocalizedText | None = None


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


def _row_value(row: sqlite3.Row, field: str, default: str = "") -> str:
    try:
        value = row[field]
    except (KeyError, IndexError):
        return default
    return value or default


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    earth_radius_km = 6371.0
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    )
    return earth_radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _place_out(
    index: int,
    place: dict,
    city: str,
    language: str = "en",
    user_lat: float | None = None,
    user_lng: float | None = None,
) -> PlaceOut:
    duration_code = place["duration"]
    coordinates = place["coordinates"]

    distance_km = None
    if user_lat is not None and user_lng is not None:
        distance_km = _haversine_km(user_lat, user_lng, coordinates["lat"], coordinates["lng"])

    return PlaceOut(
        id=index,
        city=city,
        name=place["name"]["ko" if language == "ko" else "en"],
        description=place["description"]["ko" if language == "ko" else "en"],
        name_i18n=LocalizedText(**place["name"]),
        description_i18n=LocalizedText(**place["description"]),
        type=place["type"]["ko" if language == "ko" else "en"],
        type_i18n=LocalizedText(**place["type"]),
        duration_labels=tags.labels(tags.AVAILABLE_TIME, [duration_code], language),
        duration_label_i18n=LocalizedText(
            en=tags.label(tags.AVAILABLE_TIME, duration_code, "en"),
            ko=tags.label(tags.AVAILABLE_TIME, duration_code, "ko"),
        ),
        reason=place["reason"]["ko" if language == "ko" else "en"],
        reason_i18n=LocalizedText(**place["reason"]),
        intensity_level=place["intensity_level"],
        map_position=MapPosition(**place["map_position"]),
        coordinates=Coordinates(lat=coordinates["lat"], lng=coordinates["lng"]),
        distance_km=round(distance_km, 1) if distance_km is not None else None,
    )


def _row_to_postcard(row: sqlite3.Row, language: str = "en") -> PostcardOut:
    place_name_en = _row_value(row, "place_name_en", row["place_name"])
    place_name_ko = _row_value(row, "place_name_ko", row["place_name"])
    place_name = place_name_ko if language == "ko" else place_name_en
    place_name_i18n = LocalizedText(en=place_name_en, ko=place_name_ko)

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

    clue_en = _row_value(row, "clue_en")
    clue_ko = _row_value(row, "clue_ko")
    clue_i18n = LocalizedText(en=clue_en, ko=clue_ko or clue_en) if clue_en else None

    return PostcardOut(
        id=row["id"],
        artifact_type=_row_value(row, "artifact_type", "record"),
        city=row["city"],
        place_name=place_name,
        place_name_i18n=place_name_i18n,
        title=title_ko if language == "ko" else title_en,
        message=message_ko if language == "ko" else message_en,
        title_i18n=LocalizedText(en=title_en, ko=title_ko),
        message_i18n=LocalizedText(en=message_en, ko=message_ko),
        review=row["review"],
        image_url=f"/uploads/{row['image_path']}" if row["image_path"] else None,
        created_at=row["created_at"],
        trip_id=_row_value(row, "trip_id"),
        next_place_name=next_place_name,
        next_place_name_i18n=next_place_name_i18n,
        mood_text=_row_value(row, "mood_text"),
        clue_i18n=clue_i18n,
    )


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(
    payload: AnalyzeRequest, user: sqlite3.Row | None = Depends(get_current_user)
) -> AnalyzeResponse:
    if not payload.mood_text.strip():
        raise HTTPException(status_code=400, detail="mood_text must not be empty")

    # Logged-in users can save a free-text travel-style profile (My Page)
    # that is applied automatically here; guests get plain mood-text matching.
    prefs_row = database.get_user_preferences(user["id"]) if user else None
    style_text = _row_value(prefs_row, "style_text") if prefs_row else ""

    try:
        recommendation = ai_service.recommend_trip(
            payload.city,
            payload.mood_text,
            payload.language,
            style_text=style_text,
            excluded_place_names=payload.excluded_place_names,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI recommendation failed: {exc}") from exc

    places_out = [
        _place_out(
            index,
            place,
            payload.city,
            payload.language,
            user_lat=payload.latitude,
            user_lng=payload.longitude,
        )
        for index, place in enumerate(recommendation["places"][:1])
    ]

    return AnalyzeResponse(
        clue=recommendation["clue"],
        places=places_out,
    )


@app.post("/api/place-chat", response_model=PlaceChatResponse)
def place_chat(
    payload: PlaceChatRequest, user: sqlite3.Row | None = Depends(get_current_user)
) -> PlaceChatResponse:
    if not payload.place_name.strip():
        raise HTTPException(status_code=400, detail="place_name must not be empty")
    if not payload.messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")

    prefs_row = database.get_user_preferences(user["id"]) if user else None
    style_text = _row_value(prefs_row, "style_text") if prefs_row else ""
    try:
        reply = ai_service.chat_about_place(
            city=payload.city,
            place_name=payload.place_name,
            place_type=payload.place_type,
            place_description=payload.place_description,
            place_reason=payload.place_reason,
            mood_text=payload.mood_text,
            clue=payload.clue,
            messages=[message.model_dump() for message in payload.messages],
            language=payload.language,
            style_text=style_text,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Place chat failed: {exc}") from exc
    return PlaceChatResponse(reply=reply)


@app.post("/api/postcard", response_model=PostcardOut)
def create_postcard(
    payload: PostcardRequest, user: sqlite3.Row = Depends(require_user)
) -> PostcardOut:
    if not payload.review.strip():
        raise HTTPException(status_code=400, detail="review must not be empty")

    source_images = payload.photo_base64_list or (
        [payload.image_base64] if payload.image_base64 else []
    )
    try:
        image_base64 = ai_service.generate_postcard_image(
            city=payload.city,
            place_name=payload.place_name,
            message=payload.review,
            source_images_base64=source_images,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Postcard image generation failed: {exc}"
        ) from exc

    trip_id = payload.trip_id or str(uuid.uuid4())
    image_path = _save_postcard_image(image_base64)

    # next_place is filled in later, via update_postcard_next_place, once the
    # traveler actually visits another stop on this trip — it should never be
    # a prediction made before that stop is known.
    row = database.insert_postcard(
        city=payload.city,
        place_name=payload.place_name,
        place_name_en=payload.place_name_en,
        place_name_ko=payload.place_name_ko,
        title="",
        message="",
        review=payload.review,
        trip_id=trip_id,
        image_path=image_path,
        title_en="",
        message_en="",
        title_ko="",
        message_ko="",
        user_id=user["id"],
        mood_text=payload.mood_text,
        clue_en=payload.clue_en,
        clue_ko=payload.clue_ko,
        artifact_type="record",
    )
    return _row_to_postcard(row, payload.language)


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

    row = database.update_postcard_next_place(
        postcard_id=postcard_id,
        next_place_name_en=payload.next_place_name_en,
        next_place_name_ko=payload.next_place_name_ko,
    )
    row = _ensure_postcard_image_file(row)
    return _row_to_postcard(row, language)


_CITY_NAMES_KO = {"Paris": "파리", "Seoul": "서울"}


@app.post("/api/trip/{trip_id}/final-postcard", response_model=PostcardOut)
def create_final_trip_postcard(
    trip_id: str,
    payload: FinalTripPostcardRequest,
    user: sqlite3.Row = Depends(require_user),
) -> PostcardOut:
    rows = database.get_records_by_trip(trip_id, user["id"])
    if not rows:
        raise HTTPException(status_code=404, detail="Trip records not found")

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
                "image_base64": _read_postcard_image_base64(row),
            }
        )

    # Weave each record's own clue (already saved when it was recommended)
    # into one new closing line via a text model call, rather than a plain
    # user note or a mechanical join of the existing clues.
    clue_pairs = [
        {
            "en": _row_value(row, "clue_en"),
            "ko": _row_value(row, "clue_ko"),
        }
        for row in rows
        if _row_value(row, "clue_en") or _row_value(row, "clue_ko")
    ]

    try:
        closing = ai_service.generate_trip_closing_note(city, clue_pairs)
        generated = ai_service.generate_trip_postcard(
            city=city,
            postcards=trip_items,
            language=payload.language,
            closing_note=closing["en"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Final postcard generation failed: {exc}"
        ) from exc

    place_name_en = f"{city} Trip"
    place_name_ko = f"{_CITY_NAMES_KO.get(city, city)} 여행 엽서"
    image_path = _save_postcard_image(generated["image_base64"])
    closing_note = closing["ko"] if payload.language == "ko" else closing["en"]

    # Persisted like any other postcard (same trip_id) so the trip's closing
    # memory survives a refresh and shows up in the archive instead of only
    # existing for the one render right after "Finish this trip". The back
    # shows the AI-woven closing line instead of a user-typed note.
    row = database.insert_postcard(
        city=city,
        place_name=place_name_en,
        place_name_en=place_name_en,
        place_name_ko=place_name_ko,
        title="",
        message="",
        review=closing_note,
        trip_id=trip_id,
        image_path=image_path,
        title_en="",
        message_en="",
        title_ko="",
        message_ko="",
        user_id=user["id"],
        clue_en=closing["en"],
        clue_ko=closing["ko"],
        artifact_type="postcard",
    )
    return _row_to_postcard(row, payload.language)


@app.get("/api/archive", response_model=list[PostcardOut])
def archive(
    language: str = "en", user: sqlite3.Row | None = Depends(get_current_user)
) -> list[PostcardOut]:
    rows = database.get_all_postcards(user["id"] if user else None)
    rows = [_ensure_postcard_image_file(row) for row in rows]
    return [_row_to_postcard(row, language) for row in rows]
