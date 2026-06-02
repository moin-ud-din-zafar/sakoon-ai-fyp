import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff } from "react-icons/fi";
import AuthLayout from "../layouts/AuthLayout";
import { registerUser, parseApiError } from "../services/api";
import { useApp } from "../contexts/AppContext";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useApp();

  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) return setError("Username is required.");
    if (!form.email.trim()) return setError("Email is required.");
    if (form.password.length < 8) return setError("Password must be at least 8 characters.");

    setLoading(true);
    try {
      const data = await registerUser({
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
      });
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
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Welcome !</h1>
      <p className="text-sm text-gray-500 mb-6">
        Please enter your Email to Create your account.
      </p>

      {error && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Username */}
        <div>
          <label className="block text-sm text-gray-700 mb-1">Username</label>
          <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-primary transition-colors">
            <FiUser className="text-gray-400 shrink-0" size={16} />
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Enter Username"
              className="flex-1 text-sm text-gray-700 outline-none bg-transparent placeholder-gray-400"
              autoComplete="username"
            />
          </div>
        </div>

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
              autoComplete="new-password"
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
          {loading ? "Creating..." : "Create"}
        </button>
      </form>

      <div className="flex items-center justify-between mt-4">
        <Link to="/forgot-password" className="text-sm text-primary hover:underline">
          Forgot Password?
        </Link>
        <Link to="/login" className="text-sm text-primary hover:underline">
          Have an account? Sign in
        </Link>
      </div>
    </AuthLayout>
  );
}
