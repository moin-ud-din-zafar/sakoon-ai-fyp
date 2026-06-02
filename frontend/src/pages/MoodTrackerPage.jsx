import { useState, useEffect, useCallback } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import {
  FiSmile, FiFrown, FiMeh, FiChevronLeft, FiChevronRight,
  FiTrendingUp, FiAlertTriangle, FiInfo, FiUsers, FiCalendar,
} from "react-icons/fi";
import AppLayout from "../layouts/AppLayout";
import { useApp } from "../contexts/AppContext";
import { logMood, getMoodHistory, parseApiError } from "../services/api";

// ── constants ──────────────────────────────────────────────────────────────
const MONTHS    = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const DAY_LABELS = ["Su","Mo","Tu","We","Th","Fr","Sa"];

const MOODS = [
  { label: "Happy",   score: 5, icon: FiSmile, color: "text-green-500",  bg: "bg-green-50",  border: "border-green-200",  badge: "bg-green-100 text-green-700"  },
  { label: "Neutral", score: 3, icon: FiMeh,   color: "text-amber-500",  bg: "bg-amber-50",  border: "border-amber-200",  badge: "bg-amber-100 text-amber-700"  },
  { label: "Sad",     score: 1, icon: FiFrown, color: "text-red-400",    bg: "bg-red-50",    border: "border-red-200",    badge: "bg-red-100 text-red-700"     },
];

// ── helpers ────────────────────────────────────────────────────────────────
const scoreToLabel = (s) => s >= 4 ? "happy" : s === 3 ? "neutral" : "sad";
const scoreToBadge = (s) => MOODS.find(m => m.label.toLowerCase() === scoreToLabel(s));
const formatDate   = (d) => new Date(d).toISOString().slice(0, 10);
const getDayName   = (d) => ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"][new Date(d).getDay()];

function buildCalendarDays(year, month) {
  const firstDay    = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const prevDays    = new Date(year, month, 0).getDate();
  const days = [];
  for (let i = firstDay - 1; i >= 0; i--) days.push({ day: prevDays - i, cur: false });
  for (let i = 1; i <= daysInMonth; i++)   days.push({ day: i, cur: true });
  while (days.length % 7 !== 0)             days.push({ day: days.length - firstDay - daysInMonth + 1, cur: false });
  return days;
}

function generateInsights(history) {
  if (history.length === 0) return [];
  const avg   = history.reduce((s, e) => s + e.moodScore, 0) / history.length;
  const happy = history.filter(e => e.moodScore >= 4).length;
  const sad   = history.filter(e => e.moodScore <= 2).length;
  const insights = [];

  if (happy >= history.length * 0.4)
    insights.push({ type: "positive", icon: FiSmile,        text: "You tend to feel better after therapy sessions." });
  if (avg >= 3.5)
    insights.push({ type: "info",     icon: FiUsers,        text: "Social activities boost your mood significantly." });
  if (sad > 0)
    insights.push({ type: "warning",  icon: FiAlertTriangle, text: "Work stress appears to be a common trigger." });

  return insights;
}


// ── sub-components ─────────────────────────────────────────────────────────
function LogMoodSection({ userId, onLogged }) {
  const [selected, setSelected] = useState(null);
  const [note,     setNote]     = useState("");
  const [loading,  setLoading]  = useState(false);
  const [success,  setSuccess]  = useState(false);

  const handleLog = async () => {
    if (!selected) return;
    setLoading(true);
    try {
      await logMood(userId, selected.score, note.trim() || null);
      setSelected(null);
      setNote("");
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2500);
      onLogged();
    } catch { /* silent */ }
    finally { setLoading(false); }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center gap-2 mb-1">
        <FiSmile size={15} className="text-primary" />
        <h2 className="text-sm font-semibold text-gray-800">Log Your Mood</h2>
      </div>
      <p className="text-xs text-gray-500 mb-4">How are you feeling right now?</p>

      <div className="grid grid-cols-3 gap-3 mb-4">
        {MOODS.map((m) => {
          const Icon = m.icon;
          const active = selected?.label === m.label;
          return (
            <button
              key={m.label}
              onClick={() => setSelected(active ? null : m)}
              className={`flex flex-col items-center gap-1.5 py-3 rounded-xl border-2 transition-all cursor-pointer ${
                active ? `${m.bg} ${m.border}` : "border-gray-100 hover:border-gray-200"
              }`}
            >
              <Icon size={24} className={active ? m.color : "text-gray-400"} />
              <span className={`text-xs font-medium ${active ? m.color : "text-gray-500"}`}>{m.label}</span>
            </button>
          );
        })}
      </div>

      {selected && (
        <div className="flex flex-col gap-2 mt-1">
          <input
            type="text"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Optional note…"
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-xs text-gray-700 outline-none focus:border-primary transition-colors placeholder-gray-400"
          />
          <button
            onClick={handleLog}
            disabled={loading}
            className="w-full py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-medium transition-colors disabled:opacity-60 cursor-pointer"
          >
            {loading ? "Logging…" : "Log Mood"}
          </button>
        </div>
      )}

      {success && (
        <p className="text-xs text-green-600 mt-2 text-center">Mood logged successfully!</p>
      )}
    </div>
  );
}

function MoodHistoryItem({ entry }) {
  const badge  = scoreToBadge(entry.moodScore);
  const intStr = `${entry.moodScore * 2}/10`;

  return (
    <div className="flex items-start justify-between gap-3 py-2.5 border-b border-gray-50 last:border-0">
      <div className="shrink-0">
        <div className={`w-5 h-5 rounded-full flex items-center justify-center ${badge?.bg || "bg-gray-100"}`}>
          {badge && <badge.icon size={11} className={badge.color} />}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] text-gray-400 leading-none mb-0.5">
          {formatDate(entry.loggedAt)} &middot; Intensity: {intStr}
        </p>
        <p className="text-xs text-gray-600 leading-snug line-clamp-1">
          {entry.note || "—"}
        </p>
      </div>
      <span className={`shrink-0 text-[10px] font-medium px-2 py-0.5 rounded-full ${badge?.badge || "bg-gray-100 text-gray-500"}`}>
        {scoreToLabel(entry.moodScore)}
      </span>
    </div>
  );
}

function MoodHistorySection({ title, entries }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center gap-2 mb-3">
        <FiTrendingUp size={15} className="text-primary" />
        <h2 className="text-sm font-semibold text-gray-800">{title}</h2>
      </div>
      {entries.length > 0 ? (
        <div>{entries.map((e) => <MoodHistoryItem key={e.id} entry={e} />)}</div>
      ) : (
        <p className="text-xs text-gray-400 py-4 text-center">No entries yet.</p>
      )}
    </div>
  );
}

function MoodLineChart({ history }) {
  const chartData = [...history].slice(0, 7).reverse().map((e) => ({
    day:   getDayName(e.loggedAt),
    score: Math.round((e.moodScore / 5) * 100),
  }));

  if (chartData.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h2 className="text-sm font-semibold text-gray-800 mb-4">Mood Trend</h2>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis dataKey="day" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 100]} ticks={[0,25,50,75,100]} tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ fontSize: 11, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,.08)", borderRadius: 8 }}
            formatter={(v) => [`${v}/100`, "Mood"]}
          />
          <Line type="monotone" dataKey="score" stroke="#14c6be" strokeWidth={2} dot={{ r: 4, fill: "#14c6be" }} activeDot={{ r: 5 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function CalendarSection() {
  const today = new Date();
  const [calMonth, setCalMonth] = useState(today.getMonth());
  const [calYear,  setCalYear]  = useState(today.getFullYear());

  const days = buildCalendarDays(calYear, calMonth);

  const goPrev = () => {
    if (calMonth === 0) { setCalMonth(11); setCalYear((y) => y - 1); }
    else                { setCalMonth((m) => m - 1); }
  };
  const goNext = () => {
    if (calMonth === 11) { setCalMonth(0); setCalYear((y) => y + 1); }
    else                 { setCalMonth((m) => m + 1); }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center gap-2 mb-3">
        <FiCalendar size={14} className="text-primary" />
        <h2 className="text-sm font-semibold text-gray-800">Calendar</h2>
      </div>
      <div className="flex items-center justify-between mb-3">
        <button type="button" onClick={goPrev} className="p-1 hover:bg-gray-50 rounded cursor-pointer text-gray-500">
          <FiChevronLeft size={14} />
        </button>
        <span className="text-xs font-medium text-gray-700">{MONTHS[calMonth]} {calYear}</span>
        <button type="button" onClick={goNext} className="p-1 hover:bg-gray-50 rounded cursor-pointer text-gray-500">
          <FiChevronRight size={14} />
        </button>
      </div>
      <div className="grid grid-cols-7 mb-1">
        {DAY_LABELS.map((d) => (
          <div key={d} className="text-center text-[10px] text-gray-400 font-medium py-1">{d}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-y-1">
        {days.map((d, i) => {
          const isToday = d.cur && d.day === today.getDate() && calMonth === today.getMonth() && calYear === today.getFullYear();
          return (
            <div
              key={i}
              className={`text-center text-[11px] rounded-full mx-auto w-6 h-6 flex items-center justify-center
                ${!d.cur ? "text-gray-300" : isToday ? "bg-primary text-white font-semibold" : "text-gray-600 hover:bg-gray-50"}`}
            >
              {d.day}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function WeeklySummarySection({ history }) {
  const last7 = history.slice(0, 7);
  const avg   = last7.length ? last7.reduce((s, e) => s + e.moodScore, 0) / last7.length : 0;
  const avgDisplay = (avg * 2).toFixed(1); // scale to /10
  const happy    = last7.filter(e => e.moodScore >= 4).length;
  const neutral  = last7.filter(e => e.moodScore === 3).length;
  const difficult = last7.filter(e => e.moodScore <= 2).length;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center gap-2 mb-3">
        <FiTrendingUp size={14} className="text-primary" />
        <h2 className="text-sm font-semibold text-gray-800">Weekly Summary</h2>
      </div>
      <p className="text-3xl font-bold text-primary mb-0.5">{last7.length ? avgDisplay : "—"}</p>
      <p className="text-xs text-gray-500 mb-3">Average Mood Score</p>
      <div className="flex flex-col gap-1.5">
        {[
          { label: "Happy Days",    value: happy },
          { label: "Neutral Days",  value: neutral },
          { label: "Difficult Days", value: difficult },
        ].map(({ label, value }) => (
          <div key={label} className="flex items-center justify-between">
            <span className="text-xs text-gray-500">{label}</span>
            <span className="text-xs font-semibold text-gray-700">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function InsightsSection({ history }) {
  const insights = generateInsights(history);
  const STYLES = {
    positive: { bg: "bg-green-50", icon: "text-green-500" },
    info:     { bg: "bg-blue-50",  icon: "text-blue-500"  },
    warning:  { bg: "bg-amber-50", icon: "text-amber-500" },
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center gap-2 mb-3">
        <FiInfo size={14} className="text-primary" />
        <h2 className="text-sm font-semibold text-gray-800">Insights</h2>
      </div>
      {insights.length > 0 ? (
        <div className="flex flex-col gap-2">
          {insights.map((ins, i) => {
            const Icon = ins.icon;
            const s = STYLES[ins.type] || STYLES.info;
            return (
              <div key={i} className={`flex items-start gap-2.5 rounded-lg p-3 ${s.bg}`}>
                <Icon size={13} className={`${s.icon} shrink-0 mt-0.5`} />
                <p className="text-xs text-gray-700 leading-relaxed">{ins.text}</p>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-xs text-gray-400 py-3 text-center">Log more moods to see insights.</p>
      )}
    </div>
  );
}


// ── main page ──────────────────────────────────────────────────────────────
export default function MoodTrackerPage() {
  const { user } = useApp();
  const userId   = user?.id;

  const [history,  setHistory]  = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState("");

  const fetchHistory = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    setError("");
    try {
      const data = await getMoodHistory(userId, 30);
      setHistory(data.entries || []);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const recentEntries     = history.slice(0, 7);
  const lastMonthEntries  = history;

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[50vh] text-sm text-gray-400">
          Loading mood data…
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      {error && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
          {error}
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-5">
        {/* Left column */}
        <div className="flex-1 flex flex-col gap-5 min-w-0">
          <LogMoodSection userId={userId} onLogged={fetchHistory} />
          <MoodHistorySection title="Recent Mood History"    entries={recentEntries} />
          <MoodHistorySection title="Last Month History"     entries={lastMonthEntries} />
          <MoodLineChart history={history} />
        </div>

        {/* Right column */}
        <div className="w-full lg:w-72 xl:w-80 flex flex-col gap-5 shrink-0">
          <CalendarSection />
          <WeeklySummarySection history={history} />
          <InsightsSection history={history} />
        </div>
      </div>
    </AppLayout>
  );
}
