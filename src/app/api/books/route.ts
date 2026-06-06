import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";

export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;

  const books = await prisma.book.findMany({
    where: { ownerId: userId },
    include: {
      nodes: { select: { id: true } },
      userNodeStates: {
        where: { userId },
        select: { state: true, nextDue: true },
      },
    },
    orderBy: { updatedAt: "desc" },
  });

  const enriched = books.map((b) => {
    const total = b.nodes.length;
    const mastered = b.userNodeStates.filter((s) => s.state === "mastered" || s.state === "due").length;
    const today = new Date().toISOString().split("T")[0];
    const dueToday = b.userNodeStates.filter((s) => s.nextDue && s.nextDue <= today).length;
    return { ...b, totalNodes: total, masteredNodes: mastered, dueToday };
  });

  return NextResponse.json({ books: enriched });
}

export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;

  const { title, author, isPublic } = await req.json();

  const book = await prisma.book.create({
    data: { ownerId: userId, title, author, isPublic: isPublic ?? false, status: "uploaded" },
  });

  return NextResponse.json({ book }, { status: 201 });
}
