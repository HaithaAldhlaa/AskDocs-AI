"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";


const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
type Message = {
  role: "user" | "assistant";
  content: string;
  needsClarification?: boolean;
  sources?: Source[];
};

type Source = {
  document_id: string;
  filename: string;
  chunks: string[];
};

export default function Home() {
  const [message, setMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const conversationIdRef = useRef<string | null>(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [error, setError] = useState("");


  const [showSources, setShowSources] = useState(true);



  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault();

    const text = message.trim();

    if (!text) {
      setMessage("");
      inputRef.current?.focus();
      return;
    }

    if (isLoading) return;

    if (!conversationIdRef.current) {
      conversationIdRef.current = crypto.randomUUID();
    }
    const conversationId = conversationIdRef.current;

    setError("");

    setMessages((previousMessages) => [
      ...previousMessages,
      { role: "user", content: text },
    ]);

    setMessage("");
    inputRef.current?.focus();
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            message: text, conversation_id: conversationId,
          }),
        });

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail || "Something went wrong. Please try again."
        );
      }

      const data = await response.json();

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          content: data.reply,
          needsClarification: data.structured?.needs_clarification ?? false,
          sources: data.sources ?? [],
        },
      ]);
    }
    catch (error) {
      console.error("Chat error:", error);
      setError(error instanceof Error ? error.message : "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="chat-container">

      {/* Welcome Section */}

      <div className="chat-welcome">

        <div className="welcome-logo">
          <span>✦</span>
        </div>

        <h1>AskDocs AI</h1>

        <h2>Your Documents. Your Answers.</h2>

        <p>
          An intelligent document assistant powered by LLMs and Retrieval-Augmented Generation (RAG).
        </p>

      </div>


      {/* Sources Toggle */}
      <label className="sources-toggle">
        <span className="sources-toggle-label">Show Sources</span>

        <input
          type="checkbox"
          checked={showSources}
          onChange={(event) => setShowSources(event.target.checked)}
        />

        <span className="toggle-slider"></span>
      </label>

      {/* Chat Messages */}
      <div className="chat-box">

        {messages.length === 0 && (
          <p className="empty-chat-message">
            Your conversation will appear here.
          </p>
        )}

        {messages.map((msg, index) => (
          <div key={index} className="chat-message">

            <strong>
              {msg.role === "user" ? "You: " : "AI: "}
            </strong>

            {msg.role === "assistant" ? (
              <>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>

                {msg.needsClarification && (
                  <p className="text-amber-600 text-sm">
                    AI needs more information.
                  </p>
                )}

                {showSources && msg.sources && msg.sources.length > 0 && (
                  <div className="message-sources">
                    <h4>Sources ({msg.sources.length})</h4>

                    {msg.sources.map((source, sourceIndex) => (
                      <div
                        key={source.document_id}
                        className="source-card"
                      >
                        <strong>{source.filename}</strong>

                        {source.chunks.map((chunk, chunkIndex) => (
                          <p key={chunkIndex}>
                            {chunk}
                          </p>
                        ))}
                      </div>
                    ))}
                  </div>
                )}

              </>
            ) : (
              <p>{msg.content}</p>
            )}

          </div>
        ))}

        {error && (
          <p className="error-message">
            {error}
          </p>
        )}

        {isLoading && (
          <div className="typing-indicator">
            <strong>AI: </strong>
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}

        <div ref={messagesEndRef} />

      </div>

      {/* Chat Input */}
      <form className="chat-form" onSubmit={handleSubmit}>

        <input
          ref={inputRef}
          type="text"
          placeholder="Type your message..."
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Sending..." : "Send"}
        </button>

      </form>

    </main>
  );
}