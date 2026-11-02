import { useState } from "react";
import "./App.css";

async function postPrompt(endpoint, prompt) {
  const response = await fetch(`/api${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : `Request failed with status ${response.status}`
    );
  }

  return data;
}

function formatScore(value) {
  return typeof value === "number" ? value.toFixed(4) : "—";
}

function StatusBadge({ decision }) {
  const isBlock = decision === "BLOCK";

  return (
    <span className={`badge ${isBlock ? "badge-block" : "badge-allow"}`}>
      {decision || "—"}
    </span>
  );
}

function DetectorCard({ title, result, ruleBased = false }) {
  if (!result) return null;

  return (
    <article className="detector-card">
      <div className="detector-heading">
        <h3>{title}</h3>
        <span className={result.attack_detected ? "flagged" : "clear"}>
          {result.attack_detected ? "FLAGGED" : "NOT FLAGGED"}
        </span>
      </div>

      <p>
        <strong>Label / indication:</strong> {result.attack_type}
      </p>

      {ruleBased ? (
        <>
          <p>
            <strong>Heuristic score:</strong>{" "}
            {formatScore(result.heuristic_risk_score)}
          </p>
          <p>
            <strong>Rule matches:</strong> {result.matched_rules?.length ?? 0}
          </p>
        </>
      ) : (
        <>
          <p>
            <strong>Model score for malicious:</strong>{" "}
            {formatScore(result.malicious_probability)}
          </p>
          <p>
            <strong>Predicted-label confidence:</strong>{" "}
            {formatScore(result.confidence)}
          </p>
        </>
      )}
    </article>
  );
}

function App() {
  const [prompt, setPrompt] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [chat, setChat] = useState(null);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");

  const busy = Boolean(loading);

  function updatePrompt(value) {
    setPrompt(value);
    setAnalysis(null);
    setChat(null);
    setError("");
  }

  async function handleRequest(kind) {
    if (!prompt.trim()) {
      setError("Please enter a prompt first.");
      return;
    }

    setError("");
    setLoading(kind);

    // Avoid showing results from a previous request.
    if (kind === "analysis") setAnalysis(null);
    if (kind === "chat") setChat(null);

    try {
      if (kind === "analysis") {
        const result = await postPrompt("/analyze/hybrid", prompt);
        setAnalysis(result);
      } else {
        const result = await postPrompt("/chat/protected", prompt);
        setChat(result);
      }
    } catch (err) {
      setError(err.message || "Unable to connect to the backend.");
    } finally {
      setLoading("");
    }
  }

  return (
    <div className="page">
      <header className="header">
        <div>
          <p className="eyebrow">MINOR PROJECT • RESEARCH PROTOTYPE</p>
          <h1>LLM Security Firewall</h1>
          <p className="subtitle">
            Prompt injection and jailbreak detection with protected local LLM
            access.
          </p>
        </div>
        <div className="header-pill">Local Prototype</div>
      </header>

      <main className="main-grid">
        <section className="panel input-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">PROMPT CONSOLE</p>
              <h2>Analyze a prompt</h2>
            </div>
          </div>

          <label htmlFor="prompt">Prompt</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(event) => updatePrompt(event.target.value)}
            placeholder="Enter a prompt to analyze..."
            maxLength={10000}
            disabled={busy}
          />

          <div className="input-footer">
            <span>{prompt.length} / 10000 characters</span>
            <div className="actions">
              <button
                className="button button-secondary"
                onClick={() => handleRequest("analysis")}
                disabled={busy}
              >
                {loading === "analysis" ? "Analyzing..." : "Analyze"}
              </button>

              <button
                className="button button-primary"
                onClick={() => handleRequest("chat")}
                disabled={busy}
              >
                {loading === "chat" ? "Processing..." : "Protected Chat"}
              </button>
            </div>
          </div>

          {error && <div className="error-box" role="alert">{error}</div>}

          <div className="notice">
            <strong>Policy note:</strong> Analyze uses the triple-OR hybrid.
            Protected Chat uses DistilBERT only. Their decisions may differ.
          </div>
        </section>

        <section className="panel overview-panel">
          <p className="eyebrow">HOW IT WORKS</p>
          <h2>Security workflow</h2>

          <ol className="workflow">
            <li>Enter a user prompt.</li>
            <li>Inspect detector evidence and the hybrid decision.</li>
            <li>Send through protected chat to apply the DistilBERT policy.</li>
            <li>Only allowed prompts reach the local Ollama model.</li>
          </ol>

          <p className="small-note">
            This is a research prototype. Detection can produce false positives
            and false negatives; protection is not guaranteed.
          </p>
        </section>

        {analysis && (
          <section className="panel results-panel">
            <div className="result-heading">
              <div>
                <p className="eyebrow">HYBRID ANALYSIS</p>
                <h2>Detector evidence</h2>
              </div>
              <StatusBadge decision={analysis.policy_result?.decision} />
            </div>

            <p className="small-note">
              OR policy triggers:{" "}
              {analysis.policy_result?.triggered_by?.length
                ? analysis.policy_result.triggered_by.join(", ")
                : "none"}
            </p>

            <div className="detector-grid">
              <DetectorCard
                title="Rule-based"
                result={analysis.evidence?.rule_based}
                ruleBased
              />
              <DetectorCard
                title="Logistic Regression"
                result={analysis.evidence?.logistic_regression}
              />
              <DetectorCard
                title="DistilBERT"
                result={analysis.evidence?.distilbert}
              />
            </div>

            <p className="small-note">
              Rule scores are heuristic. Model scores have not been established
              as calibrated real-world attack probabilities.
            </p>
          </section>
        )}

        {chat && (
          <section className="panel results-panel">
            <div className="result-heading">
              <div>
                <p className="eyebrow">PROTECTED CHAT</p>
                <h2>Firewall decision and response</h2>
              </div>
              <StatusBadge decision={chat.decision} />
            </div>

            <p className="small-note">
              Policy: {chat.detection_method} • {chat.message}
            </p>

            <div className="response-box">
              {chat.llm_response || "No LLM response: prompt was blocked."}
            </div>
          </section>
        )}
      </main>

      <footer>
        AI-Based Security Framework • Experimental prototype
      </footer>
    </div>
  );
}

export default App;