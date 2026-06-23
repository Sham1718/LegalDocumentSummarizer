import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register } from "../api/auth";
import { useAuth } from "../context/AuthContext";

const Register = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const { registerToken } = useAuth();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await register({ username, email, password });
      registerToken(res.data.token);
      navigate("/ask");
    } catch {
      setError("Registration failed. Username or email may already exist.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#14110d] px-4">
      <div className="w-full max-w-md bg-[#1f1b16] border border-[#3a2f25] rounded-xl p-8 text-[#f5efe6]">

        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-semibold">
            Create Your Account
          </h1>
          <p className="text-sm text-[#b6a892] mt-1">
            Get started with LegalAI
          </p>
        </div>

        {error && (
          <p className="text-red-400 text-sm text-center mb-4">
            {error}
          </p>
        )}

        {/* Form */}
        <form onSubmit={handleRegister} className="space-y-4">

          <div>
            <label className="block text-sm text-[#d6c7b5] mb-1">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="yourname"
              required
              className="w-full px-4 py-2 rounded-lg bg-[#14110d] border border-[#3a2f25]
                         text-[#f5efe6] focus:outline-none focus:ring-2 focus:ring-[#f0b35a]"
            />
          </div>

          <div>
            <label className="block text-sm text-[#d6c7b5] mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="w-full px-4 py-2 rounded-lg bg-[#14110d] border border-[#3a2f25]
                         text-[#f5efe6] focus:outline-none focus:ring-2 focus:ring-[#f0b35a]"
            />
          </div>

          <div>
            <label className="block text-sm text-[#d6c7b5] mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full px-4 py-2 rounded-lg bg-[#14110d] border border-[#3a2f25]
                         text-[#f5efe6] focus:outline-none focus:ring-2 focus:ring-[#f0b35a]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#f0b35a] text-[#14110d] py-2 rounded-lg font-medium
                       hover:opacity-90 transition disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        {/* Footer */}
        <p className="text-sm text-center text-[#b6a892] mt-6">
          Already have an account?{" "}
          <button
            onClick={() => navigate("/")}
            className="text-[#f0b35a] hover:underline"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
};

export default Register;
