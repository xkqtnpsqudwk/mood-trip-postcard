import axios from "axios";

const TOKEN_KEY = "mood-trip-postcard:token";

const api = axios.create({
  baseURL: "/api",
  timeout: 90000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

export const signup = (username, password) =>
  api.post("/auth/signup", { username, password }).then((res) => res.data);

export const login = (username, password) =>
  api.post("/auth/login", { username, password }).then((res) => res.data);

export const logout = () => api.post("/auth/logout").then((res) => res.data);

export const fetchMe = () => api.get("/auth/me").then((res) => res.data);

export const fetchPreferences = () => api.get("/preferences").then((res) => res.data);

export const savePreferences = (styleText) =>
  api.put("/preferences", { style_text: styleText || "" }).then((res) => res.data);

export const analyzeMood = ({
  city,
  moodText,
  language,
  latitude,
  longitude,
  excludedPlaceNames = [],
}) =>
  api
    .post("/analyze", {
      city,
      mood_text: moodText,
      language,
      latitude: latitude ?? null,
      longitude: longitude ?? null,
      excluded_place_names: excludedPlaceNames,
    })
    .then((res) => res.data);

export const createMomentRecord = (
  city,
  place,
  review,
  language,
  tripId,
  photoBase64List,
  moodText,
  clue
) =>
  api
    .post("/postcard", {
      city,
      place_name: place.name_i18n?.[language] || place.name,
      place_name_en: place.name_i18n?.en || place.name,
      place_name_ko: place.name_i18n?.ko || place.name,
      review,
      language,
      trip_id: tripId || null,
      photo_base64_list: photoBase64List || [],
      mood_text: moodText || "",
      clue_en: clue?.en || "",
      clue_ko: clue?.ko || "",
    })
    .then((res) => res.data);

export const createPostcard = createMomentRecord;

export const updatePostcardNextPlace = (postcardId, place, language) =>
  api
    .patch(
      `/postcard/${postcardId}/next-place`,
      {
        next_place_name_en: place.name_i18n?.en || place.name,
        next_place_name_ko: place.name_i18n?.ko || place.name,
      },
      { params: { language } }
    )
    .then((res) => res.data);

export const createFinalTripPostcard = (tripId, language) =>
  api.post(`/trip/${tripId}/final-postcard`, { language }).then((res) => res.data);

export const fetchArchive = (language) =>
  api.get("/archive", { params: { language } }).then((res) => res.data);

export default api;
