/**
 * DAG utilities — topological sort, cycle detection, prerequisite resolution.
 * These are core invariants: if the DAG is wrong, assessment + locking are wrong.
 */

export interface DAGNode {
  id: string;
  incomingEdges: { fromNodeId: string; type: string }[];
  outgoingEdges: { toNodeId: string; type: string }[];
}

/** Kahn's algorithm — returns topological order or throws if cycle detected */
export function topologicalSort(nodes: DAGNode[]): string[] {
  const inDegree = new Map<string, number>();
  const adjList = new Map<string, string[]>();

  for (const n of nodes) {
    inDegree.set(n.id, 0);
    adjList.set(n.id, []);
  }

  for (const n of nodes) {
    for (const edge of n.outgoingEdges) {
      if (edge.type === "prerequisite") {
        adjList.get(n.id)!.push(edge.toNodeId);
        inDegree.set(edge.toNodeId, (inDegree.get(edge.toNodeId) ?? 0) + 1);
      }
    }
  }

  const queue = [...inDegree.entries()]
    .filter(([, deg]) => deg === 0)
    .map(([id]) => id);

  const result: string[] = [];
  while (queue.length > 0) {
    const curr = queue.shift()!;
    result.push(curr);
    for (const next of adjList.get(curr) ?? []) {
      const newDeg = (inDegree.get(next) ?? 0) - 1;
      inDegree.set(next, newDeg);
      if (newDeg === 0) queue.push(next);
    }
  }

  if (result.length !== nodes.length) {
    throw new Error("Cycle detected in knowledge graph — DAG invariant violated");
  }

  return result;
}

/** Check if adding an edge would create a cycle */
export function wouldCreateCycle(
  nodes: DAGNode[],
  fromId: string,
  toId: string
): boolean {
  // DFS from toId — if we can reach fromId, adding fromId→toId creates a cycle
  const visited = new Set<string>();
  const adj = new Map<string, string[]>();

  for (const n of nodes) {
    adj.set(n.id, n.outgoingEdges.filter(e => e.type === "prerequisite").map(e => e.toNodeId));
  }

  function dfs(curr: string): boolean {
    if (curr === fromId) return true;
    if (visited.has(curr)) return false;
    visited.add(curr);
    return (adj.get(curr) ?? []).some(dfs);
  }

  return dfs(toId);
}

/** Get all descendants (nodes that depend on this one, directly or transitively) */
export function getDescendants(nodes: DAGNode[], nodeId: string): Set<string> {
  const result = new Set<string>();
  const adj = new Map<string, string[]>();

  for (const n of nodes) {
    // Reverse: who depends on this node? outgoing prerequisite edges point "requires"
    // So "fromNode prerequisite toNode" means toNode requires fromNode
    adj.set(n.id, []);
  }
  for (const n of nodes) {
    for (const e of n.outgoingEdges) {
      if (e.type === "prerequisite") {
        adj.get(e.toNodeId)!.push(n.id); // reversed: toNode → fromNode (dependents)
      }
    }
  }

  // Actually we want direct dependents (nodes that list nodeId as a prerequisite)
  // Edge: fromNode → toNode means toNode REQUIRES fromNode
  // Descendants = nodes that require nodeId (transitively)
  const depAdj = new Map<string, string[]>();
  for (const n of nodes) depAdj.set(n.id, []);
  for (const n of nodes) {
    for (const e of n.outgoingEdges) {
      if (e.type === "prerequisite") {
        depAdj.get(n.id)!.push(e.toNodeId);
      }
    }
  }

  const queue = [nodeId];
  while (queue.length > 0) {
    const curr = queue.shift()!;
    for (const dep of depAdj.get(curr) ?? []) {
      if (!result.has(dep)) {
        result.add(dep);
        queue.push(dep);
      }
    }
  }

  return result;
}

/** Get all prerequisites (ancestors) of a node */
export function getPrerequisites(nodes: DAGNode[], nodeId: string): Set<string> {
  const result = new Set<string>();
  const prereqAdj = new Map<string, string[]>();

  for (const n of nodes) prereqAdj.set(n.id, []);
  for (const n of nodes) {
    for (const e of n.outgoingEdges) {
      if (e.type === "prerequisite") {
        // e.toNodeId requires n.id
        prereqAdj.get(e.toNodeId)!.push(n.id);
      }
    }
  }

  const queue = [nodeId];
  while (queue.length > 0) {
    const curr = queue.shift()!;
    for (const prereq of prereqAdj.get(curr) ?? []) {
      if (!result.has(prereq)) {
        result.add(prereq);
        queue.push(prereq);
      }
    }
  }

  return result;
}

/** Check if a node is unlocked — all its prerequisite nodes are mastered */
export function isUnlocked(
  nodeId: string,
  nodes: DAGNode[],
  masteredIds: Set<string>
): boolean {
  const node = nodes.find((n) => n.id === nodeId);
  if (!node) return false;

  const prereqs = node.incomingEdges
    .filter((e) => e.type === "prerequisite")
    .map((e) => e.fromNodeId);

  return prereqs.every((p) => masteredIds.has(p));
}
