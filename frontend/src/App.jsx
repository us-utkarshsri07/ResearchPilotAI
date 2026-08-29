import {
  useRef,
  useState,
} from "react";

import "./App.css";

import {
  askQuestion,
  uploadDocument,
  getConversations,
  getConversation,
  createConversation,
  deleteConversation,
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
  if (
    typeof score !== "number" ||
    !Number.isFinite(score)
  ) {
    return 0;
  }

  const similarity =
    1 / (1 + score);

  return Math.round(
    similarity * 100
  );
}


function App() {
  const fileInputRef =
    useRef(null);


  // --------------------------------
  // Document state
  // --------------------------------

  const [file, setFile] =
    useState(null);

  const [
    uploadStatus,
    setUploadStatus,
  ] = useState("idle");

  const [
    uploadResult,
    setUploadResult,
  ] = useState(null);

  const [
    uploadError,
    setUploadError,
  ] = useState("");


  // --------------------------------
  // Question state
  // --------------------------------

  const [
    question,
    setQuestion,
  ] = useState("");

  const [
    answer,
    setAnswer,
  ] = useState("");

  const [
    sources,
    setSources,
  ] = useState([]);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    askError,
    setAskError,
  ] = useState("");

  const [
    expandedSource,
    setExpandedSource,
  ] = useState(null);


  // --------------------------------
  // Current conversation thread
  // --------------------------------

  const [
    conversationHistory,
    setConversationHistory,
  ] = useState([]);

  const [
    activeHistoryIndex,
    setActiveHistoryIndex,
  ] = useState(null);


  // --------------------------------
  // Backend conversations
  // --------------------------------

  const [
    conversations,
    setConversations,
  ] = useState([]);

  const [
    conversationId,
    setConversationId,
  ] = useState(null);

  const [
    expandedConversationId,
    setExpandedConversationId,
  ] = useState(null);


  // --------------------------------
  // Load conversations
  // --------------------------------

  const loadConversations = async (
    documentId
  ) => {
    if (!documentId) {
      return;
    }

    try {
      const data =
        await getConversations(
          documentId
        );

      setConversations(data);

    } catch (error) {
      console.error(
        "Failed to load conversations:",
        error
      );
    }
  };


  // --------------------------------
  // Convert backend messages
  // into question/answer threads
  // --------------------------------

  const formatConversationMessages = (
    messages
  ) => {
    const formattedHistory = [];

    for (
      let i = 0;
      i < messages.length;
      i++
    ) {
      const message =
        messages[i];

      if (
        message?.role !== "user"
      ) {
        continue;
      }

      const assistantMessage =
        messages[i + 1]?.role ===
        "assistant"
          ? messages[i + 1]
          : null;

      formattedHistory.push({
        question:
          message.content,

        answer:
          assistantMessage?.content ||
          "",

        sources:
          assistantMessage?.sources ||
          [],
      });
    }

    return formattedHistory;
  };


  // --------------------------------
  // Select file
  // --------------------------------

  const handleFileSelect = async (
    selectedFile
  ) => {
    if (!selectedFile) {
      return;
    }

    if (
      selectedFile.type &&
      !selectedFile.type.includes(
        "pdf"
      )
    ) {
      setUploadStatus("error");

      setUploadError(
        "Only PDF files are supported."
      );

      return;
    }

    setFile(selectedFile);

    setUploadStatus(
      "processing"
    );

    setUploadError("");

    setUploadResult(null);

    setAnswer("");

    setSources([]);

    setExpandedSource(null);

    setAskError("");

    setConversationHistory([]);

    setConversations([]);

    setActiveHistoryIndex(null);

    setConversationId(null);

    setExpandedConversationId(null);

    try {
      const result =
        await uploadDocument(
          selectedFile
        );

      setUploadResult(result);

      setUploadStatus("ready");

      const documentId =
        result
          ?.document_metadata
          ?.document_id;

      if (documentId) {
        await loadConversations(
          documentId
        );
      }

    } catch (error) {
      setUploadStatus("error");

      setUploadError(
        error.message ||
        "Failed to process the PDF."
      );
    }
  };


  // --------------------------------
  // File input
  // --------------------------------

  const handleFileChange = (
    event
  ) => {
    const selectedFile =
      event.target.files?.[0];

    handleFileSelect(
      selectedFile
    );
  };


  // --------------------------------
  // Drag and drop
  // --------------------------------

  const handleDrop = (
    event
  ) => {
    event.preventDefault();

    const selectedFile =
      event.dataTransfer.files?.[0];

    handleFileSelect(
      selectedFile
    );
  };


  // --------------------------------
  // Reset document
  // --------------------------------

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

    setConversations([]);

    setActiveHistoryIndex(null);

    setConversationId(null);

    setExpandedConversationId(null);

    if (fileInputRef.current) {
      fileInputRef.current.value =
        "";
    }
  };


  // --------------------------------
  // Create new conversation
  // --------------------------------

  const handleNewConversation =
    async () => {
      const documentId =
        uploadResult
          ?.document_metadata
          ?.document_id;

      if (!documentId) {
        return;
      }

      try {
        const data =
          await createConversation(
            documentId
          );

        setConversationId(
          data.conversation_id
        );

        setExpandedConversationId(
          data.conversation_id
        );

        setConversationHistory([]);

        setQuestion("");

        setAnswer("");

        setSources([]);

        setAskError("");

        setExpandedSource(null);

        setActiveHistoryIndex(null);

        await loadConversations(
          documentId
        );

      } catch (error) {
        setAskError(
          error.message ||
          "Could not create a new conversation."
        );
      }
    };


  // --------------------------------
  // Load old conversation
  // --------------------------------

  const handleLoadConversation =
    async (
      selectedConversationId
    ) => {
      try {
        setLoading(true);

        setAskError("");

        const data =
          await getConversation(
            selectedConversationId
          );

        const formattedHistory =
          formatConversationMessages(
            data.messages || []
          );

        setConversationId(
          data.conversation_id
        );

        setExpandedConversationId(
          selectedConversationId
        );

        setConversationHistory(
          formattedHistory
        );

        if (
          formattedHistory.length > 0
        ) {
          const latestIndex =
            formattedHistory.length - 1;

          const latest =
            formattedHistory[
              latestIndex
            ];

          setQuestion(
            latest.question
          );

          setAnswer(
            latest.answer
          );

          setSources(
            latest.sources || []
          );

          setExpandedSource(null);

          setActiveHistoryIndex(
            latestIndex
          );

        } else {
          setQuestion("");

          setAnswer("");

          setSources([]);

          setExpandedSource(null);

          setActiveHistoryIndex(null);
        }

      } catch (error) {
        setAskError(
          error.message ||
          "Could not load the conversation."
        );

      } finally {
        setLoading(false);
      }
    };


  // --------------------------------
  // Delete conversation
  // --------------------------------

  const handleDeleteConversation =
    async (
      selectedConversationId
    ) => {
      try {
        await deleteConversation(
          selectedConversationId
        );

        const documentId =
          uploadResult
            ?.document_metadata
            ?.document_id;

        if (
          selectedConversationId ===
          conversationId
        ) {
          setConversationId(null);

          setConversationHistory([]);

          setQuestion("");

          setAnswer("");

          setSources([]);

          setExpandedSource(null);

          setActiveHistoryIndex(null);

          setExpandedConversationId(
            null
          );
        }

        if (documentId) {
          await loadConversations(
            documentId
          );
        }

      } catch (error) {
        setAskError(
          error.message ||
          "Could not delete the conversation."
        );
      }
    };


  // --------------------------------
  // Ask question
  // --------------------------------

  const askResearchQuestion =
    async () => {
      const trimmedQuestion =
        question.trim();

      if (
        !trimmedQuestion ||
        uploadStatus !== "ready" ||
        loading
      ) {
        return;
      }

      const documentId =
        uploadResult
          ?.document_metadata
          ?.document_id;

      if (!documentId) {
        setAskError(
          "Document ID is missing. Please upload the PDF again."
        );

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
            trimmedQuestion,
            documentId,
            conversationId
          );

        const receivedAnswer =
          data.answer || "";

        const receivedSources =
          data.sources || [];

        const returnedConversationId =
          data.conversation_id;

        if (
          returnedConversationId
        ) {
          setConversationId(
            returnedConversationId
          );

          setExpandedConversationId(
            returnedConversationId
          );
        }

        setAnswer(
          receivedAnswer
        );

        setSources(
          receivedSources
        );

        setConversationHistory(
          (current) => [
            ...current,
            {
              question:
                trimmedQuestion,

              answer:
                receivedAnswer,

              sources:
                receivedSources,
            },
          ]
        );

        await loadConversations(
          documentId
        );

      } catch (error) {
        setAskError(
          error.message ||
          "The question could not be answered."
        );

      } finally {
        setLoading(false);
      }
    };


  // --------------------------------
  // Click question inside thread
  // --------------------------------

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
      historyItem.sources || []
    );

    setAskError("");

    setExpandedSource(null);

    setActiveHistoryIndex(
      index
    );
  };


  // --------------------------------
  // Toggle conversation thread
  // --------------------------------

  const handleConversationToggle =
    async (
      selectedConversationId
    ) => {
      if (
        expandedConversationId ===
        selectedConversationId
      ) {
        setExpandedConversationId(
          null
        );

        return;
      }

      await handleLoadConversation(
        selectedConversationId
      );
    };


  // --------------------------------
  // Keyboard shortcut
  // --------------------------------

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


          {/* ========================= */}
          {/* SOURCE DOCUMENT */}
          {/* ========================= */}

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

                  onChange={
                    handleFileChange
                  }

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
                    type="button"
                    className="remove-button"

                    onClick={
                      resetDocument
                    }

                    disabled={
                      uploadStatus ===
                      "processing"
                    }
                  >
                    ×
                  </button>

                </div>


                {uploadStatus ===
                  "ready" && (

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


          {/* ========================= */}
          {/* UNIFIED CONVERSATIONS */}
          {/* ========================= */}

          {documentReady && (

            <section className="conversations-panel">

              <div className="conversation-panel-header">

                <div>

                  <p className="step-label">
                    CONVERSATIONS
                  </p>

                  <h2>
                    Chat history
                  </h2>

                </div>


                <div className="conversation-panel-actions">

                  <span className="conversation-count">

                    {String(
                      conversations.length
                    ).padStart(
                      2,
                      "0"
                    )}

                  </span>

                  <button
                    type="button"

                    className="new-conversation-button"

                    onClick={
                      handleNewConversation
                    }
                  >
                    + New
                  </button>

                </div>

              </div>


              {conversations.length === 0 ? (

                <div className="empty-conversations">

                  No conversations yet.

                </div>

              ) : (

                <div className="conversation-list">

                  {conversations.map(
                    (
                      conversation
                    ) => {

                      const isExpanded =
                        expandedConversationId ===
                        conversation.conversation_id;

                      const isActive =
                        conversation.conversation_id ===
                        conversationId;

                      return (

                        <div
                          key={
                            conversation
                              .conversation_id
                          }

                          className={`conversation-list-item ${
                            isActive
                              ? "active"
                              : ""
                          } ${
                            isExpanded
                              ? "expanded"
                              : ""
                          }`}
                        >

                          {/* Conversation header */}

                          <div className="conversation-item-header">

                            <button
                              type="button"

                              className="conversation-select"

                              onClick={() =>
                                handleConversationToggle(
                                  conversation
                                    .conversation_id
                                )
                              }
                            >

                              <div className="conversation-preview-wrap">

                                <span className="conversation-preview">

                                  {conversation.preview ||
                                    "New conversation"}

                                </span>

                                <span className="conversation-message-count">

                                  {conversation.message_count ||
                                    0}

                                  {" questions"}

                                </span>

                              </div>


                              <span
                                className={`conversation-expand-arrow ${
                                  isExpanded
                                    ? "expanded"
                                    : ""
                                }`}
                              >
                                →
                              </span>

                            </button>


                            <button
                              type="button"

                              className="delete-conversation-button"

                              onClick={() =>
                                handleDeleteConversation(
                                  conversation
                                    .conversation_id
                                )
                              }

                              aria-label="Delete conversation"
                            >
                              ×
                            </button>

                          </div>


                          {/* Thread */}

                          {isExpanded &&
                            conversationHistory.length > 0 && (

                            <div className="conversation-thread">

                              {conversationHistory.map(
                                (
                                  historyItem,
                                  index
                                ) => (

                                  <button
                                    type="button"

                                    key={`${historyItem.question}-${index}`}

                                    className={`thread-item ${
                                      activeHistoryIndex ===
                                      index
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

                                    <span className="thread-number">

                                      {String(
                                        index + 1
                                      ).padStart(
                                        2,
                                        "0"
                                      )}

                                    </span>


                                    <div className="thread-content">

                                      <span className="thread-label">
                                        QUESTION
                                      </span>

                                      <span className="thread-question">

                                        {
                                          historyItem.question
                                        }

                                      </span>


                                      {historyItem.answer && (

                                        <span className="thread-answer-preview">

                                          {historyItem.answer}

                                        </span>

                                      )}

                                    </div>


                                    <span className="thread-arrow">
                                      →
                                    </span>

                                  </button>

                                )
                              )}

                            </div>

                          )}

                        </div>

                      );
                    }
                  )}

                </div>

              )}

            </section>

          )}


          {/* ========================= */}
          {/* ASK QUESTION */}
          {/* ========================= */}

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
                  type="button"

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
                type="button"
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
                type="button"
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
                type="button"
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


        {/* ========================= */}
        {/* RIGHT PANEL */}
        {/* ========================= */}

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
                            expandedSource ===
                            index;

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
                                type="button"

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