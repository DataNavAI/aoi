---
name: aoi-review-ideas-eval
description: Evaluate AOI retrospective reviews for reproducible paper ROI, original-forecast fidelity, unbiased cohorts, and defensible learnings.
---

# aoi-review-ideas-eval

Read [the research contract](../../docs/research-contract.md), especially the evaluation protocol. Obtain the frozen task output, raw sources, and relevant prior records. Audit the following requirements and produce an evidence-linked verdict; do not merely grade the performer’s summary.

- Reconstruct the eligible cohort and exclusions from original records; verify unexecuted status, mature/interim labels, and inclusion of failures/delistings. Unknown execution status cannot be scored as unexecuted.
- Compare the frozen forecast and cutoff with the review; check that entry, exit, horizon, success event, and benchmark were not selected after observing results. Retrospective assumptions must be labeled and separated from original forecast scoring.
- Recompute paper ROI and benchmark excess return from source prices, calendars, distributions, corporate actions, currencies, and costs. Check no-fill cases and adjusted-price dividend double counting. Missing delisting proceeds block the affected return.
- Check the review never labels hypothetical returns as actual portfolio gains. Verify resolved events, probability units, Brier arithmetic, sample counts, and calibration limitations.
- Trace each error diagnosis and learning to evidence available then versus later. Reject outcome-only reasoning, cherry-picked winners, and sweeping rules based on one case.
- Confirm original records remain immutable and learnings include a concrete future check, scope, and exceptions. Flag missing evidence as blocked and demonstrated leakage or arithmetic errors as revise.

Output: artifact identity/hash, cutoff, checks and evidence, findings with repair actions, pass/revise/blocked verdict, and remaining limitations. A pass requires every applicable requirement above and in the contract; do not modify the artifact.
