from rapidfuzz import fuzz
from typing import List, Dict, Any


class CanonicalizationEngine:
    """
    Identifies duplicate concepts using fuzzy string matching and collapses them into a canonical representation.
    """

    def __init__(self, similarity_threshold: float = 85.0):
        self.similarity_threshold = similarity_threshold

    def find_duplicates(
        self, new_concept: Dict[str, Any], existing_concepts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Finds existing concepts that are highly similar to the new concept.
        """
        duplicates = []
        new_name = new_concept.get("name", "").lower()

        for existing in existing_concepts:
            existing_name = existing.get("name", "").lower()
            # Use token_sort_ratio to handle word reordering e.g. "Linear Regression" vs "Regression Linear"
            score = fuzz.token_sort_ratio(new_name, existing_name)
            if score >= self.similarity_threshold:
                duplicates.append(existing)

        return duplicates

    def group_candidates(
        self, candidates: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Groups a flat list of candidates into clusters of duplicates.
        """
        clusters = []
        unassigned = list(candidates)

        while unassigned:
            current = unassigned.pop(0)
            cluster = [current]

            i = 0
            while i < len(unassigned):
                candidate = unassigned[i]
                score = fuzz.token_sort_ratio(
                    current.get("name", "").lower(), candidate.get("name", "").lower()
                )
                if score >= self.similarity_threshold:
                    cluster.append(unassigned.pop(i))
                else:
                    i += 1

            clusters.append(cluster)

        return clusters
