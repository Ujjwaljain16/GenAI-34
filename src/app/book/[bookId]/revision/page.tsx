"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Clock, CalendarClock, BookOpen, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sidebar } from "@/components/Sidebar";
import { estimateMinutes, timeAgo, daysUntil } from "@/lib/utils";

interface DueNode {
  nodeId: string;
  planType?: string;
  node: { title: string; summary: string };
  state: string;
  lastReviewed: string | null;
  nextDue: string | null;
  recallProbability: number;
}

export default function RevisionListPage() {
  const params = useParams();
  const router = useRouter();
  const bookId = params.bookId as string;

  const [dueNodes, setDueNodes] = useState<DueNode[]>([]);
  const [upcomingNodes, setUpcomingNodes] = useState<DueNode[]>([]);
  const [tab, setTab] = useState<"due" | "upcoming">("due");
  const [loading, setLoading] = useState(true);
  const [bookTitle, setBookTitle] = useState("");

  useEffect(() => {
    Promise.all([
      fetch(`/api/books/${bookId}/daily-plan`).then(r => r.json()),
      fetch(`/api/books/${bookId}`).then(r => r.json()),
    ]).then(([plan, { book }]) => {
      setBookTitle(book?.title ?? "");
      const today = new Date().toISOString().split("T")[0];
      const allDue = (plan.planNodes ?? []).filter((n: DueNode) => n.planType === "revise" || (n.nextDue && n.nextDue <= today));
      const upcoming = (plan.planNodes ?? []).filter((n: DueNode) => n.nextDue && n.nextDue > today);
      setDueNodes(allDue);
      setUpcomingNodes(upcoming);
      setLoading(false);
    });
  }, [bookId]);

  const displayed = tab === "due" ? dueNodes : upcomingNodes;

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
      <main className="flex-1 ml-16 lg:ml-56 p-6 max-w-2xl">
        <div className="flex items-center gap-3 mb-6">
          <button onClick={() => router.push(`/book/${bookId}`)} className="text-slate-400 hover:text-slate-600">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="font-bold text-slate-900 text-xl">Revision</h1>
            <p className="text-sm text-slate-500">{bookTitle}</p>
          </div>
        </div>

        {/* Summary */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4 text-orange-500" />
            <span className="font-medium text-slate-900">{dueNodes.length} due now</span>
          </div>
          <span className="text-slate-300">·</span>
          <span className="text-sm text-slate-500">{estimateMinutes(dueNodes.length)} min estimated</span>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-slate-100 rounded-xl p-1 mb-5 w-fit">
          <button
            onClick={() => setTab("due")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === "due" ? "bg-white shadow-sm text-slate-900" : "text-slate-500"}`}
          >
            Due now ({dueNodes.length})
          </button>
          <button
            onClick={() => setTab("upcoming")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === "upcoming" ? "bg-white shadow-sm text-slate-900" : "text-slate-500"}`}
          >
            Upcoming ({upcomingNodes.length})
          </button>
        </div>

        {displayed.length === 0 ? (
          <div className="text-center py-16">
            <div className="h-16 w-16 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <RefreshCw className="h-8 w-8 text-emerald-400" />
            </div>
            <h3 className="font-semibold text-slate-900 mb-1">
              {tab === "due" ? "All caught up!" : "Nothing upcoming"}
            </h3>
            <p className="text-sm text-slate-500">
              {tab === "due" ? "No reviews due today. Check the upcoming tab." : "Keep learning to build your review queue."}
            </p>
          </div>
        ) : (
          <>
            <div className="space-y-2 mb-6">
              {displayed.map((n, i) => (
                <Card key={i} className="hover:shadow-sm transition-shadow">
                  <CardContent className="p-4 flex items-center gap-4">
                    <div className="h-9 w-9 bg-orange-100 rounded-lg flex items-center justify-center shrink-0">
                      <RefreshCw className="h-4 w-4 text-orange-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{n.node?.title ?? n.nodeId}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-slate-500">{timeAgo(n.lastReviewed)}</span>
                        <span className="text-slate-300">·</span>
                        <span className={`text-xs font-medium ${tab === "due" ? "text-orange-600" : "text-slate-500"}`}>
                          {daysUntil(n.nextDue)}
                        </span>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs font-medium text-slate-600">
                        {Math.round((n.recallProbability ?? 0.9) * 100)}% recall
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {tab === "due" && (
              <Button className="w-full" size="lg" onClick={() => router.push(`/book/${bookId}/revision/session`)}>
                Start revision session ({dueNodes.length} cards)
              </Button>
            )}
          </>
        )}
      </main>
    </div>
  );
}
