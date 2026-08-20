import re
import sys
import zipfile
from pathlib import Path

import pytest
from docx import Document


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_bilingual_docx import build_document, find_target_ranges  # noqa: E402


def sample_data() -> list[dict]:
    return [
        {
            "sentence_id": "S001",
            "scene": "School",
            "english": "Bright students study useful words together every morning at school.",
            "chinese": "聪明的学生每天早晨在学校一起学习有用的单词。",
            "targets": [
                {"entry_id": "E001", "surface": "Bright"},
                {"entry_id": "E002", "surface": "students"},
                {"entry_id": "E003", "surface": "useful"},
            ],
        }
    ]


def extracted_text(path: Path) -> str:
    return "\n".join(paragraph.text for paragraph in Document(path).paragraphs)


def test_builds_bilingual_document_without_internal_ids(tmp_path):
    output = tmp_path / "study.docx"

    result = build_document(
        sample_data(),
        output,
        title="Vocabulary Memory Sentences",
        version="v0.1.0",
        scope_note="Synthetic example only.",
    )

    assert result["sentences"] == 1
    assert result["targets"] == 3
    assert result["unresolved"] == 0
    text = extracted_text(output)
    assert "1. Bright students study useful words" in text
    assert "中文：聪明的学生" in text
    assert "S001" not in text
    assert not re.search(r"E\d{3}", text)
    with zipfile.ZipFile(output) as archive:
        xml = archive.read("word/document.xml").decode("utf-8")
    assert len(re.findall(r"<w:u[ />]", xml)) >= 3


def test_overlapping_targets_use_distinct_occurrences():
    ranges, unresolved = find_target_ranges(
        "The chef served lamb beside fresh lamb kebabs for dinner.",
        ["lamb", "lamb kebabs", "chef"],
    )

    assert unresolved == []
    assert len(ranges) == 3


def test_missing_target_surface_prevents_document_creation(tmp_path):
    data = sample_data()
    data[0]["targets"][0]["surface"] = "absent"

    with pytest.raises(ValueError, match="Unresolved target surfaces"):
        build_document(data, tmp_path / "bad.docx", "Study", "v0.1.0", "Synthetic")
