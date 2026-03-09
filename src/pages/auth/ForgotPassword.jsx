import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ForgotPasswordmage from "../../assets/pexels-photo-4225920.jpeg";

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
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

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");
    if (!email) {
      setError("Please enter your email.");
      return;
    }
    setLoading(true);
    console.log("Recovery email:", email);
    // TODO: connect to backend API for recovery
    setTimeout(() => setLoading(false), 700);
  };

  const cardStyle = {
    display: "flex",
    flexDirection: isMobile ? "column" : "row",
    alignItems: "stretch",
    backgroundColor: "#ffffff",
    borderRadius: "18px",
    boxShadow: "0 6px 32px rgba(0,0,0,0.09)",
    overflow: "hidden",
    width: isMobile ? "100%" : "900px",
    maxWidth: "100%",
    minHeight: "500px",
  };

  const leftPanelStyle = {
    width: isMobile ? "100%" : isTablet ? "300px" : "440px",
    flexShrink: 0,
    backgroundColor: "#d9f2f2",
    display: isMobile ? "none" : "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: isMobile ? "0" : isTablet ? "20px" : "32px",
    boxSizing: "border-box",
  };

  const imageBoxStyle = {
    width: "100%",
    height: isMobile ? "0" : isTablet ? "280px" : "360px",
    border: "2px solid #a8dede",
    borderRadius: "14px",
    overflow: "hidden",
    backgroundColor: "#c2eaea",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  };

  const rightPanelStyle = {
    flex: 1,
    padding: isMobile ? "28px 20px" : isTablet ? "48px 36px" : "60px 52px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    boxSizing: "border-box",
  };

  const inputStyle = {
    width: "100%",
    padding: "11px 14px 11px 38px",
    border: "1.5px solid #e2e6ea",
    borderRadius: "8px",
    fontSize: "13.5px",
    color: "#2a2a2a",
    outline: "none",
    boxSizing: "border-box",
    backgroundColor: "#ffffff",
    minHeight: "38px",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#eef2f2",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        padding: "40px 20px",
        boxSizing: "border-box",
      }}
    >
      <div style={cardStyle}>
        {/* LEFT PANEL */}
        <div style={leftPanelStyle}>
          <div style={imageBoxStyle}>
            <img
              src={ForgotPasswordmage}
              alt="forgot"
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div style={rightPanelStyle}>
          {/* Back button */}
          <div style={{ marginBottom: "18px" }}>
            <button
              type="button"
              onClick={() => navigate("/login")}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                padding: "0",
                display: "flex",
                alignItems: "center",
              }}
            >
              <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#2dcece" strokeWidth="2.2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
          </div>

          {/* Title */}
          <h2 style={{ fontSize: "28px", fontWeight: "700", color: "#1a1a1a", margin: "0 0 6px 0", letterSpacing: "-0.3px" }}>
            Recover your account!
          </h2>

          {/* Subtitle */}
          <p style={{ fontSize: "13px", color: "#8c9aa3", margin: "0 0 30px 0", lineHeight: "1.6" }}>
            Please enter your email to access your account.
          </p>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Email input */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", position: "relative" }}>
              <label style={{ fontSize: "13.5px", fontWeight: "500", color: "#4a4a4a" }}>
                Enter your recovery email
              </label>
              <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                <span
                  style={{
                    position: "absolute",
                    left: "13px",
                    display: "flex",
                    alignItems: "center",
                    pointerEvents: "none",
                  }}
                >
                  <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="#c0c8d0" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </span>
                <input
                  type="email"
                  name="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                  style={inputStyle}
                />
              </div>
            </div>

            {/* Error */}
            {error && <div style={{ color: "#d9534f", fontSize: "13px" }}>{error}</div>}

            {/* Send Link button */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width: "100%",
                padding: "13px",
                backgroundColor: "#2dcece",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                fontSize: "15px",
                fontWeight: "600",
                cursor: loading ? "not-allowed" : "pointer",
                marginTop: "4px",
                letterSpacing: "0.4px",
                transition: "background-color 0.15s ease",
              }}
              onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = "#20bbbb")}
              onMouseLeave={(e) => !loading && (e.currentTarget.style.backgroundColor = "#2dcece")}
            >
              {loading ? "Sending..." : "Send Link"}
            </button>

            {/* Sign Up link */}
            <div style={{ display: "flex", justifyContent: "center", marginTop: "6px" }}>
              <button
                type="button"
                onClick={() => navigate("/register")}
                style={{
                  background: "none",
                  border: "none",
                  color: "#2dcece",
                  fontSize: "13.5px",
                  fontWeight: "500",
                  cursor: "pointer",
                  padding: "0",
                }}
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