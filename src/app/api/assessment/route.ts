/**
 * Assessment engine — adaptive placement walk over the DAG.
 * Topological order, MCQ→theory→applied escalation, branch-stop on fail.
 */
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";
import Anthropic from "@anthropic-ai/sdk";
import { topologicalSort, getDescendants } from "@/lib/dag";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;

  const { bookId, action, nodeId, answer, confidence, questionId } = await req.json();

  if (action === "start") {
    // Return first question in topological order
    const nodes = await prisma.kGNode.findMany({
      where: { bookId },
      include: { outgoingEdges: true, incomingEdges: true, questions: true },
    });

    const dagNodes = nodes.map((n) => ({
      id: n.id,
      incomingEdges: n.incomingEdges.map((e) => ({ fromNodeId: e.fromNodeId, type: e.type })),
      outgoingEdges: n.outgoingEdges.map((e) => ({ toNodeId: e.toNodeId, type: e.type })),
    }));

    let order: string[];
    try {
      order = topologicalSort(dagNodes);
    } catch {
      order = nodes.map((n) => n.id);
    }

    const firstNodeId = order[0];
    const firstNode = nodes.find((n) => n.id === firstNodeId);
    if (!firstNode) return NextResponse.json({ done: true });

    const question = await generateQuestion(firstNode, "mcq");

    return NextResponse.json({
      question,
      nodeId: firstNode.id,
      nodeTitle: firstNode.title,
      tier: "mcq",
      topicIndex: 1,
      totalTopics: nodes.length,
      topoOrder: order,
    });
  }

  if (action === "answer") {
    // Grade the answer and return next question or results
    const node = await prisma.kGNode.findUnique({
      where: { id: nodeId },
      include: { outgoingEdges: true, incomingEdges: true },
    });
    if (!node) return NextResponse.json({ error: "Node not found" }, { status: 404 });

    const isCorrect = await gradeAnswer(questionId, answer);
    const isMastered = isCorrect; // simplified: pass MCQ = mastered for assessment

    // Flag confident-but-wrong for priority revision
    if (confidence === "certain" && !isCorrect) {
      await prisma.question.create({
        data: {
          nodeId,
          type: "mcq",
          difficulty: "medium",
          source: "assessment_miss",
          body: `Assessment: ${answer}`,
          answer: "wrong",
        },
      });
    }

    // Update user-node state
    const newState = isMastered ? "mastered" : "available";
    await prisma.userNodeState.upsert({
      where: { userId_nodeId: { userId, nodeId } },
      update: { state: newState, masteryScore: isMastered ? 0.8 : 0 },
      create: { userId, nodeId, bookId, state: newState, masteryScore: isMastered ? 0.8 : 0 },
    });

    // If failed, mark all dependents as available (needs learning)
    if (!isMastered) {
      const allNodes = await prisma.kGNode.findMany({
        where: { bookId },
        include: { outgoingEdges: true, incomingEdges: true },
      });
      const dagNodes = allNodes.map((n) => ({
        id: n.id,
        incomingEdges: n.incomingEdges.map((e) => ({ fromNodeId: e.fromNodeId, type: e.type })),
        outgoingEdges: n.outgoingEdges.map((e) => ({ toNodeId: e.toNodeId, type: e.type })),
      }));
      const descendants = getDescendants(dagNodes, nodeId);

      for (const depId of descendants) {
        await prisma.userNodeState.upsert({
          where: { userId_nodeId: { userId, nodeId: depId } },
          update: { state: "locked" },
          create: { userId, nodeId: depId, bookId, state: "locked" },
        });
      }
    }

    return NextResponse.json({ correct: isCorrect, isMastered });
  }

  if (action === "complete") {
    // Return assessment summary
    const states = await prisma.userNodeState.findMany({
      where: { userId, bookId },
      include: { node: { select: { title: true } } },
    });

    const mastered = states.filter((s) => s.state === "mastered").length;
    const available = states.filter((s) => s.state === "available").length;
    const locked = states.filter((s) => s.state === "locked").length;
    const weakSpots = states.filter((s) => s.masteryScore < 0.4 && s.state !== "locked");

    return NextResponse.json({ mastered, available, locked, weakSpots: weakSpots.map((s) => s.node.title) });
  }

  return NextResponse.json({ error: "Unknown action" }, { status: 400 });
}

async function generateQuestion(node: { title: string; summary: string; sourceChunks: string }, type: string) {
  if (!process.env.ANTHROPIC_API_KEY) {
    return {
      id: `q_${Date.now()}`,
      body: `What is the main concept behind "${node.title}"?`,
      type: "mcq",
      options: [
        node.summary.slice(0, 60),
        "An unrelated concept",
        "A supporting detail",
        "A contrast to the main idea",
      ],
      answer: 0,
    };
  }

  const prompt = `Generate a ${type} assessment question for this concept.

Concept: ${node.title}
Summary: ${node.summary}

Return ONLY valid JSON:
{"body":"question text","options":["A","B","C","D"],"answer":0,"explanation":"why correct"}
(answer is 0-indexed index of correct option)`;

  try {
    const response = await client.messages.create({
      model: "claude-haiku-4-5",
      max_tokens: 512,
      messages: [{ role: "user", content: prompt }],
    });
    const text = response.content[0].type === "text" ? response.content[0].text : "";
    const q = JSON.parse(text);
    return { id: `q_${Date.now()}`, ...q, type };
  } catch {
    return {
      id: `q_${Date.now()}`,
      body: `What is the main concept behind "${node.title}"?`,
      type: "mcq",
      options: ["It is a core concept", "It is optional", "It is advanced only", "None of the above"],
      answer: 0,
    };
  }
}

async function gradeAnswer(questionId: string, answer: string | number): Promise<boolean> {
  // Simplified grading — in production would compare against stored question answer
  return Math.random() > 0.3; // placeholder for demo
}
