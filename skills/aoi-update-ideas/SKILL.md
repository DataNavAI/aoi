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
6. Refresh the leading TLDR in every retained idea's `IDEA.md` and matching snapshot `tldr` using [the idea TLDR contract](../../docs/idea-tldr.md). Recheck the decision window, select up to three major causal supporting observations, expose the strongest countercase, and update every target's sourced price and attributed/dated ratings. Keep AOI rubric scores separate. Recompute the current-entry annualized net bear–bull return range from the updated model and actual remaining calendar days; do not carry forward an old cumulative range as an annual forecast. Label stale/unavailable inputs, preserve failed coverage cutoffs, and record retrieval next checks. Invalidated ideas need an invalidation TLDR with a suppressed actionable forecast.
7. Save a new snapshot per idea and a run manifest listing updated/unchanged/invalidated/incomplete ideas, successful cutoff per idea, failures, and next checks. Failed coverage does not advance the successful cutoff. Hand the frozen outputs to `aoi-update-ideas-eval`.

## Freeze checks

- Normalize success-event likelihoods to the contract's 0–100 percent scale in new snapshots, with an explicit `unit: percent`; convert fractional legacy inputs explicitly, preserve their original files, and keep percentage-point changes distinct from scenario weights. Read the generated site's visible probability and title, not just embedded JSON.
- Resolve every structured TLDR source/model reference relative to the file containing it (including nested snapshots); do not reuse Markdown-relative paths inside a deeper JSON file. Copy references needed by a public TLDR as concise public-safe evidence/calculation records or use actual external source URLs, and rewrite paths after export. Private receipt links may remain private, but they cannot be the only evidence/model reference for the public TLDR.
- Validate links and exact referenced fragments in the final public Markdown, exported snapshots and generated pages after all copying/rebasing. A file hash or a self-reported publication check does not establish that its references resolve.
- Give every unavailable TLDR field its own concrete retrieval next check, including missing provider rating categories and the missing AOI score authority; a generic run-manifest next step is insufficient for a public summary.
- Write `tldr.idea` as the current state-aware summary, especially after invalidation. When failed coverage leaves a prior likelihood retained, preserve its numeric history, record its source cutoff, and provide `likelihood.display` explicitly labeling it as a prior estimate, rather than a newly verified probability.
