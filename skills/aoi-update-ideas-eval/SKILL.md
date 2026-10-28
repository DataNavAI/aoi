---
name: aoi-update-ideas-eval
description: Evaluate a daily AOI idea update against prior snapshots, fresh sources, coverage, evidence changes, probability trends, and ROI calculations.
---

# aoi-update-ideas-eval

Read [the research contract](../../docs/research-contract.md), especially the evaluation protocol. Obtain the frozen task output, raw sources, and relevant prior records. Audit the following requirements and produce an evidence-linked verdict; do not merely grade the performer’s summary.

- Reconcile the run manifest with the expected idea inventory. Check cutoffs, overlap, search results, source failures, and per-idea coverage; a failed fetch cannot count as unchanged or advance a successful cutoff.
- Compare prior/new snapshots. Verify the original forecast survives and each material change has dated evidence. Check corrections, opposing evidence, correlated-source deduplication, and fired falsifiers.
- Independently verify material latest releases and quote freshness against the cutoff. Separate unavailable data from stale data and genuine absence of news.
- Check probability arithmetic, event/horizon comparability, trend history, and reasons for changes or justified no-change. Confirm market appreciation alone did not become proof of the thesis.
- Verify equity changes and recompute today/later returns; attribute differences to price, valuation, probabilities, costs, or horizon. Reject hindsight prices in future-entry scenarios.
- Check invalidations, open gaps, and next actions. Unsupported completeness, silently dropped ideas, rewritten forecasts, or fabricated numbers require revision.

## TLDR acceptance rubric

- Enforce [the idea TLDR contract](../../docs/idea-tldr.md) on **every retained idea**, including incomplete/ineligible/invalidated items, in Markdown, structured current snapshot and exported/rendered output when supplied. Verify its leading placement and readability; all three parts must be understandable without opening JSON.
- Check that the source-derived thesis and falsifiable outcome have a bounded, anchored decision window; distinguish earliest informative check, final resolution and return holding period. Reject an unanchored “long term” or catalyst date presented as certain thesis resolution.
- Count at most three major supporting observations, each source-linked and causally explained. Verify roles, strength and independence; correlated repetitions are not independent support. Require a concise countercase/falsifier and no disguised fourth supporting argument.
- Reconcile **every** target instrument/share class/exchange/direction/currency. Check current reference marks against dated price receipts, session, adjustment basis and cutoff freshness; stale/failed coverage cannot be labeled current. Ratings require provider/type/value/scale/as-of and faithful source context. Article-author opinion cannot become Quant/consensus; AOI score/band/eligibility remains separate and is not success probability. Check available material ratings were actually sought; report specific gaps and next checks without fabrication.
- Independently recompute the predicted **annualized net total-return bear–bull range** from sourced current-entry inputs, scenario exit values, distributions, costs, FX conventions and positive actual holding days. Verify the 365/day exponent, downside, numeric endpoint ordering and distinction from cumulative ROI; later-entry ranges need their own duration/fill/no-fill conditions. A price-target upside is not an annual return. Invalidated ideas cannot retain an actionable current forecast.
- An unavailable field passes only the missing-data handling criterion when the gap/retrieval evidence is truthful, specific and visible with a next check, and unsupported/stale forecasts are suppressed. It does not establish complete source coverage or waive another required check. If supplied lawful sources support a calculation, blanket “unavailable” is a revision finding. In a declared offline fixture replay, judge freshness and source truth against the fixed fixture cutoff and label any pass as fixture-only; this cannot establish live market verification.
- Rate each TLDR dimension **pass / revise / blocked**: (1) thesis and decision window, (2) support/countercase, (3) target/price provenance, (4) ratings/AOI distinction, (5) annualized range arithmetic or justified gap, (6) readability and cross-artifact freshness. Record criterion-level evidence and calculation checks; every applicable dimension and the existing research gate must pass for an overall pass.

Output: artifact identity/hash, cutoff, checks and evidence, findings with repair actions, pass/revise/blocked verdict, and remaining limitations. A pass requires every applicable requirement above and in the contract; do not modify the artifact.
