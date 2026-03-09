import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import registerImage from "../../assets/pexels-photo-4225920.jpeg";

export default function Register() {
  const navigate = useNavigate();
  const location = useLocation();

  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({ username: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Responsive detection
  const isWindow = typeof window !== "undefined";
  const [isMobile, setIsMobile] = useState(isWindow ? window.innerWidth <= 680 : false);
  const [isTablet, setIsTablet] = useState(isWindow ? window.innerWidth <= 900 : false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 680);
      setIsTablet(window.innerWidth <= 900);
    };
    window.addEventListener("resize", handleResize);
    handleResize();
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Prefill email if navigated from another page
  useEffect(() => {
    if (location.state?.email) {
      setFormData((p) => ({ ...p, email: location.state.email }));
    }
  }, [location.state]);

  const handleChange = (e) =>
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const fakeRegister = async ({ username, email, password }) => {
    await new Promise((r) => setTimeout(r, 700));
    if (username && email && password) return { ok: true };
    return { ok: false, message: "All fields are required" };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!formData.username || !formData.email || !formData.password) {
      setError("Please fill in all fields.");
      return;
    }
    try {
      setLoading(true);
      const json = await fakeRegister(formData);
      if (!json.ok) {
        setError(json.message || "Registration failed.");
        setLoading(false);
        return;
      }
      navigate("/login", { state: { email: formData.email }, replace: true });
    } catch (err) {
      console.error("Register error:", err);
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ── Responsive inline styles ──
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
    display: isMobile ? "none" : "flex",
    alignItems: "center",
    justifyContent: "center",
    boxSizing: "border-box",
  };

  const imageBoxStyle = {
    width: "100%",
    height: isMobile ? "0" : isTablet ? "320px" : "380px",
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
        @media (max-width: 420px) { .right-title { font-size: 22px !important; } }
      `}</style>

      <div style={cardStyle}>
        {/* LEFT IMAGE PANEL */}
        <div style={leftPanelStyle}>
          <div style={imageBoxStyle}>
            <img
              src={registerImage}
              alt="Register"
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </div>
        </div>

        {/* RIGHT FORM PANEL */}
        <div style={rightPanelStyle}>
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
            Welcome!
          </h2>

          <p style={{ fontSize: "13px", color: "#8a9199", marginBottom: "28px", lineHeight: "1.6" }}>
            Please enter your details to create your account.
          </p>

          <form onSubmit={handleSubmit} noValidate style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
            {/* USERNAME */}
            <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
              <label style={{ fontSize: "13px", fontWeight: "600", color: "#2c2c2c" }}>Username</label>
              <input
                type="text"
                name="username"
                placeholder="Enter Username"
                value={formData.username}
                onChange={handleChange}
                required
                disabled={loading}
                style={inputStyle}
              />
            </div>

            {/* EMAIL */}
            <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
              <label style={{ fontSize: "13px", fontWeight: "600", color: "#2c2c2c" }}>Email</label>
              <input
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

            {/* PASSWORD */}
            <div style={{ display: "flex", flexDirection: "column", gap: "5px", position: "relative" }}>
              <label style={{ fontSize: "13px", fontWeight: "600", color: "#2c2c2c" }}>Password</label>
              <input
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
                style={{ position: "absolute", right: "12px", top: "50%", transform: "translateY(-50%)", border: "none", background: "none", cursor: loading ? "not-allowed" : "pointer" }}
              >
                {showPassword ? (
                  // Eye-off SVG
                  <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#888" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M3 3l18 18" />
                  </svg>
                ) : (
                  // Eye SVG
                  <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#888" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>

            {error && <div style={{ color: "#d9534f", fontSize: "13px" }}>{error}</div>}

            {/* CREATE BUTTON */}
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Creating..." : "Create Account"}
            </button>

            {/* LOGIN LINK */}
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "-4px" }}>
              <button
                type="button"
                onClick={() => navigate("/login")}
                disabled={loading}
                style={{ background: "none", border: "none", color: "#2bcece", fontSize: "13px", fontWeight: "500", cursor: "pointer", padding: "0" }}
              >
                Already have an account? Sign In
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}