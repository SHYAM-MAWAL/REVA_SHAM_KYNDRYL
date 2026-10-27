"""Email agent, refactored from notebooks/module-3/3.5_email_agent.py into a
reusable module the web server can import.

Behaviour (unchanged from the lesson):
- Users must authenticate with the correct email + password before the inbox
  and send-email tools become available (dynamic tools + dynamic prompt).
- `check_inbox` returns a canned email from Jane.
- `send_email` is gated by human-in-the-loop: the agent pauses (interrupt)
  and waits for an approve/reject decision before actually sending.
"""

from dataclasses import dataclass
from typing import Callable

from langchain.agents import AgentState, create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain.messages import ToolMessage
from langchain.agents.middleware import (
    wrap_model_call,
    dynamic_prompt,
    HumanInTheLoopMiddleware,
    ModelRequest,
    ModelResponse,
)
from langgraph.checkpoint.memory import InMemorySaver


@dataclass
class EmailContext:
    """Credentials the agent authenticates against (demo values)."""

    email_address: str = "julie@example.com"
    password: str = "password123"


class AuthenticatedState(AgentState):
    """Agent state extended with an authentication flag."""

    authenticated: bool


@tool
def check_inbox() -> str:
    """Check the inbox for recent emails"""
    return (
        "\n    Hi Julie, \n"
        "    I'm going to be in town next week and was wondering if we could grab a coffee?\n"
        "    - best, Jane (jane@example.com)\n    "
    )


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an response email"""
    return f"Email sent to {to} with subject {subject} and body {body}"


@tool
def authenticate(email: str, password: str, runtime: ToolRuntime) -> Command:
    """Authenticate the user with the given email and password"""
    if email == runtime.context.email_address and password == runtime.context.password:
        return Command(
            update={
                "authenticated": True,
                "messages": [
                    ToolMessage("Successfully authenticated", tool_call_id=runtime.tool_call_id)
                ],
            }
        )
    return Command(
        update={
            "authenticated": False,
            "messages": [
                ToolMessage("Authentication failed", tool_call_id=runtime.tool_call_id)
            ],
        }
    )


@wrap_model_call
def dynamic_tool_call(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Only expose inbox/send tools once the user is authenticated."""
    authenticated = request.state.get("authenticated")
    tools = [check_inbox, send_email] if authenticated else [authenticate]
    request = request.override(tools=tools)
    return handler(request)


authenticated_prompt = (
    "You are a helpful assistant that can check the inbox and send emails. \n"
    "Your first step after authentication is to check the inbox."
)
unauthenticated_prompt = "You are a helpful assistant that can authenticate users."


@dynamic_prompt
def dynamic_prompt_func(request: ModelRequest) -> str:
    """Pick the system prompt based on authentication status."""
    if request.state.get("authenticated"):
        return authenticated_prompt
    return unauthenticated_prompt


def build_agent():
    """Create a fresh agent instance with an in-memory checkpointer.

    A checkpointer is required so human-in-the-loop interrupts (send_email)
    can pause and later resume on the same thread_id.
    """
    return create_agent(
        "gpt-5-nano",
        tools=[authenticate, check_inbox, send_email],
        checkpointer=InMemorySaver(),
        state_schema=AuthenticatedState,
        context_schema=EmailContext,
        middleware=[
            dynamic_tool_call,
            dynamic_prompt_func,
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "authenticate": False,
                    "check_inbox": False,
                    "send_email": True,
                }
            ),
        ],
    )
