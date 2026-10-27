---
name: aoi-review-ideas
description: Review unexecuted past investment forecasts, measure subsequent paper returns, and record evidence-based lessons from errors.
---

# aoi-review-ideas

Review AOI's unexecuted ideas without hindsight leakage.

1. Read [the research contract](../../docs/research-contract.md). Select all eligible unexecuted forecasts using a declared review window and maturity rule. Include losers, invalidated ideas, delisted equities, and rejected ideas with an actual forecast; preserve exclusion reasons. Verify execution status from available records, marking unknowns ineligible pending confirmation.
2. Freeze the original thesis, probabilities, targets, horizon, entry/exit rules, source cutoff, and reasons for nonexecution. Use the predeclared trade convention. If no convention was recorded, report alternative assumptions as retrospective sensitivity analysis rather than a scored original prediction.
3. Reconstruct feasible entry after the forecast became available and exit at its stated horizon or original rule. For later triggers use contemporaneous trigger/price data and no-fill outcomes. Handle exchange calendars, splits, dividends, mergers, delistings, currency, costs, and data gaps. Avoid double-counting distributions in adjusted data. Unmatured ideas get interim marks, not final verdicts.
4. Compute realized hypothetical (paper) ROI, benchmark total return on matching dates/currency, and excess return. Label these as observed paper outcomes, never actual portfolio P&L. Show prices, dates, source/adjustment basis, formula, and costs so the result can be reproduced.
5. Assess the predefined success event independently from ROI. Compare forecast ranges and probabilities with outcomes; use Brier score `(p-y)^2` for resolved binary events and aggregate calibration only with sample count and uncertainty. One miss does not prove a probability was miscalibrated.
6. Diagnose thesis/mechanism, valuation, timing, implementation, data, or unforeseeable-event errors, separating information available then from learned later. Record what went right as well as wrong. Each learning cites cases and evidence, proposes a concrete future check, and states applicability and exceptions; do not rewrite history or automatically change skills from one anecdote.
7. Save the complete cohort, exclusions, reproducible return calculations, outcome labels, and learning log. Route to `aoi-review-ideas-eval`.
