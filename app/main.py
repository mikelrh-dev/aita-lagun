"""FastAPI application for Aita-Lagun chat backend.

Exposes the ADK agent behind a REST API so the chat frontend can interact
with it. CORS is open for local development. Static files (frontend) are
mounted after API routes so API paths take precedence.

Design decisions:
- ``agent_runner`` is imported lazily inside the handler to avoid triggering
  ADK singleton creation at import time — test-friendly and fast startup.
- ``python-multipart`` is required for form data parsing but only imported
  internally by Starlette when needed.
- Static files are mounted last so the catch-all ``/`` pattern doesn't
  shadow explicit API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Aita-Lagun API")

# CORS — allow all origins for local development (spec R3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request body for POST /api/chat."""

    message: str


class ChatResponse(BaseModel):
    """Response body for POST /api/chat."""

    reply: str


@app.get("/health")
async def health():
    """Simple health check — returns 200 when the server is running."""
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a message to the ADK agent and return its reply.

    The ``agent_runner`` module is imported lazily to avoid triggering
    ADK singleton creation at import time.
    """
    from app.agent_runner import ask_agent

    reply = await ask_agent(req.message)
    return ChatResponse(reply=reply)


# Mount static files AFTER API routes so /api/* takes precedence
# over the catch-all static file handler.
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
