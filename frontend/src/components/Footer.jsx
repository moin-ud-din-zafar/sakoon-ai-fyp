import { Link } from "react-router-dom";
import { FaFacebook, FaTwitter, FaInstagram, FaLinkedin } from "react-icons/fa";
import logo from "../assets/images/logo.jpeg";

const PLATFORM_LINKS = ["About Us", "Features", "Pricing"];
const RESOURCE_LINKS = ["Blog", "FAQ", "Support"];
const LEGAL_LINKS    = ["Terms of Service", "Privacy Policy"];

const SOCIAL_ICONS = [
  { icon: FaFacebook,  label: "Facebook" },
  { icon: FaTwitter,   label: "Twitter" },
  { icon: FaInstagram, label: "Instagram" },
  { icon: FaLinkedin,  label: "LinkedIn" },
];

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">

          {/* Brand */}
          <div>
            <img src={logo} alt="Sakoon AI" className="h-8 w-auto object-contain mb-3" />
            <p className="text-sm text-gray-500 leading-relaxed mb-4 max-w-[220px]">
              Your AI companion for mental wellness, offering accessible therapy and support.
            </p>
            <div className="flex items-center gap-3">
              {SOCIAL_ICONS.map(({ icon: Icon, label }) => (
                <Link
                  key={label}
                  to="/session"
                  aria-label={label}
                  className="text-gray-400 hover:text-primary transition-colors"
                >
                  <Icon size={18} />
                </Link>
              ))}
            </div>
          </div>

          {/* Platform */}
          <div>
            <h4 className="text-sm font-semibold text-gray-800 mb-3">Platform</h4>
            <ul className="flex flex-col gap-2">
              {PLATFORM_LINKS.map((item) => (
                <li key={item}>
                  <Link
                    to="/session"
                    className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
                  >
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-sm font-semibold text-gray-800 mb-3">Resources</h4>
            <ul className="flex flex-col gap-2">
              {RESOURCE_LINKS.map((item) => (
                <li key={item}>
                  <Link
                    to="/session"
                    className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
                  >
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-sm font-semibold text-gray-800 mb-3">Legal</h4>
            <ul className="flex flex-col gap-2">
              {LEGAL_LINKS.map((item) => (
                <li key={item}>
                  <Link
                    to="/session"
                    className="text-sm text-gray-500 hover:text-gray-800 transition-colors"
                  >
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-6 border-t border-gray-100">
          <p className="text-sm text-gray-400">© 2024 Sakoon AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
