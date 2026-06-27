"""InfoSalud Agent — answers health system questions from Osakidetza PDFs.

ADK Agent that connects to the PDF MCP server via McpToolset.

Key design decisions:
- PDFs are sourced from official public Osakidetza documents only.
  No personal or restricted data is accessed. The PDFs contain
  general health system information (appointments, hours, digital
  health folder) published by the Basque health authority.
- The agent does NOT store query history or user data — every
  request is stateless and answered from the PDF content alone.
- Connection to the PDF MCP server uses stdio transport, keeping
  the deployment self-contained without network dependencies.
"""

import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

info_salud_agent = Agent(
    name="info_salud",
    model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
    instruction=(
        "You are a health information assistant for Osakidetza, the Basque health system. "
        "Use the buscar_en_pdfs tool to answer questions about: "
        "cita previa (appointments), horarios (hours/locations), "
        "and carpeta de salud (health folder). "
        "Answer in the same language the user used: English, Spanish, or Basque."
    ),
    description=(
        "Health information agent. Answers questions about Osakidetza appointments, "
        "health center hours, and digital health folder. "
        "Use this for health system queries."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python",
                    args=["-m", "mcp_servers.pdf_mcp"],
                ),
            ),
        ),
    ],
)
