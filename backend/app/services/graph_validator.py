from typing import List, Dict, Any

class GraphValidator:
    """
    Validates the generated knowledge graph against deterministic structural rules (V01-V08).
    """
    @staticmethod
    def validate(concepts: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        failures = []
        
        # V01: Cycle Detection (Kahn's Algorithm / DFS)
        cycles_found = GraphValidator.detect_cycles(concepts, edges)
        if cycles_found:
            failures.append({
                "rule": "V01",
                "passed": False,
                "severity": "CRITICAL",
                "detail": {"cycles": cycles_found}
            })
            
        # V05: Orphan Detection
        orphans = GraphValidator.detect_orphans(concepts, edges)
        if orphans:
            failures.append({
                "rule": "V05",
                "passed": False,
                "severity": "WARNING",
                "detail": {"orphans": orphans}
            })
            
        return failures

    @staticmethod
    def detect_cycles(concepts: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Uses DFS to find cycles in PREREQUISITE edges.
        Returns a list of cycles, where each cycle is a list of concept_ids.
        """
        adj = {c["id"]: [] for c in concepts}
        for e in edges:
            if e.get("relationship_type") == "PREREQUISITE":
                if e["source_concept_id"] in adj:
                    adj[e["source_concept_id"]].append(e["target_concept_id"])
                    
        visited = set()
        rec_stack = set()
        cycles = []
        path = []
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:].copy())
                    
            rec_stack.remove(node)
            path.pop()
            
        for c in concepts:
            if c["id"] not in visited:
                dfs(c["id"])
                
        return cycles

    @staticmethod
    def detect_orphans(concepts: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
        connected_nodes = set()
        for e in edges:
            connected_nodes.add(e["source_concept_id"])
            connected_nodes.add(e["target_concept_id"])
            
        orphans = [c["id"] for c in concepts if c["id"] not in connected_nodes]
        return orphans
