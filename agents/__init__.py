"""Aita-Lagun agents package — exports sub-agent instances.

Import order is intentional to avoid circular imports:
1. ``recordatorio_agent`` first (no agent imports, pure function)
2. ``orchestrator.py`` second (imports from recordatorio_agent)
3. ``info_salud_agent.py`` third (standalone, no inter-agent deps)
4. ``agent.py`` last (imports from orchestrator and info_salud_agent)

Running ``python -m agents.agent`` triggers ``agents/__init__.py`` first,
which is why we don't import ``agent.py`` here — that would cause a
double-load of the root agent module.

``load_dotenv()`` is called here because ``__init__.py`` runs before
any other module in the package. If it were in ``agent.py``, the sub-agents
would be created with default env values before ``.env`` is loaded.
"""

import logging
import warnings

# --- Suppress non-actionable warnings for clean user experience ---

# Python 3.10 EOL warning from google-api-core (noisy, non-blocking)
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")

# ADK non-actionable warnings (experimental features, API key preferences, etc.)
warnings.filterwarnings("ignore", category=UserWarning, module="google.adk")
warnings.filterwarnings("ignore", category=UserWarning, module="google.genai")

# Regional Access Boundary — non-blocking Google Cloud policy check
logging.getLogger("google.api_core").setLevel(logging.ERROR)

from dotenv import load_dotenv

load_dotenv()

from agents.orchestrator import recordatorio
from agents.info_salud_agent import info_salud_agent

__all__ = [
    "recordatorio",
    "info_salud_agent",
]
