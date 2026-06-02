import { useNavigate } from "react-router-dom";
import { useApp } from "../contexts/AppContext";

export default function HomePage() {
  const { user, logout } = useApp();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-[#f0f5f5] flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Hello World</h1>
        {user && (
          <p className="text-gray-500 mb-6">
            Welcome back, <span className="text-primary font-medium">{user.name}</span>
          </p>
        )}
        <button
          onClick={handleLogout}
          className="px-6 py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
