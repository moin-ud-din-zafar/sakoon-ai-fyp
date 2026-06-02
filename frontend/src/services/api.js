import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 120000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sakoon_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !err.config?.url?.includes("/auth/login")) {
      localStorage.removeItem("sakoon_token");
      localStorage.removeItem("sakoon_user");
    }
    return Promise.reject(err);
  }
);

export const getStoredToken = () => localStorage.getItem("sakoon_token");

export const getStoredUser = () => {
  try {
    const u = localStorage.getItem("sakoon_user");
    return u ? JSON.parse(u) : null;
  } catch {
    return null;
  }
};

export const setAuth = ({ accessToken, user }) => {
  if (accessToken) localStorage.setItem("sakoon_token", accessToken);
  if (user) localStorage.setItem("sakoon_user", JSON.stringify(user));
};

export const clearAuth = () => {
  localStorage.removeItem("sakoon_token");
  localStorage.removeItem("sakoon_user");
};

export const parseApiError = (err) => {
  const d = err?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x.msg).join(", ");
  return err?.message || "Something went wrong";
};

// ── Auth ────────────────────────────────────────────────────────
export const registerUser = ({ name, email, password, languagePreference = "en" }) =>
  api.post("/auth/register", { name, email, password, languagePreference }).then((r) => r.data);

export const loginUser = ({ email, password }) =>
  api.post("/auth/login", { email, password }).then((r) => r.data);

export const getMe = () => api.get("/auth/me").then((r) => r.data);

export const changePassword = ({ currentPassword, newPassword }) =>
  api.patch("/auth/change-password", { currentPassword, newPassword }).then((r) => r.data);

export const forgotPassword = (email) =>
  api.post("/auth/forgot-password", { email }).then((r) => r.data);

export const resetPassword = ({ token, newPassword }) =>
  api.post("/auth/reset-password", { token, newPassword }).then((r) => r.data);

export const uploadProfileImage = (userId, file) => {
  const form = new FormData();
  form.append("file", file);
  // Pass FormData without explicit Content-Type — Axios sets multipart boundary automatically
  return api.post(`/user/${userId}/profile-image`, form, {
    headers: { "Content-Type": undefined },
  }).then((r) => r.data);
};

export const getSession = () => api.get("/auth/session").then((r) => r.data);

// ── Chat ────────────────────────────────────────────────────────
export const sendMessage = ({ userId, sessionId, message }) =>
  api.post("/chat/message", { userId, sessionId, message }).then((r) => r.data);

export const getChatHistory = (sessionId) =>
  api.get(`/session/${sessionId}/history`).then((r) => r.data);

// ── User ────────────────────────────────────────────────────────
export const getMoodSummary = (userId) =>
  api.get(`/user/${userId}/mood-summary`).then((r) => r.data);

export const getRecommendations = (userId) =>
  api.get(`/user/${userId}/recommendations`).then((r) => r.data);

export const submitExerciseFeedback = (userId, body) =>
  api.post(`/user/${userId}/exercise-feedback`, body).then((r) => r.data);

// ── Mood ────────────────────────────────────────────────────────
export const logMood = (userId, moodScore, note = null) =>
  api.post("/mood/log", { user_id: userId, mood_score: moodScore, note }).then((r) => r.data);

export const getMoodHistory = (userId, limit = 30) =>
  api.get(`/mood/history/${userId}`, { params: { limit } }).then((r) => r.data);

// ── Admin ───────────────────────────────────────────────────────
export const adminLogin = ({ username, password }) =>
  api.post("/admin/login", { username, password }).then((r) => r.data);

export const getAdminStats = (adminKey) =>
  api.get("/admin/stats", { headers: { "X-Admin-Key": adminKey } }).then((r) => r.data);

export const getAdminSessions = (adminKey) =>
  api.get("/admin/sessions", { headers: { "X-Admin-Key": adminKey } }).then((r) => r.data);

export const getAdminCrisisAlerts = (adminKey) =>
  api.get("/admin/crisis-alerts", { headers: { "X-Admin-Key": adminKey } }).then((r) => r.data);
