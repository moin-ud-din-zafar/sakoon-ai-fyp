import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSignIn } from "@clerk/react";
import forgotImage from "../../assets/pexels-photo-4225920.jpeg";

export default function ForgotPassword() {
  const navigate = useNavigate();
  const { signIn, fetchStatus } = useSignIn();
  const [emailAddress, setEmailAddress] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [error, setError] = useState("");

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

  const sendCode = async (e) => {
    e.preventDefault();
    setError("");
    if (!signIn) return;
    if (!emailAddress.trim()) {
      setError("Please enter your email.");
      return;
    }
    const { error: createError } = await signIn.create({ identifier: emailAddress.trim() });
    if (createError) {
      setError(createError.errors?.[0]?.message || "Invalid email or account not found.");
      return;
    }
    const { error: sendCodeError } = await signIn.resetPasswordEmailCode.sendCode();
    if (sendCodeError) {
      setError(sendCodeError.errors?.[0]?.message || "Failed to send code.");
      return;
    }
    setCodeSent(true);
  };

  const verifyCode = async (e) => {
    e.preventDefault();
    setError("");
    if (!signIn) return;
    if (!code.trim()) {
      setError("Please enter the code.");
      return;
    }
    const { error: verifyErr } = await signIn.resetPasswordEmailCode.verifyCode({ code: code.trim() });
    if (verifyErr) {
      setError(verifyErr.errors?.[0]?.message || "Invalid code.");
      return;
    }
  };

  const submitNewPassword = async (e) => {
    e.preventDefault();
    setError("");
    if (!signIn) return;
    if (!password || password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    const { error: submitErr } = await signIn.resetPasswordEmailCode.submitPassword({ password });
    if (submitErr) {
      setError(submitErr.errors?.[0]?.message || "Failed to set password.");
      return;
    }
    if (signIn.status === "complete") {
      const { error: finalError } = await signIn.finalize({
        navigate: async ({ decorateUrl }) => {
          const url = decorateUrl("/session");
          if (url.startsWith("http")) {
            window.location.href = url;
          } else {
            navigate(url, { replace: true });
          }
        },
      });
      if (finalError) {
        setError(finalError.errors?.[0]?.message || "Something went wrong.");
        return;
      }
    }
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
    padding: "11px 14px",
    border: "1.5px solid #e2e6ea",
    borderRadius: "8px",
    fontSize: "13.5px",
    color: "#2a2a2a",
    outline: "none",
    boxSizing: "border-box",
    backgroundColor: "#ffffff",
    minHeight: "38px",
  };

  const btnStyle = {
    width: "100%",
    padding: "13px",
    backgroundColor: "#2dcece",
    color: "#ffffff",
    border: "none",
    borderRadius: "8px",
    fontSize: "15px",
    fontWeight: "600",
    cursor: fetchStatus === "fetching" ? "not-allowed" : "pointer",
    marginTop: "4px",
    opacity: fetchStatus === "fetching" ? 0.7 : 1,
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
        <div style={leftPanelStyle}>
          <div style={imageBoxStyle}>
            <img src={forgotImage} alt="Recover" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </div>
        </div>
        <div style={rightPanelStyle}>
          <button
            type="button"
            onClick={() => navigate("/login")}
            style={{ background: "none", border: "none", cursor: "pointer", padding: 0, marginBottom: 18 }}
            aria-label="Back to login"
          >
            <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#2dcece" strokeWidth="2.2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>

          <h2 style={{ fontSize: "28px", fontWeight: 700, color: "#1a1a1a", margin: "0 0 6px 0" }}>
            Recover your account
          </h2>
          <p style={{ fontSize: 13, color: "#8c9aa3", margin: "0 0 30px 0", lineHeight: 1.6 }}>
            {!codeSent
              ? "Enter your email and we’ll send you a reset code."
              : signIn?.status === "needs_new_password"
                ? "Enter your new password."
                : "Enter the code we sent to your email."}
          </p>

          {error && (
            <div style={{ color: "#c0392b", fontSize: 13, marginBottom: 12 }}>{error}</div>
          )}

          {!codeSent && (
            <form onSubmit={sendCode} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <label style={{ fontSize: 13.5, fontWeight: 500, color: "#4a4a4a" }}>Email</label>
              <input
                type="email"
                placeholder="e.g. you@example.com"
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                disabled={fetchStatus === "fetching"}
                style={inputStyle}
              />
              <button type="submit" disabled={fetchStatus === "fetching"} style={btnStyle}>
                {fetchStatus === "fetching" ? "Sending..." : "Send reset code"}
              </button>
            </form>
          )}

          {codeSent && signIn?.status !== "needs_new_password" && (
            <form onSubmit={verifyCode} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <label style={{ fontSize: 13.5, fontWeight: 500, color: "#4a4a4a" }}>Verification code</label>
              <input
                type="text"
                placeholder="Enter code from email"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                disabled={fetchStatus === "fetching"}
                style={inputStyle}
              />
              <button type="submit" disabled={fetchStatus === "fetching"} style={btnStyle}>
                {fetchStatus === "fetching" ? "Verifying..." : "Verify code"}
              </button>
            </form>
          )}

          {codeSent && signIn?.status === "needs_new_password" && (
            <form onSubmit={submitNewPassword} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <label style={{ fontSize: 13.5, fontWeight: 500, color: "#4a4a4a" }}>New password</label>
              <input
                type="password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={fetchStatus === "fetching"}
                style={inputStyle}
                minLength={8}
              />
              <button type="submit" disabled={fetchStatus === "fetching"} style={btnStyle}>
                {fetchStatus === "fetching" ? "Updating..." : "Set new password"}
              </button>
            </form>
          )}

          <div style={{ marginTop: 24, textAlign: "center" }}>
            <button
              type="button"
              onClick={() => navigate("/login")}
              style={{ background: "none", border: "none", color: "#2dcece", fontSize: 13.5, fontWeight: 500, cursor: "pointer" }}
            >
              Back to Sign in
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
