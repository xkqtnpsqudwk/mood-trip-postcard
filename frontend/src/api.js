import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 90000,
});

export const analyzeMood = ({
  city,
  moodText,
  language,
  companions,
  availableTime,
  mobility,
  environment,
  avoid,
  emotions,
  emotionIntensity,
  preferences,
}) =>
  api
    .post("/analyze", {
      city,
      mood_text: moodText || "",
      language,
      companions: companions || null,
      available_time: availableTime || null,
      mobility: mobility || null,
      environment: environment || null,
      avoid: avoid || [],
      emotions: emotions || [],
      emotion_intensity: emotionIntensity || null,
      preferences: preferences || [],
    })
    .then((res) => res.data);

export const createPostcard = (
  city,
  placeId,
  review,
  language,
  tripId,
  nextPlaceId
) =>
  api
    .post("/postcard", {
      city,
      place_id: placeId,
      review,
      language,
      trip_id: tripId || null,
      next_place_id: nextPlaceId || null,
    })
    .then((res) => res.data);

export const fetchArchive = (language) =>
  api.get("/archive", { params: { language } }).then((res) => res.data);

export default api;
