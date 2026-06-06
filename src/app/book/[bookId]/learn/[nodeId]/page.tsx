"use client";
import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Send, BookOpen, X, CheckCircle, ChevronDown, ChevronUp, Loader2, MessageSquare, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sidebar } from "@/components/Sidebar";

interface Message { role: "user" | "assistant"; content: string; }

export default function LearnSessionPage() {
  const params = useParams();
  const router = useRouter();
  const bookId = params.bookId as string;
  const nodeId = params.nodeId as string;

  const [node, setNode] = useState<{ id: string; title: string; summary: string; sourceChunks: string; sectionName?: string } | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [questionSaved, setQuestionSaved] = useState(false);
  const [sourceOpen, setSourceOpen] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [unlockedNodes, setUnlockedNodes] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load node
    fetch(`/api/books/${bookId}`)
      .then(r => r.json())
      .then(({ book }) => {
        const n = book?.nodes?.find((x: { id: string }) => x.id === nodeId);
        setNode(n ?? null);
      });

    // Create session
    fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bookId, mode: "learning", nodeIds: [nodeId] }),
    })
      .then(r => r.json())
      .then(({ session }) => {
        setSessionId(session.id);
        // Opening Socratic message
        setMessages([{
          role: "assistant",
          content: `Let's explore this concept together. Before I explain anything — what do you already know or think about this topic? Any initial thoughts or questions?`,
        }]);
      });
  }, [bookId, nodeId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || !sessionId || sending) return;
    const msg = input.trim();
    const isQuestion = msg.includes("?") || msg.toLowerCase().startsWith("what") || msg.toLowerCase().startsWith("how") || msg.toLowerCase().startsWith("why");

    setInput("");
    setSending(true);
    setMessages(prev => [...prev, { role: "user", content: msg }]);
    if (isQuestion) setQuestionSaved(true);

    const res = await fetch(`/api/sessions/${sessionId}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, nodeId, isQuestion }),
    });
    const data = await res.json();
    setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
    setSending(false);
  };

  const complete = async () => {
    if (!sessionId) return;
    setCompleting(true);
    const res = await fetch(`/api/sessions/${sessionId}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    setUnlockedNodes(data.unlockedNodes ?? []);
    setCompleted(true);
    setCompleting(false);
  };

  const sourceChunks = node ? JSON.parse(node.sourceChunks || "[]") as string[] : [];

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 ml-16 lg:ml-56 flex flex-col" style={{ height: "100vh" }}>
        {/* Header */}
        <div className="border-b border-slate-200 bg-white px-6 py-3 flex items-center justify-between shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="info" className="text-xs">Learning</Badge>
              <span className="font-semibold text-slate-900 text-sm">{node?.title ?? "Loading..."}</span>
            </div>
            {node?.sectionName && <p className="text-xs text-slate-400 mt-0.5">§ {node.sectionName}</p>}
          </div>
          <div className="flex items-center gap-2">
            {questionSaved && (
              <div className="flex items-center gap-1.5 text-xs text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full border border-indigo-200">
                <MessageSquare className="h-3 w-3" /> Question saved for revision
              </div>
            )}
            <Button variant="success" size="sm" onClick={complete} disabled={completing || completed}>
              {completing ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
              I've got this
            </Button>
            <button onClick={() => router.push(`/book/${bookId}/course`)} className="text-slate-400 hover:text-slate-600">
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Completion overlay */}
        {completed && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="max-w-md w-full mx-4 shadow-2xl">
              <CardContent className="p-6 text-center">
                <div className="h-16 w-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="h-8 w-8 text-emerald-600" />
                </div>
                <h2 className="text-xl font-bold text-slate-900 mb-2">Node mastered!</h2>
                <p className="text-slate-600 text-sm mb-4">{node?.title} is now in your spaced-repetition schedule.</p>
                {unlockedNodes.length > 0 && (
                  <div className="bg-indigo-50 rounded-lg p-3 mb-4 text-left">
                    <p className="text-xs font-semibold text-indigo-700 mb-1 flex items-center gap-1">
                      <Sparkles className="h-3.5 w-3.5" /> Unlocked {unlockedNodes.length} new topic{unlockedNodes.length > 1 ? "s" : ""}:
                    </p>
                    {unlockedNodes.map((n, i) => (
                      <p key={i} className="text-xs text-indigo-600">→ {n}</p>
                    ))}
                  </div>
                )}
                <Button className="w-full" onClick={() => router.push(`/book/${bookId}`)}>
                  Back to daily plan
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="flex flex-1 overflow-hidden">
          {/* Chat area */}
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  {m.role === "assistant" && (
                    <div className="h-7 w-7 bg-indigo-100 rounded-full flex items-center justify-center mr-2 mt-1 shrink-0">
                      <span className="text-xs">🧠</span>
                    </div>
                  )}
                  <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    m.role === "user"
                      ? "bg-indigo-600 text-white rounded-br-sm"
                      : "bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm"
                  }`}>
                    {m.content}
                  </div>
                </div>
              ))}
              {sending && (
                <div className="flex justify-start">
                  <div className="h-7 w-7 bg-indigo-100 rounded-full flex items-center justify-center mr-2 shrink-0">
                    <span className="text-xs">🧠</span>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                    <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Source panel */}
            {sourceChunks[0] && (
              <div className="border-t border-slate-200 bg-slate-50">
                <button
                  onClick={() => setSourceOpen(v => !v)}
                  className="w-full flex items-center justify-between px-6 py-2 text-xs text-slate-500 hover:text-slate-700"
                >
                  <span className="flex items-center gap-1.5"><BookOpen className="h-3.5 w-3.5" /> Book reference</span>
                  {sourceOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
                </button>
                {sourceOpen && (
                  <div className="px-6 pb-4">
                    <p className="text-xs text-slate-600 leading-relaxed bg-white border border-slate-200 rounded-lg p-3 max-h-32 overflow-y-auto">
                      {sourceChunks[0].slice(0, 500)}...
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Input */}
            <div className="border-t border-slate-200 bg-white p-4">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
                  placeholder="Reply or ask a question... (questions are saved for revision)"
                  className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <Button onClick={send} disabled={!input.trim() || sending} size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
