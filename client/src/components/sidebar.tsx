import { Fingerprint, Rss, ShieldAlert, BotMessageSquare } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

const navLinks = [
  {
    label: "Network Logs",
    href: "/",
    icon: Rss,
  },
  {
    label: "Security Alerts",
    href: "/security-alerts",
    icon: ShieldAlert,
  },
  {
    label: "GOC AI",
    href: "/goc-ai",
    icon: BotMessageSquare,
  },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <div className="w-[250px] h-screen bg-white px-4 py-6 shadow-lg">
      <div className="flex flex-col items-center">
        <div className="flex items-center space-x-5 mb-10">
          <Fingerprint className="p-2 w-[35px] h-[35px] bg-[#bdfae8] text-[#27bb90] rounded-lg" />
          <p className="font-bold text-[#27bb90] text-[18px]">GAMEOFCODE</p>
        </div>
        {/* Links */}
        <div className="w-full">
          <ul className="flex flex-col space-y-2">
            {navLinks.map((link, index) => (
              <Link
                to={link.href}
                className={`flex items-center px-3 py-3 font-bold border-l-[5px] rounded-lg w-full transition-colors duration-300 ${
                  location.pathname === link.href
                    ? "bg-[#27bb90]/20 border-l-[#27bb90]"
                    : "bg-transparent border-l-transparent hover:bg-[#27bb90]/10"
                }`}
                key={index}
              >
                <link.icon className="mr-3 text-[#27bb90]" size={22} />
                <span className="font-semibold text-gray-700">
                  {link.label}
                </span>
              </Link>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
