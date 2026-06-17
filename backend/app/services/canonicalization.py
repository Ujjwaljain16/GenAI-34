import re
import string
import logging
from typing import List, Dict, Any
from rapidfuzz import fuzz

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CanonicalizationEngine:
    """
    Identifies duplicate concepts using a 4-Layer pipeline:
    1. Exact Normalization
    2. RapidFuzz (Auto-Merge & Candidates)
    3. Embedding Retrieval (FAISS)
    4. Gemini LLM Judge
    """

    def __init__(self, llm_extractor):
        self.llm = llm_extractor
        
        # Thresholds
        self.auto_merge_threshold = 97.0
        self.candidate_threshold = 92.0
        self.embedding_threshold = 0.75
        
        # Negative Lexical Signals
        self.negative_pairs = [
            {"encryption", "decryption"},
            {"encode", "decode"},
            {"mitosis", "meiosis"},
            {"dfs", "bfs"},
            {"precision", "recall"},
        ]

    def _extract_ordinal(self, name: str) -> str:
        name = name.lower()
        match = re.search(r'\b(first|second|third|fourth|fifth|type i|type ii|layer 1|layer 2|layer 3|\d+)\b', name)
        return match.group(1) if match else None

    def _normalize(self, name: str) -> str:
        name = name.lower()
        name = name.replace("'s", "")
        name = name.translate(str.maketrans('', '', string.punctuation))
        return " ".join(name.split())

    def _are_negatives(self, name1: str, name2: str) -> bool:
        tokens1 = set(self._normalize(name1).split())
        tokens2 = set(self._normalize(name2).split())
        for pair in self.negative_pairs:
            intersection1 = tokens1.intersection(pair)
            intersection2 = tokens2.intersection(pair)
            if intersection1 and intersection2 and intersection1 != intersection2:
                return True
        return False

    def group_candidates(
        self, candidates: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        if not candidates:
            return []

        # Graph of merged connections (adjacency list)
        n = len(candidates)
        adj = {i: set() for i in range(n)}
        
        def add_edge(u, v):
            adj[u].add(v)
            adj[v].add(u)

        # Precompute embeddings
        texts = [f"{c.get('name', '')}. {c.get('summary', '')}" for c in candidates]
        
        try:
            embeddings = self.llm.get_embeddings(texts)
        except Exception as e:
            logger.error(f"Failed to fetch embeddings: {e}")
            embeddings = None
        
        if FAISS_AVAILABLE and embeddings is not None:
            embeddings_arr = np.array(embeddings, dtype=np.float32)
            # Normalize embeddings for Inner Product -> Cosine Similarity
            norms = np.linalg.norm(embeddings_arr, axis=1, keepdims=True)
            norms[norms == 0] = 1e-10
            embeddings_arr = embeddings_arr / norms
            
            d = embeddings_arr.shape[1]
            index = faiss.IndexFlatIP(d)
            index.add(embeddings_arr)
            
            k = min(5, n)
            D, I = index.search(embeddings_arr, k)
        else:
            # Fallback if faiss or embeddings API fails
            D, I = None, None

        # Determine edges
        for i in range(n):
            curr_name = candidates[i].get("name", "")
            curr_ord = self._extract_ordinal(curr_name)
            curr_norm = self._normalize(curr_name)
            
            # Use FAISS neighbors if available, else all subsequent indices
            if FAISS_AVAILABLE and I is not None:
                neighbors = I[i]
                distances = D[i]
                targets = [(j, distances[idx]) for idx, j in enumerate(neighbors) if j > i]
            else:
                targets = [(j, 0.0) for j in range(i + 1, n)]

            for j, cos_sim in targets:
                cand_name = candidates[j].get("name", "")
                
                # Layer 0: Ordinal Guardrail
                cand_ord = self._extract_ordinal(cand_name)
                if curr_ord is not None and cand_ord is not None and curr_ord != cand_ord:
                    continue
                    
                # Layer 0: Negative Lexical Signals
                if self._are_negatives(curr_name, cand_name):
                    continue
                    
                cand_norm = self._normalize(cand_name)
                
                # Layer 1: Normalization
                if curr_norm == cand_norm:
                    add_edge(i, j)
                    continue
                    
                # Layer 2: RapidFuzz
                score = fuzz.token_sort_ratio(curr_norm, cand_norm)
                if score >= self.auto_merge_threshold:
                    add_edge(i, j)
                    continue
                    
                # Layer 3: Embedding Candidate Retrieval
                # Only evaluate LLM judge if it's a FAISS candidate (high cos_sim) or fuzzy candidate
                is_candidate = (score >= self.candidate_threshold)
                if FAISS_AVAILABLE and I is not None and cos_sim >= self.embedding_threshold:
                    is_candidate = True
                    
                if is_candidate:
                    # Layer 4: Gemini LLM Judge
                    try:
                        if self.llm.judge_merge(candidates[i], candidates[j]):
                            add_edge(i, j)
                    except Exception as e:
                        logger.error(f"Error calling LLM Judge for merge: {e}")

        # Extract Connected Components
        visited = set()
        clusters = []
        for i in range(n):
            if i not in visited:
                cluster_indices = []
                stack = [i]
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        cluster_indices.append(node)
                        stack.extend(adj[node] - visited)
                clusters.append([candidates[idx] for idx in cluster_indices])
                
        return clusters
