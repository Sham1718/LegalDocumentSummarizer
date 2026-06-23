import React, { useState } from "react";
import { loginUser } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await loginUser({ email, password });
      login(res.data.token);
      navigate("/ask");
    } catch {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#14110d]">
      <div className="w-full max-w-md bg-[#1f1b16] border border-[#3a2f25] rounded-xl p-8 text-[#f5efe6]">
        
        <h2 className="text-2xl font-semibold text-center mb-6">
          Login to Your Account
        </h2>

        {error && (
          <p className="text-red-400 text-sm text-center mb-4">
            {error}
          </p>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          
          <div>
            <label className="block text-sm font-medium text-[#d6c7b5] mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-4 py-2 rounded-lg bg-[#14110d] border border-[#3a2f25] text-[#f5efe6]
                         focus:outline-none focus:ring-2 focus:ring-[#f0b35a]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#d6c7b5] mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-2 rounded-lg bg-[#14110d] border border-[#3a2f25] text-[#f5efe6]
                         focus:outline-none focus:ring-2 focus:ring-[#f0b35a]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#f0b35a] text-[#14110d] py-2 rounded-lg font-medium
                       hover:opacity-90 transition disabled:opacity-50"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
