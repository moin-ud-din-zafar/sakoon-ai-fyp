import { Navigate } from "react-router-dom";
import { getStoredToken } from "../services/api";

export default function ProtectedRoute({ children }) {
  if (!getStoredToken()) return <Navigate to="/login" replace />;
  return children;
}
