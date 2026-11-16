
"use client";

import { useEffect, useState } from "react";


const API_BASE_URL =process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Document = {
  document_id: string;
  original_filename: string;
  status: string;
  chunks_count: number;
  uploaded_at: string | null;
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState("");

  async function fetchDocuments() {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/documents`);

      if (!response.ok) {
        throw new Error("Failed to load documents.");
      }

      const data = await response.json();

      setDocuments(data.documents);
    } catch (error) {
      console.error("Documents error:", error);

      setError(
        error instanceof Error
          ? error.message
          : "An unexpected error occurred."
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) return;

    setUploadError("");
    setUploadSuccess("");

    const allowedExtensions = [".pdf", ".txt"];
    const fileExtension = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
      setUploadError("Only PDF and TXT files are allowed.");
      event.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to upload document."
        );
      }

      setUploadSuccess(
        `${data.original_filename} uploaded successfully.`
      );

      await fetchDocuments();

    } catch (error) {
      console.error("Upload error:", error);

      setUploadError(
        error instanceof Error
          ? error.message
          : "An unexpected error occurred."
      );
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleDelete(documentId: string) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this document?"
    );

    if (!confirmed) return;

    setDeleteError("");
    setDeletingId(documentId);

    try {
      const response = await fetch(
        `${API_BASE_URL}/documents/${documentId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to delete document."
        );
      }

      await fetchDocuments();

    } catch (error) {
      console.error("Delete error:", error);

      setDeleteError(
        error instanceof Error
          ? error.message
          : "An unexpected error occurred."
      );
    } finally {
      setDeletingId(null);
    }
  }

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <main className="documents-page">
      <header className="documents-header">
        <div>
          <h1>Documents</h1>
          <p>Manage your knowledge base documents.</p>
        </div>

        <div className="documents-count">
          {documents.length} Documents
        </div>
      </header>
      <section className="upload-section">
        <div className="upload-info">
          <h2>Upload New Document</h2>
          <p>
            Add PDF or TXT files to your knowledge base.
          </p>
        </div>

        <label className="upload-button">
          {uploading ? "Uploading..." : "Choose File"}

          <input
            type="file"
            accept=".pdf,.txt"
            onChange={handleUpload}
            disabled={uploading}
            hidden
          />
        </label>

        {uploadError && (
          <p className="error-message">{uploadError}</p>
        )}

        {uploadSuccess && (
          <p className="upload-success">{uploadSuccess}</p>
        )}
      </section>

      <section className="documents-list-section">
        <h2>Uploaded Documents</h2>

        {deleteError && (
          <p className="error-message">{deleteError}</p>
        )}

        {isLoading && (
          <p className="documents-message">
            Loading documents...
          </p>
        )}

        {error && (
          <p className="error-message">{error}</p>
        )}

        {!isLoading && !error && documents.length === 0 && (
          <p className="documents-message">
            No documents uploaded yet.
          </p>
        )}

        {!isLoading && documents.map((document) => (
          <article
            key={document.document_id}
            className="document-card"
          >
            <div className="document-card-info">
              <h3>{document.original_filename}</h3>

              <p>
                Status: {document.status}
              </p>

              <p>
                Chunks: {document.chunks_count}
              </p>

              <p>
                Uploaded:{" "}
                {document.uploaded_at
                  ? new Date(document.uploaded_at).toLocaleString()
                  : "Unknown"}
              </p>
            </div>
            <button
              className="delete-button"
              onClick={() => handleDelete(document.document_id)}
              disabled={deletingId === document.document_id}
            >
              {deletingId === document.document_id
                ? "Deleting..."
                : "Delete"}
            </button>
          </article>
        ))}
      </section>
    </main>
  );
}
