from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__", "build", ".worktrees"}
BINARY_SUFFIXES = {".docx", ".png", ".jpg", ".jpeg", ".gif", ".pdf"}
FORBIDDEN_PATH_NAMES = {".DS_Store"}
FORBIDDEN_TEXT = (
    "/Users/" + "zhongtianwei",
    "g" + "hp_",
    "BEGIN OPENSSH" + " PRIVATE KEY",
)


def repository_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts)
    ]


def test_repository_contains_no_cache_or_private_source_files():
    paths = repository_files()

    assert not [path for path in paths if path.name in FORBIDDEN_PATH_NAMES]
    assert not [path for path in paths if path.suffix.casefold() == ".pdf"]


def test_text_files_contain_no_personal_path_or_token_prefix():
    matches: list[str] = []
    for path in repository_files():
        if path.suffix.casefold() in BINARY_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in text:
                matches.append(f"{path.relative_to(ROOT)}:{forbidden}")

    assert matches == []


def test_repository_has_no_unexpected_large_file():
    oversized = [
        str(path.relative_to(ROOT))
        for path in repository_files()
        if path.stat().st_size > 2_000_000
    ]

    assert oversized == []
