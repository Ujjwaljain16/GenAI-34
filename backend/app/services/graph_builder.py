from typing import List, Dict, Any, Tuple


class CandidatePairGenerator:
    """
    Generates candidate pairs of concepts for relationship extraction.
    Uses heuristic filtering to reduce LLM calls.
    Only pairs concepts found in the same chunk, section, or chapter.
    """

    @staticmethod
    def generate_pairs(concepts: List[Dict[str, Any]]) -> set[Tuple[str, str]]:
        """
        Takes a list of concepts (with source metadata) and returns a set of (concept_id_A, concept_id_B).
        A -> B and B -> A are both evaluated since PREREQUISITE is directional.
        """
        pairs = set()

        # In a real implementation with DB data, concepts would have chapter_id and chunk_ids attached.
        # This is a mock heuristic based on the architecture specification.
        for i, concept_a in enumerate(concepts):
            for j, concept_b in enumerate(concepts):
                if i == j:
                    continue

                a_id = concept_a.get("id")
                b_id = concept_b.get("id")

                # Mock heuristic: If they are adjacent in the list, we assume they are close in text.
                # In DB implementation: check if set(a_chunk_ids) & set(b_chunk_ids) OR a_chapter_id == b_chapter_id

                # Add directional pairs
                pairs.add((a_id, b_id))
                pairs.add((b_id, a_id))

        return pairs
