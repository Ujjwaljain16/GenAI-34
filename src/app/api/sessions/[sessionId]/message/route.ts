/**
 * Socratic learning — streams Claude's response to a user message.
 * Claude teaches by questioning, not lecturing, grounded in sourceChunks.
 */
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

export async function POST(req: NextRequest, { params }: { params: Promise<{ sessionId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;
  const { sessionId } = await params;

  const { message, nodeId, isQuestion } = await req.json();

  const learningSession = await prisma.session.findFirst({
    where: { id: sessionId, userId },
  });
  if (!learningSession) return NextResponse.json({ error: "Session not found" }, { status: 404 });

  const node = await prisma.kGNode.findUnique({ where: { id: nodeId } });
  if (!node) return NextResponse.json({ error: "Node not found" }, { status: 404 });

  // If user asked a question, save it for revision
  if (isQuestion) {
    await prisma.question.create({
      data: {
        nodeId,
        type: "theory",
        difficulty: "medium",
        source: "user_asked",
        body: message,
      },
    });
  }

  const transcript = JSON.parse(learningSession.transcript || "[]");
  const sourceChunks = JSON.parse(node.sourceChunks || "[]");
  const sourceText = sourceChunks.join("\n\n").slice(0, 1500);

  const systemPrompt = `You are a Socratic tutor teaching the concept "${node.title}" from a book.

Concept summary: ${node.summary}

Relevant source text:
${sourceText}

RULES:
- Teach by asking probing questions, NOT by lecturing.
- Never give the answer directly — guide the student to discover it.
- Keep responses concise (2-4 sentences max).
- If the student asks a question, answer it briefly then probe further.
- After ~5-6 exchanges, ask "I think you've got this — shall we wrap up?" to signal completion.
- Stay grounded in the source text.`;

  const messages = [
    ...transcript.map((t: { role: string; content: string }) => ({
      role: t.role as "user" | "assistant",
      content: t.content,
    })),
    { role: "user" as const, content: message },
  ];

  if (!process.env.ANTHROPIC_API_KEY) {
    // Demo mode
    const demoResponse = `Interesting thought! Let me ask you this: based on what you know about "${node.title}", what do you think would happen if we applied this concept to a real-world scenario? What comes to mind?`;

    const newTranscript = [...transcript, { role: "user", content: message }, { role: "assistant", content: demoResponse }];
    await prisma.session.update({
      where: { id: sessionId },
      data: { transcript: JSON.stringify(newTranscript) },
    });

    return NextResponse.json({ response: demoResponse, questionSaved: isQuestion });
  }

  const aiResponse = await client.messages.create({
    model: "claude-sonnet-4-5",
    max_tokens: 300,
    system: systemPrompt,
    messages,
  });

  const responseText = aiResponse.content[0].type === "text" ? aiResponse.content[0].text : "";

  // Update transcript
  const newTranscript = [
    ...transcript,
    { role: "user", content: message },
    { role: "assistant", content: responseText },
  ];

  await prisma.session.update({
    where: { id: sessionId },
    data: { transcript: JSON.stringify(newTranscript) },
  });

  return NextResponse.json({ response: responseText, questionSaved: isQuestion });
}
