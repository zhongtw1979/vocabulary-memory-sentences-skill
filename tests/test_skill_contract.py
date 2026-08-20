import re
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def test_skill_has_discoverable_frontmatter():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)

    assert frontmatter["name"] == "building-vocabulary-memory-sentences"
    assert frontmatter["description"].startswith("Use when ")
    assert "vocabulary" in frontmatter["description"].lower()
    assert len(frontmatter["description"]) < 500


def test_every_local_markdown_link_resolves():
    skill_path = ROOT / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    links = re.findall(r"\[[^]]+\]\(([^)]+)\)", text)
    local_links = [link for link in links if "://" not in link and not link.startswith("#")]

    assert local_links, "SKILL.md must route detailed guidance to local resources"
    for link in local_links:
        assert (ROOT / link).exists(), f"broken local resource link: {link}"


def test_package_metadata_supports_clean_installation():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert config["project"]["requires-python"] == ">=3.10"
    assert "python-docx>=1.1" in config["project"]["dependencies"]
    assert "pytest>=8" in config["project"]["optional-dependencies"]["dev"]
    assert config["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]


def test_agent_interface_has_no_unfinished_values():
    text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert "display_name:" in text
    assert "short_description:" in text
    assert "default_prompt:" in text
    assert "[PLACEHOLDER]" not in text
