/**
 * Daily plan engine — returns the day's scheduled nodes.
 * Three modes: revise_only | learn_only | both
 */
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { getRecallProbability } from "@/lib/fsrs";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ bookId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;
  const { bookId } = await params;

  const user = await prisma.user.findUnique({ where: { id: userId }, select: { dailyNewNodeCap: true } });
  const dailyCap = user?.dailyNewNodeCap ?? 5;

  const today = new Date().toISOString().split("T")[0];

  const allStates = await prisma.userNodeState.findMany({
    where: { userId, bookId },
    include: { node: { select: { id: true, title: true, summary: true, difficultyTier: true } } },
  });

  // Due nodes (nextDue <= today, state = due or mastered with overdue)
  const dueNodes = allStates
    .filter((s) => s.nextDue && s.nextDue <= today && (s.state === "due" || s.state === "mastered"))
    .map((s) => ({
      ...s,
      recallProbability: getRecallProbability({
        stability: s.recallStability,
        difficulty: s.recallDifficulty,
        recallProbability: s.recallProbability,
        lapseCount: s.lapseCount,
        reviewCount: s.reviewCount,
        lastReviewed: s.lastReviewed,
        nextDue: s.nextDue,
      }),
    }))
    .sort((a, b) => a.recallProbability - b.recallProbability) // most forgotten first
    .slice(0, 20);

  // Available nodes (unlocked, not started)
  const availableNodes = allStates
    .filter((s) => s.state === "available")
    .sort((a, b) => 0) // preserve topological order
    .slice(0, dailyCap);

  const hasDue = dueNodes.length > 0;
  const hasAvailable = availableNodes.length > 0;

  let mode: "revise_only" | "learn_only" | "both" | "all_caught_up";
  if (!hasDue && !hasAvailable) mode = "all_caught_up";
  else if (hasDue && !hasAvailable) mode = "revise_only";
  else if (!hasDue && hasAvailable) mode = "learn_only";
  else mode = "both";

  const planNodes = [
    ...dueNodes.map((n) => ({ ...n, planType: "revise" as const })),
    ...(mode !== "revise_only" ? availableNodes.slice(0, dailyCap - Math.min(dueNodes.length, dailyCap)).map((n) => ({ ...n, planType: "learn" as const })) : []),
  ];

  const totalNodes = allStates.length;
  const masteredCount = allStates.filter((s) => s.state === "mastered" || s.state === "due").length;

  return NextResponse.json({
    mode,
    planNodes,
    dueCount: dueNodes.length,
    availableCount: availableNodes.length,
    totalNodes,
    masteredCount,
    progressPct: totalNodes > 0 ? Math.round((masteredCount / totalNodes) * 100) : 0,
  });
}
