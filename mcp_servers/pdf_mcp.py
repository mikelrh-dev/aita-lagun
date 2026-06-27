"""FastMCP server for PDF search integration.

Exposes a single tool ``buscar_en_pdfs`` that searches across all Osakidetza
PDF documents for matching content.

Key design decisions:
- PDFs are loaded from local disk (``data/`` directory) — no network requests
  for document fetching. This makes the server deterministic and testable
  without external dependencies.
- Search is case-insensitive to accommodate user typos and language variation
  (e.g., "Cita Previa" vs "cita previa").
- Snippets are limited to 300 characters to keep LLM context manageable.
  This is a pragmatic balance between completeness and token economy.
- Documents are sourced from official public Osakidetza PDFs only.
  No personal or restricted data is accessed.
"""

import os
from typing import Optional

import fitz
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PDF Server")

# Paths to the three Osakidetza health system PDFs stored locally.
# These are official public documents downloaded from the Osakidetza website.
# Paths are resolved relative to the mcp_servers/ directory using __file__.
PDF_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "data", "01_cita_previa_osakidetza.pdf"),
    os.path.join(os.path.dirname(__file__), "..", "data", "02_horarios_barakaldo.pdf"),
    os.path.join(os.path.dirname(__file__), "..", "data", "03_carpeta_salud_funciones.pdf"),
]


def _extract_text_from_pdf(path: str) -> Optional[str]:
    """Extract all text from a PDF file using PyMuPDF (fitz).

    Iterates over all pages and concatenates their text content.
    Returns ``None`` for unreadable files (missing, corrupted, or encrypted)
    rather than raising — this lets the search skip bad files gracefully.

    Args:
        path: Absolute or relative filesystem path to the PDF.

    Returns:
        All text content as a single string, or None on failure.
    """
    try:
        doc = fitz.open(path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return " ".join(text_parts)
    except Exception:
        # Catching broadly because fitz can raise various errors:
        # FileNotFoundError, fitz.FileDataError for corrupted PDFs, etc.
        # Returning None lets the caller handle the absence gracefully.
        return None


def _search_pdfs(query: str) -> str:
    """Search across all PDFs for the given query.

    Performs a case-insensitive substring search across all three PDFs.
    Matching snippets are collected and truncated to 300 characters each
    to keep responses concise for the LLM.

    Args:
        query: The search term (lowercased internally for matching).

    Returns:
        Combined matching text (up to 3000 chars, each snippet up to 300
        chars) or a no-result message in the query's detected language.
    """
    query_lower = query.lower()
    results = []

    for pdf_path in PDF_PATHS:
        text = _extract_text_from_pdf(pdf_path)
        if text is None:
            # Skip PDFs that can't be read (e.g., file missing on disk).
            # This keeps the search resilient even if one document is removed.
            continue
        # Case-insensitive search: lowercase both query and document text.
        if query_lower in text.lower():
            start = text.lower().find(query_lower)
            # Return the snippet starting from the match, up to 300 chars.
            # 300 chars is a heuristic: enough to provide context, short
            # enough to fit multiple matches in the LLM's context window.
            snippet = text[start : start + 300]
            results.append(snippet.strip())

    if results:
        # Join snippets from all matched PDFs.
        # Each snippet is already limited to 300 chars independently,
        # so all matches are preserved for the LLM.
        combined = "\n\n---\n\n".join(results)
        # Cap total context to 3000 chars to keep LLM context manageable
        # while preserving multi-document matches.
        return combined[:3000]

    # Return "no results" in the query's language so the LLM can respond
    # consistently with the user's language.
    query_lower = query.lower()
    if any(w in query_lower for w in ['how', 'what', 'where', 'when', 'appointment', 'schedule', 'book']):
        return "No information was found for that query in the available documents."
    if any(w in query_lower for w in ['nola', 'zer', 'non', 'noiz', 'hitord', 'zita']):
        return "Ez da informaziorik aurkitu galdera horretarako eskuragarri dauden dokumentuetan."

    return "No se encontró información sobre esa consulta en los documentos disponibles."


@mcp.tool()
def buscar_en_pdfs(query: str) -> str:
    """Search for information across Osakidetza health system PDFs.

    Args:
        query: Search query in Spanish, Basque, or English

    Returns:
        Matching text snippet (up to 300 characters) or no-result message
    """
    return _search_pdfs(query)


if __name__ == "__main__":
    mcp.run(transport="stdio")
