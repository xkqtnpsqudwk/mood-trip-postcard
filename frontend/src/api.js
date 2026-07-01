import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 0,
});

export const analyzeMood = (city, moodText, language) =>
  api
    .post("/analyze", { city, mood_text: moodText, language })
    .then((res) => res.data);

export const createPostcard = (city, placeName, review, language) =>
  api
    .post("/postcard", { city, place_name: placeName, review, language })
    .then((res) => res.data);

export const fetchArchive = () =>
  api.get("/archive").then((res) => res.data);

export default api;
