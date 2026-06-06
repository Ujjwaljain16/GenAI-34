"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { CheckCircle, Loader2, XCircle, ArrowRight, BrainCircuit } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sidebar } from "@/components/Sidebar";

const STAGES = [
  { key: "parsing", label: "Parsing & chunking", desc: "Extracting text and splitting into sections" },
  { key: "kg_built", label: "Extracting concepts", desc: "Identifying key nodes from each section" },
  { key: "kg_verified", label: "Inferring prerequisites", desc: "Building the dependency graph" },
  { key: "ready", label: "Ready for review", desc: "Knowledge graph built — review before starting" },
];

const STATUS_TO_INDEX: Record<string, number> = {
  uploaded: 0, parsing: 0, kg_built: 1, kg_verified: 2, ready: 3,
};

export default function ProcessingPage() {
  const router = useRouter();
  const params = useParams();
  const bookId = params.bookId as string;

  const [bookTitle, setBookTitle] = useState("Your book");
  const [status, setStatus] = useState("parsing");
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    // Poll for status
    let attempts = 0;
    const poll = async () => {
      const res = await fetch(`/api/books/${bookId}`);
      if (!res.ok) { setFailed(true); return; }
      const { book } = await res.json();
      setBookTitle(book.title);
      setStatus(book.status);
      if (book.status === "kg_verified" || book.status === "ready") {
        // Done polling
        return;
      }
      if (attempts++ < 60) setTimeout(poll, 3000);
      else setFailed(true);
    };
    poll();
  }, [bookId]);

  const currentIdx = STATUS_TO_INDEX[status] ?? 0;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 p-6 max-w-xl">
        <div className="mt-12">
          <div className="flex items-center justify-center h-16 w-16 bg-indigo-100 rounded-2xl mb-6">
            <BrainCircuit className="h-8 w-8 text-indigo-600" />
          </div>

          <h1 className="text-2xl font-bold text-slate-900 mb-1">Building your knowledge graph</h1>
          <p className="text-slate-500 mb-8">{bookTitle}</p>

          {/* Pipeline stepper */}
          <div className="space-y-4 mb-10">
            {STAGES.map((stage, i) => {
              const done = i < currentIdx || status === "ready";
              const active = i === currentIdx && status !== "ready";
              return (
                <div key={stage.key} className="flex items-start gap-4">
                  <div className="mt-0.5 flex-shrink-0">
                    {failed && active ? (
                      <XCircle className="h-6 w-6 text-red-500" />
                    ) : done || (status === "ready" && i <= 3) ? (
                      <CheckCircle className="h-6 w-6 text-emerald-500" />
                    ) : active ? (
                      <Loader2 className="h-6 w-6 text-indigo-500 animate-spin" />
                    ) : (
                      <div className="h-6 w-6 rounded-full border-2 border-slate-200" />
                    )}
                  </div>
                  <div>
                    <p className={`text-sm font-medium ${active ? "text-indigo-700" : done ? "text-slate-700" : "text-slate-400"}`}>
                      {stage.label}
                    </p>
                    {(active || done) && <p className="text-xs text-slate-500 mt-0.5">{stage.desc}</p>}
                  </div>
                </div>
              );
            })}
          </div>

          {failed ? (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
              <p className="text-sm font-medium text-red-700">Processing failed</p>
              <p className="text-xs text-red-600 mt-1">We couldn't parse this file. Try a different format.</p>
              <Button variant="outline" size="sm" className="mt-3" onClick={() => router.push("/upload")}>
                Try again
              </Button>
            </div>
          ) : (status === "kg_verified" || status === "ready") ? (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-6">
              <p className="text-sm font-medium text-emerald-700">Knowledge graph built!</p>
              <p className="text-xs text-emerald-600 mt-1">Review the graph before starting your learning journey.</p>
              <Button className="mt-3" onClick={() => router.push(`/book/${bookId}/verify`)}>
                Review graph <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              This usually takes 1–2 minutes. You can leave — we'll notify you when it's ready.
            </p>
          )}

          <button onClick={() => router.push("/library")} className="text-sm text-slate-400 hover:text-slate-600 underline">
            Go back to library
          </button>
        </div>
      </main>
    </div>
  );
}
