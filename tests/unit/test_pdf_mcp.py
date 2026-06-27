"""Tests for pdf_mcp.py FastMCP server."""

from unittest.mock import MagicMock, patch

from mcp_servers.pdf_mcp import _search_pdfs, buscar_en_pdfs


class TestPdfMCP:
    """Unit tests for the PDF MCP buscar_en_pdfs tool."""

    @patch("mcp_servers.pdf_mcp.fitz.open")
    def test_buscar_en_pdfs_finds_match(self, mock_fitz_open):
        """Searches across all PDFs and returns matching content."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = (
            "Osakidetza cita previa: llame al 900 123 456 "
            "para solicitar consulta médica."
        )
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        result = buscar_en_pdfs(query="cita previa")

        assert "cita previa" in result.lower()
        assert "900 123 456" in result

    @patch("mcp_servers.pdf_mcp.fitz.open")
    def test_buscar_en_pdfs_empty_result(self, mock_fitz_open):
        """Returns empty result when query matches nothing."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = (
            "Información sobre Osakidetza y servicios de salud."
        )
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        result = buscar_en_pdfs(query="hospital universitario")

        assert "No se encontró información" in result

    @patch("mcp_servers.pdf_mcp.fitz.open")
    def test_buscar_en_pdfs_multi_pdf_scan(self, mock_fitz_open):
        """Searches across all configured PDF files."""
        docs = []
        texts = [
            "Cómo pedir cita en Osakidetza: online o teléfono.",
            "Centros de salud en Barakaldo: Centro 1, Centro 2.",
            "Acceda a su carpeta de salud digital.",
        ]
        for text in texts:
            mock_doc = MagicMock()
            mock_page = MagicMock()
            mock_page.get_text.return_value = text
            mock_doc.__iter__.return_value = [mock_page]
            docs.append(mock_doc)

        mock_fitz_open.side_effect = docs

        result = buscar_en_pdfs(query="Barakaldo")

        assert "Barakaldo" in result
        assert "Centro 1" in result
        # Should only return first 300 chars
        assert len(result) <= 300

    @patch("mcp_servers.pdf_mcp.fitz.open")
    def test_buscar_en_pdfs_skips_missing_file(self, mock_fitz_open):
        """Skips files that cannot be opened."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Only available content."
        mock_doc.__iter__.return_value = [mock_page]

        # First file fails, second succeeds
        mock_fitz_open.side_effect = [FileNotFoundError("not found"), mock_doc]

        result = buscar_en_pdfs(query="available")

        assert "available" in result.lower()


class TestSearchPdfsMultiLang:
    """Tests for multi-language no-result messages in _search_pdfs."""

    def test_no_match_english(self):
        """English keywords produce English no-result message."""
        result = _search_pdfs("how to book an appointment")
        assert "No information was found" in result

    def test_no_match_basque(self):
        """Basque keywords produce Basque no-result message."""
        result = _search_pdfs("nola hitzordua eskatu")
        assert "Ez da informaziorik aurkitu" in result

    def test_no_match_spanish(self):
        """Spanish/unknown query produces Spanish no-result message."""
        result = _search_pdfs("horarios centro salud")
        assert "No se encontró información" in result

    @patch("mcp_servers.pdf_mcp.fitz.open")
    def test_match_multiple_pdfs_has_separator(self, mock_fitz_open):
        """When query matches multiple PDFs, snippets are separated by '---'."""
        texts = [
            "Información sobre cómo pedir cita médica en Osakidetza.",
            "Horarios del centro de salud en Barakaldo: citas disponibles.",
            "Acceda a su carpeta de salud digital.",
        ]
        docs = []
        for text in texts:
            mock_doc = MagicMock()
            mock_page = MagicMock()
            mock_page.get_text.return_value = text
            mock_doc.__iter__.return_value = [mock_page]
            docs.append(mock_doc)
        mock_fitz_open.side_effect = docs

        result = buscar_en_pdfs(query="cita")

        # 'cita' appears in first two PDFs — separator should be present
        assert "---" in result
        assert "cita médica" in result
        assert "citas disponibles" in result
