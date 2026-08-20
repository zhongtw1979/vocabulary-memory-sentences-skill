#!/usr/bin/env python3
"""Flag sentence patterns that require deliberate language or fact review."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from audit_sentence_coverage import read_inventory, read_sentences


PATTERNS: tuple[tuple[str, re.Pattern[str], str, str], ...] = (
    (
        "ABSOLUTE_QUANTIFIER",
        re.compile(r"\b(?:all|every|always|never|completely|guarantee[sd]?)\b", re.IGNORECASE),
        "P1",
        "Check whether the absolute scope is justified.",
    ),
    (
        "SCIENTIFIC_CAPABILITY",
        re.compile(r"\b(?:identify|detect|diagnose|cure|prove|guarantee|measure)\w*\b", re.IGNORECASE),
        "P1",
        "Check the actor, method, conditions, and claimed scientific or medical capability.",
    ),
    (
        "AMBIGUOUS_ACTOR_CONTROL",
        re.compile(
            r"\b(?:choose|chooses|chose|chosen|select|selects|selected)\s+"
            r"(?:[A-Za-z-]+\s+){0,2}[A-Za-z-]+s\s+to\s+[A-Za-z-]+\b",
            re.IGNORECASE,
        ),
        "P2",
        "Name who performs the infinitive action and rewrite if the structure misleads.",
    ),
    (
        "TRANSLATION_RELATION",
        re.compile(r"\b(?:through|over|across|before|after|during|into|onto|from)\b", re.IGNORECASE),
        "P1",
        "Check that the Chinese preserves path, direction, time, or logical relation.",
    ),
)


def make_flag(
    sentence_id: str,
    code: str,
    severity_hint: str,
    message: str,
) -> dict[str, Any]:
    return {
        "sentence_id": sentence_id,
        "code": code,
        "severity_hint": severity_hint,
        "message": message,
        "needs_review": True,
    }


def lint_records(
    sentences: list[dict[str, Any]],
    inventory: list[dict[str, str]],
) -> dict[str, Any]:
    flags: list[dict[str, Any]] = []
    for row in inventory:
        status = row.get("metadata_status", "").strip().casefold()
        if status != "ok":
            flags.append(
                make_flag(
                    "INVENTORY",
                    "METADATA_CONFLICT",
                    "P1",
                    f'{row.get("entry_id", "?")} has metadata_status={status or "blank"}.',
                )
            )

    for sentence in sentences:
        sentence_id = str(sentence.get("sentence_id", "?"))
        english = str(sentence.get("english", ""))
        for code, pattern, severity, message in PATTERNS:
            if pattern.search(english):
                flags.append(make_flag(sentence_id, code, severity, message))

    counts: dict[str, int] = {}
    for flag in flags:
        counts[flag["code"]] = counts.get(flag["code"], 0) + 1
    return {
        "result": "REVIEW_REQUIRED" if flags else "NO_FLAGS",
        "sentence_count": len(sentences),
        "flag_count": len(flags),
        "counts_by_code": dict(sorted(counts.items())),
        "flags": flags,
        "note": "Flags require adjudication and are not automatic error verdicts.",
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Vocabulary Sentence Risk Report",
        "",
        f'- Result: {result["result"]}',
        f'- Sentences: {result["sentence_count"]}',
        f'- Flags: {result["flag_count"]}',
        "- Interpretation: Flags require adjudication and are not automatic errors.",
        "",
        "| Sentence | Code | Severity hint | Review question |",
        "|---|---|---|---|",
    ]
    if result["flags"]:
        lines.extend(
            f'| {flag["sentence_id"]} | {flag["code"]} | {flag["severity_hint"]} | {flag["message"]} |'
            for flag in result["flags"]
        )
    else:
        lines.append("| — | — | — | No risk pattern was flagged. |")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--sentences", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = lint_records(read_sentences(args.sentences), read_inventory(args.inventory))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
