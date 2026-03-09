import React from "react";

export default function Home() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#f2f4f4",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        padding: "24px",
        boxSizing: "border-box",
      }}
    >
      <h1
        style={{
          fontSize: "40px",
          fontWeight: 700,
          color: "#1a1a1a",
          margin: 0,
          textAlign: "center",
        }}
      >
        Welcome
      </h1>
    </div>
  );
}