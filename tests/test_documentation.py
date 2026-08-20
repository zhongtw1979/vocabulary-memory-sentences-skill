import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = [
    "README.md",
    "README.zh-CN.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "docs/installation.md",
    "docs/user-guide.md",
    "docs/quality-assurance.md",
    "docs/complete-example.md",
    "docs/troubleshooting.md",
    "docs/cli-reference.md",
]


def public_markdown_files() -> list[Path]:
    files = [ROOT / relative for relative in REQUIRED_DOCS]
    files.extend((ROOT / "references").glob("*.md"))
    return files


def test_required_public_documentation_exists():
    missing = [relative for relative in REQUIRED_DOCS if not (ROOT / relative).exists()]

    assert missing == []


def test_all_local_markdown_links_resolve():
    broken: list[str] = []
    for path in public_markdown_files():
        text = path.read_text(encoding="utf-8")
        for raw_link in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            link = raw_link.split("#", 1)[0]
            if not link or "://" in link or link.startswith("mailto:"):
                continue
            target = (path.parent / link).resolve()
            if not target.exists():
                broken.append(f"{path.relative_to(ROOT)} -> {raw_link}")

    assert broken == []


def test_public_docs_contain_no_private_paths_or_unfinished_markers():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in public_markdown_files())

    assert "/Users/" not in combined
    assert "[PLACEHOLDER]" not in combined
    assert "g" + "hp_" not in combined


def test_both_readmes_link_installation_example_and_license():
    for relative in ("README.md", "README.zh-CN.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "docs/installation.md" in text
        assert "docs/complete-example.md" in text
        assert "LICENSE" in text
        assert "audit_sentence_coverage.py" in text
