/**
 * Graph verification — mark ready, update node/edge structure.
 */
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { topologicalSort } from "@/lib/dag";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ bookId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const { bookId } = await params;

  const nodes = await prisma.kGNode.findMany({
    where: { bookId },
    include: { outgoingEdges: true, incomingEdges: true },
    orderBy: { orderIndex: "asc" },
  });

  const edges = await prisma.kGEdge.findMany({
    where: { fromNode: { bookId } },
  });

  return NextResponse.json({ nodes, edges });
}

export async function POST(req: NextRequest, { params }: { params: Promise<{ bookId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;
  const { bookId } = await params;

  const book = await prisma.book.findFirst({ where: { id: bookId, ownerId: userId } });
  if (!book) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const { action, nodeData, edgeData } = await req.json();

  if (action === "confirm") {
    // Validate DAG before marking ready
    const nodes = await prisma.kGNode.findMany({
      where: { bookId },
      include: { outgoingEdges: true, incomingEdges: true },
    });

    const dagNodes = nodes.map((n) => ({
      id: n.id,
      incomingEdges: n.incomingEdges.map((e) => ({ fromNodeId: e.fromNodeId, type: e.type })),
      outgoingEdges: n.outgoingEdges.map((e) => ({ toNodeId: e.toNodeId, type: e.type })),
    }));

    try {
      topologicalSort(dagNodes);
    } catch {
      return NextResponse.json({ error: "Graph has cycles — fix before confirming" }, { status: 400 });
    }

    await prisma.book.update({ where: { id: bookId }, data: { status: "ready" } });

    // Initialize user-node states: first nodes (no prereqs) = available, rest = locked
    const masteredIds = new Set<string>();
    for (const n of nodes) {
      const prereqs = n.incomingEdges.filter((e) => e.type === "prerequisite");
      const state = prereqs.length === 0 ? "available" : "locked";
      await prisma.userNodeState.upsert({
        where: { userId_nodeId: { userId, nodeId: n.id } },
        update: {},
        create: { userId, nodeId: n.id, bookId, state },
      });
      if (state === "available") masteredIds.add(n.id);
    }

    return NextResponse.json({ status: "ready" });
  }

  if (action === "update_node" && nodeData) {
    await prisma.kGNode.update({ where: { id: nodeData.id }, data: nodeData });
    return NextResponse.json({ ok: true });
  }

  if (action === "delete_node" && nodeData?.id) {
    await prisma.kGNode.delete({ where: { id: nodeData.id } });
    return NextResponse.json({ ok: true });
  }

  if (action === "add_edge" && edgeData) {
    await prisma.kGEdge.create({ data: edgeData });
    return NextResponse.json({ ok: true });
  }

  if (action === "delete_edge" && edgeData?.id) {
    await prisma.kGEdge.delete({ where: { id: edgeData.id } });
    return NextResponse.json({ ok: true });
  }

  return NextResponse.json({ error: "Unknown action" }, { status: 400 });
}
