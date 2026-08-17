# Day 2 · Your first agent

The conceptual leap: from *"I call the model"* to *"the model decides to call my
code."* You'll package Day 1's `search()`/`analyze()` as **tools**, hand them to
an ADK `LlmAgent`, and watch it plan, call, and chain them in `adk web`.

**Outcome:** a data-analyst agent that answers questions about the Playfield
dataset by calling tools you wrote.

| Time | Part | Focus |
|------|------|-------|
| 1h | 1 · Meet ADK | agent anatomy, `adk web`, honest failure without tools |
| 50m | 2 · The model-tool loop | functionCall/functionResponse, docstrings as UI |
| 45m | 3 · Power tools | port Day-1 search & extraction into the agent |
| 35m | 4 · Instructions | job-description instructions, red-teaming, the two walls |

Start here → [`WALKTHROUGH.md`](WALKTHROUGH.md). End-of-day state → [`solutions/`](solutions/).

Prerequisite from Day 1: your `day1/cache/review_embeddings.npy` (the tools
reuse it; if it's missing they re-embed once, which needs a working API key).
