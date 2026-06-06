"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Lock, Loader2, ArrowLeft, RefreshCw, BookOpen, ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Sidebar } from "@/components/Sidebar";
import { NodeStateBadge } from "@/components/NodeStateBadge";
import { NODE_STATE_COLORS } from "@/lib/utils";

type TabType = "learning" | "revision";

interface NodeRow {
  id: string;
  title: string;
  summary: string;
  difficultyTier: string;
  sectionName?: string;
  orderIndex: number;
  userNodeStates: Array<{ state: string; masteryScore: number; nextDue?: string }>;
  incomingEdges: Array<{ fromNodeId: string; fromNode?: { title: string } }>;
}

export default function CourseViewPage() {
  const params = useParams();
  const router = useRouter();
  const bookId = params.bookId as string;

  const [nodes, setNodes] = useState<NodeRow[]>([]);
  const [tab, setTab] = useState<TabType>("learning");
  const [loading, setLoading] = useState(true);
  const [bookTitle, setBookTitle] = useState("");

  useEffect(() => {
    fetch(`/api/books/${bookId}`)
      .then(r => r.json())
      .then(({ book }) => {
        setBookTitle(book?.title ?? "");
        setNodes(book?.nodes ?? []);
        setLoading(false);
      });
  }, [bookId]);

  const sections = [...new Set(nodes.map(n => n.sectionName ?? "General"))];

  const filtered = tab === "revision"
    ? nodes.filter(n => {
        const s = n.userNodeStates?.[0];
        return s?.state === "due" || s?.state === "mastered";
      })
    : nodes;

  const getNodeAction = (n: NodeRow) => {
    const s = n.userNodeStates?.[0];
    const state = s?.state ?? "locked";
    if (state === "locked") return null;
    if (state === "due") return () => router.push(`/book/${bookId}/revision`);
    if (state === "mastered") return () => router.push(`/book/${bookId}/node/${n.id}`);
    return () => router.push(`/book/${bookId}/node/${n.id}`);
  };

  if (loading) return (
    <div className="flex min-h-screen"><Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </main>
    </div>
  );

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 max-w-3xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <button onClick={() => router.push(`/book/${bookId}`)} className="text-slate-400 hover:text-slate-600">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <h1 className="font-bold text-slate-900 text-xl">{bookTitle}</h1>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-slate-100 rounded-xl p-1 mb-6 w-fit">
          <button
            onClick={() => setTab("learning")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === "learning" ? "bg-white shadow-sm text-slate-900" : "text-slate-500"}`}
          >
            <BookOpen className="h-4 w-4" /> Learning
          </button>
          <button
            onClick={() => setTab("revision")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === "revision" ? "bg-white shadow-sm text-slate-900" : "text-slate-500"}`}
          >
            <RefreshCw className="h-4 w-4" /> Revision
          </button>
        </div>

        {/* Sections */}
        {sections.map(section => {
          const sectionNodes = filtered.filter(n => (n.sectionName ?? "General") === section);
          if (sectionNodes.length === 0) return null;
          const mastered = sectionNodes.filter(n => {
            const s = n.userNodeStates?.[0]?.state;
            return s === "mastered" || s === "due";
          }).length;
          const sectionPct = Math.round((mastered / sectionNodes.length) * 100);

          return (
            <div key={section} className="mb-8">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-slate-800">{section}</h2>
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <span>{mastered}/{sectionNodes.length}</span>
                  <Progress value={sectionPct} className="w-20 h-1.5" />
                </div>
              </div>

              <div className="space-y-2">
                {sectionNodes.map(node => {
                  const s = node.userNodeStates?.[0];
                  const state = (s?.state ?? "locked") as "locked" | "available" | "in_progress" | "mastered" | "due";
                  const isLocked = state === "locked";
                  const action = getNodeAction(node);
                  const prereqTitle = isLocked && node.incomingEdges?.[0]?.fromNode?.title;

                  return (
                    <div
                      key={node.id}
                      onClick={() => !isLocked && action?.()}
                      className={`flex items-center gap-4 p-4 rounded-xl border transition-all ${
                        isLocked
                          ? "bg-slate-50 border-slate-100 opacity-60 cursor-not-allowed"
                          : "bg-white border-slate-200 hover:border-indigo-200 hover:shadow-sm cursor-pointer"
                      }`}
                    >
                      <div className={`h-9 w-9 rounded-lg flex items-center justify-center shrink-0 ${NODE_STATE_COLORS[state].bg}`}>
                        {isLocked ? <Lock className="h-4 w-4 text-slate-400" /> : <span className="text-sm">{state === "mastered" ? "✓" : state === "due" ? "↺" : "→"}</span>}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className={`text-sm font-medium truncate ${isLocked ? "text-slate-400" : "text-slate-900"}`}>{node.title}</p>
                          <NodeStateBadge state={state} />
                        </div>
                        {isLocked && prereqTitle ? (
                          <p className="text-xs text-slate-400 mt-0.5">Complete "{prereqTitle}" first</p>
                        ) : (
                          <p className="text-xs text-slate-500 mt-0.5 truncate">{node.summary}</p>
                        )}
                      </div>

                      {!isLocked && (
                        <div className="text-right shrink-0">
                          {s?.masteryScore ? <p className="text-xs font-medium text-slate-700">{Math.round(s.masteryScore * 100)}%</p> : null}
                          <ChevronRight className="h-4 w-4 text-slate-300 ml-auto mt-0.5" />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </main>
    </div>
  );
}
