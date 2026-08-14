"""Day 3, Part 2 side-quest — a BUILT-IN tool.

Custom tools run YOUR code on YOUR machine. Built-in tools run on Google's
side, inside the model call itself — you get capability without writing any
implementation. `google_search` grounds answers in live web results.

Built-in tools come with restrictions custom tools don't have (supported
models, and limits on combining them with other tools in one agent) — which is
why this demo lives in its own tiny agent instead of inside playfield_analyst.
Check the ADK docs ("Built-in tools") for the current rules.
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

root_agent = LlmAgent(
    model="gemini-3.5-flash-lite",
    name="web_scout",
    description="Answers questions using live Google Search results.",
    instruction=(
        "Answer using Google Search. Always mention which sources you used. "
        "If results conflict, say so."
    ),
    tools=[google_search],
)
