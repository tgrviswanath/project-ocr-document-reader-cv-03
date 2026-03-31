import axios from "axios";

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });

export const extractText = (formData) =>
  api.post("/api/v1/extract", formData, { headers: { "Content-Type": "multipart/form-data" } });
