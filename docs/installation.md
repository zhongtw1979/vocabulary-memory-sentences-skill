# Installation / 安装说明

## Requirements

- Codex with local skills support;
- Python 3.10 or later;
- Git for repository installation;
- Word-compatible software only when opening generated DOCX files.

## Install the Codex skill

Clone directly into the Codex skills directory:

```bash
git clone https://github.com/zhongtw1979/vocabulary-memory-sentences-skill.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/building-vocabulary-memory-sentences"
cd "${CODEX_HOME:-$HOME/.codex}/skills/building-vocabulary-memory-sentences"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

Restart Codex if the new skill is not immediately discoverable. Invoke it explicitly as `$building-vocabulary-memory-sentences`, or make a matching natural-language request with a vocabulary file.

## Install for local script use only

Clone anywhere, create a virtual environment, and install the project:

```bash
git clone https://github.com/zhongtw1979/vocabulary-memory-sentences-skill.git
cd vocabulary-memory-sentences-skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python scripts/run_example.py --output-dir build/example
```

## Update

```bash
git pull --ff-only
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

Inspect release notes in [CHANGELOG.md](../CHANGELOG.md) before updating production workflows.

## Uninstall

Delete only the cloned skill directory after confirming that it contains no user-created inventory, review, or output files. Project examples and build outputs are separate from the Codex installation.

---

## 中文说明

环境要求：Codex支持本地Skill、Python 3.10以上版本、Git；只有打开生成的DOCX时才需要Word或兼容软件。

推荐把仓库直接克隆到Codex技能目录：

```bash
git clone https://github.com/zhongtw1979/vocabulary-memory-sentences-skill.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/building-vocabulary-memory-sentences"
cd "${CODEX_HOME:-$HOME/.codex}/skills/building-vocabulary-memory-sentences"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

如果Codex没有立即显示新Skill，请重启Codex。可以显式使用 `$building-vocabulary-memory-sentences`，也可以直接提出“把这份词表排重并重组为中英短句”等匹配请求。

更新时使用 `git pull --ff-only`，重新安装依赖并执行完整测试。卸载前应确认技能目录内没有自己创建的词库、复核记录和学习材料。
