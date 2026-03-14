import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { SignIn } from "@clerk/react";
import loginImage from "../../assets/pexels-photo-4225920.jpeg";

export default function Login() {
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
    alignItems: "center",
    boxSizing: "border-box",
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
      <div style={cardStyle}>
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
        <div style={rightPanelStyle}>
          <SignIn
            signUpUrl="/register"
            fallbackRedirectUrl="/session?from=signin"
            forceRedirectUrl="/session?from=signin"
            appearance={{
              elements: {
                rootBox: "w-full max-w-full",
                card: "shadow-none w-full",
              },
            }}
          />
          <div style={{ marginTop: "12px", textAlign: "center", width: "100%" }}>
            <Link
              to="/forgot-password"
              style={{
                color: "#32c4c3",
                fontSize: "13px",
                fontWeight: "500",
                textDecoration: "none",
              }}
            >
              Forgot password?
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
