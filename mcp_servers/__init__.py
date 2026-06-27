"""MCP servers package for Aita-Lagun.

Provides FastMCP servers for:
- ``calendar_mcp``: Google Calendar event creation (service account auth)
- ``pdf_mcp``: Osakidetza PDF document search (local PyMuPDF)

Both servers expose tools via the MCP stdio transport protocol and are
consumed by ADK agents through ``McpToolset(StdioConnectionParams(...))``.
"""
