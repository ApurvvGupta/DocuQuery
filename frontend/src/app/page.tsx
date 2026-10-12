"use client";

import React, { useState } from "react";
import { UploadCloud, FileText, Search, BookOpen, Clock, AlertCircle } from "lucide-react";

interface Citation {
  page_number: number;
  source_document: str;
  snippet: string;
  relevance_score: number;
}

interface QueryResponse {
  answer: string;
  citations: Citation[];
  query_latency_ms: number;
}

export default function DocuQueryHome() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadedDoc, setUploadedDoc] = useState<any>(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/api/documents/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setUploadedDoc(data);
    } catch (err) {
      console.error("Upload error", err);
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/documents/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query, doc_id: uploadedDoc?.doc_id }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error("Query error", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 p-8">
      <header className="max-w-6xl mx-auto mb-8 border-b pb-4 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-blue-600 tracking-tight">DocuQuery</h1>
          <p className="text-sm text-slate-500">AI-Powered Document Intelligence & Grounded RAG Platform</p>
        </div>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
          FastAPI + ChromaDB + Next.js
        </span>
      </header>

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Document Ingestion Sidebar */}
        <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
            <UploadCloud className="w-5 h-5 text-blue-500" />
            Ingest Document
          </h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="text-xs file:mr-3 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer w-full"
            />
            <button
              type="submit"
              disabled={!file || uploading}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs rounded-lg transition disabled:opacity-50"
            >
              {uploading ? "Extracting & Embedding..." : "Upload & Index Document"}
            </button>
          </form>

          {uploadedDoc && (
            <div className="mt-6 p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-xs space-y-1">
              <div className="font-semibold text-emerald-800 flex items-center gap-1">
                <FileText className="w-4 h-4" /> Indexed: {uploadedDoc.filename}
              </div>
              <p className="text-slate-600">Total Pages: <span className="font-medium">{uploadedDoc.total_pages}</span></p>
              <p className="text-slate-600">Semantic Chunks: <span className="font-medium">{uploadedDoc.total_chunks}</span></p>
            </div>
          )}
        </section>

        {/* Q&A and Citation Grounding Engine */}
        <section className="md:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <BookOpen className="w-5 h-5 text-indigo-500" />
              Grounded Document Q&A
            </h2>

            <form onSubmit={handleQuery} className="flex gap-2 mb-6">
              <input
                type="text"
                placeholder="Ask questions (e.g. What are the key contract liabilities?)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1 px-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg transition disabled:opacity-50 flex items-center gap-1"
              >
                <Search className="w-4 h-4" /> {loading ? "Analyzing..." : "Query"}
              </button>
            </form>

            {response && (
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Synthesized Answer</h3>
                  <p className="text-slate-800 text-sm leading-relaxed">{response.answer}</p>
                  <div className="mt-3 flex items-center gap-2 text-xs text-slate-400">
                    <Clock className="w-3.5 h-3.5" /> Latency: {response.query_latency_ms} ms
                  </div>
                </div>

                {response.citations.length > 0 && (
                  <div>
                    <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Source Page Citations</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {response.citations.map((cite, i) => (
                        <div key={i} className="p-3 bg-blue-50/60 border border-blue-200 rounded-md text-xs">
                          <span className="font-bold text-blue-700">Page {cite.page_number}</span>
                          <span className="text-slate-500 text-[10px] ml-2">({(cite.relevance_score * 100).toFixed(1)}% match)</span>
                          <p className="text-slate-600 mt-1 italic line-clamp-3">"{cite.snippet}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
