"""Day 5, Part 3 — the token callback (step 3.3).

join_game returns your secret token, and every later tool call needs it.
Right now the token lives ONLY in the conversation history — if the model
drops or garbles it (long games, long contexts…), your player is locked out
of its own game.

The fix is Day 3's lesson: important state is EXPLICIT state. An
after_tool_callback fires after every tool call, sees the tool's result,
and can write to session state — the perfect place to catch the token the
moment join_game returns it.
"""

import json
from typing import Any, Optional

from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool


def save_token(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    """After join_game succeeds, stash the token in session state.

    Return None so the tool result flows through unchanged — this callback
    observes, it doesn't rewrite.
    """
    if tool.name != "join_game":
        return None

    token = None
    try:
        if isinstance(tool_response, dict):
            if "token" in tool_response:
                token = tool_response["token"]
            elif "content" in tool_response and isinstance(tool_response["content"], list) and len(tool_response["content"]) > 0:
                item = tool_response["content"][0]
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content = item.get("text", "")
                    data = json.loads(text_content)
                    if isinstance(data, dict):
                        token = data.get("token")
    except Exception as e:
        print(f"Error parsing token from tool response: {e}")

    if token:
        tool_context.state["game:token"] = token
        print(f"Confirmation: Token saved to state['game:token']: {token}")

    return None
