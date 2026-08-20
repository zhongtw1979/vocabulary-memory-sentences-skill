# Complete Example / 完整示例

The example is synthetic and safe to publish. It contains 12 target entries, four sentences, two final reviews, two adjudicated translation-relation flags, expected reports, and a DOCX.

## Inspect the inputs

- [sample inventory](../examples/sample-inventory.csv)
- [sample sentences](../examples/sample-sentences.json)
- [language review](../examples/reviews/language-review.json)
- [meaning/fact review](../examples/reviews/meaning-fact-review.json)

## Run everything with one command

```bash
python scripts/run_example.py --output-dir build/example
```

Expected summary:

```text
Coverage: PASS
Risk flags: 2 (reviewed, not automatic errors)
Review completeness: PASS
Sentences: 4
Targets: 12
DOCX unresolved targets: 0
```

## Run each gate manually

```bash
python scripts/audit_sentence_coverage.py \
  --inventory examples/sample-inventory.csv \
  --sentences examples/sample-sentences.json \
  --report build/example/coverage-audit.md

python scripts/lint_sentence_risks.py \
  --inventory examples/sample-inventory.csv \
  --sentences examples/sample-sentences.json \
  --report build/example/risk-report.md

python scripts/build_blind_review_packet.py \
  --inventory examples/sample-inventory.csv \
  --sentences examples/sample-sentences.json \
  --focus language --seed 17 \
  --output build/example/language-review-packet.json

python scripts/build_blind_review_packet.py \
  --inventory examples/sample-inventory.csv \
  --sentences examples/sample-sentences.json \
  --focus meaning_fact --seed 29 \
  --output build/example/meaning-fact-review-packet.json

python scripts/audit_review_completeness.py \
  --sentences examples/sample-sentences.json \
  --reviews examples/reviews/language-review.json examples/reviews/meaning-fact-review.json \
  --report build/example/review-completeness.md

python scripts/build_bilingual_docx.py \
  --data examples/sample-sentences.json \
  --output build/example/vocabulary-memory-sentences.docx \
  --title "Vocabulary Memory Sentences" \
  --version "v0.1.0" \
  --scope-note "Synthetic example only."
```

Compare with [expected outputs](../examples/expected-output/). The risk report deliberately contains two flags. Both are explicitly accepted with reasons in the meaning/fact review; therefore flags do not block release.

## 中文说明

这套示例全部为本项目新造内容，可以公开传播。它展示了12个词条如何组成4个短句，并完整经过：覆盖审计、风险扫描、两份盲审任务包、两轮独立复核、复核完整性审计和Word生成。

风险报告会标记S001和S004中的路径或时间关系词。两句话本身没有错误；词义事实复核记录说明了中译如何保持对应关系，并把风险项标记为已解决。这正是“风险提示不等于自动判错”的完整示范。

可直接查看[示例Word](../examples/expected-output/sample-handout.docx)。
