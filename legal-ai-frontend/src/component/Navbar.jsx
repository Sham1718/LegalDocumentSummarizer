import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="h-14 w-full bg-[#1f1b16] border-b border-[#3a2f25] flex items-center justify-between px-6">
      
      {/* App Icon / Name */}
      <div className="text-lg font-semibold text-[#f5efe6]">
        LegalAI
      </div>

      {/* If NOT logged in */}
      {!isAuthenticated && (
        <div className="flex gap-6 text-sm font-medium">
          <Link
            to="/login"
            className="text-[#d6c7b5] hover:text-[#f0b35a] transition"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="text-[#d6c7b5] hover:text-[#f0b35a] transition"
          >
            Register
          </Link>
        </div>
      )}

      {/* If logged in */}
      {isAuthenticated && (
        <>
          <div className="flex gap-6 text-sm font-medium text-[#d6c7b5]">
            <Link to="/ask" className="hover:text-[#f0b35a] transition">
              Ask
            </Link>
            <Link to="/upload" className="hover:text-[#f0b35a] transition">
              Upload
            </Link>
            <Link to="/history" className="hover:text-[#f0b35a] transition">
              History
            </Link>
          </div>

          <button
            onClick={handleLogout}
            className="text-sm text-[#f08c5a] hover:text-[#ff9f6e] font-medium transition"
          >
            Logout
          </button>
        </>
      )}

    </nav>
  );
}
