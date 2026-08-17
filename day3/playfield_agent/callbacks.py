"""Day 3, Part 4 — callbacks: observation and guardrails.

Callbacks are hooks around the agent loop. Two lessons today:

- before_tool_callback  → SEE everything the agent does (logging / observability)
- before_model_callback → STOP things before they reach the model (guardrails)

Return None  → proceed normally.
Return a value → REPLACE that step's result (skip the tool / skip the model).
"""

import time
from typing import Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types


def log_tool_calls(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> Optional[dict]:
    """Prints every tool call to the terminal running `adk web`.

    Poor-man's observability — but this exact hook is where real deployments
    attach metrics, audit logs, and cost tracking.
    """
    stamp = time.strftime("%H:%M:%S")
    print(f"[{stamp}] 🔧 {tool_context.agent_name} → {tool.name}({args})")
    return None  # never blocks — observation only


def refund_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Playfield policy: the agent must NOT handle refunds or payments —
    a human teammate does. Intercept those requests before the model sees them.
    """
    # TODO(you): Part 4, step 4.2
    #   1. find the last user message text in llm_request.contents
    #      (loop over reversed(llm_request.contents); take the first content
    #       with role == "user" and a text part)
    #   2. if any of REFUND_WORDS is in it (lowercased):
    #        - record it: callback_context.state["temp:refund_blocked"] = True
    #        - return LlmResponse(content=types.Content(
    #              role="model",
    #              parts=[types.Part(text=POLICY_ANSWER)]))
    #   3. otherwise return None (allow the model call)
<<<<<<< HEAD
    # raise NotImplementedError("Part 4, step 4.2")
    if "temp:citations" not in callback_context.state:
        callback_context.state["temp:citations"] = "No citations"
    lastmsg = next(
        (c for c in reversed(llm_request.contents) if c.role == "user" and any(p.text for p in c.parts)),
        None,
    )
    if lastmsg:
        text = " ".join(p.text for p in lastmsg.parts if p.text).lower()
        if any(word in text for word in REFUND_WORDS):
            callback_context.state["temp:refund_blocked"] = True
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=POLICY_ANSWER)],
                )
            )
    return None  # allow the model call

def record_docs(
    tool: BaseTool, args: dict[str, Any], tool_response: dict[str, Any], tool_context: ToolContext
) -> dict[str, Any] | None:
    if tool.name == "search_docs" and tool_response.get("status") == "success":
        hits = tool_response.get("hits", [])
        files = [hit["file"] for hit in hits if "file" in hit]
        if files:
            current = tool_context.state.get("temp:citations")
            existing = [c.strip() for c in current.split(",")] if current and current != "No citations" else []
            for f in files:
                if f not in existing:
                    existing.append(f)
            tool_context.state["temp:citations"] = ", ".join(existing)
    return None


REFUND_WORDS = ["refund", "money back", "chargeback", "rambursare", "banii inapoi", "return my money", "return my payment", "return my purchase"]
=======
    raise NotImplementedError("Part 4, step 4.2")


REFUND_WORDS = ["refund", "money back", "chargeback", "rambursare"]
>>>>>>> d1ea12a6a15ec2657950d3d950137aefcd9cfe8e

POLICY_ANSWER = (
    "I can't help with refunds or payments — that's handled by a human on the "
    "Playfield support team (support@playfield.example). I'm happy to help with "
    "anything about the games or their reviews!"
)
