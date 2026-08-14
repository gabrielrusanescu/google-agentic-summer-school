"""Day 3, Part 2 side-quest — MCP tools: the THIRD kind of tool.

The taxonomy so far: custom tools run YOUR code; built-in tools run GOOGLE's
code. MCP tools run ANYONE's code: the Model Context Protocol is an open
standard for exposing tools over a connection, and thousands of servers exist
(filesystems, databases, Slack, GitHub, …) that any MCP client — ADK, Claude,
your IDE — can plug into.

Below, `McpToolset` launches the reference *filesystem server* (a Node package,
via npx) as a subprocess, asks it what tools it offers, and hands them to the
agent. We never wrote read_text_file or list_directory — we only pointed at
the server. Day 2's lesson comes full circle: because a tool's schema IS its
interface, tools written by total strangers compose with your agent.

Two things worth stealing from this file:

- `tool_filter`: the server also offers write_file, edit_file, move_file…
  We take the read-only subset. Never grant a stranger's server more than the
  job needs — a tool list is a permission list.
- The tools are GENERIC (list, read, search-by-name). Ask this librarian a
  Playfield question and watch it rummage through files by name — capability
  without understanding. That's why the analyst keeps its own `search_docs`:
  MCP gives you reach; retrieval quality is still your job.

Requires Node (`npx`) — the first launch downloads the server package.
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "data" / "docs"
load_dotenv(REPO_ROOT / ".env", override=True)

docs_folder_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(DOCS_DIR),
            ],
        ),
        timeout=30,  # first run downloads the package; give npx some room
    ),
    # Read-only subset — the server also offers write/edit/move tools.
    tool_filter=["list_directory", "read_text_file", "search_files"],
)

root_agent = LlmAgent(
    model="gemini-3.5-flash-lite",
    name="docs_librarian",
    description="Browses the Playfield docs folder via an MCP filesystem server.",
    instruction=(
        f"You are a librarian for the Playfield game documents in {DOCS_DIR} "
        "(store pages and patch notes, one file set per game id, like "
        "'g07-store-page.md'). Use your filesystem tools to list, find, and "
        "read files before answering — pass paths inside that folder. Always "
        "say which file(s) you read. If the folder doesn't contain the "
        "answer, say so."
    ),
    tools=[docs_folder_tools],
)
