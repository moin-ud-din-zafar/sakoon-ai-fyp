import { Routes, Route, Navigate } from "react-router-dom";
import { AppProvider } from "./contexts/AppContext";
import ProtectedRoute from "./components/ProtectedRoute";
import GuestRoute from "./components/GuestRoute";

import LoginPage          from "./pages/LoginPage";
import RegisterPage       from "./pages/RegisterPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import SessionPage        from "./pages/SessionPage";
import SummaryPage        from "./pages/SummaryPage";
import MoodTrackerPage    from "./pages/MoodTrackerPage";
import PsychoeducationPage from "./pages/PsychoeducationPage";
import SettingPage        from "./pages/SettingPage";

export default function App() {
  return (
    <AppProvider>
      <Routes>
        {/* Default → session */}
        <Route path="/" element={<Navigate to="/session" replace />} />
        <Route path="/home" element={<Navigate to="/session" replace />} />

        {/* Public — redirect to /session if already authenticated */}
        <Route path="/login"           element={<GuestRoute><LoginPage /></GuestRoute>} />
        <Route path="/register"        element={<GuestRoute><RegisterPage /></GuestRoute>} />
        <Route path="/forgot-password" element={<GuestRoute><ForgotPasswordPage /></GuestRoute>} />

        {/* Protected */}
        <Route path="/session"        element={<ProtectedRoute><SessionPage /></ProtectedRoute>} />
        <Route path="/summary"        element={<ProtectedRoute><SummaryPage /></ProtectedRoute>} />
        <Route path="/mood-tracker"   element={<ProtectedRoute><MoodTrackerPage /></ProtectedRoute>} />
        <Route path="/psychoeducation" element={<ProtectedRoute><PsychoeducationPage /></ProtectedRoute>} />
        <Route path="/setting"        element={<ProtectedRoute><SettingPage /></ProtectedRoute>} />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/session" replace />} />
      </Routes>
    </AppProvider>
  );
}
