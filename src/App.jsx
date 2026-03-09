import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Register from "./pages/auth/Register";
import Login from "./pages/auth/Login";
import ForgotPassword from "./pages/auth/ForgotPassword";
import Home from "./pages/HomePage/Home";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Default → Login */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Auth */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* Home */}
        <Route path="/home" element={<Home />} />

        {/* Fallback → Login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;