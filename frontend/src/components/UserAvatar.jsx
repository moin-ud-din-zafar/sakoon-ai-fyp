import { useState, useEffect } from "react";

const BACKEND_ORIGIN = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1").replace("/api/v1", "");

// Relative URLs from the backend (e.g. /uploads/...) must point to the backend
// origin, not the Vite dev server.
function resolveUrl(src) {
  if (!src) return "";
  if (src.startsWith("/")) return `${BACKEND_ORIGIN}${src}`;
  return src;
}

/**
 * Shows a profile image; falls back to the user's initial if the image
 * is missing, empty, or fails to load (broken URL / 404).
 * Handles both absolute URLs (Cloudinary) and relative backend paths.
 */
export default function UserAvatar({ src, name, className = "" }) {
  const [broken, setBroken] = useState(false);
  const initials = name?.charAt(0)?.toUpperCase() || "U";
  const resolved = resolveUrl(src);

  // Reset broken state whenever a new src comes in
  useEffect(() => { setBroken(false); }, [src]);

  return resolved && !broken ? (
    <img
      src={resolved}
      alt={initials}
      className={`w-full h-full object-cover ${className}`}
      onError={() => setBroken(true)}
    />
  ) : (
    <span>{initials}</span>
  );
}
