# Email Assistant — Web Frontend

A small web UI for the Module 3.5 email agent. It wraps the same agent from
`3.5_email_agent.py` in a Starlette + uvicorn server and serves a single-page
chat UI with a human-in-the-loop approval step for sending email.

No extra dependencies are needed — `starlette` and `uvicorn` already ship with
this project (via `langgraph`).

## Run

From the project root:

```bash
uv run python notebooks/module-3/email_agent_app/server.py
```

Then open http://127.0.0.1:8100 in your browser.

To use a different port:

```bash
PORT=8200 uv run python notebooks/module-3/email_agent_app/server.py
```

> Requires a valid `OPENAI_API_KEY` in the project `.env` (the server loads it
> automatically).

## Try it

1. Authenticate: `julie@example.com, password123`
2. Ask it to check the inbox / draft a reply to Jane.
3. When the agent proposes sending an email, an **Approve & send / Reject**
   panel appears. Approving resumes the run and "sends" the email; rejecting
   cancels it.

## How it works

- **`agent.py`** — the agent factory (dynamic tools + dynamic prompt gated on
  authentication, and `HumanInTheLoopMiddleware` interrupting on `send_email`).
- **`server.py`** — Starlette app with:
  - `POST /api/chat` — send a user message; runs the agent on the session's thread.
  - `POST /api/decision` — resume a paused `send_email` with `approve` or `reject`.
  - `GET /` — serves the chat UI.
- **`static/index.html`** — the chat frontend. It creates a random `session_id`
  per browser tab so each tab gets its own agent + authentication state.

The send-email interrupt is read from `result["__interrupt__"]` and resumed with
`Command(resume={"decisions": [{"type": "approve" | "reject"}]})`, matching the
notebook flow.

## Notes

- State is kept in memory (`InMemorySaver`) per session. Restarting the server
  clears all sessions.
- The inbox and "sending" are mocked in the tools, exactly as in the lesson.
