/**
 * KG Construction pipeline — runs concept extraction + edge inference via Claude.
 * Pipeline: uploaded → parsing → kg_built → kg_verified → ready
 */
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";
import Anthropic from "@anthropic-ai/sdk";
import { wouldCreateCycle } from "@/lib/dag";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

export async function POST(req: NextRequest, { params }: { params: Promise<{ bookId: string }> }) {
  const session = await getServerSession(authOptions);
  if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const userId = (session.user as { id: string }).id;
  const { bookId } = await params;

  const book = await prisma.book.findFirst({ where: { id: bookId, ownerId: userId } });
  if (!book) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const { content } = await req.json();
  if (!content) return NextResponse.json({ error: "No content provided" }, { status: 400 });

  // Mark as parsing
  await prisma.book.update({ where: { id: bookId }, data: { status: "parsing" } });

  try {
    // Step 1: Chunk content by sections
    const chunks = chunkContent(content);

    // Step 2: Extract concepts
    await prisma.book.update({ where: { id: bookId }, data: { status: "parsing" } });

    const extractionPrompt = `You are a knowledge graph builder. Given these text chunks from a book, extract key concepts as nodes.

For each concept, provide:
- title: short concept name
- summary: 1-2 sentence explanation
- sourceChunk: the chunk index it came from (0-indexed)
- difficultyTier: "beginner" | "intermediate" | "advanced"
- sectionName: chapter/section name if identifiable

Text chunks:
${chunks.map((c, i) => `[${i}] ${c.slice(0, 500)}`).join("\n\n")}

Return ONLY valid JSON array of concepts (20-40 nodes for a typical book chapter). No markdown.
Format: [{"title":"...","summary":"...","sourceChunk":0,"difficultyTier":"beginner","sectionName":"..."}]`;

    const conceptResponse = await client.messages.create({
      model: "claude-opus-4-5",
      max_tokens: 4096,
      messages: [{ role: "user", content: extractionPrompt }],
    });

    let concepts: Array<{ title: string; summary: string; sourceChunk: number; difficultyTier: string; sectionName: string }>;
    try {
      const text = conceptResponse.content[0].type === "text" ? conceptResponse.content[0].text : "[]";
      concepts = JSON.parse(text);
    } catch {
      concepts = generateFallbackConcepts(chunks);
    }

    // Delete existing nodes for this book
    await prisma.kGNode.deleteMany({ where: { bookId } });

    // Create nodes
    const nodes = await Promise.all(
      concepts.map((c, i) =>
        prisma.kGNode.create({
          data: {
            bookId,
            title: c.title,
            summary: c.summary,
            sourceChunks: JSON.stringify([chunks[c.sourceChunk] ?? chunks[0] ?? content.slice(0, 500)]),
            difficultyTier: c.difficultyTier ?? "beginner",
            orderIndex: i,
            sectionName: c.sectionName,
          },
        })
      )
    );

    await prisma.book.update({ where: { id: bookId }, data: { status: "kg_built" } });

    // Step 3: Infer edges
    const edgePrompt = `Given these concepts from a book, identify prerequisite relationships.
A prerequisite edge from A to B means: "you must understand A before you can understand B."

Concepts:
${nodes.map((n, i) => `[${i}] ${n.title}: ${n.summary}`).join("\n")}

Return ONLY valid JSON array of edges. Be conservative — only high-confidence prerequisites.
No cycles allowed. Format: [{"from":0,"to":1,"confidence":0.8}]
(use array indices, not IDs)`;

    const edgeResponse = await client.messages.create({
      model: "claude-opus-4-5",
      max_tokens: 2048,
      messages: [{ role: "user", content: edgePrompt }],
    });

    let edgeProposals: Array<{ from: number; to: number; confidence: number }>;
    try {
      const text = edgeResponse.content[0].type === "text" ? edgeResponse.content[0].text : "[]";
      edgeProposals = JSON.parse(text);
    } catch {
      edgeProposals = generateFallbackEdges(nodes.length);
    }

    // Delete existing edges
    await prisma.kGEdge.deleteMany({ where: { fromNode: { bookId } } });

    // Build DAG-safe edges (skip cycles)
    const createdEdges: Array<{ fromNodeId: string; toNodeId: string }> = [];
    for (const ep of edgeProposals) {
      const from = nodes[ep.from];
      const to = nodes[ep.to];
      if (!from || !to || from.id === to.id) continue;

      // Build current state for cycle check
      const dagNodes = nodes.map((n) => ({
        id: n.id,
        incomingEdges: createdEdges.filter((e) => e.toNodeId === n.id).map((e) => ({ fromNodeId: e.fromNodeId, type: "prerequisite" })),
        outgoingEdges: createdEdges.filter((e) => e.fromNodeId === n.id).map((e) => ({ toNodeId: e.toNodeId, type: "prerequisite" })),
      }));

      if (!wouldCreateCycle(dagNodes, from.id, to.id)) {
        await prisma.kGEdge.create({
          data: {
            fromNodeId: from.id,
            toNodeId: to.id,
            type: "prerequisite",
            confidence: ep.confidence ?? 0.5,
          },
        }).catch(() => {}); // skip if duplicate
        createdEdges.push({ fromNodeId: from.id, toNodeId: to.id });
      }
    }

    await prisma.book.update({ where: { id: bookId }, data: { status: "kg_verified" } });

    return NextResponse.json({
      status: "kg_verified",
      nodeCount: nodes.length,
      edgeCount: createdEdges.length,
    });
  } catch (err) {
    await prisma.book.update({ where: { id: bookId }, data: { status: "uploaded" } });
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}

function chunkContent(content: string): string[] {
  const lines = content.split("\n");
  const chunks: string[] = [];
  let current = "";

  for (const line of lines) {
    if ((line.startsWith("#") || line.startsWith("Chapter") || line.startsWith("Section")) && current.length > 200) {
      chunks.push(current.trim());
      current = line + "\n";
    } else {
      current += line + "\n";
      if (current.length > 1500) {
        chunks.push(current.trim());
        current = "";
      }
    }
  }
  if (current.trim()) chunks.push(current.trim());
  return chunks.length > 0 ? chunks : [content.slice(0, 2000)];
}

function generateFallbackConcepts(chunks: string[]): Array<{ title: string; summary: string; sourceChunk: number; difficultyTier: string; sectionName: string }> {
  return chunks.slice(0, 10).map((c, i) => ({
    title: `Concept ${i + 1}`,
    summary: c.slice(0, 100) + "...",
    sourceChunk: i,
    difficultyTier: i < 3 ? "beginner" : i < 7 ? "intermediate" : "advanced",
    sectionName: `Section ${i + 1}`,
  }));
}

function generateFallbackEdges(nodeCount: number): Array<{ from: number; to: number; confidence: number }> {
  const edges = [];
  for (let i = 0; i < nodeCount - 1 && i < 5; i++) {
    edges.push({ from: i, to: i + 1, confidence: 0.6 });
  }
  return edges;
}
