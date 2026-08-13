---
name: feed-fix
description: Turn product feed issues into safe, previewable SKULayer rules. Use when the user wants to fix feed issues, clean up titles, fill missing fields, map product categories, write or edit feed rules, or apply fixes that came out of a feed audit. Preview-first, always.
---

# Fix feed issues with SKULayer rules

SKULayer never edits a live feed directly. Fixes are rules: transformations that apply on the next run and stay inspectable in the app at https://skulayer.com/app. Your job is to draft good rules and enforce the preview-first contract: **the human sees the preview before anything is enabled. No exceptions.**

## Workflow

1. **Know what you are fixing.** If there is no recent audit context, run the essentials from the `feed-audit` skill first (`get_audit_findings`, `get_merchant_issues`, `get_field_inventory`). Check `list_rules` so you do not duplicate or fight an existing rule.

2. **Draft narrow rules.** One rule per problem. A rule that fixes titles and categories and availability at once is impossible to review and dangerous to disable later.

3. **Preview before create when exploring.** `preview_rule` shows what a rule would do without saving anything. Use it to iterate.

4. **Create, then show the report.** `create_rule` saves the rule disabled and returns the standard preview report, including any danger-level warnings. Show that report to the human every time: items touched, before and after examples, and every warning, verbatim. Never summarize a danger warning away.

5. **Enable only on explicit approval.** After the human approves what they saw, `set_rule_enabled`. Then `trigger_run` if they want the change out now, `get_run_status` to confirm the run finished, and `search_items` to spot-check real items came out as promised.

## Category mapping

`map_categories` proposes a Google taxonomy mapping over the feed's product types and **saves nothing**. Show the proposal, take corrections, and land the agreed mapping through `create_rule` like any other change. `search_taxonomy` resolves individual category questions.

## Rules

- Never enable a rule whose preview report the human has not seen in this conversation.
- Never batch-enable several rules on one approval. One report, one yes, one rule.
- A rule touching most of the feed, or any rule with a danger warning, deserves a direct question ("this touches 4,200 of 4,600 items, sure?") before enabling.
- Deleting a rule (`delete_rule`) changes the feed too. Same bar: say what removing it will do, then act.
- Write tools need a write-scoped token. If they fail on authorization, say so plainly and point the user to their SKULayer settings rather than retrying.
