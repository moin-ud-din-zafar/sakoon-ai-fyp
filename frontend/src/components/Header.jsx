import { useState } from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import { HiMenu, HiX } from "react-icons/hi";
import { FiHelpCircle } from "react-icons/fi";
import logo from "../assets/images/logo.jpeg";
import { useApp } from "../contexts/AppContext";

const NAV_LINKS = [
  { label: "Session",         to: "/session" },
  { label: "Summary",         to: "/summary" },
  { label: "Mood Tracker",    to: "/mood-tracker" },
  { label: "Psychoeducation", to: "/psychoeducation" },
  { label: "Setting",         to: "/setting" },
];

// ── shared ──────────────────────────────────────────────────────────────────
function HelpBtn() {
  return (
    <button
      onClick={() => console.log("Help clicked")}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50 transition-colors leading-none cursor-pointer"
    >
      <FiHelpCircle size={16} className="text-gray-500 shrink-0" />
      Help
    </button>
  );
}

// ── per-route action groups ──────────────────────────────────────────────────
function SessionActions({ onEndSession, mobile }) {
  const base = mobile
    ? "w-full py-2 rounded-lg text-sm font-medium transition-colors leading-none cursor-pointer"
    : "px-4 py-1.5 rounded-lg text-sm font-medium transition-colors leading-none cursor-pointer";

  return (
    <>
      <button
        onClick={onEndSession}
        className={`${base} bg-[#FF7070] hover:bg-[#f05e5e] text-white`}
      >
        End Session
      </button>
      <button
        onClick={() => console.log("Save Session clicked")}
        className={`${base} ${mobile ? "border border-gray-200 text-gray-700 hover:bg-gray-50" : "text-gray-700 hover:text-gray-900"}`}
      >
        Save Session
      </button>
      <button
        onClick={() => console.log("Share clicked")}
        className={`${base} ${mobile ? "border border-gray-200 text-gray-700 hover:bg-gray-50" : "text-gray-700 hover:text-gray-900"}`}
      >
        Share
      </button>
    </>
  );
}

function SettingActions({ user, mobile }) {
  const initials = user?.name?.charAt(0)?.toUpperCase() || "U";

  const handleSave = () => {
    // No API yet — wire up PATCH /user or similar when backend supports it
    console.log("Save settings clicked");
  };

  if (mobile) {
    return (
      <>
        <HelpBtn />
        <button
          onClick={handleSave}
          className="w-full py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors leading-none cursor-pointer"
        >
          Save
        </button>
      </>
    );
  }

  return (
    <>
      <HelpBtn />
      <button
        onClick={handleSave}
        className="px-5 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors leading-none cursor-pointer"
      >
        Save
      </button>
      <div className="w-8 h-8 rounded-full bg-primary-light overflow-hidden flex items-center justify-center text-primary text-sm font-bold select-none shrink-0">
        {user?.profileImageUrl ? (
          <img src={user.profileImageUrl} alt={initials} className="w-full h-full object-cover" />
        ) : initials}
      </div>
    </>
  );
}

function OtherActions() {
  return <HelpBtn />;
}

// ── main ─────────────────────────────────────────────────────────────────────
export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { logout, user } = useApp();
  const navigate     = useNavigate();
  const { pathname } = useLocation();

  const handleEndSession = () => {
    setMenuOpen(false);
    logout();
    navigate("/login");
  };

  const renderActions = (mobile = false) => {
    if (pathname === "/session") return <SessionActions onEndSession={handleEndSession} mobile={mobile} />;
    if (pathname === "/setting") return <SettingActions user={user} mobile={mobile} />;
    return <OtherActions />;
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      {/* Single row — breakpoint at 1050px */}
      <div className="flex items-center justify-between h-14 px-4 sm:px-6 lg:px-8">

        {/* Logo */}
        <NavLink to="/session" className="shrink-0 flex items-center">
          <img src={logo} alt="Sakoon AI" className="h-8 w-auto object-contain block" />
        </NavLink>

        {/* Desktop nav — visible >= 1050px */}
        <nav className="hidden min-[1050px]:flex items-center gap-6">
          {NAV_LINKS.map(({ label, to }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `text-sm font-medium leading-none transition-colors ${
                  isActive ? "text-primary" : "text-gray-600 hover:text-gray-900"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Desktop actions — visible >= 1050px */}
        <div className="hidden min-[1050px]:flex items-center gap-2">
          {renderActions(false)}
        </div>

        {/* Hamburger — visible < 1050px */}
        <button
          className="min-[1050px]:hidden flex items-center justify-center p-1.5 text-gray-600 hover:text-gray-900 transition-colors cursor-pointer"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          {menuOpen ? <HiX size={22} /> : <HiMenu size={22} />}
        </button>
      </div>

      {/* Mobile menu — visible < 1050px */}
      {menuOpen && (
        <div className="min-[1050px]:hidden border-t border-gray-100 bg-white px-4 pb-4 pt-2">
          <nav className="flex flex-col gap-1 mb-3">
            {NAV_LINKS.map(({ label, to }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `px-2 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "text-primary bg-primary-light"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="flex flex-col gap-2 pt-2 border-t border-gray-100">
            {renderActions(true)}
          </div>
        </div>
      )}
    </header>
  );
}
