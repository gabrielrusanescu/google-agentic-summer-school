"""Day 4 · Multi-agent systems — scaffold.

You build the report pipeline in stages. Part 1 already works: run it first,
then upgrade it part by part.

    Part 1 (works now):  researcher ──▶ writer
    Part 2 (you build):  [reviews researcher ∥ docs researcher] ──▶ writer
    Part 3 (you build):  … ──▶ writer with the full report template
    Part 4 (you build):  … ──▶ writer ──▶ (critic ⇄ reviser) loop
"""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from pydantic import BaseModel, Field

from . import tools

load_dotenv(tools.repo_root() / ".env", override=True)

MODEL = "gemini-3.5-flash-lite"


# --------------------------------------------------------------------------
# Part 1 — a two-stage pipeline
# --------------------------------------------------------------------------

reviews_researcher = LlmAgent(
    name="reviews_researcher",
    model=MODEL,
    description="Researches player sentiment in the review corpus.",
    instruction="""You are a research specialist for Playfield. The user message
contains a research question about one or more Playfield games.

Call search_reviews 2 to 4 times with DIFFERENT, specific queries that cover the
question from several angles (e.g. technical problems, value for money, praise,
comparisons). If you need a game's catalog stats, call get_game_details.

Then output your findings as concise bullet points:
- one bullet per distinct theme you found,
- each bullet ends with the supporting review ids, e.g. (r042, r187),
- note whether the reviewers recommend the game or not.

Facts only. No recommendations, no report — that is another agent's job.""",
    tools=[tools.search_reviews, tools.get_game_details, tools.list_games],
    output_key="reviews_findings",
)


# --------------------------------------------------------------------------
# Part 2 — parallel researchers
# --------------------------------------------------------------------------

docs_researcher = LlmAgent(
    name="docs_researcher",
    model=MODEL,
    description="Researches player sentiment in the official docs corpus.",
    instruction="""You are a research specialist for Playfield. The user message
contains a research question about one or more Playfield games.

Call search_docs 2 to 4 times with DIFFERENT, specific queries that cover the
question from several angles (e.g. technical problems, value for money, praise,
comparisons). If you need a game's catalog stats, call get_game_details.

Then output your findings as concise bullet points:
- one bullet per distinct theme you found,
- each bullet ends with the supporting doc ids, e.g. (d042, d187),
- note whether the reviewers recommend the game or not.

Facts only. No recommendations, no report — that is another agent's job.""",
    tools=[tools.search_docs, tools.get_game_details, tools.list_games],
    output_key="docs_findings",
)


catalog_researcher = LlmAgent(
    name="catalog_researcher",
    model=MODEL,
    description="Pulls prices and ratings context.",
    instruction="""You are a research specialist for Playfield. The user message
contains a research question about one or more Playfield games.

Call the tools - list_games or get_game_details 2 to 4 times with DIFFERENT, specific queries that cover the
question from several angles (e.g. technical problems, value for money, praise,
comparisons). If you need a game's catalog stats, call get_game_details.

Then output your findings as concise bullet points:
- one bullet per distinct theme you found,
- each bullet ends with the supporting doc ids, e.g. (d042, d187),
- note whether the reviewers recommend the game or not.

Facts only. No recommendations, no report — that is another agent's job.""",
    tools=[tools.get_game_details, tools.list_games],
    output_key="catalog_findings",
)


research_team = ParallelAgent(
    name="research_team",
    description="Researches reviews, official docs, and catalog context in parallel.",
    sub_agents=[
        reviews_researcher,
        docs_researcher,
        catalog_researcher,
    ],
)


# --------------------------------------------------------------------------
# Part 3 — writer
# --------------------------------------------------------------------------

writer = LlmAgent(
    name="report_writer",
    model=MODEL,
    description="Writes the final report from the researchers' findings.",
    instruction="""
## Question         restate it in one sentence
## What players say  themes with review-id citations
## What the docs say  facts with file names and dates
## Timeline check    complaints vs fixes: is the criticism still current?
## Verdict           actionable recommendation + confidence (high/medium/low)

{reviews_findings}

{docs_findings}

{catalog_findings}

Under 400 words, evidence only (Do not invent evidence: say it explicitly).""",
    output_key="report_draft",
)


# --------------------------------------------------------------------------
# Part 4 — quality loop (Critic & Reviser)
# --------------------------------------------------------------------------


class Critique(BaseModel):
    citations_present: bool = Field(
        description="True if citations (review IDs etc.) are present on claims."
    )
    all_sections_present: bool = Field(
        description="True if all 5 required sections are present."
    )
    actionable_verdict: bool = Field(
        description="True if verdict is actionable with an explicit confidence level."
    )
    under_400_words: bool = Field(
        description="True if report is concise and under 400 words."
    )
    passed: bool = Field(
        description="True ONLY if all checklist criteria pass."
    )
    fixes: list[str] = Field(
        description="Actionable list of required fixes if passed is False and empty if passed is True."
    )


critic_agent = LlmAgent(
    name="critic_agent",
    model=MODEL,
    description="Judges the draft report against the quality checklist.",
    instruction="""You are a critic specialist for Playfield.

Evaluate the draft report below against this checklist:
- Citations on every claim (e.g. review IDs like r042 or doc files like patch notes)
- All five required sections present
- Actionable verdict with an explicit confidence level (high/medium/low)
- Under 400 words

If all checklist criteria pass (passed=True), call the exit_loop tool.
Otherwise, specify the concrete fixes required in the fixes list.

Draft to critique: {report_draft}

""",
    tools=[tools.exit_loop],
    output_key="critique",
    output_schema=Critique,
    include_contents="none",
)


revise_agent = LlmAgent(
    name="reviser_agent",
    model=MODEL,
    description="Revises the draft report according to critic feedback.",
    instruction="""You are a revising specialist for Playfield.

Apply the required fixes from the critique to improve the report draft.

Current Draft: {report_draft}

Critique Feedback: {critique}

Output the updated, complete draft report preserving all five required sections.""",
    output_key="report_draft",
    include_contents="none",
)


quality = LoopAgent(
    name="quality_loop",
    description="Loops critic and reviser until the draft passes or maximum iterations are reached.",
    sub_agents=[
        critic_agent,
        revise_agent,
    ],
    max_iterations=5,
)


# --------------------------------------------------------------------------
# The complete pipeline
# --------------------------------------------------------------------------

root_agent = SequentialAgent(
    name="report_pipeline",
    description="Researches a question about Playfield games and produces a structured, reviewed report.",
    sub_agents=[
        research_team,
        writer,
        quality,
    ],
)