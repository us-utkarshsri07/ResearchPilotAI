import { useRef, useState } from "react";

import "./App.css";

import {
  askQuestion,
  uploadDocument,
} from "./services/api";

function formatFileSize(bytes) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(
      1,
      Math.round(bytes / 1024)
    )} KB`;
  }

  return `${(
    bytes /
    (1024 * 1024)
  ).toFixed(1)} MB`;
}

function App() {
  const fileInputRef = useRef(null);

  const [file, setFile] = useState(null);

  const [uploadStatus, setUploadStatus] =
    useState("idle");

  const [uploadResult, setUploadResult] =
    useState(null);

  const [uploadError, setUploadError] =
    useState("");

  const [question, setQuestion] =
    useState("");

  const [answer, setAnswer] =
    useState("");

  const [sources, setSources] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [askError, setAskError] =
    useState("");

  const handleFileSelect = async (
    selectedFile
  ) => {
    if (!selectedFile) {
      return;
    }

    if (
      selectedFile.type &&
      !selectedFile.type.includes("pdf")
    ) {
      setUploadStatus("error");

      setUploadError(
        "Only PDF files are supported."
      );

      return;
    }

    setFile(selectedFile);

    setUploadStatus("processing");

    setUploadError("");

    setUploadResult(null);

    setAnswer("");

    setSources([]);

    setAskError("");

    try {
      const result =
        await uploadDocument(selectedFile);

      setUploadResult(result);

      setUploadStatus("ready");
    } catch (error) {
      setUploadStatus("error");

      setUploadError(
        error.message ||
          "Failed to process the PDF."
      );
    }
  };

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0];

    handleFileSelect(selectedFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();

    const selectedFile =
      event.dataTransfer.files?.[0];

    handleFileSelect(selectedFile);
  };

  const resetDocument = () => {
    setFile(null);

    setUploadStatus("idle");

    setUploadResult(null);

    setUploadError("");

    setQuestion("");

    setAnswer("");

    setSources([]);

    setAskError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const askResearchQuestion = async () => {
    const trimmedQuestion =
      question.trim();

    if (
      !trimmedQuestion ||
      uploadStatus !== "ready" ||
      loading
    ) {
      return;
    }

    setLoading(true);

    setAskError("");

    setAnswer("");

    setSources([]);

    try {
      const data =
        await askQuestion(trimmedQuestion);

      setAnswer(data.answer || "");

      setSources(data.sources || []);
    } catch (error) {
      setAskError(
        error.message ||
          "The question could not be answered."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      (event.ctrlKey || event.metaKey)
    ) {
      event.preventDefault();

      askResearchQuestion();
    }
  };

  const documentReady =
    uploadStatus === "ready";

  return (
    <div className="app">
      <header className="navbar">
        <div className="nav-brand">
          <div className="brand-icon">
            ◈
          </div>

          <div>
            <div className="logo">
              ResearchPilot
            </div>

            <div className="logo-subtitle">
              AI RESEARCH ASSISTANT
            </div>
          </div>
        </div>

        <div className="system-status">
          RETRIEVAL AUGMENTED
        </div>
      </header>

      <section className="hero">
        <div className="hero-grid">
          <p className="eyebrow">
            READ LESS · UNDERSTAND MORE
          </p>

          <h1>
            Interrogate dense research papers.
            <br />
            Get answers you can trace.
          </h1>

          <p className="hero-description">
            Upload a research document,
            build a searchable knowledge base,
            and get grounded answers with
            page-level sources.
          </p>

          <div className="feature-tags">
            <span>
              ◉ Page-level citations
            </span>

            <span>
              ✦ Grounded answers
            </span>

            <span>
              ◇ Hybrid retrieval
            </span>
          </div>
        </div>
      </section>

      <main className="workspace">
        <div className="left-panel">
          <section className="panel">
            <div className="section-header">
              <div>
                <p className="step-label">
                  STEP 01
                </p>

                <h2>
                  Source document
                </h2>
              </div>

              <span className="pdf-badge">
                PDF
              </span>
            </div>

            {uploadStatus === "idle" ||
            uploadStatus === "error" ? (
              <div
                className="upload-zone"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                onDragOver={(event) =>
                  event.preventDefault()
                }
                onDrop={handleDrop}
              >
                <div className="upload-icon">
                  ↑
                </div>

                <h3>
                  Drop a research PDF here
                </h3>

                <p>
                  or click to browse your files
                </p>

                <span>
                  Papers, reports and long-form
                  documents
                </span>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileChange}
                  hidden
                />
              </div>
            ) : (
              <div className="document-card">
                <div className="document-top">
                  <div className="document-icon">
                    ▤
                  </div>

                  <div className="document-info">
                    <h3>
                      {file?.name ||
                        uploadResult?.filename}
                    </h3>

                    <p>
                      {file
                        ? formatFileSize(
                            file.size
                          )
                        : "Document"}

                      {uploadResult?.pages
                        ? ` · ${uploadResult.pages} pages`
                        : ""}

                      {uploadResult?.chunks
                        ? ` · ${uploadResult.chunks} chunks`
                        : ""}
                    </p>
                  </div>

                  <button
                    className="remove-button"
                    onClick={resetDocument}
                    disabled={
                      uploadStatus ===
                      "processing"
                    }
                  >
                    ×
                  </button>
                </div>

                {uploadStatus ===
                  "processing" && (
                  <div className="processing-state">
                    <div className="processing-text">
                      <span className="spinner" />

                      Processing document and
                      creating embeddings...
                    </div>

                    <div className="progress-track">
                      <div className="progress-bar" />
                    </div>
                  </div>
                )}

                {uploadStatus === "ready" && (
                  <div className="success-state">
                    ✓ Indexed successfully and
                    ready for questions
                  </div>
                )}
              </div>
            )}

            {uploadError && (
              <div className="error-box">
                {uploadError}
              </div>
            )}
          </section>

          <section className="question-section">
            <div className="section-header question-header">
              <div>
                <p className="step-label">
                  STEP 02
                </p>

                <h2>
                  Ask the document
                </h2>
              </div>

              <span className="sparkle">
                ✦
              </span>
            </div>

            <div
              className={`question-card ${
                !documentReady
                  ? "disabled"
                  : ""
              }`}
            >
              <textarea
                placeholder={
                  documentReady
                    ? "Ask anything about this document..."
                    : "Upload a document to start asking questions..."
                }
                value={question}
                disabled={
                  !documentReady ||
                  loading
                }
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                onKeyDown={
                  handleQuestionKeyDown
                }
              />

              <div className="question-footer">
                <span className="keyboard-hint">
                  Ctrl + Enter to send
                </span>

                <button
                  className="ask-button"
                  onClick={
                    askResearchQuestion
                  }
                  disabled={
                    !documentReady ||
                    loading ||
                    !question.trim()
                  }
                >
                  {loading
                    ? "Researching..."
                    : "Ask ResearchPilot"}
                </button>
              </div>
            </div>

            <div className="suggestions">
              <button
                disabled={!documentReady}
                onClick={() =>
                  setQuestion(
                    "Summarise the core contribution"
                  )
                }
              >
                Summarise the contribution
              </button>

              <button
                disabled={!documentReady}
                onClick={() =>
                  setQuestion(
                    "What methodology was used?"
                  )
                }
              >
                Methodology
              </button>

              <button
                disabled={!documentReady}
                onClick={() =>
                  setQuestion(
                    "What are the key limitations?"
                  )
                }
              >
                Key limitations
              </button>
            </div>
          </section>
        </div>

        <div className="right-panel">
          {loading && (
            <section className="answer-loading">
              <div className="loading-label">
                <span className="pulse-dot" />

                RETRIEVING PASSAGES ·
                GENERATING ANSWER
              </div>

              <div className="skeleton-lines">
                <div />
                <div />
                <div />
                <div />
              </div>

              <div className="progress-track">
                <div className="progress-bar" />
              </div>
            </section>
          )}

          {!loading &&
            askError && (
              <section className="error-answer">
                <h3>
                  Answer unavailable
                </h3>

                <p>
                  {askError}
                </p>
              </section>
            )}

          {!loading &&
            !askError &&
            answer && (
              <div className="answer-container">
                <section className="answer-card">
                  <div className="answer-question">
                    “{question}”
                  </div>

                  <div className="answer-content">
                    {answer}
                  </div>
                </section>

                <section className="sources-section">
                  <div className="sources-title">
                    RETRIEVED SOURCES
                    {sources.length > 0 &&
                      ` · ${sources.length}`}
                  </div>

                  {sources.length === 0 ? (
                    <div className="empty-sources">
                      No supporting passages were
                      returned for this answer.
                    </div>
                  ) : (
                    <div className="sources-grid">
                      {sources.map(
                        (source, index) => (
                          <article
                            className="source-card"
                            key={
                              source.chunk_id ||
                              `${source.page_number}-${source.chunk_index}-${index}`
                            }
                          >
                            <div className="source-top">
                              <span className="source-number">
                                {String(
                                  index + 1
                                ).padStart(
                                  2,
                                  "0"
                                )}
                              </span>

                              <span className="source-location">
                                Page{" "}
                                {source.page_number ??
                                  "—"}{" "}
                                · Chunk{" "}
                                {source.chunk_index ??
                                  index + 1}
                              </span>

                              <span>
                                ▤
                              </span>
                            </div>

                            <p className="source-content">
                              {source.content ||
                                "No passage text returned."}
                            </p>

                            {typeof source.score ===
                              "number" && (
                              <div className="relevance">
                                <div className="relevance-label">
                                  <span>
                                    RELEVANCE
                                  </span>

                                  <span>
                                    {Math.round(
                                      source.score *
                                        100
                                    )}
                                    %
                                  </span>
                                </div>

                                <div className="relevance-track">
                                  <div
                                    className="relevance-bar"
                                    style={{
                                      width: `${Math.min(
                                        100,
                                        Math.max(
                                          3,
                                          source.score *
                                            100
                                        )
                                      )}%`,
                                    }}
                                  />
                                </div>
                              </div>
                            )}
                          </article>
                        )
                      )}
                    </div>
                  )}
                </section>
              </div>
            )}

          {!loading &&
            !askError &&
            !answer && (
              <section className="empty-workspace">
                <div className="empty-icon">
                  ◈
                </div>

                <h2>
                  {documentReady
                    ? "Ask your first question"
                    : "Your workspace is empty"}
                </h2>

                <p>
                  {documentReady
                    ? "Answers will appear here together with the retrieved passages used to generate them."
                    : "Upload a PDF to build a searchable research workspace."}
                </p>
              </section>
            )}
        </div>
      </main>

      <footer>
        <span>
          RESEARCHPILOT AI
        </span>

        <span>
          Answers are generated from your uploaded document.
        </span>
      </footer>
    </div>
  );
}

export default App;