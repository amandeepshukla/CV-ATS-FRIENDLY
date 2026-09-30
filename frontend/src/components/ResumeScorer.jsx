import { useState, useRef } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const ACCEPT = ".pdf,.docx,.png,.jpg,.jpeg";

const scoreColor = (s) =>
  s >= 80 ? "text-green-500" : s >= 60 ? "text-yellow-500" : "text-red-500";
const sevStyle = {
  high: "bg-red-100 text-red-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-blue-100 text-blue-700",
};

export default function ResumeScorer() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [drag, setDrag] = useState(false);
  const inputRef = useRef();

  const pick = (f) => {
    if (!f) return;
    setFile(f);
    setResult(null);
    setError("");
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDrag(false);
    pick(e.dataTransfer.files[0]);
  };

  const submit = async () => {
    if (!file) return setError("Pehle resume upload karo.");
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("job_description", jd);
      const res = await fetch(`${API}/score-resume`, { method: "POST", body: fd });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error (${res.status})`);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">ATS Resume Scorer</h1>

      <div
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current.click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition
          ${drag ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"}`}
      >
        <input ref={inputRef} type="file" accept={ACCEPT} hidden
               onChange={(e) => pick(e.target.files[0])} />
        {file ? (
          <p className="font-medium">{file.name} ({(file.size / 1024).toFixed(0)} KB)</p>
        ) : (
          <p className="text-gray-500">Drag & drop PDF / DOCX / PNG / JPG, ya click karo</p>
        )}
      </div>

      <textarea
        value={jd}
        onChange={(e) => setJd(e.target.value)}
        rows={6}
        placeholder="(Optional) Target job description yahan paste karo..."
        className="w-full border rounded-lg p-3 bg-white"
      />

      <button
        onClick={submit}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Score My Resume"}
      </button>

      {error && <p className="text-red-600 bg-red-50 p-3 rounded-lg">{error}</p>}

      {result && (
        <div className="space-y-6">
          <div className="text-center">
            <div className={`text-7xl font-extrabold ${scoreColor(result.ats_score)}`}>
              {result.ats_score}%
            </div>
            <p className="text-gray-600 mt-2">{result.summary}</p>
          </div>

          <section>
            <h2 className="font-semibold text-xl mb-2">Keyword Match</h2>
            <p className="text-sm text-gray-500 mb-1">Matched</p>
            <div className="flex flex-wrap gap-2 mb-3">
              {result.keyword_match.matched.map((k) => (
                <span key={k} className="px-2 py-1 rounded bg-green-100 text-green-700 text-sm">{k}</span>
              ))}
            </div>
            <p className="text-sm text-gray-500 mb-1">Missing</p>
            <div className="flex flex-wrap gap-2">
              {result.keyword_match.missing.map((k) => (
                <span key={k} className="px-2 py-1 rounded bg-red-100 text-red-700 text-sm">{k}</span>
              ))}
            </div>
          </section>

          <section>
            <h2 className="font-semibold text-xl mb-2">Formatting Check</h2>
            {result.formatting_issues.length === 0 ? (
              <p className="text-green-600">Koi ATS-breaking issue nahi mila.</p>
            ) : (
              <ul className="space-y-2">
                {result.formatting_issues.map((f, i) => (
                  <li key={i} className="border rounded-lg p-3 bg-white">
                    <span className={`text-xs px-2 py-0.5 rounded mr-2 ${sevStyle[f.severity]}`}>
                      {f.severity.toUpperCase()}
                    </span>
                    {f.issue}
                    <p className="text-sm text-gray-500 mt-1">Fix: {f.fix}</p>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section>
            <h2 className="font-semibold text-xl mb-2">Recommendations</h2>
            <ul className="list-disc pl-5 space-y-1">
              {result.recommendations.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </section>
        </div>
      )}
    </div>
  );
}
