---
name: aoi-update-ideas
description: Research existing investment ideas daily and update evidence, likelihood trends, target equities, and entry-dependent ROI estimates.
---

# aoi-update-ideas

Update AOI's investment idea ledger.

1. Read [the research contract](../../docs/research-contract.md). Load all active ideas, previous successful cutoffs, pending candidates requiring follow-up, and original forecasts. Record the expected idea inventory so omitted ideas are visible.
2. For each idea, search new analysis and primary releases since the prior cutoff through this run's cutoff. Use overlap and deduplication. Recheck catalysts, falsifiers, corrections/retractions, equity identity, and price freshness; follow material developments even when the original source is unavailable.
3. Append evidence with direction and explained strength. Explicitly identify what changed versus what merely repeats old information. Preserve contradictory evidence; revise assumptions when falsifiers fire, including invalidating or closing an idea when warranted.
4. Update the same defined success-event probability and dated trend with evidence-linked reasoning. Separate market price moves from thesis confirmation. Update target equities and explain additions/removals and exposure changes.
5. Recalculate today/later scenario ROI using current sourced prices and updated assumptions; show prior/current values and explain whether changes came from price, valuation, horizon, probabilities, or costs. Preserve the original forecast and record changed horizons separately.
6. Save a new snapshot per idea and a run manifest listing updated/unchanged/invalidated/incomplete ideas, successful cutoff per idea, failures, and next checks. Failed coverage does not advance the successful cutoff. Hand the frozen outputs to `aoi-evaluate-idea-update`.
