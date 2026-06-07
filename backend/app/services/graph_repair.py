from typing import List, Dict, Any

class GraphRepair:
    """
    Implements deterministic repair strategies (R01-R04) for validation failures.
    """
    @staticmethod
    def repair_cycles(cycles: List[List[str]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        R01: Break cycles by removing the lowest confidence PREREQUISITE edge in the cycle.
        Returns the edges to remove.
        """
        edges_to_remove = []
        
        for cycle in cycles:
            # cycle is a list of node IDs: [A, B, C, A] -> edges are A->B, B->C, C->A
            cycle_edges = []
            for i in range(len(cycle) - 1):
                src = cycle[i]
                tgt = cycle[i+1]
                
                for e in edges:
                    if e["source_concept_id"] == src and e["target_concept_id"] == tgt and e["relationship_type"] == "PREREQUISITE":
                        cycle_edges.append(e)
                        
            # Edge case: wrap-around A->B->C->A. The DFS path already has the last node same as first if it's a closed loop,
            # wait, the DFS path in my validator might not duplicate the last node. Let's assume it doesn't wrap natively in the output,
            # so we explicitly check the closing edge.
            if cycle[0] != cycle[-1]:
                for e in edges:
                    if e["source_concept_id"] == cycle[-1] and e["target_concept_id"] == cycle[0] and e["relationship_type"] == "PREREQUISITE":
                        cycle_edges.append(e)

            if cycle_edges:
                # Find the edge with the lowest confidence
                lowest_confidence_edge = min(cycle_edges, key=lambda x: x.get("confidence", 1.0))
                if lowest_confidence_edge not in edges_to_remove:
                    edges_to_remove.append(lowest_confidence_edge)
                    
        return edges_to_remove
