import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { FiLock, FiEye, FiEyeOff } from "react-icons/fi";
import AuthLayout from "../layouts/AuthLayout";
import { resetPassword, parseApiError } from "../services/api";

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams]  = useSearchParams();
  const token           = searchParams.get("token") || "";

  const [form, setForm]             = useState({ newPassword: "", confirm: "" });
  const [show, setShow]             = useState({ newPassword: false, confirm: false });
  const [error, setError]           = useState("");
  const [success, setSuccess]       = useState(false);
  const [loading, setLoading]       = useState(false);

  const handle = (e) => { setForm((f) => ({ ...f, [e.target.name]: e.target.value })); setError(""); };
  const toggle = (field) => setShow((s) => ({ ...s, [field]: !s[field] }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token) return setError("Reset token is missing. Please use the link from your email.");
    if (form.newPassword.length < 8) return setError("Password must be at least 8 characters.");
    if (form.newPassword !== form.confirm) return setError("Passwords do not match.");

    setLoading(true);
    setError("");
    try {
      await resetPassword({ token, newPassword: form.newPassword });
      setSuccess(true);
      setTimeout(() => navigate("/login"), 2500);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Reset Password</h1>
      <p className="text-sm text-gray-500 mb-6">Enter your new password below.</p>

      {!token && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 text-sm">
          No reset token found. Please use the link from your email.
        </div>
      )}

      {error && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
          {error}
        </div>
      )}

      {success ? (
        <div className="px-3 py-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
          Password reset successfully! Redirecting to login…
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {[
            { name: "newPassword", label: "New Password",      placeholder: "Min 8 characters" },
            { name: "confirm",     label: "Confirm Password",  placeholder: "Repeat new password" },
          ].map(({ name, label, placeholder }) => (
            <div key={name}>
              <label className="block text-sm text-gray-700 mb-1">{label}</label>
              <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-primary transition-colors">
                <FiLock className="text-gray-400 shrink-0" size={16} />
                <input
                  type={show[name] ? "text" : "password"}
                  name={name}
                  value={form[name]}
                  onChange={handle}
                  placeholder={placeholder}
                  className="flex-1 text-sm text-gray-700 outline-none bg-transparent placeholder-gray-400"
                />
                <button type="button" tabIndex={-1} onClick={() => toggle(name)}
                  className="text-gray-400 hover:text-gray-600 transition-colors cursor-pointer">
                  {show[name] ? <FiEyeOff size={16} /> : <FiEye size={16} />}
                </button>
              </div>
            </div>
          ))}

          <button
            type="submit"
            disabled={loading || !token}
            className="mt-1 w-full py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Resetting…" : "Reset Password"}
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
