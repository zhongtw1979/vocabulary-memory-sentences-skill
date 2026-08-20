# Troubleshooting / 常见问题

## `Inventory is missing required columns`

Use the exact header in [the data schema](../references/data-schema.md). Save CSV as UTF-8 and keep optional values blank rather than removing their columns.

## `inventory_metadata_not_ok`

One or more retained entries have `conflict`, `unresolved`, or blank metadata status. Resolve the required part of speech and intended sense before composition.

## `target_surface_missing`

The exact surface is absent as a distinct token or phrase. A substring inside another word does not count. Update the sentence or target surface.

## `target_surface_not_allowed`

The surface exists in the sentence but is not listed in `allowed_surfaces` and does not equal the source entry. Confirm the inflection, then update the authoritative inventory or sentence.

## Risk report says `REVIEW_REQUIRED`

This is normal when patterns need adjudication. Read each flag, decide whether the sentence is valid, revised, regrouped, or escalated, and record the reason in the final review.

## `stale_artifact_checksum`

The sentence JSON changed after the review packet or record was created. Rebuild both blind packets and repeat both final reviews.

## `incomplete_target_checks`

The `meaning_fact` review did not check every target ID in the current sentence. Add exactly one target-level record per primary target.

## DOCX reports unresolved surfaces

The Word builder could not find a distinct occurrence for every target. Run the coverage audit first, then check overlapping phrases and duplicate target surfaces.

## Chinese glyphs look wrong in a renderer

The document requests `Noto Sans CJK SC`, but a renderer may substitute or lack the font. If archive and text extraction checks pass, open the DOCX in the target word processor. Install a CJK font or change the constant in `build_bilingual_docx.py` for your environment.

## `No module named pytest` or `No module named docx`

Activate the project environment and install dependencies:

```bash
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## 中文速查

- 缺少CSV列：按数据结构恢复完整表头。
- 元数据不为 `ok`：先解决词性和义项冲突。
- 目标词找不到：检查是否只出现在另一个单词内部。
- 风险报告要求复核：逐项裁决，不能直接当作错误。
- 校验和过期：句子已经修改，必须重新做两份全量盲审。
- Word中文显示异常：先验证文本和结构，再检查本地字体或渲染器。
