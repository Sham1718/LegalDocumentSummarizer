import { useState, useEffect } from "react";
import api from "../utils/axios";
import { useNavigate } from "react-router-dom";
import Sidebar from "../component/Sidebar";
import { uploadDocument } from "../api/document";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [explanation, setExplanation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError("");
    setSummary("");
    setExplanation([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await uploadDocument(formData);
      setSummary(res.data.summary);
      setExplanation(res.data.explanation || []);
    } catch {
      setError("Failed to process document.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#14110d]">
      
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-8 text-[#f5efe6]">
        
        <h1 className="text-2xl font-semibold mb-6">
          Upload Legal Document
        </h1>

        {/* Upload Card */}
        <div className="bg-[#1f1b16] border border-[#3a2f25] rounded-xl p-6 mb-6">
          
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => setFile(e.target.files[0])}
            className="block w-full text-sm text-[#d6c7b5]
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:bg-[#2a231c] file:text-[#f5efe6]
              hover:file:bg-[#3a2f25]"
          />

          <button
            onClick={handleUpload}
            disabled={loading}
            className="mt-4 bg-[#f0b35a] text-[#14110d] px-6 py-2 rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Processing..." : "Upload & Analyze"}
          </button>

          {error && (
            <p className="mt-3 text-red-400 text-sm">
              {error}
            </p>
          )}
        </div>

        {/* Summary */}
        {summary && (
          <div className="bg-[#1f1b16] border border-[#3a2f25] rounded-xl p-6 mb-6">
            <h3 className="text-lg font-semibold text-[#f0b35a] mb-2">
              Summary
            </h3>
            <p className="text-[#e6d8c7] leading-relaxed">
              {summary}
            </p>
          </div>
        )}

        {/* Explanation */}
        {explanation.length > 0 && (
          <div className="bg-[#1f1b16] border border-[#3a2f25] rounded-xl p-6">
            <h3 className="text-lg font-semibold text-[#f0b35a] mb-4">
              Explanation
            </h3>

            <ul className="space-y-3 text-sm text-[#d6c7b5]">
              {explanation.map((e, i) => (
                <li key={i}>
                  <span className="font-semibold text-[#f5efe6]">
                    {e.section}:
                  </span>{" "}
                  {e.sentence}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
