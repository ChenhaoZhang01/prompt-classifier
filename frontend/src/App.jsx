import React, { useState } from "react";

const EXAMPLES = [
  "What is the correct dosage of ibuprofen in mg for a 30lb child?",
  "Brainstorm creative names for a coffee shop.",
  "Calculate the compound interest on $5000 at 4% for 3 years.",
  "Write a short poem about autumn.",
];

const RISK_COLORS = { low: "#3fb950", moderate: "#d29922", high: "#f85149" };

export default function App() {
  const [prompt, setPrompt] = useState(EXAMPLES[0]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function classify() {
    setError(null);
    try {
      const r = await fetch("/api/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      if (!r.ok) throw new Error("bad response");
      setResult(await r.json());
    } catch (e) {
      setError("Backend not reachable — start the FastAPI server on :8000.");
    }
  }

  return (
    <div className="app">
      <h1>Prompt Classifier</h1>
      <p className="sub">
        Convergent (one right answer) vs. divergent (open-ended), with an
        overreliance warning for high-stakes verifiable questions.
      </p>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Type or paste a prompt..."
      />
      <div className="examples">
        {EXAMPLES.map((ex) => (
          <button key={ex} className="chip" onClick={() => setPrompt(ex)}>
            {ex.slice(0, 28)}…
          </button>
        ))}
      </div>
      <button className="primary" onClick={classify}>
        Classify
      </button>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <div className="row">
            <span
              className="label"
              style={{
                background: result.label === "convergent" ? "#1f6feb" : "#8957e5",
              }}
            >
              {result.label}
            </span>
            <span className="conf">
              P(convergent) = {result.convergent_probability} · confidence{" "}
              {result.confidence}
            </span>
          </div>

          <div className="risk" style={{ color: RISK_COLORS[result.overreliance_risk] }}>
            Overreliance risk: <strong>{result.overreliance_risk}</strong>
          </div>

          {result.warning && <div className="warning">⚠️ {result.warning}</div>}

          <pre>{JSON.stringify(result.features, null, 2)}</pre>
          <p className="rationale">{result.rationale}</p>
        </div>
      )}
      <style>{styles}</style>
    </div>
  );
}

const styles = `
  body { margin:0; background:#0d1117; color:#e6edf3; font-family: ui-sans-serif, system-ui, sans-serif; }
  .app { max-width: 720px; margin: 0 auto; padding: 32px 20px; }
  h1 { margin: 0; }
  .sub { color:#8b949e; }
  textarea { width:100%; height:90px; background:#161b22; color:#e6edf3; border:1px solid #30363d; border-radius:8px; padding:10px; box-sizing:border-box; }
  .examples { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0; }
  .chip { background:#21262d; color:#8b949e; border:1px solid #30363d; border-radius:14px; padding:4px 10px; cursor:pointer; font-size:12px; }
  .primary { background:#1f6feb; color:#fff; border:0; border-radius:8px; padding:10px 20px; cursor:pointer; }
  .error { color:#f85149; }
  .result { margin-top:20px; background:#161b22; border:1px solid #30363d; border-radius:10px; padding:16px; }
  .row { display:flex; align-items:center; gap:12px; }
  .label { color:#fff; padding:4px 12px; border-radius:6px; text-transform:capitalize; font-weight:700; }
  .conf { color:#8b949e; font-size:13px; }
  .risk { margin:12px 0; }
  .warning { background:#341a1a; border:1px solid #f85149; border-radius:8px; padding:10px; margin:8px 0; }
  pre { background:#0d1117; border:1px solid #30363d; border-radius:8px; padding:10px; font-size:12px; }
  .rationale { color:#8b949e; font-size:13px; }
`;
