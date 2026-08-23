import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: question,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get an answer");
      }

      const data = await response.json();

      setAnswer(data.answer);
      setSources(data.sources);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="navbar">
        <div className="logo">
          ResearchPilot <span>AI</span>
        </div>

        <div className="status">
          ● RAG System Online
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <p className="tag">AI-POWERED RESEARCH ASSISTANT</p>

          <h1>
            Research smarter.
            <br />
            Find answers faster.
          </h1>

          <p className="subtitle">
            Ask questions and get answers grounded in your research documents.
          </p>
        </section>

        <section className="search-section">
          <textarea
            placeholder="Ask a question about your research..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                askQuestion();
              }
            }}
          />

          <button
            onClick={askQuestion}
            disabled={loading}
          >
            {loading ? "Researching..." : "Ask ResearchPilot"}
          </button>
        </section>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {answer && (
          <section className="results">
            <div className="answer-card">
              <div className="card-label">
                RESEARCHPILOT ANSWER
              </div>

              <div className="answer">
                {answer}
              </div>
            </div>

            <div className="sources-section">
              <h2>Sources</h2>

              <div className="sources-grid">
                {sources.map((source, index) => (
                  <div
                    className="source-card"
                    key={index}
                  >
                    <div className="source-number">
                      [{index + 1}]
                    </div>

                    <div className="source-meta">
                      Page {source.page_number}
                      {" · "}
                      Chunk {source.chunk_index}
                    </div>

                    <div className="score">
                      Relevance: {source.score.toFixed(2)}
                    </div>

                    <p>
                      {source.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;