import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";

export async function GET(_req: NextRequest, { params }: { params: Promise<{ bookId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;
  const { bookId } = await params;

  const book = await prisma.book.findFirst({
    where: { id: bookId, ownerId: userId },
    include: {
      nodes: {
        include: {
          outgoingEdges: true,
          incomingEdges: true,
          userNodeStates: { where: { userId } },
        },
        orderBy: { orderIndex: "asc" },
      },
    },
  });

  if (!book) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json({ book });
}

export async function PATCH(req: NextRequest, { params }: { params: Promise<{ bookId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;
  const { bookId } = await params;

  const data = await req.json();
  const book = await prisma.book.updateMany({
    where: { id: bookId, ownerId: userId },
    data,
  });

  return NextResponse.json({ book });
}
