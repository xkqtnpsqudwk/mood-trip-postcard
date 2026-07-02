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

export const analyzeMood = ({ city, moodText, language }) =>
  api.post("/analyze", { city, mood_text: moodText, language }).then((res) => res.data);

export const createPostcard = (city, placeId, review, language, tripId) =>
  api
    .post("/postcard", {
      city,
      place_id: placeId,
      review,
      language,
      trip_id: tripId || null,
    })
    .then((res) => res.data);

export const updatePostcardNextPlace = (postcardId, nextPlaceId, language) =>
  api
    .patch(
      `/postcard/${postcardId}/next-place`,
      { next_place_id: nextPlaceId },
      { params: { language } }
    )
    .then((res) => res.data);

export const fetchArchive = (language) =>
  api.get("/archive", { params: { language } }).then((res) => res.data);

export default api;
