import { useState, useEffect, useCallback } from "react";
import {
  FiActivity, FiUsers, FiCheckCircle, FiAlertOctagon,
  FiPlus, FiGrid, FiFileText, FiSettings,
  FiUserCheck, FiUserX, FiMessageSquare,
  FiAlertCircle, FiAlertTriangle, FiInfo,
  FiLogOut, FiRefreshCw, FiEye, FiEyeOff,
} from "react-icons/fi";
import {
  adminLogin, getAdminStats, getAdminSessions,
  getAdminCrisisAlerts, parseApiError,
} from "../services/api";

const ADMIN_KEY = "sakoon_admin_key";

// ── helpers ────────────────────────────────────────────────────────────────
const fmt = (n) => (n === null || n === undefined ? "—" : Number(n).toLocaleString());

function timeAgo(dateStr) {
  if (!dateStr) return "";
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 60)    return "just now";
  if (diff < 3600)  return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
  return `${Math.floor(diff / 86400)} days ago`;
}

// ── Admin Login ────────────────────────────────────────────────────────────
function AdminLoginPage({ onLogin }) {
  const [form, setForm]           = useState({ username: "", password: "" });
  const [showPassword, setShowPwd] = useState(false);
  const [error, setError]          = useState("");
  const [loading, setLoading]      = useState(false);

  const handle = (e) => { setForm((f) => ({ ...f, [e.target.name]: e.target.value })); setError(""); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) return setError("Both fields are required.");
    setLoading(true);
    try {
      const data = await adminLogin(form);
      sessionStorage.setItem(ADMIN_KEY, data.adminKey);
      onLogin(data.adminKey);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 w-full max-w-sm">
        <h1 className="text-xl font-bold text-gray-800 mb-1">Admin Login</h1>
        <p className="text-sm text-gray-500 mb-6">Access the Sakoon AI admin panel.</p>

        {error && (
          <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Username */}
          <div>
            <label className="block text-sm text-gray-700 mb-1">Username</label>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handle}
              placeholder="Admin username"
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm text-gray-700 outline-none focus:border-primary transition-colors"
              autoComplete="username"
            />
          </div>

          {/* Password with eye toggle */}
          <div>
            <label className="block text-sm text-gray-700 mb-1">Password</label>
            <div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-primary transition-colors">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={form.password}
                onChange={handle}
                placeholder="Admin password"
                className="flex-1 text-sm text-gray-700 outline-none bg-transparent placeholder-gray-400"
                autoComplete="current-password"
              />
              <button
                type="button"
                tabIndex={-1}
                onClick={() => setShowPwd((v) => !v)}
                className="text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
              >
                {showPassword ? <FiEyeOff size={16} /> : <FiEye size={16} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-1 w-full py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors disabled:opacity-60 cursor-pointer"
          >
            {loading ? "Signing in…" : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ── Stat Card ──────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, subtext, subtextColor = "text-green-500" }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-500">{label}</span>
        <Icon size={13} className="text-gray-400" />
      </div>
      <p className="text-2xl font-bold text-gray-800 mb-0.5">{value}</p>
      <p className={`text-xs ${subtextColor}`}>{subtext}</p>
    </div>
  );
}

// ── Management Card ────────────────────────────────────────────────────────
function ManagementCard({ title, items }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex-1 min-w-0">
      <h2 className="text-sm font-semibold text-gray-800 mb-3">{title}</h2>
      <div className="flex flex-col">
        {items.map(({ icon: Icon, label, onClick }) => (
          <button
            key={label}
            onClick={onClick}
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-colors text-left cursor-pointer"
          >
            <Icon size={13} className="text-gray-400 shrink-0" />
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}

// ── Activity Item ──────────────────────────────────────────────────────────
function ActivityItem({ name, action, time }) {
  return (
    <div className="flex items-start gap-2.5">
      <div className="w-6 h-6 rounded-full bg-primary-light flex items-center justify-center text-primary text-xs font-bold shrink-0 mt-0.5">
        {name?.charAt(0)?.toUpperCase() || "U"}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-700 leading-snug">
          <span className="font-medium">{name}</span> {action}
        </p>
        <p className="text-[11px] text-gray-400 mt-0.5">{time}</p>
      </div>
    </div>
  );
}

// ── Alert Item ─────────────────────────────────────────────────────────────
const ALERT_STYLES = {
  critical: { Icon: FiAlertCircle,   color: "text-red-500",    bg: "bg-red-50" },
  warning:  { Icon: FiAlertTriangle, color: "text-orange-500", bg: "bg-orange-50" },
  info:     { Icon: FiInfo,          color: "text-blue-500",   bg: "bg-blue-50" },
};

function AlertItem({ type, message }) {
  const { Icon, color, bg } = ALERT_STYLES[type] ?? ALERT_STYLES.info;
  return (
    <div className={`flex items-start gap-2.5 rounded-lg p-2.5 ${bg}`}>
      <Icon size={13} className={`${color} shrink-0 mt-0.5`} />
      <p className="text-xs text-gray-700 leading-snug">{message}</p>
    </div>
  );
}

// ── Dashboard ──────────────────────────────────────────────────────────────
function AdminDashboard({ adminKey, onLogout }) {
  const [stats,    setStats]    = useState(null);
  const [sessions, setSessions] = useState([]);
  const [alerts,   setAlerts]   = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState("");

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [statsRes, sessionsRes, alertsRes] = await Promise.all([
        getAdminStats(adminKey),
        getAdminSessions(adminKey),
        getAdminCrisisAlerts(adminKey),
      ]);
      setStats(statsRes);
      setSessions(sessionsRes.sessions || []);
      setAlerts(alertsRes.alerts || []);
    } catch (err) {
      if (err?.response?.status === 401) {
        sessionStorage.removeItem(ADMIN_KEY);
        onLogout();
      } else {
        setError(parseApiError(err));
      }
    } finally {
      setLoading(false);
    }
  }, [adminKey, onLogout]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const completedSessions = sessions.filter((s) => s.status === "completed").length;
  const uniqueUsers       = new Set(sessions.map((s) => s.userId)).size;

  const CONTENT_ITEMS = [
    { icon: FiPlus,      label: "Add New Lesson",          onClick: () => console.log("Add New Lesson") },
    { icon: FiGrid,      label: "Manage Categories",        onClick: () => console.log("Manage Categories") },
    { icon: FiCheckCircle, label: "Review Submissions",     onClick: () => console.log("Review Submissions") },
    { icon: FiSettings,  label: "Psychoeducation Settings", onClick: () => console.log("Psychoeducation Settings") },
  ];
  const USER_ITEMS = [
    { icon: FiUsers,        label: "View All Users",      onClick: () => console.log("View All Users") },
    { icon: FiUserCheck,    label: "Manage Roles",        onClick: () => console.log("Manage Roles") },
    { icon: FiUserX,        label: "Deactivate Accounts", onClick: () => console.log("Deactivate Accounts") },
    { icon: FiMessageSquare, label: "User Feedback",      onClick: () => console.log("User Feedback") },
  ];

  const systemAlerts = alerts.map((a) => ({
    type: "critical",
    message: `Crisis alert — ${a.userName || "User"}: "${String(a.lastMessage || "").slice(0, 80)}"`,
  }));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header bar */}
      <div className="bg-white border-b border-gray-200 px-4 sm:px-8 py-3 flex items-center justify-between">
        <h1 className="text-sm font-semibold text-gray-800">Admin Panel Dashboard</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchAll}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 text-xs text-gray-600 hover:bg-gray-50 transition-colors cursor-pointer"
          >
            <FiRefreshCw size={11} />
            Refresh
          </button>
          <button
            onClick={() => { sessionStorage.removeItem(ADMIN_KEY); onLogout(); }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 text-xs text-gray-600 hover:bg-gray-50 transition-colors cursor-pointer"
          >
            <FiLogOut size={11} />
            Logout
          </button>
        </div>
      </div>

      <div className="max-w-[90vw] mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {error && (
          <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-24 text-sm text-gray-400">
            Loading dashboard…
          </div>
        ) : (
          <>
            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
              <StatCard
                icon={FiActivity}
                label="Active Sessions"
                value={fmt(stats?.totalSessions)}
                subtext="+52% from last month"
              />
              <StatCard
                icon={FiUsers}
                label="Total Users"
                value={fmt(uniqueUsers)}
                subtext="+6% from last month"
              />
              <StatCard
                icon={FiCheckCircle}
                label="Completed Sessions"
                value={fmt(completedSessions)}
                subtext="+48% from last month"
              />
              <StatCard
                icon={FiAlertOctagon}
                label="Crisis Alerts"
                value={fmt(stats?.crisisCount)}
                subtext="+4% from last month"
                subtextColor="text-red-500"
              />
            </div>

            {/* Management */}
            <div className="flex flex-col sm:flex-row gap-4 mb-5">
              <ManagementCard title="Content Management" items={CONTENT_ITEMS} />
              <ManagementCard title="User Management"    items={USER_ITEMS} />
            </div>

            {/* Activity + Alerts */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="bg-white rounded-xl border border-gray-200 p-5 flex-1 min-w-0">
                <h2 className="text-sm font-semibold text-gray-800 mb-3">Recent User Activity</h2>
                {sessions.length > 0 ? (
                  <div className="flex flex-col gap-3">
                    {sessions.slice(0, 6).map((s) => (
                      <ActivityItem
                        key={s.id}
                        name={s.userName || `User #${s.userId}`}
                        action={`started session #${s.sessionNo} · ${s.status}`}
                        time={timeAgo(s.createdAt)}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-gray-400">No recent activity found.</p>
                )}
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-5 flex-1 min-w-0">
                <h2 className="text-sm font-semibold text-gray-800 mb-3">System Alerts</h2>
                {systemAlerts.length > 0 ? (
                  <div className="flex flex-col gap-2">
                    {systemAlerts.map((a, i) => (
                      <AlertItem key={i} type={a.type} message={a.message} />
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-gray-400">No active alerts.</p>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ── Page export ────────────────────────────────────────────────────────────
export default function AdminDashboardPage() {
  const [adminKey, setAdminKey] = useState(
    () => sessionStorage.getItem(ADMIN_KEY) || ""
  );

  if (!adminKey) return <AdminLoginPage onLogin={setAdminKey} />;
  return <AdminDashboard adminKey={adminKey} onLogout={() => setAdminKey("")} />;
}
