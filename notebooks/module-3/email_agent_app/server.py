"""Starlette web server for the email agent.

Runs on stdlib-adjacent deps already present in this project (starlette +
uvicorn, pulled in by langgraph), so no extra installs are needed.

Endpoints:
  GET  /                -> serves the chat UI (static/index.html)
  POST /api/chat        -> {session_id, message} : run the agent with a user message
  POST /api/decision    -> {session_id, decision}: resume a paused send_email (approve|reject)

Each session_id maps to its own agent instance + thread, so multiple browser
tabs don't share authentication state.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

# Load .env from the project root (two levels up from this file).
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

from langchain.messages import HumanMessage  # noqa: E402
from langgraph.types import Command  # noqa: E402

from agent import build_agent, EmailContext  # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent / "static"

# session_id -> {"agent": agent, "config": {...}}
SESSIONS: dict[str, dict] = {}


def get_session(session_id: str) -> dict:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "agent": build_agent(),
            "config": {"configurable": {"thread_id": session_id}},
        }
    return SESSIONS[session_id]


def extract_pending_email(result: dict) -> dict | None:
    """If the run paused on a send_email interrupt, return the draft email."""
    interrupts = result.get("__interrupt__")
    if not interrupts:
        return None
    try:
        value = interrupts[0].value
        # value may be an object or a dict depending on version.
        if isinstance(value, dict):
            action_requests = value.get("action_requests", [])
        else:
            action_requests = getattr(value, "action_requests", [])
        req = action_requests[0]
        args = req["args"] if isinstance(req, dict) else req.args
        name = req.get("action") if isinstance(req, dict) else getattr(req, "action", "send_email")
        return {
            "action": name or "send_email",
            "to": args.get("to", ""),
            "subject": args.get("subject", ""),
            "body": args.get("body", ""),
        }
    except (IndexError, KeyError, AttributeError, TypeError):
        return None


def final_text(result: dict) -> str:
    """Best-effort human-readable text from the last AI message."""
    messages = result.get("messages") or []
    for msg in reversed(messages):
        content = getattr(msg, "content", "")
        if content and getattr(msg, "type", "") == "ai":
            return content
    # Fallback: last message with any content.
    for msg in reversed(messages):
        content = getattr(msg, "content", "")
        if content:
            return content
    return ""


def build_payload(result: dict) -> dict:
    pending = extract_pending_email(result)
    return {
        "reply": final_text(result),
        "pending_email": pending,
        "awaiting_approval": pending is not None,
    }


async def chat(request):
    data = await request.json()
    session_id = (data.get("session_id") or "default").strip()
    message = (data.get("message") or "").strip()
    if not message:
        return JSONResponse({"error": "message is required"}, status_code=400)

    session = get_session(session_id)
    try:
        result = session["agent"].invoke(
            {"messages": [HumanMessage(content=message)]},
            context=EmailContext(),
            config=session["config"],
        )
    except Exception as exc:  # surface errors to the UI instead of 500 HTML
        return JSONResponse({"error": str(exc)}, status_code=500)

    return JSONResponse(build_payload(result))


async def decision(request):
    data = await request.json()
    session_id = (data.get("session_id") or "default").strip()
    choice = (data.get("decision") or "").strip().lower()
    if choice not in ("approve", "reject"):
        return JSONResponse({"error": "decision must be 'approve' or 'reject'"}, status_code=400)
    if session_id not in SESSIONS:
        return JSONResponse({"error": "unknown session"}, status_code=400)

    session = SESSIONS[session_id]
    try:
        result = session["agent"].invoke(
            Command(resume={"decisions": [{"type": choice}]}),
            config=session["config"],
        )
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)

    return JSONResponse(build_payload(result))


async def index(request):
    return FileResponse(STATIC_DIR / "index.html")


routes = [
    Route("/", index),
    Route("/api/chat", chat, methods=["POST"]),
    Route("/api/decision", decision, methods=["POST"]),
    Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
]

app = Starlette(routes=routes)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8100"))
    uvicorn.run(app, host="127.0.0.1", port=port)
