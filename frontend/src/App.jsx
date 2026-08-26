import { useRef, useState } from "react";

import "./App.css";

import {
  askQuestion,
  uploadDocument,
} from "./services/api";


function formatFileSize(bytes) {
  if (!bytes) {
    return "Unknown size";
  }

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


function formatAuthors(author) {
  if (!author) {
    return "Not available";
  }

  const authors = author
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  if (authors.length <= 3) {
    return authors.join(", ");
  }

  return `${authors
    .slice(0, 3)
    .join(", ")} +${authors.length - 3} more`;
}


function formatRelevance(score) {
  console.log("RAW RELEVANCE SCORE:", score);

  if (
    typeof score !== "number" ||
    !Number.isFinite(score)
  ) {
    return 0;
  }

  const similarity = 1 / (1 + score);

  return Math.round(
    similarity * 100
  );
}


function App() {
  const fileInputRef = useRef(null);

  const [file, setFile] =
    useState(null);

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

  const [expandedSource, setExpandedSource] =
    useState(null);

  const [
    conversationHistory,
    setConversationHistory,
  ] = useState([]);

  const [
    activeHistoryIndex,
    setActiveHistoryIndex,
  ] = useState(null);


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

    setExpandedSource(null);

    setAskError("");

    setConversationHistory([]);

    setActiveHistoryIndex(null);

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


  const handleFileChange = (
    event
  ) => {
    const selectedFile =
      event.target.files?.[0];

    handleFileSelect(selectedFile);
  };


  const handleDrop = (
    event
  ) => {
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

    setExpandedSource(null);

    setAskError("");

    setConversationHistory([]);

    setActiveHistoryIndex(null);

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

    setExpandedSource(null);

    setActiveHistoryIndex(null);

    try {
      const data =
        await askQuestion(
          trimmedQuestion
        );

      const receivedAnswer =
        data.answer || "";

      const receivedSources =
        data.sources || [];

      setAnswer(
        receivedAnswer
      );

      setSources(
        receivedSources
      );

      setConversationHistory(
        (current) => [
          {
            question:
              trimmedQuestion,
            answer:
              receivedAnswer,
            sources:
              receivedSources,
          },
          ...current,
        ]
      );

      setActiveHistoryIndex(0);

    } catch (error) {
      setAskError(
        error.message ||
        "The question could not be answered."
      );

    } finally {
      setLoading(false);
    }
  };


  const handleHistoryClick = (
    historyItem,
    index
  ) => {
    setQuestion(
      historyItem.question
    );

    setAnswer(
      historyItem.answer
    );

    setSources(
      historyItem.sources
    );

    setAskError("");

    setExpandedSource(null);

    setActiveHistoryIndex(
      index
    );
  };


  const handleQuestionKeyDown = (
    event
  ) => {
    if (
      event.key === "Enter" &&
      (
        event.ctrlKey ||
        event.metaKey
      )
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
                      {uploadResult
                        ?.document_metadata
                        ?.filename ||
                        file?.name ||
                        uploadResult?.filename}
                    </h3>

                    <p>

                      {file
                        ? formatFileSize(
                            file.size
                          )
                        : formatFileSize(
                            uploadResult
                              ?.document_metadata
                              ?.file_size
                          )}

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


                {uploadStatus === "ready" && (

                  <>

                    <div className="document-metadata">

                      <div className="metadata-item">

                        <span>
                          TITLE
                        </span>

                        <p>
                          {uploadResult
                            ?.document_metadata
                            ?.title ||
                            "Not available"}
                        </p>

                      </div>


                      <div className="metadata-item">

                        <span>
                          AUTHOR
                        </span>

                        <p>
                          {formatAuthors(
                            uploadResult
                              ?.document_metadata
                              ?.author
                          )}
                        </p>

                      </div>


                      <div className="metadata-item">

                        <span>
                          PAGES
                        </span>

                        <p>
                          {uploadResult
                            ?.document_metadata
                            ?.page_count ||
                            uploadResult?.pages ||
                            "—"}
                        </p>

                      </div>


                      <div className="metadata-item">

                        <span>
                          FILE SIZE
                        </span>

                        <p>
                          {formatFileSize(
                            uploadResult
                              ?.document_metadata
                              ?.file_size ||
                              file?.size
                          )}
                        </p>

                      </div>

                    </div>


                    <div className="success-state">
                      ✓ Indexed successfully and
                      ready for questions
                    </div>

                  </>

                )}


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


            {conversationHistory.length > 0 && (

              <section className="conversation-history">

                <div className="conversation-history-header">

                  <span className="conversation-history-label">
                    CONVERSATION HISTORY
                  </span>

                  <span className="history-count">
                    {String(
                      conversationHistory.length
                    ).padStart(
                      2,
                      "0"
                    )}
                  </span>

                </div>


                <div className="conversation-history-list">

                  {conversationHistory.map(
                    (
                      historyItem,
                      index
                    ) => (

                      <button
                        type="button"
                        key={`${historyItem.question}-${index}`}
                        className={`history-item ${
                          activeHistoryIndex === index
                            ? "active"
                            : ""
                        }`}
                        onClick={() =>
                          handleHistoryClick(
                            historyItem,
                            index
                          )
                        }
                      >

                        <span className="history-item-number">

                          {String(
                            conversationHistory.length -
                            index
                          ).padStart(
                            2,
                            "0"
                          )}

                        </span>


                        <div className="history-item-content">

                          <span className="history-item-label">
                            QUESTION
                          </span>

                          <span className="history-question">
                            {historyItem.question}
                          </span>

                        </div>


                        <span className="history-arrow">
                          →
                        </span>

                      </button>

                    )
                  )}

                </div>

              </section>

            )}

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
                        (
                          source,
                          index
                        ) => {

                          const isExpanded =
                            expandedSource === index;

                          const relevance =
                            formatRelevance(
                              source.score
                            );

                          return (

                            <article
                              className={`source-card ${
                                isExpanded
                                  ? "expanded"
                                  : ""
                              }`}
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
                                    "—"}

                                  {" · "}

                                  Chunk{" "}

                                  {source.chunk_index ??
                                    index + 1}

                                </span>


                                <span>
                                  ▤
                                </span>

                              </div>


                              <p
                                className={`source-content ${
                                  isExpanded
                                    ? "show-full"
                                    : ""
                                }`}
                              >

                                {source.content ||
                                  "No passage text returned."}

                              </p>


                              {typeof source.score ===
                                "number" && (

                                <div className="relevance">

                                  <div className="relevance-label">

                                    <span>
                                      RETRIEVAL MATCH
                                    </span>

                                    <span>
                                      {relevance}%
                                    </span>

                                  </div>


                                  <div className="relevance-track">

                                    <div
                                      className="relevance-bar"
                                      style={{
                                        width:
                                          `${relevance}%`,
                                      }}
                                    />

                                  </div>

                                </div>

                              )}


                              <button
                                className="source-toggle"
                                onClick={() =>
                                  setExpandedSource(
                                    isExpanded
                                      ? null
                                      : index
                                  )
                                }
                              >

                                {isExpanded
                                  ? "Show less"
                                  : "View full source"}

                              </button>

                            </article>

                          );

                        }
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