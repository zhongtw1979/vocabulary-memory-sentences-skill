import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lint_sentence_risks import lint_records  # noqa: E402


def sentence(english: str, chinese: str = "合成示例。") -> dict:
    return {
        "sentence_id": "S001",
        "scene": "Synthetic",
        "english": english,
        "chinese": chinese,
        "targets": [{"entry_id": "E001", "surface": "test"}],
    }


def inventory(status: str = "ok") -> list[dict[str, str]]:
    return [
        {
            "entry_id": "E001",
            "entry": "test",
            "required_pos": "verb",
            "required_sense_zh": "检测",
            "metadata_status": status,
        }
    ]


def test_flags_absolute_scientific_claim():
    result = lint_records(
        [sentence("This test can identify every molecule in the sample accurately.")],
        inventory(),
    )

    codes = {flag["code"] for flag in result["flags"]}
    assert {"ABSOLUTE_QUANTIFIER", "SCIENTIFIC_CAPABILITY"} <= codes


def test_flags_ambiguous_actor_control():
    result = lint_records(
        [sentence("The producer chose actors to produce the independent film carefully.")],
        inventory(),
    )

    assert "AMBIGUOUS_ACTOR_CONTROL" in {flag["code"] for flag in result["flags"]}


def test_flags_translation_relation_for_manual_alignment():
    result = lint_records(
        [sentence("The dolphin tossed the ball through the hoop during practice.")],
        inventory(),
    )

    assert "TRANSLATION_RELATION" in {flag["code"] for flag in result["flags"]}


def test_flags_inventory_metadata_conflict():
    result = lint_records([sentence("Students test the water carefully before class today.")], inventory("conflict"))

    assert "METADATA_CONFLICT" in {flag["code"] for flag in result["flags"]}


def test_ordinary_sentence_has_no_risk_flags():
    result = lint_records(
        [sentence("Students test the water carefully in science class this morning.")],
        inventory(),
    )

    assert result["flags"] == []
    assert result["flag_count"] == 0


def test_flags_request_review_without_automatic_error_verdict():
    result = lint_records(
        [sentence("This test can identify every molecule in the sample accurately.")],
        inventory(),
    )

    assert result["flags"]
    assert all(flag["needs_review"] is True for flag in result["flags"])
    assert all("verdict" not in flag for flag in result["flags"])


def test_cli_writes_machine_readable_risk_json(tmp_path):
    output = tmp_path / "risk.json"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "lint_sentence_risks.py"),
            "--inventory",
            str(ROOT / "examples" / "sample-inventory.csv"),
            "--sentences",
            str(ROOT / "examples" / "sample-sentences.json"),
            "--json-output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["flag_count"] == 2
    assert all(flag["needs_review"] is True for flag in payload["flags"])
