#!/usr/bin/env python3
"""Run the complete synthetic vocabulary-memory workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_review_completeness import audit_reviews, render_report as render_review_report
from audit_sentence_coverage import (
    audit,
    read_inventory,
    read_sentences,
    render_report as render_coverage_report,
)
from build_bilingual_docx import build_document
from build_blind_review_packet import build_packet
from lint_sentence_risks import lint_records, render_report as render_risk_report


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_example(example_root: str | Path, output_dir: str | Path) -> dict[str, Any]:
    example = Path(example_root)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    inventory_path = example / "sample-inventory.csv"
    sentences_path = example / "sample-sentences.json"
    review_paths = [
        example / "reviews" / "language-review.json",
        example / "reviews" / "meaning-fact-review.json",
    ]

    coverage = audit(inventory_path, sentences_path)
    (output / "coverage-audit.md").write_text(
        render_coverage_report(coverage, "Synthetic example only."),
        encoding="utf-8",
    )
    if coverage["result"] != "PASS":
        raise ValueError("Synthetic coverage audit failed")

    sentences = read_sentences(sentences_path)
    risk = lint_records(sentences, read_inventory(inventory_path))
    (output / "risk-report.md").write_text(render_risk_report(risk), encoding="utf-8")
    risk_json_path = output / "risk-report.json"
    write_json(risk_json_path, risk)

    language_packet = build_packet(
        inventory_path,
        sentences_path,
        focus="language",
        seed=17,
    )
    meaning_packet = build_packet(
        inventory_path,
        sentences_path,
        focus="meaning_fact",
        seed=29,
    )
    write_json(output / "language-review-packet.json", language_packet)
    write_json(output / "meaning-fact-review-packet.json", meaning_packet)

    review = audit_reviews(sentences_path, review_paths, risk_path=risk_json_path)
    (output / "review-completeness.md").write_text(
        render_review_report(review), encoding="utf-8"
    )
    if review["result"] != "PASS":
        raise ValueError("Synthetic review completeness audit failed")

    document = build_document(
        sentences,
        output / "vocabulary-memory-sentences.docx",
        "Vocabulary Memory Sentences",
        "v0.1.0",
        "Synthetic example only.",
    )
    summary = {
        "coverage": coverage["result"],
        "risk_flags": risk["flag_count"],
        "reviews": review["result"],
        "sentences": coverage["sentence_count"],
        "targets": coverage["inventory_count"],
        "docx_unresolved": document["unresolved"],
        "output_dir": str(output),
    }
    write_json(output / "summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_example = Path(__file__).resolve().parents[1] / "examples"
    parser.add_argument("--example-root", type=Path, default=default_example)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(run_example(args.example_root, args.output_dir), ensure_ascii=False))


if __name__ == "__main__":
    main()
