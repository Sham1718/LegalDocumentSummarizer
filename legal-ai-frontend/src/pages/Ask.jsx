import { useState } from "react";
import api from "../utils/axios";
import Sidebar from '../component/Sidebar'
import { ask } from "../api/ask";

export default function Ask() {
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState("en");
  const [answer, setAnswer] = useState("");
  const[evidence,setEvidence]=useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const[resLang,setResLang]=useState("");

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const res = await ask({
        question,
        language,
        top_k: 6,
        include_explanation: false,
        answer_length: "medium"});
        // console.log(res);
      setEvidence(res.data.evidence_chunks);
      setAnswer(res.data.answer);
      setSources(res.data.sources || []);
      setResLang(res.data.language);
    } catch {
      setError("Failed to fetch answer.");
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
          Ask a Legal Question
        </h1>

        {/* Question Card */}
        <div className="bg-[#1f1b16] border border-[#3a2f25] rounded-xl p-6 mb-6">
          <textarea
            rows={4}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter your legal question..."
            className="w-full bg-[#14110d] border border-[#3a2f25] rounded-lg p-3 text-[#f5efe6] focus:outline-none focus:ring-2 focus:ring-[#f0b35a]"
          />
          <select
  value={language}
  onChange={(e) => setLanguage(e.target.value)}
  className="mt-3 bg-[#14110d] border border-[#3a2f25] rounded-lg p-2 text-[#f5efe6]"
>
  <option value="en">English</option>
  <option value="hi">Hindi</option>
  <option value="ta">Tamil</option>
  <option value="te">Telugu</option>
  <option value="bn">Bengali</option>
  <option value="mr">Marathi</option>
  <option value="gu">Gujarati</option>
</select>
{/* <p>{language}</p> */}

          <button
            onClick={askQuestion}
            disabled={loading}
            className="mt-4 bg-[#f0b35a] text-[#14110d] px-6 py-2 rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Thinking..." : "Ask"}
          </button>
        </div>

        {error && (
          <p className="text-red-400 mb-4">{error}</p>
        )}

        {answer && (
          <div className="bg-[#1f1b16] border border-[#3a2f25] rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-2 text-[#f0b35a]">
              Answer
            </h3>
            <p className="leading-relaxed text-[#e6d8c7]">
              {answer}
              {resLang}
            </p>

            {sources.length > 0 && (
              <>
                <h4 className="mt-4 text-sm uppercase tracking-wide text-[#9f8f7a]">
                  Sources
                </h4>
                <ul className="mt-2 text-sm text-[#d6c7b5] list-disc list-inside">
                  {sources.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </>
            )}
            {evidence.length > 0 && (
              <>
                <h4 className="mt-4 text-sm uppercase tracking-wide text-[#9f8f7a]">
                  evidence
                </h4>
                <ul className="mt-2 text-sm text-[#d6c7b5] list-disc list-inside">
                  {evidence.map((s, i) => (
                    <li key={i}>{s.text}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
