import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { FiLogOut, FiX, FiLock, FiEye, FiEyeOff, FiCamera } from "react-icons/fi";
import AppLayout from "../layouts/AppLayout";
import { useApp } from "../contexts/AppContext";
import { changePassword, uploadProfileImage, parseApiError } from "../services/api";

// ── constants ──────────────────────────────────────────────────────────────
const AVATAR_LOOK_OPTIONS = ["Professional", "Casual", "Friendly", "Clinical"];
const VOICE_STYLE_OPTIONS = ["Warm & Empathetic", "Professional", "Gentle", "Energetic"];
const CULTURAL_OPTIONS    = ["Global Standard", "South Asian", "Western", "Middle Eastern"];
const LANGUAGE_OPTIONS    = [
  { value: "en", label: "English (US)" },
  { value: "ur", label: "Urdu" },
  { value: "hi", label: "Hindi" },
  { value: "ps", label: "Pashto" },
  { value: "sd", label: "Sindhi" },
  { value: "sk", label: "Saraiki" },
];
const PREFS_KEY  = "sakoon_preferences";
const MAX_TRAITS = 200;

// ── helpers ────────────────────────────────────────────────────────────────
function loadPrefs() {
  try {
    return JSON.parse(localStorage.getItem(PREFS_KEY) || "{}");
  } catch {
    return {};
  }
}

// ── sub-components ─────────────────────────────────────────────────────────
function SectionCard({ title, children }) {
  return (
    <section className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
      <h2 className="text-sm font-semibold text-gray-800 mb-4">{title}</h2>
      {children}
    </section>
  );
}

function SelectField({ label, value, onChange, options }) {
  return (
    <div>
      <label className="block text-sm text-gray-600 mb-1">{label}</label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 bg-white appearance-none focus:outline-none focus:border-primary transition-colors pr-8"
        >
          {options.map((o) =>
            typeof o === "string"
              ? <option key={o} value={o}>{o}</option>
              : <option key={o.value} value={o.value}>{o.label}</option>
          )}
        </select>
        <span className="pointer-events-none absolute inset-y-0 right-2.5 flex items-center text-gray-400">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </span>
      </div>
    </div>
  );
}

function ChangePasswordModal({ onClose }) {
  const [form,    setForm]    = useState({ current: "", next: "", confirm: "" });
  const [show,    setShow]    = useState({ current: false, next: false, confirm: false });
  const [error,   setError]   = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const toggle = (field) => setShow((s) => ({ ...s, [field]: !s[field] }));
  const handle = (e) => { setForm((f) => ({ ...f, [e.target.name]: e.target.value })); setError(""); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.current) return setError("Current password is required.");
    if (form.next.length < 8) return setError("New password must be at least 8 characters.");
    if (form.next !== form.confirm) return setError("Passwords do not match.");
    setLoading(true);
    setError("");
    try {
      const data = await changePassword({ currentPassword: form.current, newPassword: form.next });
      setSuccess(data.message || "Password updated successfully.");
      setTimeout(() => onClose(), 1800);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors">
          <FiX size={20} />
        </button>
        <h3 className="text-base font-semibold text-gray-800 mb-1">Change Password</h3>
        <p className="text-sm text-gray-500 mb-5">Update your account password below.</p>

        {error && (
          <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 px-3 py-2 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {[
            { name: "current", label: "Current Password", placeholder: "Enter current password" },
            { name: "next",    label: "New Password",      placeholder: "Min 8 characters" },
            { name: "confirm", label: "Confirm Password",  placeholder: "Repeat new password" },
          ].map(({ name, label, placeholder }) => (
            <div key={name}>
              <label className="block text-sm text-gray-700 mb-1">{label}</label>
              <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-primary transition-colors">
                <FiLock className="text-gray-400 shrink-0" size={15} />
                <input
                  type={show[name] ? "text" : "password"}
                  name={name}
                  value={form[name]}
                  onChange={handle}
                  placeholder={placeholder}
                  className="flex-1 text-sm text-gray-700 outline-none bg-transparent placeholder-gray-400"
                />
                <button type="button" tabIndex={-1} onClick={() => toggle(name)} className="text-gray-400 hover:text-gray-600">
                  {show[name] ? <FiEyeOff size={15} /> : <FiEye size={15} />}
                </button>
              </div>
            </div>
          ))}
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose}
              className="flex-1 py-2 rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
              Cancel
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors disabled:opacity-60">
              {loading ? "Updating…" : "Update"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── main page ──────────────────────────────────────────────────────────────
export default function SettingPage() {
  const { user, setUser, logout } = useApp();
  const navigate = useNavigate();

  const saved = loadPrefs();
  const [avatarLook,        setAvatarLook]        = useState(saved.avatarLook        || "Professional");
  const [voiceStyle,        setVoiceStyle]         = useState(saved.voiceStyle        || "Warm & Empathetic");
  const [personalityTraits, setPersonalityTraits]  = useState(saved.personalityTraits || "");
  const [language,          setLanguage]           = useState(saved.language          || user?.languagePreference || "en");
  const [culturalAdapt,     setCulturalAdapt]      = useState(saved.culturalAdapt     || "Global Standard");
  const [showChangePwd,   setShowChangePwd]   = useState(false);
  const [imgLoading,      setImgLoading]      = useState(false);
  const [imgError,        setImgError]        = useState("");
  const fileInputRef = useRef(null);

  useEffect(() => {
    localStorage.setItem(
      PREFS_KEY,
      JSON.stringify({ avatarLook, voiceStyle, personalityTraits, language, culturalAdapt })
    );
  }, [avatarLook, voiceStyle, personalityTraits, language, culturalAdapt]);

  const handleTraitsChange = (e) => {
    if (e.target.value.length <= MAX_TRAITS) setPersonalityTraits(e.target.value);
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleImageChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImgLoading(true);
    setImgError("");
    try {
      const data = await uploadProfileImage(user.id, file);
      // Resolve relative upload paths to the backend origin
      const rawUrl = (data.user?.profileImageUrl) || data.imageUrl || "";
      const backendOrigin = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1").replace("/api/v1", "");
      const resolvedUrl = rawUrl.startsWith("/") ? `${backendOrigin}${rawUrl}` : rawUrl;
      const updatedUser = { ...(data.user || user), profileImageUrl: resolvedUrl };
      setUser(updatedUser);
      localStorage.setItem("sakoon_user", JSON.stringify(updatedUser));
    } catch (err) {
      setImgError(parseApiError(err));
    } finally {
      setImgLoading(false);
      e.target.value = "";
    }
  };

  const initials = user?.name?.charAt(0)?.toUpperCase() || "U";

  return (
    <AppLayout>
      {showChangePwd && <ChangePasswordModal onClose={() => setShowChangePwd(false)} />}

      <h1 className="text-2xl font-bold text-gray-800 mb-6">Settings</h1>

      <SectionCard title="Avatar & Preferences">
        <div className="flex items-center gap-3 mb-5">
          {/* Clickable avatar — uploads profile image */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={imgLoading}
            className="relative w-12 h-12 rounded-full shrink-0 overflow-hidden group cursor-pointer"
            title="Click to change profile photo"
          >
            {user?.profileImageUrl ? (
              <img
                src={
                  user.profileImageUrl.startsWith("/")
                    ? `${(import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1").replace("/api/v1", "")}${user.profileImageUrl}`
                    : user.profileImageUrl
                }
                alt={user.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full bg-primary-light flex items-center justify-center text-primary font-bold text-lg select-none">
                {initials}
              </div>
            )}
            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-full">
              <FiCamera size={16} className="text-white" />
            </div>
            {imgLoading && (
              <div className="absolute inset-0 bg-white/70 flex items-center justify-center rounded-full">
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleImageChange}
            className="hidden"
          />

          <div>
            <p className="text-sm font-medium text-gray-800">{user?.name || "—"}</p>
            <p className="text-xs text-gray-500">{user?.email || "—"}</p>
            {imgError && <p className="text-xs text-red-500 mt-0.5">{imgError}</p>}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <SelectField label="Avatar Visual Look" value={avatarLook} onChange={setAvatarLook} options={AVATAR_LOOK_OPTIONS} />
          <SelectField label="Voice Style"         value={voiceStyle} onChange={setVoiceStyle} options={VOICE_STYLE_OPTIONS} />
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Personality Traits</label>
          <div className="relative">
            <textarea
              value={personalityTraits}
              onChange={handleTraitsChange}
              placeholder="e.g., Calm, analytical, supportive, curious, observant"
              rows={3}
              className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm text-gray-700 placeholder-gray-400 resize-none focus:outline-none focus:border-primary transition-colors pb-6"
            />
            <span className="absolute bottom-2.5 right-3 text-xs text-gray-400">
              {personalityTraits.length}/{MAX_TRAITS} characters
            </span>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="General Preferences">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <SelectField label="Language"           value={language}      onChange={setLanguage}      options={LANGUAGE_OPTIONS} />
          <SelectField label="Cultural Adaptation" value={culturalAdapt} onChange={setCulturalAdapt} options={CULTURAL_OPTIONS} />
        </div>
      </SectionCard>

      <SectionCard title="Account">
        <div className="flex flex-col items-start gap-3">
          <button
            onClick={() => setShowChangePwd(true)}
            className="px-4 py-2 rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Change Password
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <FiLogOut size={15} />
            Logout
          </button>
        </div>
      </SectionCard>
    </AppLayout>
  );
}
