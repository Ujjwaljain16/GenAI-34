/**
 * Complete a learning session — mark node mastered, init FSRS, unlock downstream.
 */
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { scheduleCard } from "@/lib/fsrs";
import { isUnlocked } from "@/lib/dag";

export async function POST(req: NextRequest, { params }: { params: Promise<{ sessionId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;
  const { sessionId } = await params;

  const learningSession = await prisma.session.findFirst({ where: { id: sessionId, userId } });
  if (!learningSession) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const nodeIds: string[] = JSON.parse(learningSession.nodeIds || "[]");
  const bookId = learningSession.bookId;
  const nodeId = nodeIds[0];

  if (!nodeId) return NextResponse.json({ error: "No node" }, { status: 400 });

  // Initialize FSRS for this node (first review = "Good")
  const fsrsResult = scheduleCard(
    { stability: 1, difficulty: 0.3, recallProbability: 1, lapseCount: 0, reviewCount: 0, lastReviewed: null, nextDue: null },
    3 // Good
  );

  const today = new Date().toISOString().split("T")[0];

  await prisma.userNodeState.upsert({
    where: { userId_nodeId: { userId, nodeId } },
    update: {
      state: "mastered",
      masteryScore: 1.0,
      recallStability: fsrsResult.stability,
      recallDifficulty: fsrsResult.difficulty,
      recallProbability: fsrsResult.recallProbability,
      lastReviewed: today,
      nextDue: fsrsResult.nextDue,
      reviewCount: 1,
    },
    create: {
      userId, nodeId, bookId,
      state: "mastered",
      masteryScore: 1.0,
      recallStability: fsrsResult.stability,
      recallDifficulty: fsrsResult.difficulty,
      recallProbability: fsrsResult.recallProbability,
      lastReviewed: today,
      nextDue: fsrsResult.nextDue,
      reviewCount: 1,
    },
  });

  // Mark session complete
  await prisma.session.update({ where: { id: sessionId }, data: { completedAt: today } });

  // Re-evaluate downstream nodes for unlocking
  const allNodes = await prisma.kGNode.findMany({
    where: { bookId },
    include: { outgoingEdges: true, incomingEdges: true },
  });

  const allStates = await prisma.userNodeState.findMany({ where: { userId, bookId } });
  const masteredIds = new Set(allStates.filter((s) => s.state === "mastered" || s.state === "due").map((s) => s.nodeId));
  masteredIds.add(nodeId); // just mastered

  const dagNodes = allNodes.map((n) => ({
    id: n.id,
    incomingEdges: n.incomingEdges.map((e) => ({ fromNodeId: e.fromNodeId, type: e.type })),
    outgoingEdges: n.outgoingEdges.map((e) => ({ toNodeId: e.toNodeId, type: e.type })),
  }));

  const unlockedNodes: string[] = [];
  for (const n of allNodes) {
    const currentState = allStates.find((s) => s.nodeId === n.id);
    if (currentState?.state === "locked" && isUnlocked(n.id, dagNodes, masteredIds)) {
      await prisma.userNodeState.upsert({
        where: { userId_nodeId: { userId, nodeId: n.id } },
        update: { state: "available" },
        create: { userId, nodeId: n.id, bookId, state: "available" },
      });
      unlockedNodes.push(n.title);
    }
  }

  // Update book streak and last studied
  await prisma.book.update({
    where: { id: bookId },
    data: { lastStudied: today },
  });

  return NextResponse.json({
    mastered: true,
    nextDue: fsrsResult.nextDue,
    unlockedNodes,
  });
}
