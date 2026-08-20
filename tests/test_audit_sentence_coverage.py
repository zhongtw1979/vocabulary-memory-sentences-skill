import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_sentence_coverage import audit  # noqa: E402


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


def write_fixture(
    tmp_path: Path,
    *,
    english: str = "Bright students study useful words together every morning at school.",
    targets: list[dict[str, str]] | None = None,
    metadata_status: str = "ok",
) -> tuple[Path, Path]:
    inventory_path = tmp_path / "inventory.csv"
    sentences_path = tmp_path / "sentences.json"
    rows = [
        {
            "entry_id": "E001",
            "entry": "bright",
            "meaning": "明亮的",
            "entry_type": "adjective",
            "required_pos": "adjective",
            "required_sense_zh": "明亮的",
            "allowed_surfaces": "bright|Bright",
            "metadata_status": metadata_status,
            "source_file": "synthetic.csv",
            "source_page": "1",
            "book": "",
            "unit": "1",
            "decision": "retain",
            "sentence_id": "S001",
        },
        {
            "entry_id": "E002",
            "entry": "student",
            "meaning": "学生",
            "entry_type": "noun",
            "required_pos": "noun",
            "required_sense_zh": "学生",
            "allowed_surfaces": "student|students",
            "metadata_status": "ok",
            "source_file": "synthetic.csv",
            "source_page": "1",
            "book": "",
            "unit": "1",
            "decision": "retain",
            "sentence_id": "S001",
        },
        {
            "entry_id": "E003",
            "entry": "useful",
            "meaning": "有用的",
            "entry_type": "adjective",
            "required_pos": "adjective",
            "required_sense_zh": "有用的",
            "allowed_surfaces": "useful",
            "metadata_status": "ok",
            "source_file": "synthetic.csv",
            "source_page": "1",
            "book": "",
            "unit": "1",
            "decision": "retain",
            "sentence_id": "S001",
        },
    ]
    with inventory_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    payload = [
        {
            "sentence_id": "S001",
            "scene": "School",
            "english": english,
            "chinese": "聪明的学生每天早晨在学校一起学习有用的单词。",
            "targets": targets
            or [
                {"entry_id": "E001", "surface": "Bright"},
                {"entry_id": "E002", "surface": "students"},
                {"entry_id": "E003", "surface": "useful"},
            ],
        }
    ]
    sentences_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return inventory_path, sentences_path


def test_complete_dataset_passes(tmp_path):
    inventory, sentences = write_fixture(tmp_path)

    result = audit(inventory, sentences)

    assert result["result"] == "PASS"
    assert result["failures"] == 0


def test_metadata_conflict_blocks_generation(tmp_path):
    inventory, sentences = write_fixture(tmp_path, metadata_status="conflict")

    result = audit(inventory, sentences)

    assert result["result"] == "FAIL"
    assert result["checks"]["inventory_metadata_not_ok"] == 1


def test_missing_and_duplicate_assignments_fail(tmp_path):
    inventory, sentences = write_fixture(
        tmp_path,
        targets=[
            {"entry_id": "E001", "surface": "Bright"},
            {"entry_id": "E001", "surface": "students"},
            {"entry_id": "E002", "surface": "useful"},
        ],
    )

    result = audit(inventory, sentences)

    assert result["checks"]["unassigned_entries"] == 1
    assert result["checks"]["duplicate_assignments"] == 1


def test_surface_must_be_a_distinct_token_not_a_substring(tmp_path):
    inventory, sentences = write_fixture(
        tmp_path,
        english="Young students explore brightwork together every morning at school today.",
        targets=[
            {"entry_id": "E001", "surface": "bright"},
            {"entry_id": "E002", "surface": "students"},
            {"entry_id": "E003", "surface": "useful"},
        ],
    )

    result = audit(inventory, sentences)

    assert result["checks"]["target_surface_missing"] == 2


def test_surface_must_be_authorized_by_inventory(tmp_path):
    inventory, sentences = write_fixture(
        tmp_path,
        targets=[
            {"entry_id": "E001", "surface": "Bright"},
            {"entry_id": "E002", "surface": "students"},
            {"entry_id": "E003", "surface": "usefully"},
        ],
        english="Bright students study words usefully together every morning at school.",
    )

    result = audit(inventory, sentences)

    assert result["checks"]["target_surface_not_allowed"] == 1


def test_primary_target_surface_must_appear_exactly_once(tmp_path):
    inventory, sentences = write_fixture(
        tmp_path,
        english="Bright bright students study useful words together every morning at school.",
    )

    result = audit(inventory, sentences)

    assert result["checks"]["target_surface_occurrence_not_one"] == 1


def test_sentence_mapping_and_continuity_are_checked(tmp_path):
    inventory, sentences = write_fixture(tmp_path)
    payload = json.loads(sentences.read_text(encoding="utf-8"))
    payload[0]["sentence_id"] = "S002"
    sentences.write_text(json.dumps(payload), encoding="utf-8")

    result = audit(inventory, sentences)

    assert result["checks"]["sentence_ids_not_continuous"] == 1
    assert result["checks"]["inventory_sentence_mapping_mismatch"] == 3


def test_word_and_target_bounds_are_checked(tmp_path):
    inventory, sentences = write_fixture(
        tmp_path,
        english="Bright students study useful words.",
        targets=[
            {"entry_id": "E001", "surface": "Bright"},
            {"entry_id": "E002", "surface": "students"},
        ],
    )

    result = audit(inventory, sentences)

    assert result["checks"]["word_count_out_of_range"] == 1
    assert result["checks"]["target_count_out_of_range"] == 1
