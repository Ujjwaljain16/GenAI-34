"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import ReactFlow, { Node, Edge, MarkerType, Controls, Background, MiniMap, useNodesState, useEdgesState } from "reactflow";
import "reactflow/dist/style.css";
import { Filter, Loader2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Sidebar } from "@/components/Sidebar";
import { NodeStateBadge } from "@/components/NodeStateBadge";
import { NODE_STATE_COLORS, timeAgo, daysUntil } from "@/lib/utils";

type FilterKey = "all" | "due" | "available" | "mastered" | "locked";

const NODE_COLORS: Record<string, { border: string; bg: string }> = {
  locked: { border: "#cbd5e1", bg: "#f8fafc" },
  available: { border: "#60a5fa", bg: "#eff6ff" },
  in_progress: { border: "#fbbf24", bg: "#fffbeb" },
  mastered: { border: "#34d399", bg: "#f0fdf4" },
  due: { border: "#fb923c", bg: "#fff7ed" },
};

export default function GraphPage() {
  const params = useParams();
  const router = useRouter();
  const bookId = params.bookId as string;

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [rawData, setRawData] = useState<{ nodes: unknown[]; edges: unknown[] }>({ nodes: [], edges: [] });
  const [filter, setFilter] = useState<FilterKey>("all");
  const [selectedNode, setSelectedNode] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ mastered: 0, total: 0, revealed: 0 });

  useEffect(() => {
    Promise.all([
      fetch(`/api/books/${bookId}/graph`).then(r => r.json()),
      fetch(`/api/books/${bookId}`).then(r => r.json()),
    ]).then(([{ nodes: kgNodes, edges: kgEdges }, { book }]) => {
      setRawData({ nodes: kgNodes, edges: kgEdges });
      buildGraph(kgNodes, kgEdges, book?.userNodeStates ?? [], "all");
      const allStates = book?.userNodeStates ?? [];
      setStats({
        mastered: allStates.filter((s: Record<string, string>) => s.state === "mastered" || s.state === "due").length,
        total: kgNodes.length,
        revealed: allStates.filter((s: Record<string, string>) => s.state !== "locked").length,
      });
      setLoading(false);
    });
  }, [bookId]);

  const buildGraph = (kgNodes: unknown[], kgEdges: unknown[], userStates: unknown[], f: FilterKey) => {
    const stateMap = new Map((userStates as Record<string, string>[]).map(s => [s.nodeId, s]));

    const flowNodes: Node[] = (kgNodes as Record<string, unknown>[])
      .filter(n => {
        const s = stateMap.get(n.id as string);
        const state = s?.state ?? "locked";
        if (f === "all") return true;
        return state === f || (f === "mastered" && state === "mastered");
      })
      .map((n, i) => {
        const s = stateMap.get(n.id as string);
        const state = (s?.state ?? "locked") as string;
        const colors = NODE_COLORS[state] ?? NODE_COLORS.locked;
        return {
          id: n.id as string,
          data: {
            label: n.title,
            state,
            userState: s,
          },
          position: { x: (i % 5) * 200, y: Math.floor(i / 5) * 110 },
          style: {
            background: colors.bg,
            border: `2px solid ${colors.border}`,
            borderRadius: 10,
            padding: "8px 12px",
            fontSize: 11,
            fontWeight: 500,
            color: state === "locked" ? "#94a3b8" : "#1e293b",
            opacity: state === "locked" ? 0.6 : 1,
            maxWidth: 160,
          },
        };
      });

    const nodeIds = new Set(flowNodes.map(n => n.id));
    const flowEdges: Edge[] = (kgEdges as Record<string, string>[])
      .filter(e => nodeIds.has(e.fromNodeId) && nodeIds.has(e.toNodeId))
      .map(e => ({
        id: e.id,
        source: e.fromNodeId,
        target: e.toNodeId,
        style: { stroke: "#94a3b8", strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#94a3b8" },
      }));

    setNodes(flowNodes);
    setEdges(flowEdges);
  };

  const applyFilter = (f: FilterKey) => {
    setFilter(f);
    const userStates = (rawData.nodes as Record<string, unknown>[]).map(() => ({}));
    buildGraph(rawData.nodes, rawData.edges, userStates, f);
    // Re-fetch with states
    fetch(`/api/books/${bookId}`).then(r => r.json()).then(({ book }) => {
      buildGraph(rawData.nodes, rawData.edges, book?.userNodeStates ?? [], f);
    });
  };

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    const raw = (rawData.nodes as Record<string, unknown>[]).find(n => n.id === node.id);
    setSelectedNode({ ...raw, ...node.data });
  };

  const masteredPct = stats.total > 0 ? Math.round((stats.mastered / stats.total) * 100) : 0;
  const revealedPct = stats.total > 0 ? Math.round((stats.revealed / stats.total) * 100) : 0;

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
      <div className="flex-1 ml-16 lg:ml-56 flex flex-col">
        {/* Header */}
        <div className="border-b border-slate-200 bg-white px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => router.push(`/book/${bookId}`)} className="text-slate-400 hover:text-slate-600">
              <ArrowLeft className="h-5 w-5" />
            </button>
            <h1 className="font-semibold text-slate-900">Knowledge Graph</h1>
          </div>
          <div className="flex items-center gap-2">
            {/* Progress overlay */}
            <span className="text-xs text-slate-500">{masteredPct}% mastered · {revealedPct}% revealed</span>

            {/* Filters */}
            <div className="flex items-center gap-1 ml-4">
              <Filter className="h-4 w-4 text-slate-400" />
              {(["all", "available", "due", "mastered", "locked"] as FilterKey[]).map(f => (
                <button
                  key={f}
                  onClick={() => applyFilter(f)}
                  className={`px-2 py-1 rounded text-xs font-medium transition-colors capitalize ${
                    filter === f ? "bg-indigo-100 text-indigo-700" : "text-slate-500 hover:bg-slate-100"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 px-6 py-2 bg-slate-50 border-b border-slate-200 text-xs">
          {Object.entries(NODE_COLORS).map(([state, colors]) => (
            <div key={state} className="flex items-center gap-1.5">
              <div className="h-3 w-3 rounded border-2" style={{ borderColor: colors.border, backgroundColor: colors.bg }} />
              <span className="capitalize text-slate-600">{state.replace("_", " ")}</span>
            </div>
          ))}
        </div>

        <div className="flex flex-1">
          <div className="flex-1" style={{ height: "calc(100vh - 120px)" }}>
            <ReactFlow
              nodes={nodes} edges={edges}
              onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              fitView
            >
              <Controls />
              <MiniMap nodeStrokeWidth={3} />
              <Background gap={16} color="#f1f5f9" />
            </ReactFlow>
          </div>

          {/* Node popover */}
          {selectedNode && (
            <div className="w-72 border-l border-slate-200 bg-white p-4 overflow-y-auto">
              <div className="flex items-center justify-between mb-3">
                <p className="font-semibold text-sm text-slate-900 flex-1">{String(selectedNode.title ?? selectedNode.label ?? "Node")}</p>
                <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-slate-600 text-xs">✕</button>
              </div>
              <NodeStateBadge state={(selectedNode.state as "locked" | "available" | "mastered" | "due" | "in_progress") ?? "locked"} />

              {selectedNode.userState != null && (
                <div className="mt-3 space-y-1.5 text-xs text-slate-600">
                  <p>Mastery: <strong>{Math.round(((selectedNode.userState as Record<string, number>).masteryScore ?? 0) * 100)}%</strong></p>
                  <p>Last reviewed: <strong>{timeAgo(String((selectedNode.userState as Record<string, unknown>).lastReviewed ?? ""))}</strong></p>
                  <p>Next due: <strong>{daysUntil(String((selectedNode.userState as Record<string, unknown>).nextDue ?? ""))}</strong></p>
                </div>
              )}

              {selectedNode.summary != null && (
                <p className="text-xs text-slate-600 mt-3 leading-relaxed">{String(selectedNode.summary)}</p>
              )}

              {selectedNode.state === "locked" ? (
                <p className="text-xs text-slate-400 mt-3 italic">Complete prerequisites to unlock.</p>
              ) : selectedNode.state === "due" ? (
                <Button size="sm" variant="warning" className="mt-3 w-full" onClick={() => router.push(`/book/${bookId}/revision`)}>
                  Revise this
                </Button>
              ) : selectedNode.state === "available" || selectedNode.state === "in_progress" ? (
                <Button size="sm" className="mt-3 w-full" onClick={() => router.push(`/book/${bookId}/node/${String(selectedNode.id ?? "")}`)}>
                  Learn this
                </Button>
              ) : (
                <Button size="sm" variant="outline" className="mt-3 w-full" onClick={() => router.push(`/book/${bookId}/node/${String(selectedNode.id ?? "")}`)}>
                  View details
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
