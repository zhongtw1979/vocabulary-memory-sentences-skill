#!/usr/bin/env python3
"""Audit vocabulary inventory coverage and bilingual sentence constraints."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


WORD_PATTERN = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:\.\d+)?")
REQUIRED_INVENTORY_COLUMNS = {
    "entry_id",
    "entry",
    "required_pos",
    "required_sense_zh",
    "allowed_surfaces",
    "metadata_status",
    "decision",
    "sentence_id",
}


def word_count(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def surface_occurrences(text: str, surface: str) -> int:
    if not surface:
        return 0
    pattern = re.compile(
        rf"(?<![A-Za-z0-9]){re.escape(surface)}(?![A-Za-z0-9])",
        re.IGNORECASE,
    )
    return len(pattern.findall(text))


def read_inventory(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_INVENTORY_COLUMNS - fieldnames)
        if missing:
            raise ValueError("Inventory is missing required columns: " + ", ".join(missing))
        rows = list(reader)
    if not rows:
        raise ValueError("Inventory is empty")
    return rows


def read_sentences(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("Sentence JSON must be a non-empty list")
    return payload


def retained_rows(inventory: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in inventory
        if row.get("decision", "retain").strip().casefold() in {"", "retain", "keep"}
    ]


def allowed_surfaces(row: dict[str, str]) -> set[str]:
    values = [row.get("entry", "")]
    values.extend(row.get("allowed_surfaces", "").split("|"))
    return {value.strip().casefold() for value in values if value.strip()}


def audit(
    inventory_path: str | Path,
    sentences_path: str | Path,
    *,
    min_words: int = 9,
    max_words: int = 12,
    min_targets: int = 3,
    max_targets: int = 4,
    expected_pages: set[str] | None = None,
) -> dict[str, Any]:
    inventory = read_inventory(inventory_path)
    retained = retained_rows(inventory)
    sentences = read_sentences(sentences_path)

    all_ids = [row["entry_id"].strip() for row in inventory]
    retained_by_id = {row["entry_id"].strip(): row for row in retained}
    retained_ids = set(retained_by_id)
    assigned = [
        str(target.get("entry_id", "")).strip()
        for sentence in sentences
        for target in sentence.get("targets", [])
    ]
    assignment_counts = Counter(assigned)
    assigned_set = set(assigned)
    sentence_ids = [str(sentence.get("sentence_id", "")) for sentence in sentences]
    expected_sentence_ids = [f"S{index:03d}" for index in range(1, len(sentences) + 1)]

    missing_surfaces: list[str] = []
    occurrence_errors: list[str] = []
    unauthorized_surfaces: list[str] = []
    mapping_errors: list[str] = []

    for sentence in sentences:
        sentence_id = str(sentence.get("sentence_id", ""))
        english = str(sentence.get("english", ""))
        for target in sentence.get("targets", []):
            entry_id = str(target.get("entry_id", "")).strip()
            surface = str(target.get("surface", "")).strip()
            occurrences = surface_occurrences(english, surface)
            label = f"{sentence_id or '?'}:{entry_id or '?'}"
            if occurrences == 0:
                missing_surfaces.append(label)
            if occurrences != 1:
                occurrence_errors.append(label)
            row = retained_by_id.get(entry_id)
            if row is not None and surface.casefold() not in allowed_surfaces(row):
                unauthorized_surfaces.append(label)
            if row is not None and row.get("sentence_id", "").strip() != sentence_id:
                mapping_errors.append(label)

    metadata_not_ok = [
        row["entry_id"].strip()
        for row in retained
        if row.get("metadata_status", "").strip().casefold() != "ok"
    ]

    checks: dict[str, int] = {
        "duplicate_inventory_ids": len(all_ids) - len(set(all_ids)),
        "inventory_metadata_not_ok": len(metadata_not_ok),
        "unassigned_entries": len(retained_ids - assigned_set),
        "duplicate_assignments": sum(
            count - 1 for count in assignment_counts.values() if count > 1
        ),
        "unknown_entry_ids": len(assigned_set - retained_ids),
        "sentence_ids_not_continuous": int(sentence_ids != expected_sentence_ids),
        "word_count_out_of_range": sum(
            not min_words <= word_count(str(sentence.get("english", ""))) <= max_words
            for sentence in sentences
        ),
        "target_count_out_of_range": sum(
            not min_targets <= len(sentence.get("targets", [])) <= max_targets
            for sentence in sentences
        ),
        "target_surface_missing": len(missing_surfaces),
        "target_surface_occurrence_not_one": len(occurrence_errors),
        "target_surface_not_allowed": len(unauthorized_surfaces),
        "blank_english": sum(not str(sentence.get("english", "")).strip() for sentence in sentences),
        "blank_chinese": sum(not str(sentence.get("chinese", "")).strip() for sentence in sentences),
        "inventory_sentence_mapping_mismatch": len(mapping_errors),
    }

    if expected_pages is not None:
        actual_pages = {
            row.get("source_page", "").strip()
            for row in retained
            if row.get("source_page", "").strip()
        }
        checks["source_page_set_mismatch"] = int(actual_pages != expected_pages)

    details = {
        "metadata_not_ok": sorted(metadata_not_ok),
        "unassigned_entries": sorted(retained_ids - assigned_set),
        "duplicate_assignments": sorted(
            entry_id for entry_id, count in assignment_counts.items() if count > 1
        ),
        "unknown_entry_ids": sorted(assigned_set - retained_ids),
        "missing_surfaces": sorted(missing_surfaces),
        "occurrence_errors": sorted(occurrence_errors),
        "unauthorized_surfaces": sorted(unauthorized_surfaces),
        "mapping_errors": sorted(mapping_errors),
    }
    failures = sum(checks.values())
    return {
        "result": "PASS" if failures == 0 else "FAIL",
        "failures": failures,
        "inventory_count": len(retained),
        "sentence_count": len(sentences),
        "assigned_count": len(assigned),
        "checks": checks,
        "details": details,
        "word_count_distribution": dict(
            sorted(Counter(word_count(str(item.get("english", ""))) for item in sentences).items())
        ),
        "target_count_distribution": dict(
            sorted(Counter(len(item.get("targets", [])) for item in sentences).items())
        ),
    }


def render_report(result: dict[str, Any], scope_note: str) -> str:
    lines = [
        "# Vocabulary Sentence Coverage Audit",
        "",
        "## Result",
        "",
        f'- Status: {result["result"]}',
        f'- Inventory entries: {result["inventory_count"]}',
        f'- Sentences: {result["sentence_count"]}',
        f'- Assigned targets: {result["assigned_count"]}',
        f"- Scope: {scope_note}",
        "",
        "## Checks",
        "",
        "| Check | Exceptions |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {value} |" for name, value in result["checks"].items())
    lines.extend(["", "## Details", ""])
    populated = False
    for name, values in result["details"].items():
        if values:
            populated = True
            lines.append(f"- {name}: {', '.join(values)}")
    if not populated:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--sentences", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--min-words", type=int, default=9)
    parser.add_argument("--max-words", type=int, default=12)
    parser.add_argument("--min-targets", type=int, default=3)
    parser.add_argument("--max-targets", type=int, default=4)
    parser.add_argument("--expected-pages", help="Comma-separated physical source pages")
    parser.add_argument(
        "--scope-note",
        default="Visible source entries only; missing pages are not filled without authorization.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    expected_pages = set(filter(None, (args.expected_pages or "").split(","))) or None
    result = audit(
        args.inventory,
        args.sentences,
        min_words=args.min_words,
        max_words=args.max_words,
        min_targets=args.min_targets,
        max_targets=args.max_targets,
        expected_pages=expected_pages,
    )
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(result, args.scope_note), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
