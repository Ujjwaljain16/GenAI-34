import fitz  # PyMuPDF
from typing import Dict, Any


class DocumentParser:
    """
    Parses documents (PDFs initially) to extract raw text and metadata.
    """

    @staticmethod
    def parse_pdf(file_path: str) -> Dict[str, Any]:
        """
        Parses a PDF file and returns its text organized by pages, along with metadata.
        """
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            pages = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                pages.append(
                    {
                        "page_num": page_num + 1,  # 1-indexed
                        "text": text,
                    }
                )

            return {"metadata": metadata, "page_count": len(doc), "pages": pages}
        except Exception as e:
            raise ValueError(f"Failed to parse PDF {file_path}: {str(e)}")

    @staticmethod
    def parse(file_path: str, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Generic parsing entrypoint.
        """
        if "pdf" in mime_type.lower() or file_path.lower().endswith(".pdf"):
            return DocumentParser.parse_pdf(file_path)
        else:
            raise NotImplementedError(
                f"Parsing for mime type {mime_type} is not supported yet."
            )
