"""Merge the generated review shards into data/reviews.csv and validate the result.

Usage: python tools/build_dataset.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SHARDS = DATA / "shards"

REQUIRED_FIELDS = {"game_id", "author", "hours_played", "recommended", "helpful_votes", "date", "review_text"}


def load_shards() -> pd.DataFrame:
    rows = []
    for shard in sorted(SHARDS.glob("reviews_*.jsonl")):
        for lineno, line in enumerate(shard.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                sys.exit(f"{shard.name}:{lineno}: invalid JSON — {e}")
            missing = REQUIRED_FIELDS - row.keys()
            if missing:
                sys.exit(f"{shard.name}:{lineno}: missing fields {missing}")
            rows.append(row)
    if not rows:
        sys.exit(f"No shards found in {SHARDS}")
    return pd.DataFrame(rows)


def validate(reviews: pd.DataFrame, games: pd.DataFrame) -> None:
    problems = []

    unknown = set(reviews["game_id"]) - set(games["game_id"])
    if unknown:
        problems.append(f"unknown game_ids: {unknown}")

    counts = reviews["game_id"].value_counts()
    uneven = counts[counts != 15]
    if not uneven.empty:
        problems.append(f"games without exactly 15 reviews:\n{uneven}")

    dates = pd.to_datetime(reviews["date"], errors="coerce")
    if dates.isna().any():
        bad = reviews.loc[dates.isna(), "date"].tolist()
        problems.append(f"unparseable dates: {bad}")
    else:
        merged = reviews.merge(games, on="game_id")
        merged["date"] = pd.to_datetime(merged["date"])
        early = merged[merged["date"].dt.year < merged["release_year"]]
        if not early.empty:
            problems.append(
                "reviews dated before release:\n"
                + early[["game_id", "date", "release_year"]].to_string()
            )

    if not reviews["hours_played"].between(0.1, 2000).all():
        problems.append("hours_played out of range [0.1, 2000]")
    if not reviews["helpful_votes"].between(0, 1000).all():
        problems.append("helpful_votes out of range [0, 1000]")
    if reviews["review_text"].str.strip().eq("").any():
        problems.append("empty review_text found")

    if problems:
        sys.exit("VALIDATION FAILED:\n" + "\n\n".join(problems))


def main() -> None:
    games = pd.read_csv(DATA / "games.csv")
    reviews = load_shards()
    validate(reviews, games)

    # Deterministic shuffle so the CSV isn't ordered by game, then stable ids.
    reviews = reviews.sample(frac=1, random_state=42).reset_index(drop=True)
    reviews.insert(0, "review_id", [f"r{i:03d}" for i in range(1, len(reviews) + 1)])
    reviews = reviews[
        ["review_id", "game_id", "author", "hours_played", "recommended", "helpful_votes", "date", "review_text"]
    ]

    out = DATA / "reviews.csv"
    reviews.to_csv(out, index=False)

    rec = reviews["recommended"].mean()
    print(f"OK: wrote {len(reviews)} reviews for {reviews['game_id'].nunique()} games to {out}")
    print(f"    {rec:.0%} recommended overall; docs corpus: {len(list((DATA / 'docs').glob('*.md')))} files")


if __name__ == "__main__":
    main()
