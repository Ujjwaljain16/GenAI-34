import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";

export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;

  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: {
      id: true, name: true, email: true, avatarUrl: true,
      dailyNewNodeCap: true, dailyReminderTime: true, sessionLengthPref: true,
      notifyReminders: true, notifyDueReviews: true, notifyProcessing: true,
      globalStreak: true, lastActiveDate: true, createdAt: true,
    },
  });

  return NextResponse.json({ user });
}

export async function PATCH(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;

  const data = await req.json();
  const allowed = ["name", "avatarUrl", "dailyNewNodeCap", "dailyReminderTime", "sessionLengthPref", "notifyReminders", "notifyDueReviews", "notifyProcessing"];
  const update: Record<string, unknown> = {};
  for (const k of allowed) {
    if (k in data) update[k] = data[k];
  }

  const user = await prisma.user.update({ where: { id: userId }, data: update });
  return NextResponse.json({ user });
}
