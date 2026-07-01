"""FastAPI application for Mood Trip Postcard."""
import random
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


class PlaceOut(BaseModel):
    id: int
    city: str
    name: str
    description: str
    mood_tags: str
    image_url: str | None = None
    match_score: int = 0


class AnalyzeResponse(BaseModel):
    clue: str
    tags: list[str]
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
    title: str
    message: str
    review: str
    next_recommendation: str | None
    image_base64: str | None = None
    created_at: str


def _localized(row: sqlite3.Row, field: str, language: str) -> str:
    if language == "ko":
        localized = row[f"{field}_ko"]
        if localized:
            return localized
    return row[field]


def _row_to_place(row: sqlite3.Row, score: int = 0, language: str = "en") -> PlaceOut:
    return PlaceOut(
        id=row["id"],
        city=row["city"],
        name=_localized(row, "name", language),
        description=_localized(row, "description", language),
        mood_tags=_localized(row, "mood_tags", language),
        image_url=row["image_url"],
        match_score=score,
    )


def _row_to_postcard(row: sqlite3.Row) -> PostcardOut:
    return PostcardOut(
        id=row["id"],
        city=row["city"],
        place_name=row["place_name"],
        title=row["title"],
        message=row["message"],
        review=row["review"],
        next_recommendation=row["next_recommendation"],
        image_base64=row["image_base64"],
        created_at=row["created_at"],
    )


def _rank_places_by_tags(
    places: list[sqlite3.Row], tags: list[str], language: str = "en"
) -> list[PlaceOut]:
    tag_set = {t.lower() for t in tags}
    scored = []
    for place in places:
        # Matching always uses the canonical English mood_tags, regardless of
        # display language, since the AI always extracts tags in English.
        place_tags = {t.strip().lower() for t in place["mood_tags"].split(",")}
        score = len(tag_set & place_tags)
        scored.append((score, place))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [_row_to_place(place, score, language) for score, place in scored]


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

    ranked = _rank_places_by_tags(places, analysis["tags"], payload.language)
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

    other_places = [p for p in places if p["id"] != payload.place_id]
    next_place = random.choice(other_places) if other_places else place

    place_name = _localized(place, "name", payload.language)
    next_place_name = _localized(next_place, "name", payload.language)

    try:
        generated = ai_service.generate_postcard(
            city=payload.city,
            place_name=place_name,
            review=payload.review,
            next_place_name=next_place_name,
            language=payload.language,
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
        title=generated["title"],
        message=generated["message"],
        review=payload.review,
        next_recommendation=next_place_name,
        image_base64=image_base64,
    )
    return _row_to_postcard(row)


@app.get("/api/archive", response_model=list[PostcardOut])
def archive() -> list[PostcardOut]:
    rows = database.get_all_postcards()
    return [_row_to_postcard(row) for row in rows]


@app.get("/api/places", response_model=list[PlaceOut])
def list_places(city: str | None = None, language: str = "en") -> list[PlaceOut]:
    rows = database.get_places_by_city(city) if city else database.get_all_places()
    return [_row_to_place(row, language=language) for row in rows]
