# 词表短句重组 Skill

[English](README.md)

这是一个中英双语 Codex Skill，用于把PDF、图片、Word、CSV或电子表格中的词表，转化为可追溯的短句背诵材料和可打印Word。

它覆盖源文件边界确认、词条排重、跨单元场景重组、机械覆盖审计、独立语言复核、词义与事实复核，以及DOCX生成。

## 为什么要做这个项目

“每个词都用上”可以通过程序验证；“句子自然、词义准确、适合学生模仿”需要独立语言判断。本项目把两类质量门分开：

- 自动脚本检查覆盖、映射、词数、目标词数量和复核完整性；
- 盲审任务包支持语法、搭配、词义、翻译、逻辑和事实的独立复核；
- 风险扫描器只提出需要复核的问题，不自动判错；
- 最终句子一旦修改，之前的最终复核立即失效。

## 快速开始

```bash
git clone https://github.com/zhongtw1979/vocabulary-memory-sentences-skill.git
cd vocabulary-memory-sentences-skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python scripts/run_example.py --output-dir build/example
```

示例会在 `build/example` 中生成覆盖报告、风险报告、复核完整性报告、盲审任务包和Word材料。

Codex Skill安装方法见[安装说明](docs/installation.md)，完整处理流程见[使用手册](docs/user-guide.md)。

## 核心命令

```bash
python scripts/audit_sentence_coverage.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --report coverage-audit.md

python scripts/lint_sentence_risks.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --report risk-report.md

python scripts/audit_review_completeness.py \
  --sentences sentences.json \
  --reviews language-review.json meaning-fact-review.json \
  --report review-completeness.md
```

全部参数见[命令行参考](docs/cli-reference.md)。

## 最终质量门

最终输出必须同时满足：

- 当前覆盖审计为 `PASS`；
- 一份绑定当前校验和的独立 `language` 全量复核；
- 一份绑定同一校验和的独立 `meaning_fact` 全量复核；
- 没有未解决的 `P0`、`P1`、`P2`；
- 当前复核完整性审计为 `PASS`；
- Word文件通过结构、文字、数量、中英对应和目标词强调检查。

`CLEAN PASS` 的准确含义是：在规定复核维度下，没有发现未解决的阻断性问题。它不表示不存在其他风格选择。

完整规则见[质量保障说明](docs/quality-assurance.md)。

## 完整示例

仓库内提供了一套原创合成示例，共12个目标词、4个中英短句：

- [示例词库](examples/sample-inventory.csv)
- [示例短句JSON](examples/sample-sentences.json)
- [两份复核记录](examples/reviews/)
- [预期报告和Word](examples/expected-output/)
- [完整操作演示](docs/complete-example.md)

仓库不包含私人PDF、个人词库或真实生产材料。

## 项目边界

当前版本不提供OCR、图形界面或在线审查服务。自动检查也不能单独证明英语表达自然。处理源PDF、电子表格或Word时，Codex可以按需调用相应文件能力。

## 文档目录

- [安装说明](docs/installation.md)
- [使用手册](docs/user-guide.md)
- [质量保障](docs/quality-assurance.md)
- [完整示例](docs/complete-example.md)
- [命令行参考](docs/cli-reference.md)
- [常见问题](docs/troubleshooting.md)
- [数据结构](references/data-schema.md)
- [复核量表](references/review-rubric.md)
- [失败模式案例库](references/failure-library.md)

## 参与贡献

请阅读[贡献指南](CONTRIBUTING.md)、[行为准则](CODE_OF_CONDUCT.md)和[安全政策](SECURITY.md)。

## 开源协议

本项目采用[MIT License](LICENSE)。
