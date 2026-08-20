# User Guide / 使用手册

## End-to-end workflow

### 1. Freeze the source boundary

Record physical pages, exact duplicates, partial duplicates, missing pages, and unreadable content. Do not infer missing entries unless the user explicitly authorizes supplementation.

### 2. Build the inventory

Create a UTF-8 CSV using [the data schema](../references/data-schema.md). Resolve each entry's required part of speech and intended Chinese sense. Stop when `metadata_status` is `conflict` or `unresolved`.

### 3. Deduplicate and group

Deduplicate by headword, part of speech, and sense. Group entries by a believable scene and actor-action relationship. Prefer three targets when a fourth makes the sentence forced.

### 4. Compose sentence JSON

Use 9–12 English words and 3–4 targets by default. Store the exact surface for every target. Assign every retained entry to one primary sentence.

### 5. Run structural coverage

```bash
python scripts/audit_sentence_coverage.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --report coverage-audit.md
```

Resolve every exception. This `PASS` proves traceability, not language quality.

### 6. Scan review risks

```bash
python scripts/lint_sentence_risks.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --report risk-report.md \
  --json-output risk-report.json
```

Flags identify review questions such as absolute scope, scientific capability, actor ambiguity, and translation relations. A flagged sentence may still be correct.

### 7. Perform diagnostic revision

Review the whole dataset for grammar, collocation, idiom, actor-action logic, learner suitability, target sense, translation, and fact scope. Revise or regroup blocking issues.

### 8. Build blind final-review packets

```bash
python scripts/build_blind_review_packet.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --focus language \
  --seed 17 \
  --output language-packet.json

python scripts/build_blind_review_packet.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --focus meaning_fact \
  --seed 29 \
  --output meaning-fact-packet.json
```

Use separate review passes. Do not show reviewers old verdicts or diffs. Follow [the review rubric](../references/review-rubric.md).

### 9. Audit final-review completeness

```bash
python scripts/audit_review_completeness.py \
  --sentences sentences.json \
  --reviews language-review.json meaning-fact-review.json \
  --risk-json risk-report.json \
  --report review-completeness.md
```

Any accepted English or Chinese edit changes the artifact checksum and invalidates both final reviews. Rebuild packets and repeat.

### 10. Rerun coverage and build the handout

```bash
python scripts/audit_sentence_coverage.py \
  --inventory inventory.csv \
  --sentences sentences.json \
  --report final-coverage-audit.md

python scripts/build_bilingual_docx.py \
  --data sentences.json \
  --output vocabulary-memory-sentences.docx \
  --title "Vocabulary Memory Sentences" \
  --version "Final"
```

Verify archive integrity, extracted text, counts, bilingual alignment, target emphasis, and unresolved surfaces.

## Working with large lists

Maintain one authoritative inventory and sentence JSON. Split review packets into manageable operational batches only when each final review record still proves full-dataset coverage against one checksum. Randomized order helps reduce sequence anchoring; it does not replace full coverage.

## 中文流程摘要

1. 固定可见源文件范围，记录重复页、缺页和不可读内容。
2. 按[数据结构](../references/data-schema.md)建立词库，先解决词性和义项冲突。
3. 按场景和角色关系排重分组；4词勉强时改为3词。
4. 生成9—12词、3—4目标词的短句JSON。
5. 执行覆盖审计，确认没有漏词、重复、映射和表面形式问题。
6. 运行风险扫描，把绝对化、科学能力、施事歧义和翻译关系交给复核者裁决。
7. 完成诊断性修改。
8. 分别生成语言盲审包和词义事实盲审包，独立全量复核。
9. 执行复核完整性审计。任何修改都会使两份最终复核失效。
10. 重新执行覆盖审计，生成并验证Word。

详细严重度和停止条件见[质量保障](quality-assurance.md)。
