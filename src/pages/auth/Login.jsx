import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import loginImage from "../../assets/pexels-photo-4225920.jpeg";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Safely initialize responsive states (avoid SSR issues)
  const isWindow = typeof window !== "undefined";
  const [isMobile, setIsMobile] = useState(isWindow ? window.innerWidth <= 680 : false);
  const [isTablet, setIsTablet] = useState(isWindow ? window.innerWidth <= 900 : false);

  // Prefill email if Register navigated here with state
  useEffect(() => {
    if (location.state?.email) {
      setFormData((p) => ({ ...p, email: location.state.email }));
    }
  }, [location.state]);

  // Responsive listener
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 680);
      setIsTablet(window.innerWidth <= 900);
    };
    window.addEventListener("resize", handleResize);
    // run once to pick up current size (in case initial state was SSR fallback)
    handleResize();
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleChange = (e) =>
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  // Mock auth — replace with real backend call
  const fakeAuth = async ({ email, password }) => {
    await new Promise((r) => setTimeout(r, 700));
    if (email && password) return { ok: true, token: "demo-token-xyz" };
    return { ok: false, message: "Invalid credentials" };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!formData.email || !formData.password) {
      setError("Please enter both email and password.");
      return;
    }
    try {
      setLoading(true);
      // Replace fakeAuth with your API call:
      // const res = await fetch("/api/auth/login", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(formData) });
      // const json = await res.json();
      const json = await fakeAuth(formData);
      if (!json.ok) {
        setError(json.message || "Login failed. Check credentials.");
        setLoading(false);
        return;
      }
      if (json.token) localStorage.setItem("authToken", json.token);
      navigate("/home", { replace: true });
    } catch (err) {
      console.error("Login error:", err);
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ── Responsive values ──
  const cardStyle = {
    display: "flex",
    flexDirection: isMobile ? "column" : "row",
    alignItems: "stretch",
    backgroundColor: "#ffffff",
    borderRadius: "16px",
    boxShadow: "0 4px 24px rgba(0,0,0,0.07)",
    overflow: "hidden",
    width: isMobile ? "100%" : "960px",
    maxWidth: "100%",
  };

  const leftPanelStyle = {
    width: isMobile ? "100%" : isTablet ? "360px" : "460px",
    flexShrink: 0,
    backgroundColor: "#d6f0f0",
    padding: isMobile ? "0" : isTablet ? "22px" : "28px",
    boxSizing: "border-box",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  };

  const imageBoxStyle = {
    width: "100%",
    height: isMobile ? "0" : isTablet ? "300px" : "380px",
    borderRadius: "12px",
    overflow: "hidden",
    backgroundColor: "#b8e6e6",
  };

  const rightPanelStyle = {
    flex: 1,
    padding: isMobile ? "28px 20px" : isTablet ? "48px 36px" : "64px 52px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    boxSizing: "border-box",
  };

  const inputStyle = {
    width: "100%",
    padding: "10px 14px 10px 36px",
    border: "1.5px solid #e3e7ea",
    borderRadius: "8px",
    fontSize: "13px",
    color: "#2c2c2c",
    outline: "none",
    boxSizing: "border-box",
    backgroundColor: "#fff",
    minHeight: "38px",
  };

  return (
    /* ── Page ── */
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#f2f4f4",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        padding: "40px 20px",
        boxSizing: "border-box",
      }}
    >
      {/* small CSS block for hover and button states */}
      <style>{`
        .btn-primary {
          width: 100%;
          padding: 12px;
          background-color: #2bcece;
          color: #ffffff;
          border: none;
          border-radius: 8px;
          font-size: 14.5px;
          font-weight: 600;
          cursor: pointer;
          margin-top: 4px;
          letter-spacing: 0.3px;
          transition: background-color .12s ease, opacity .12s ease;
        }
        .btn-primary:hover { background-color: #20bbbb; }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; background-color: #2bcece; }

        /* small responsive helpers in case container shrinks */
        @media (max-width: 420px) {
          .right-title { font-size: 22px !important; }
        }
      `}</style>

      {/* ── Card ── */}
      <div style={cardStyle}>
        {/* LEFT — image panel
            Remove/hide on mobile: we simply don't render content height when isMobile is true.
        */}
        {!isMobile && (
          <div style={leftPanelStyle} aria-hidden>
            <div style={imageBoxStyle}>
              <img
                 src={loginImage}
                 alt="Login"
                 style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
            </div>
          </div>
        )}

        {/* RIGHT — form panel */}
        <div style={rightPanelStyle}>
          {/* Title */}
          <h2
            className="right-title"
            style={{
              fontSize: isMobile ? "22px" : "28px",
              fontWeight: "700",
              color: "#1c1c1c",
              margin: "0 0 6px 0",
              letterSpacing: "-0.2px",
            }}
          >
            Welcome Back!
          </h2>

          {/* Subtitle */}
          <p
            style={{
              fontSize: "13px",
              color: "#8a9199",
              margin: "0 0 28px 0",
              lineHeight: "1.6",
            }}
          >
            Please enter your Email to access your account.
          </p>

          <form onSubmit={handleSubmit} noValidate style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
            {/* Email */}
            <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
              <label htmlFor="email" style={{ fontSize: "13px", fontWeight: "600", color: "#2c2c2c" }}>
                Email
              </label>
              <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                <span style={{ position: "absolute", left: "12px", display: "flex", alignItems: "center", pointerEvents: "none" }}>
                  <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="#c2cad2" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </span>
                <input
                  id="email"
                  type="email"
                  name="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  style={inputStyle}
                />
              </div>
            </div>

            {/* Password */}
            <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
              <label htmlFor="password" style={{ fontSize: "13px", fontWeight: "600", color: "#2c2c2c" }}>
                Password
              </label>
              <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                <span style={{ position: "absolute", left: "12px", display: "flex", alignItems: "center", pointerEvents: "none" }}>
                  <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="#c2cad2" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </span>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  name="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  disabled={loading}
                  style={{ ...inputStyle, padding: "10px 40px 10px 36px" }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  disabled={loading}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  style={{ position: "absolute", right: "12px", background: "none", border: "none", cursor: loading ? "not-allowed" : "pointer", padding: "0", display: "flex", alignItems: "center" }}
                >
                  {showPassword ? (
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#c2cad2" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#c2cad2" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && <div style={{ color: "#d9534f", fontSize: "13px" }}>{error}</div>}

            {/* Login button */}
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Signing in..." : "Login"}
            </button>

            {/* Forgot Password */}
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "-4px" }}>
              <button
                type="button"
                onClick={() => navigate("/forgot-password")}
                disabled={loading}
                style={{ background: "none", border: "none", color: "#2bcece", fontSize: "13px", fontWeight: "500", cursor: "pointer", padding: "0" }}
              >
                Forgot Password?
              </button>
            </div>

            <div style={{ borderTop: "1px solid #f0f0f0", margin: "4px 0" }} />

            {/* Sign Up */}
            <div style={{ display: "flex", justifyContent: "center" }}>
              <button
                type="button"
                onClick={() => navigate("/register")}
                disabled={loading}
                style={{ background: "none", border: "none", color: "#2bcece", fontSize: "13px", fontWeight: "500", cursor: "pointer", padding: "0" }}
              >
                Don't have an account? Sign Up
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}