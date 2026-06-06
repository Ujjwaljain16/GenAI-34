import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";

export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;

  const { bookId, mode, nodeIds } = await req.json();

  const learningSession = await prisma.session.create({
    data: {
      userId,
      bookId,
      mode,
      nodeIds: JSON.stringify(nodeIds),
    },
  });

  // Mark node as in_progress
  if (nodeIds?.length > 0) {
    await prisma.userNodeState.upsert({
      where: { userId_nodeId: { userId, nodeId: nodeIds[0] } },
      update: { state: "in_progress" },
      create: { userId, nodeId: nodeIds[0], bookId, state: "in_progress" },
    });
  }

  return NextResponse.json({ session: learningSession }, { status: 201 });
}
