import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Register from "./pages/auth/Register";
import Login from "./pages/auth/Login";
import ForgotPassword from "./pages/auth/ForgotPassword";
import Home from "./pages/HomePage/Home";
import Summary from "./pages/Summary/Summary";
import MoodTracker from "./pages/MoodTracker/MoodTracker";
import PsychoEducation from "./pages/PsychoEducation/PsychoEducation";
import Settings from "./pages/Settings/Settings";
import Header from "./components/layout/Header";

function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Navigate to="/session" replace />} />
        <Route path="/session" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/summary" element={<Summary />} />
        <Route path="/mood-tracker" element={<MoodTracker />} />
        <Route path="/psycho-education" element={<PsychoEducation />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="*" element={<Navigate to="/session" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;