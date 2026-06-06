/**
 * Revision review — grade recall, update FSRS schedule.
 */
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { scheduleCard, gradeFromLabel } from "@/lib/fsrs";

export async function POST(req: NextRequest, { params }: { params: Promise<{ nodeId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;
  const { nodeId } = await params;

  const { grade, bookId } = await req.json();
  // grade: "Again" | "Hard" | "Good" | "Easy"

  const state = await prisma.userNodeState.findUnique({ where: { userId_nodeId: { userId, nodeId } } });
  if (!state) return NextResponse.json({ error: "State not found" }, { status: 404 });

  const fsrsGrade = gradeFromLabel(grade);
  const result = scheduleCard(
    {
      stability: state.recallStability,
      difficulty: state.recallDifficulty,
      recallProbability: state.recallProbability,
      lapseCount: state.lapseCount,
      reviewCount: state.reviewCount,
      lastReviewed: state.lastReviewed,
      nextDue: state.nextDue,
    },
    fsrsGrade
  );

  const today = new Date().toISOString().split("T")[0];
  const newState = fsrsGrade === 1 ? "due" : "mastered";

  await prisma.userNodeState.update({
    where: { userId_nodeId: { userId, nodeId } },
    data: {
      state: newState,
      recallStability: result.stability,
      recallDifficulty: result.difficulty,
      recallProbability: result.recallProbability,
      lastReviewed: today,
      nextDue: result.nextDue,
      reviewCount: { increment: 1 },
      lapseCount: fsrsGrade === 1 ? { increment: 1 } : undefined,
    },
  });

  await prisma.book.update({ where: { id: bookId }, data: { lastStudied: today } });

  return NextResponse.json({ nextDue: result.nextDue, interval: result.interval, state: newState });
}
