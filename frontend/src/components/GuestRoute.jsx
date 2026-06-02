import { Navigate } from "react-router-dom";
import { getStoredToken } from "../services/api";

export default function GuestRoute({ children }) {
  if (getStoredToken()) return <Navigate to="/session" replace />;
  return children;
}
