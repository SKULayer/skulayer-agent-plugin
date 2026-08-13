---
name: feed-health
description: Quick recurring health check on a SKULayer feed. Use when the user asks how their feed is doing, whether the last run worked, whether anything new is disapproved, or wants a weekly or scheduled feed check. Reports change, not state.
---

# Feed health check

A health check answers three questions fast: did the last run work, has Google's verdict on anything changed, and did any rule do something unexpected. It is a pulse, not an audit. If the check uncovers something structural, recommend a full audit (`feed-audit` skill) rather than stretching this one.

## Workflow

1. `get_run_status`: did the latest run complete, when, and how many items were delivered? A run that silently shrank the item count is the first thing to flag.
2. `get_merchant_issues`: compare against the previous check if you have one in context or in prior conversation. New disapprovals lead the report. Resolved ones are worth a sentence.
3. `get_activity`: any rule changes, run failures, or config changes since last time worth the user knowing about.

## Reporting

Report deltas, not inventories. "No change since last week, 4,580 items serving, nothing new from Google" is a complete and excellent report. Only expand on what moved. If a new issue has an obvious rule-shaped fix, name it in one line and offer the `feed-fix` workflow; do not build the fix unasked.

If this check runs on a schedule, stay silent-friendly: lead with a one-line verdict (all clear, or N things need eyes) so the user can stop reading there.
