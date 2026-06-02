import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FiMail, FiLock, FiEye, FiEyeOff } from "react-icons/fi";
import AuthLayout from "../layouts/AuthLayout";
import { loginUser, parseApiError } from "../services/api";
import { useApp } from "../contexts/AppContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useApp();

  const [form, setForm] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email.trim()) return setError("Email is required.");
    if (!form.password) return setError("Password is required.");

    setLoading(true);
    try {
      const data = await loginUser({ email: form.email.trim(), password: form.password });
      login({ accessToken: data.accessToken, user: data.user });
      navigate("/session");
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Welcome Back!</h1>
      <p className="text-sm text-gray-500 mb-6">
        Please enter your Email to access your account.
      </p>

      {error && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Email */}
        <div>
          <label className="block text-sm text-gray-700 mb-1">Email</label>
          <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-primary transition-colors">
            <FiMail className="text-gray-400 shrink-0" size={16} />
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="Enter your email"
              className="flex-1 text-sm text-gray-700 outline-none bg-transparent placeholder-gray-400"
              autoComplete="email"
            />
          </div>
        </div>

        {/* Password */}
        <div>
          <label className="block text-sm text-gray-700 mb-1">Password</label>
          <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-primary transition-colors">
            <FiLock className="text-gray-400 shrink-0" size={16} />
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Enter your password"
              className="flex-1 text-sm text-gray-700 outline-none bg-transparent placeholder-gray-400"
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              tabIndex={-1}
            >
              {showPassword ? <FiEyeOff size={16} /> : <FiEye size={16} />}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="mt-1 w-full py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      <div className="flex justify-end mt-3">
        <Link to="/forgot-password" className="text-sm text-primary hover:underline">
          Forgot Password?
        </Link>
      </div>

      <div className="text-center mt-2">
        <Link to="/register" className="text-sm text-primary hover:underline">
          Don't have an account? Sign Up
        </Link>
      </div>
    </AuthLayout>
  );
}
