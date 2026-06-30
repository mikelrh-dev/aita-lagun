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
from datetime import date as date_mod

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


def _build_instruction(callback_context: CallbackContext) -> str:
    """Build dynamic instruction with the detected language.

    Reads the language detected by the root agent's ``_detect_language``
    callback from shared session state, so this sub-agent responds in
    the same language as the user's first message.

    Args:
        callback_context: ADK callback context with session state access.

    Returns:
        Instruction string for the info_salud agent.
    """
    lang = callback_context.state.get("lang", "en")
    today = date_mod.today()
    return (
        "You are a health information assistant for Osakidetza, the Basque health system. "
        f"The user's language has been detected as: {lang.upper()}. "
        f"Today's date is {today.isoformat()}. "
        "You MUST respond in that language. Do NOT switch languages. "
        "Use the buscar_en_pdfs tool to answer questions about: "
        "cita previa (appointments), horarios (hours/locations), "
        "and carpeta de salud (health folder)."
    )


info_salud_agent = Agent(
    name="info_salud",
    model=os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
    instruction=_build_instruction,
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
