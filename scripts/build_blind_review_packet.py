#!/usr/bin/env python3
"""Build a reproducible blind-review packet from current sentence artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from audit_sentence_coverage import read_inventory, read_sentences, retained_rows


FOCUSES = {"language", "meaning_fact"}


def clean_sentence(sentence: dict[str, Any]) -> dict[str, Any]:
    return {
        "sentence_id": str(sentence.get("sentence_id", "")),
        "scene": str(sentence.get("scene", "")),
        "english": str(sentence.get("english", "")),
        "chinese": str(sentence.get("chinese", "")),
        "targets": [
            {
                "entry_id": str(target.get("entry_id", "")),
                "surface": str(target.get("surface", "")),
            }
            for target in sentence.get("targets", [])
        ],
    }


def artifact_sha256(sentences: list[dict[str, Any]]) -> str:
    clean = [clean_sentence(sentence) for sentence in sentences]
    canonical = json.dumps(
        clean,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def split_surfaces(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def build_packet(
    inventory_path: str | Path,
    sentences_path: str | Path,
    *,
    focus: str,
    seed: int = 0,
) -> dict[str, Any]:
    if focus not in FOCUSES:
        raise ValueError(f"focus must be one of: {', '.join(sorted(FOCUSES))}")
    inventory = retained_rows(read_inventory(inventory_path))
    bad_metadata = [
        row.get("entry_id", "?")
        for row in inventory
        if row.get("metadata_status", "").strip().casefold() != "ok"
    ]
    if bad_metadata:
        raise ValueError("metadata_status must be ok for: " + ", ".join(bad_metadata))

    sentences = read_sentences(sentences_path)
    inventory_by_id = {row["entry_id"].strip(): row for row in inventory}
    packet_sentences: list[dict[str, Any]] = []
    for raw_sentence in sentences:
        sentence = clean_sentence(raw_sentence)
        enriched_targets = []
        for target in sentence["targets"]:
            entry_id = target["entry_id"]
            if entry_id not in inventory_by_id:
                raise ValueError(f"unknown target entry_id: {entry_id}")
            row = inventory_by_id[entry_id]
            enriched_targets.append(
                {
                    "entry_id": entry_id,
                    "surface": target["surface"],
                    "entry": row.get("entry", ""),
                    "required_pos": row.get("required_pos", ""),
                    "required_sense_zh": row.get("required_sense_zh", ""),
                    "allowed_surfaces": split_surfaces(row.get("allowed_surfaces", "")),
                }
            )
        sentence["targets"] = enriched_targets
        packet_sentences.append(sentence)

    random.Random(seed).shuffle(packet_sentences)
    return {
        "schema_version": 1,
        "focus": focus,
        "artifact_sha256": artifact_sha256(sentences),
        "seed": seed,
        "instructions": (
            "Review every sentence independently. Do not infer a pass from prior wording. "
            "Record checks, issues, and a PASS, REVISE, REGROUP, or ESCALATE verdict."
        ),
        "sentences": packet_sentences,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--sentences", required=True, type=Path)
    parser.add_argument("--focus", required=True, choices=sorted(FOCUSES))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    packet = build_packet(
        args.inventory,
        args.sentences,
        focus=args.focus,
        seed=args.seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "sentences": len(packet["sentences"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
