import tiktoken
from typing import List, Dict, Any


class Chunker:
    """
    Implements a deterministic sliding window chunking algorithm.
    Target: 800-1200 tokens per chunk with 15% overlap.
    """

    def __init__(
        self,
        model_name: str = "cl100k_base",
        chunk_size: int = 1000,
        overlap_percent: float = 0.15,
    ):
        self.encoder = tiktoken.get_encoding(model_name)
        self.chunk_size = chunk_size
        self.overlap = int(chunk_size * overlap_percent)

    def chunk_document(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes the output of DocumentParser and creates semantic chunks.
        Tracks page numbers for citation rendering.
        """
        pages = parsed_doc.get("pages", [])

        # Flatten text while keeping track of page boundaries
        tokens_with_pages = []
        for page in pages:
            text = page.get("text", "")
            page_num = page.get("page_num")

            # Encode text to tokens
            tokens = self.encoder.encode(text)
            for token in tokens:
                tokens_with_pages.append((token, page_num))

        chunks = []
        chunk_index = 0
        i = 0
        n_tokens = len(tokens_with_pages)

        while i < n_tokens:
            end = min(i + self.chunk_size, n_tokens)
            chunk_tokens_info = tokens_with_pages[i:end]

            if not chunk_tokens_info:
                break

            chunk_tokens = [t[0] for t in chunk_tokens_info]
            page_start = chunk_tokens_info[0][1]
            page_end = chunk_tokens_info[-1][1]

            chunk_text = self.encoder.decode(chunk_tokens)

            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "content": chunk_text,
                    "token_count": len(chunk_tokens),
                    "page_start": page_start,
                    "page_end": page_end,
                    "metadata": {},
                }
            )

            chunk_index += 1
            i += self.chunk_size - self.overlap

        return chunks
