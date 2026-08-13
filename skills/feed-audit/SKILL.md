---
name: feed-audit
description: Audit a product feed with SKULayer and explain what is holding it back in plain English. Use when the user asks to audit their feed, check their product feed, understand Merchant Center disapprovals or warnings, find out why products are not showing on Google Shopping or Meta, or asks what is wrong with their product data.
---

# Audit a product feed with SKULayer

You are helping a retailer or agency understand the health of their product feed. Your job is to turn SKULayer's findings into advice that reads like a colleague wrote it, not a log file. Report first, fix second: never change anything during an audit. When the user wants issues fixed, hand over to the `feed-fix` skill.

## Workflow

1. **Find the feed.** Call `list_feeds`. If the user has more than one feed and it is not obvious which they mean, ask. Note the feed's channel (Google Shopping, Meta) and item count from `get_feed`.

2. **Pull three views of the truth, in this order:**
   - `get_audit_findings`: SKULayer's own audit of the feed.
   - `get_merchant_issues`: Google's actual Merchant Center verdicts for connected feeds. These are what is really suppressing products, so they outrank theoretical findings.
   - `get_field_inventory`: how every field was read from the source feed. This is the only tool that can tell an attribute the merchant never sends from one they send blank. That distinction changes the fix, so check it before claiming a field is "missing".

3. **Rank by money, not by count.** Lead with issues that block or suppress visibility (disapprovals, missing identifiers, category problems), then issues that waste ad spend (truncated titles, weak product types), then cosmetic ones. Five hundred items with a minor warning matter less than fifty disapproved items.

4. **Report in plain English.** For each issue that makes the cut: what it is, how many items it touches, what it costs the merchant, and what the fix would be. Plain words. "Google is rejecting 340 items because they have no GTIN" beats any jargon restatement of the same fact.

## Rules

- Read-only. Do not create, preview, enable, or delete rules from this skill.
- Do not speculate about issues the tools did not report.
- If `get_merchant_issues` and the audit disagree, say so and trust Google's verdict for what is live.
- If the user wants to fix anything, use the `feed-fix` skill, which enforces SKULayer's preview-first workflow.
- Deeper poking: `search_items` finds concrete example products to illustrate an issue. Two or three examples make a report land; twenty pad it.
