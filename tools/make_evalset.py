"""Generate day5/evals/analyst_smoke.evalset.json using ADK's own eval models.

Cases come from instructor/dataset-ground-truth.md. Regenerate after editing:

    .venv/bin/python tools/make_evalset.py
"""

from pathlib import Path

from google.adk.evaluation.eval_case import EvalCase, IntermediateData, Invocation
from google.adk.evaluation.eval_set import EvalSet
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "day5" / "evals" / "analyst_smoke.evalset.json"


def text(role: str, s: str) -> types.Content:
    return types.Content(role=role, parts=[types.Part(text=s)])


def case(eval_id, question, reference, tool_uses) -> EvalCase:
    return EvalCase(
        eval_id=eval_id,
        conversation=[
            Invocation(
                invocation_id=f"{eval_id}-inv1",
                user_content=text("user", question),
                final_response=text("model", reference),
                intermediate_data=IntermediateData(
                    tool_uses=[types.FunctionCall(name=n, args=a) for n, a in tool_uses]
                ),
            )
        ],
    )


CASES = [
    case(
        "price_and_developer",
        "How much does Neon Drift Racers cost, and who developed it?",
        "Neon Drift Racers costs €19.99 and was developed by Velocity Forge.",
        [("list_games", {}), ("get_game_details", {"game_id": "g01"})],
    ),
    case(
        "worst_netcode",
        "Which game do players complain about most when it comes to disconnects and netcode problems?",
        "Star Salvage Crew — players report desync, rubber-banding, disconnects and "
        "failed host migrations in its multiplayer.",
        [("search_reviews", {"query": "disconnects desync netcode problems", "top_k": 5})],
    ),
    case(
        "save_bug_fixed",
        "Players say Silent Depths corrupts save files — did the developers ever fix that, and when?",
        "Yes. The save-corruption bug in Silent Depths was fixed in patch v1.2, released "
        "January 2026, according to the official patch notes (g12-patch-notes.md). "
        "Reviews after that patch confirm saves work.",
        [
            ("search_reviews", {"query": "Silent Depths save corruption lost progress", "top_k": 5}),
            ("search_docs", {"query": "Silent Depths save corruption fix patch", "top_k": 3}),
        ],
    ),
    case(
        "refund_guardrail",
        "I want a refund for Glacier Punk, it's broken.",
        "I can't help with refunds or payments — that's handled by a human on the "
        "Playfield support team (support@playfield.example). I'm happy to help with "
        "anything about the games or their reviews!",
        [],  # the guardrail must answer BEFORE any model/tool activity
    ),
]


def main() -> None:
    eval_set = EvalSet(
        eval_set_id="analyst_smoke",
        name="Playfield analyst smoke tests",
        description=(
            "Four ground-truth checks for the Day-5 analyst: a catalog lookup, a "
            "review-sentiment question, a cross-corpus timeline question, and the "
            "refund guardrail."
        ),
        eval_cases=CASES,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(eval_set.model_dump_json(indent=2, exclude_none=True), encoding="utf-8")
    print(f"wrote {len(CASES)} cases → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
