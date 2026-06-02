import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FiArrowLeft, FiMail } from "react-icons/fi";
import AuthLayout from "../layouts/AuthLayout";
import { forgotPassword, parseApiError } from "../services/api";

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email,   setEmail]   = useState("");
  const [error,   setError]   = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) return setError("Email is required.");
    setLoading(true);
    setError("");
    try {
      const data = await forgotPassword(email.trim());
      setSuccess(data.message || "If this email is registered, a reset link has been sent.");
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-primary hover:text-primary-hover mb-5 w-fit transition-colors"
      >
        <FiArrowLeft size={20} />
      </button>

      <h1 className="text-2xl font-bold text-gray-800 mb-1">Recover your account !</h1>
      <p className="text-sm text-gray-500 mb-6">
        Please enter your Email to access your account.
      </p>

      {error && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
          {error}
        </div>
      )}

      {success ? (
        <div className="px-3 py-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm mb-5">
          {success}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm text-gray-700 mb-1">Enter your recovery email</label>
            <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-primary transition-colors">
              <FiMail className="text-gray-400 shrink-0" size={16} />
              <input
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setError(""); }}
                placeholder="Enter your email"
                className="flex-1 text-sm text-gray-700 outline-none bg-transparent placeholder-gray-400"
                autoComplete="email"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-1 w-full py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Sending…" : "Send Link"}
          </button>
        </form>
      )}

      <div className="text-center mt-5">
        <Link to="/login" className="text-sm text-primary hover:underline">
          Back to Sign In
        </Link>
      </div>
    </AuthLayout>
  );
}
