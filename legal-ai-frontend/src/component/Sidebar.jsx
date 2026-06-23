import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../utils/axios";
import { useAuth } from "../context/AuthContext";
import { getQueryHistory } from "../api/ask";

export default function Sidebar() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [recent, setRecent] = useState([]);

  useEffect(() => {
      getQueryHistory()
      .then((res) => setRecent(res.data.content))
      .catch(() => {});
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <aside className="w-60 h-screen bg-[#1a1612] border-r border-[#3a2f25] flex flex-col p-4">
      
      {/* Navigation */}
      <nav className="flex flex-col gap-4 text-base font-medium text-[#e6d8c7] mt-2">
        <Link to="/ask" className="hover:text-[#f0b35a] transition">
          Ask
        </Link>
        <Link to="/upload" className="hover:text-[#f0b35a] transition">
          Upload
        </Link>
        <Link to="/history" className="hover:text-[#f0b35a] transition">
          Full History
        </Link>
      </nav>

      {/* Divider */}
      <div className="my-6 border-t border-[#3a2f25]" />

      {/* Recent Queries */}
      <div className="flex-1 overflow-hidden">
        <h4 className="text-sm uppercase tracking-wide text-[#b6a892] mb-3">
          Recent Queries
        </h4>

        <ul className="text-sm text-[#d6c7b5] space-y-2 overflow-y-auto max-h-40 pr-1">
          {recent.length === 0 && (
            <li className="text-[#7a6a58]">No recent queries</li>
          )}
          {recent.map((r, i) => (
            <li
              key={i}
              className="truncate hover:text-[#f0b35a] cursor-pointer"
              title={r.question}
            >
              {r.question}
            </li>
          ))}
        </ul>
      </div>

      {/* Logout */}
      <button
        onClick={handleLogout}
        className="mt-6 text-base text-[#f08c5a] hover:text-[#ff9f6e] transition text-left"
      >
        Logout
      </button>
    </aside>
  );
}
