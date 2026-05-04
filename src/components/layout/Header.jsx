import { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { Show, UserButton } from "@clerk/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowUpFromBracket } from "@fortawesome/free-solid-svg-icons";
import Button from "../common/Button";
import logo from "../../assets/logo.jpeg";

const navLinks = [
  { label: "Session", to: "/session" },
  { label: "Summary", to: "/summary" },
  { label: "Mood Tracker", to: "/mood-tracker" },
  { label: "Psycho Education", to: "/psycho-education" },
  { label: "Settings", to: "/settings" },
];

const navClassName = ({ isActive }) =>
  `text-sm font-medium transition-colors ${
    isActive ? "text-[#32c4c3]" : "text-black hover:text-[#32c4c3]"
  }`;

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 1480) {
        setIsMenuOpen(false);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-16 w-full items-center px-4 md:px-6" style={{padding:"0 5px"}}>
        <div className="flex flex-1 items-center">
          <img src={logo} alt="SakoonAi logo" className="h-9 w-auto" />
        </div>

        <nav className="nav-desktop hidden flex-none items-center justify-center gap-8 xl:gap-10 lg:flex">
          {navLinks.map((link) => (
            <NavLink key={link.to} to={link.to} className={navClassName}>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="actions-desktop hidden flex-1 items-center justify-end gap-3 lg:flex">
          <Show when="signed-in">
            <Button text="End Session" backgroundColor="red" />
            <Button text="Save Session" border />
            <Button
              text="Share"
              border
              icon={<FontAwesomeIcon icon={faArrowUpFromBracket} />}
            />
            <UserButton afterSignOutUrl="/login" />
          </Show>
          <Show when="signed-out">
            <NavLink
              to="/login"
              className="text-sm font-medium text-black hover:text-[#32c4c3]"
            >
              Sign In
            </NavLink>
            <NavLink
              to="/register"
              className="rounded-md bg-[#32c4c3] px-4 py-2 text-sm font-medium text-white hover:bg-[#27a5a4]"
            >
              Sign Up
            </NavLink>
          </Show>
        </div>

        <div className="mobile-profile hidden flex items-center gap-3 lg:hidden">
          <Show when="signed-in">
            <UserButton afterSignOutUrl="/login" />
          </Show>
          <Show when="signed-out">
            <NavLink
              to="/login"
              className="text-sm font-medium text-black hover:text-[#32c4c3]"
            >
              Sign In
            </NavLink>
          </Show>
        </div>

        <button
          type="button"
          aria-label="Toggle navigation menu"
          onClick={() => setIsMenuOpen((prev) => !prev)}
          className="mobile-menu-btn hidden ml-3 rounded-md p-2 text-black transition-colors hover:bg-gray-100 lg:hidden"
        >
          {isMenuOpen ? (
            <svg
              className="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          ) : (
            <svg
              className="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          )}
        </button>
      </div>

      {isMenuOpen ? (
        <div className="border-t border-gray-200 bg-white !px-2 py-4 shadow-sm">
          <nav className="flex flex-col gap-2 !my-4">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `rounded-md !px-1 !py-2 text-base font-medium transition-colors ${
                    isActive
                      ? "bg-[#32c4c3]/10 text-[#32c4c3]"
                      : "text-black hover:bg-gray-100 hover:text-[#32c4c3]"
                  }`
                }
                onClick={() => setIsMenuOpen(false)}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-4 flex flex-col gap-2">
            <Show when="signed-in">
              <Button text="End Session" backgroundColor="red" className="w-full" />
              <Button text="Save Session" border className="w-full" />
              <Button
                text="Share"
                border
                className="w-full"
                icon={<FontAwesomeIcon icon={faArrowUpFromBracket} />}
              />
            </Show>
            <Show when="signed-out">
              <NavLink
                to="/register"
                className="rounded-md bg-[#32c4c3] py-2 text-center text-base font-medium text-white hover:bg-[#27a5a4]"
                onClick={() => setIsMenuOpen(false)}
              >
                Sign Up
              </NavLink>
            </Show>
          </div>
        </div>
      ) : null}
    </header>
  );
}
