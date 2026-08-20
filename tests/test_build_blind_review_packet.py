import csv
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_blind_review_packet import build_packet  # noqa: E402


FIELDS = [
    "entry_id",
    "entry",
    "meaning",
    "entry_type",
    "required_pos",
    "required_sense_zh",
    "allowed_surfaces",
    "metadata_status",
    "source_file",
    "source_page",
    "book",
    "unit",
    "decision",
    "sentence_id",
]


def write_fixture(tmp_path: Path, status: str = "ok") -> tuple[Path, Path]:
    inventory = tmp_path / "inventory.csv"
    sentences = tmp_path / "sentences.json"
    rows = [
        {
            "entry_id": "E001",
            "entry": "test",
            "meaning": "检测",
            "entry_type": "verb",
            "required_pos": "verb",
            "required_sense_zh": "检测",
            "allowed_surfaces": "test|tests|tested|testing",
            "metadata_status": status,
            "source_file": "synthetic.csv",
            "source_page": "1",
            "book": "",
            "unit": "1",
            "decision": "retain",
            "sentence_id": "S001",
        }
    ]
    with inventory.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    payload = [
        {
            "sentence_id": "S001",
            "scene": "Science class",
            "english": "Students test the water carefully in science class this morning.",
            "chinese": "学生们今天早晨在科学课上认真检测水样。",
            "targets": [{"entry_id": "E001", "surface": "test"}],
            "previous_verdict": "PASS",
            "revision_history": ["hidden"],
        }
    ]
    sentences.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return inventory, sentences


def test_packet_is_reproducible_and_hides_prior_verdicts(tmp_path):
    inventory, sentences = write_fixture(tmp_path)

    first = build_packet(inventory, sentences, focus="language", seed=17)
    second = build_packet(inventory, sentences, focus="language", seed=17)

    assert first == second
    serialized = json.dumps(first, ensure_ascii=False)
    assert "previous_verdict" not in serialized
    assert "revision_history" not in serialized
    assert len(first["artifact_sha256"]) == 64


def test_packet_attaches_authoritative_target_metadata(tmp_path):
    inventory, sentences = write_fixture(tmp_path)

    packet = build_packet(inventory, sentences, focus="meaning_fact", seed=0)
    target = packet["sentences"][0]["targets"][0]

    assert target["entry_id"] == "E001"
    assert target["required_pos"] == "verb"
    assert target["required_sense_zh"] == "检测"
    assert target["allowed_surfaces"] == ["test", "tests", "tested", "testing"]


def test_invalid_focus_is_rejected(tmp_path):
    inventory, sentences = write_fixture(tmp_path)

    with pytest.raises(ValueError, match="focus"):
        build_packet(inventory, sentences, focus="style", seed=0)


def test_metadata_conflict_is_rejected(tmp_path):
    inventory, sentences = write_fixture(tmp_path, status="conflict")

    with pytest.raises(ValueError, match="metadata_status"):
        build_packet(inventory, sentences, focus="language", seed=0)
