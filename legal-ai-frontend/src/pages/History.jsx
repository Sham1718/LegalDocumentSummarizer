import { useEffect, useState } from "react";
import api from "../utils/axios";
import Sidebar from "../component/Sidebar";
import { getQueryHistory } from "../api/ask";

export default function History() {
  const [history, setHistory] = useState([]);
  const [page, setPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHistory(page);
  }, [page]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const res = await getQueryHistory(page);
      setHistory(res.data.content);
      setTotalPages(res.data.totalPages);
    } catch {
      console.error("Failed to load history");
    } finally {
      setLoading(false);
    }
  };
  console.log(history);
  console.log(totalPages);
  
  

  return (
    <div className="flex h-screen bg-[#14110d]">
      
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-8 text-[#f5efe6]">
        
        <h1 className="text-2xl font-semibold mb-6">
          Query History
        </h1>

        {loading && (
          <p className="text-[#b6a892]">Loading...</p>
        )}

        {!loading && history.length === 0 && (
          <p className="text-[#b6a892]">No queries found.</p>
        )}

        {/* History Cards */}
        <div className="space-y-6">
          {history.map((h, i) => (
            <div
              key={i}
              className="bg-[#1f1b16] border border-[#3a2f25] rounded-xl p-6"
            >
              <p className="mb-2">
                <span className="font-semibold text-[#f0b35a]">
                  Question:
                </span>{" "}
                {h.question}
              </p>

              <p className="mb-3 text-[#e6d8c7]">
                <span className="font-semibold text-[#f0b35a]">
                  Answer:
                </span>{" "}
                {h.answer}
              </p>

              {h.sources && (
                <p className="text-sm text-[#d6c7b5] mb-2">
                  <span className="font-semibold text-[#9f8f7a]">
                    Sources:
                  </span>{" "}
                  {h.sources}
                </p>
              )}

              <p className="text-xs text-[#7a6a58]">
                {new Date(h.createdAt).toLocaleString()}
              </p>
            </div>
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center gap-4 mt-8">
            <button
              disabled={page === 0}
              onClick={() => setPage(page - 1)}
              className="px-4 py-2 rounded-lg bg-[#1f1b16] border border-[#3a2f25] text-sm hover:bg-[#2a231c] disabled:opacity-40"
            >
              Prev
            </button>

            <span className="text-sm text-[#b6a892]">
              Page {page + 1} of {totalPages}
            </span>

            <button
              disabled={page + 1 >= totalPages}
              onClick={() => setPage(page + 1)}
              className="px-4 py-2 rounded-lg bg-[#1f1b16] border border-[#3a2f25] text-sm hover:bg-[#2a231c] disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
