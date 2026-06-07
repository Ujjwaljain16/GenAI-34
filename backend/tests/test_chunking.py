import pytest
from app.services.chunking import Chunker

def test_sliding_window_chunking():
    chunker = Chunker(chunk_size=100, overlap_percent=0.15)
    
    # Mock DocumentParser output
    # Generate 300 words, roughly 300-400 tokens
    text = " ".join([f"word_{i}" for i in range(300)])
    parsed_doc = {
        "pages": [{"page_num": 1, "text": text}]
    }
    
    chunks = chunker.chunk_document(parsed_doc)
    
    # Assert deterministic token bounds
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["token_count"] <= chunker.chunk_size
        
    # Check overlap explicitly (the chunk size is 100, overlap is 15)
    if len(chunks) > 1:
        tokens_first = chunker.encoder.encode(chunks[0]["content"])
        tokens_second = chunker.encoder.encode(chunks[1]["content"])
        
        # The last 15 tokens of the first chunk should match the first 15 tokens of the second chunk
        overlap_size = chunker.overlap
        assert tokens_first[-overlap_size:] == tokens_second[:overlap_size]
