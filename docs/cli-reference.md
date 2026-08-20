# CLI Reference / 命令行参考

Run any command with `--help` for current arguments.

## Coverage audit

```bash
python scripts/audit_sentence_coverage.py --inventory FILE --sentences FILE [options]
```

| Option | Meaning |
|---|---|
| `--report FILE` | Write a Markdown report. |
| `--min-words N` / `--max-words N` | Override sentence word bounds. |
| `--min-targets N` / `--max-targets N` | Override primary-target bounds. |
| `--expected-pages LIST` | Require a comma-separated physical-page set. |
| `--scope-note TEXT` | Record the source boundary in the report. |

Exit code is `1` when structural checks fail.

## Risk linter

```bash
python scripts/lint_sentence_risks.py --inventory FILE --sentences FILE [--report FILE] [--json-output FILE]
```

The command exits successfully even when flags exist because flags require adjudication and are not automatic errors. Use `--json-output` when the review-completeness audit must verify that every flag was adjudicated.

## Blind-review packet

```bash
python scripts/build_blind_review_packet.py \
  --inventory FILE --sentences FILE \
  --focus language|meaning_fact \
  --seed N --output FILE
```

The same seed and artifacts produce the same packet order and checksum.

## Review-completeness audit

```bash
python scripts/audit_review_completeness.py \
  --sentences FILE \
  --reviews LANGUAGE_JSON MEANING_JSON \
  [--risk-json RISK_JSON] \
  [--report FILE]
```

Exit code is `1` for missing focus, stale checksum, incomplete coverage, failed checks, missing risk adjudications, unresolved blocking issues, or non-pass final verdicts.

## DOCX builder

```bash
python scripts/build_bilingual_docx.py \
  --data FILE --output FILE \
  [--title TEXT] [--version TEXT] [--scope-note TEXT]
```

Generation fails when a target surface cannot be resolved to a distinct occurrence.

## Complete example

```bash
python scripts/run_example.py --output-dir DIRECTORY
```

The command writes fresh reports, both blind packets, and a DOCX without modifying tracked example fixtures.

## 中文说明

覆盖审计和复核完整性审计发现阻断问题时返回非零退出码，适合CI使用。风险扫描即使发现提示项也返回成功，因为提示项还需要人工或模型裁决。盲审包的随机种子用于复现顺序，句子校验和用于证明复核针对当前版本。
