"use client";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileText, X, Globe, Lock, Loader2, AlertCircle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sidebar } from "@/components/Sidebar";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFile(dropped);
  }, []);

  const handleFile = (f: File) => {
    const ok = f.name.endsWith(".pdf") || f.name.endsWith(".epub") || f.name.endsWith(".txt");
    if (!ok) { setError("Unsupported format. Please upload PDF, EPUB, or TXT."); return; }
    if (f.size > 50 * 1024 * 1024) { setError("File too large (max 50 MB)."); return; }
    setError("");
    setFile(f);
    if (!title) setTitle(f.name.replace(/\.(pdf|epub|txt)$/i, ""));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) { setError("Please add a title."); return; }
    setUploading(true);

    // Create book record
    const res = await fetch("/api/books", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: title.trim(), author: author.trim() || undefined, isPublic }),
    });
    const data = await res.json();
    if (!res.ok) { setError(data.error || "Failed to create book"); setUploading(false); return; }

    const bookId = data.book.id;

    // If there's an actual file, read it and kick off processing
    if (file) {
      const text = await file.text().catch(() => `Content from ${file.name}`);
      // Kick off async processing
      fetch(`/api/books/${bookId}/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text.slice(0, 20000) }),
      });
    }

    router.push(`/book/${bookId}/processing`);
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 p-6 max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-6">
          <ArrowLeft className="h-4 w-4" /> Back
        </button>

        <h1 className="text-2xl font-bold text-slate-900 mb-1">Add a book</h1>
        <p className="text-slate-500 mb-8">Upload a file and Lexis will build a knowledge graph from it.</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Drop zone */}
          <div
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onClick={() => document.getElementById("file-input")?.click()}
            className={`relative flex flex-col items-center justify-center gap-3 p-12 rounded-xl border-2 border-dashed cursor-pointer transition-colors ${
              dragOver ? "border-indigo-400 bg-indigo-50" : file ? "border-emerald-300 bg-emerald-50" : "border-slate-200 bg-white hover:border-slate-300"
            }`}
          >
            <input id="file-input" type="file" accept=".pdf,.epub,.txt" className="hidden" onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />
            {file ? (
              <>
                <FileText className="h-10 w-10 text-emerald-500" />
                <div className="text-center">
                  <p className="font-medium text-slate-900">{file.name}</p>
                  <p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                </div>
                <button type="button" onClick={e => { e.stopPropagation(); setFile(null); }} className="absolute top-3 right-3 text-slate-400 hover:text-slate-600">
                  <X className="h-4 w-4" />
                </button>
              </>
            ) : (
              <>
                <Upload className="h-10 w-10 text-slate-400" />
                <div className="text-center">
                  <p className="font-medium text-slate-700">Drop your book here</p>
                  <p className="text-sm text-slate-400">or click to browse — PDF, EPUB, TXT · max 50 MB</p>
                </div>
              </>
            )}
          </div>

          {/* Metadata */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Title *</label>
              <input
                required value={title} onChange={e => setTitle(e.target.value)}
                placeholder="Book title"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Author <span className="text-slate-400 font-normal">(optional)</span></label>
              <input
                value={author} onChange={e => setAuthor(e.target.value)}
                placeholder="Author name"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Visibility */}
          <Card>
            <CardContent className="p-4">
              <p className="text-sm font-medium text-slate-700 mb-3">Graph visibility</p>
              <div className="space-y-2">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="radio" checked={!isPublic} onChange={() => setIsPublic(false)} className="text-indigo-600" />
                  <Lock className="h-4 w-4 text-slate-400" />
                  <div>
                    <p className="text-sm font-medium text-slate-900">Private to me</p>
                    <p className="text-xs text-slate-500">Only you can use this knowledge graph.</p>
                  </div>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="radio" checked={isPublic} onChange={() => setIsPublic(true)} className="text-indigo-600" />
                  <Globe className="h-4 w-4 text-indigo-400" />
                  <div>
                    <p className="text-sm font-medium text-slate-900">Contribute to shared library</p>
                    <p className="text-xs text-slate-500">For public-domain books. Others can use your verified graph.</p>
                  </div>
                </label>
              </div>
            </CardContent>
          </Card>

          {error && (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">
              <AlertCircle className="h-4 w-4 shrink-0" /> {error}
            </div>
          )}

          <Button type="submit" className="w-full" size="lg" disabled={uploading}>
            {uploading ? <><Loader2 className="h-4 w-4 animate-spin" /> Creating...</> : "Upload & build knowledge graph"}
          </Button>
        </form>
      </main>
    </div>
  );
}
