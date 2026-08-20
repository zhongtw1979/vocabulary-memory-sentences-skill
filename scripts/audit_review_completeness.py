#!/usr/bin/env python3
"""Verify that independent final reviews cover the current sentence artifact."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from audit_sentence_coverage import read_sentences
from build_blind_review_packet import artifact_sha256


REQUIRED_FOCUSES = {"language", "meaning_fact"}
LANGUAGE_CHECKS = {
    "grammar_ok",
    "collocation_ok",
    "idiomatic_ok",
    "actor_action_ok",
    "learner_model_ok",
}
MEANING_CHECKS = {"translation_logic_ok", "fact_scope_ok"}
TARGET_CHECKS = {"pos_ok", "sense_ok", "surface_ok", "translation_ok"}
BLOCKING_SEVERITIES = {"P0", "P1", "P2"}


def load_review(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Review must be a JSON object: {path}")
    return payload


def audit_reviews(
    sentences_path: str | Path,
    review_paths: Sequence[str | Path],
) -> dict[str, Any]:
    sentences = read_sentences(sentences_path)
    expected_checksum = artifact_sha256(sentences)
    expected_sentence_ids = {str(item.get("sentence_id", "")) for item in sentences}
    targets_by_sentence = {
        str(item.get("sentence_id", "")): {
            str(target.get("entry_id", "")) for target in item.get("targets", [])
        }
        for item in sentences
    }
    reviews = [load_review(path) for path in review_paths]
    focuses = [str(review.get("focus", "")) for review in reviews]
    focus_counts = Counter(focuses)

    checks = {
        "missing_required_focus": len(REQUIRED_FOCUSES - set(focuses)),
        "duplicate_focus": sum(count - 1 for count in focus_counts.values() if count > 1),
        "unknown_focus": len(set(focuses) - REQUIRED_FOCUSES),
        "stale_artifact_checksum": 0,
        "missing_completion_time": 0,
        "incomplete_sentence_coverage": 0,
        "duplicate_sentence_reviews": 0,
        "failed_required_checks": 0,
        "incomplete_target_checks": 0,
        "unresolved_blocking_issues": 0,
        "unresolved_risk_adjudications": 0,
        "non_pass_verdicts": 0,
    }
    details: dict[str, list[str]] = {name: [] for name in checks}

    for review in reviews:
        focus = str(review.get("focus", ""))
        review_id = str(review.get("review_id", focus or "unknown"))
        if review.get("artifact_sha256") != expected_checksum:
            checks["stale_artifact_checksum"] += 1
            details["stale_artifact_checksum"].append(review_id)
        if not str(review.get("completed_at", "")).strip():
            checks["missing_completion_time"] += 1
            details["missing_completion_time"].append(review_id)

        reviewed = review.get("sentences", [])
        reviewed_ids = [str(item.get("sentence_id", "")) for item in reviewed]
        reviewed_set = set(reviewed_ids)
        coverage_delta = expected_sentence_ids.symmetric_difference(reviewed_set)
        checks["incomplete_sentence_coverage"] += len(coverage_delta)
        details["incomplete_sentence_coverage"].extend(
            f"{review_id}:{sentence_id}" for sentence_id in sorted(coverage_delta)
        )
        duplicates = sum(count - 1 for count in Counter(reviewed_ids).values() if count > 1)
        checks["duplicate_sentence_reviews"] += duplicates

        required_checks = LANGUAGE_CHECKS if focus == "language" else MEANING_CHECKS
        for sentence_review in reviewed:
            sentence_id = str(sentence_review.get("sentence_id", ""))
            if str(sentence_review.get("verdict", "")).upper() != "PASS":
                checks["non_pass_verdicts"] += 1
                details["non_pass_verdicts"].append(f"{review_id}:{sentence_id}")

            sentence_checks = sentence_review.get("checks", {})
            for check_name in required_checks:
                if sentence_checks.get(check_name) is not True:
                    checks["failed_required_checks"] += 1
                    details["failed_required_checks"].append(
                        f"{review_id}:{sentence_id}:{check_name}"
                    )

            if focus == "meaning_fact":
                target_checks = sentence_review.get("target_checks", [])
                checked_ids = {
                    str(target.get("entry_id", "")) for target in target_checks
                }
                expected_targets = targets_by_sentence.get(sentence_id, set())
                target_delta = expected_targets.symmetric_difference(checked_ids)
                checks["incomplete_target_checks"] += len(target_delta)
                details["incomplete_target_checks"].extend(
                    f"{review_id}:{sentence_id}:{entry_id}"
                    for entry_id in sorted(target_delta)
                )
                for target in target_checks:
                    entry_id = str(target.get("entry_id", ""))
                    for check_name in TARGET_CHECKS:
                        if target.get(check_name) is not True:
                            checks["failed_required_checks"] += 1
                            details["failed_required_checks"].append(
                                f"{review_id}:{sentence_id}:{entry_id}:{check_name}"
                            )

            for issue in sentence_review.get("issues", []):
                severity = str(issue.get("severity", "")).upper()
                status = str(issue.get("status", "")).casefold()
                if severity in BLOCKING_SEVERITIES and status != "resolved":
                    checks["unresolved_blocking_issues"] += 1
                    details["unresolved_blocking_issues"].append(
                        f"{review_id}:{sentence_id}:{severity}"
                    )

        for adjudication in review.get("risk_adjudications", []):
            if str(adjudication.get("status", "")).casefold() != "resolved":
                checks["unresolved_risk_adjudications"] += 1
                details["unresolved_risk_adjudications"].append(
                    f'{review_id}:{adjudication.get("sentence_id", "?")}:{adjudication.get("code", "?")}'
                )

    failures = sum(checks.values())
    return {
        "result": "PASS" if failures == 0 else "FAIL",
        "failures": failures,
        "artifact_sha256": expected_checksum,
        "sentence_count": len(sentences),
        "review_count": len(reviews),
        "focuses": sorted(focuses),
        "checks": checks,
        "details": details,
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Review Completeness Audit",
        "",
        f'- Status: {result["result"]}',
        f'- Sentences: {result["sentence_count"]}',
        f'- Reviews: {result["review_count"]}',
        f'- Artifact SHA-256: `{result["artifact_sha256"]}`',
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
    parser.add_argument("--sentences", required=True, type=Path)
    parser.add_argument("--reviews", required=True, nargs="+", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = audit_reviews(args.sentences, args.reviews)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
