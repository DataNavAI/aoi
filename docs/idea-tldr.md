# Idea TLDR contract

Applies to development and every refinement/update of a retained idea. Start each
`IDEA.md` with `## TLDR` immediately after the title/status/as-of line and back link,
before detailed evidence, scoring or audit sections. Aim for a short screenful
(roughly 150–250 words plus a small target table), using these three parts:

1. **Idea and decision window.** One plain-language, source-derived thesis; its
   measurable success/failure condition; the earliest informative check and latest
   expected resolution, as dates or a bounded time range anchored to the as-of date.
   Distinguish an early catalyst/check from final resolution and from the holding
   period used to calculate returns. A known unresolved timing gap is explicit.
2. **Why it could work.** At most three major supporting observations, ordered by
   importance, each with a source link and a short causal explanation. Prefer
   independently corroborated facts; label issuer forecasts, analyst opinion and
   AOI assumptions. Repetitions of one underlying event count as one observation.
   Include one concise strongest countercase/falsifier; do not use it to hide a
   fourth supporting argument. If no support is verified, say so rather than padding.
3. **Targets, price, ratings and annual return.** Cover every target instrument,
   using a compact table or bullets with readable names, ticker/share class, product
   type, exchange, direction and currency. A company name alone is not a product.
   Include the following fields for every target, even when unavailable.

## Price and ratings

- **Current price:** a sourced, timestamped reference mark with currency and session
  (live/delayed/regular close/etc.), adjustment basis and freshness relative to the
  research cutoff. A reference mark is not an executable fill. For closed markets,
  identify the latest completed session. A stale observed mark may be shown with its
  original date and a stale label, but it cannot be called current or silently used
  for a current-return forecast. Keep necessary short provenance in the TLDR and
  link detailed price receipts below it.
- **Ratings:** label provider, rating type, value, scale and as-of date. Seek Seeking
  Alpha Quant, SA analyst and Wall Street consensus ratings when lawfully available;
  report the types checked and gaps, not invented consensus. An individual article
  author's Buy is author opinion, not aggregate analyst consensus or a Quant rating.
  Never average incompatible rating scales. Show **AOI rubric score/band/eligibility**
  separately, with explicit incomplete subtotal/range where applicable. No rating or
  rubric score is the probability that the thesis succeeds.

## Predicted annual return range

Show the modeled **annualized net total-return bear–bull range** for entry at the
current sourced reference mark, tied to the declared resolution date and scenario
model. Label it a conditional forecast, not guaranteed performance, a confidence
interval or realized ROI. Include the downside even when negative; sort range
endpoints numerically. State the holding period, dividend/reinvestment convention,
costs and material FX assumptions in a short footnote or nearby linked calculation.

For a supported long, unlevered model, use the contract's scenario net cumulative
ROI. With `R` as a decimal net cumulative return and `d > 0` calendar days:

`annualized_percent = 100 * ((1 + R) ** (365 / d) - 1)`

Calculate each scenario independently before selecting range endpoints. Keep the
cumulative range distinct from the annualized range, especially outside one year.
An annualized equivalent over a short holding period is not a forecast that the
same return repeats every year. A total loss (`R = -1`) is -100%; for `R < -1`,
shorts, leverage or nonpositive durations, do not apply this formula; use a justified
model or mark annual return unavailable. Keep any later-entry annualized range
separate with its own duration, trigger, fill uncertainty and no-fill outcome.

When current price, valuation/scenario support, duration, costs or another required
input cannot be verified after a reasonable permitted retrieval attempt, write
**“Predicted annual return: unavailable — <specific missing inputs>; next check:
<retrieval/action>.”** Never substitute an old historical model, a price target's
cumulative upside, the AOI score or a rating. Missing ratings alone do not invalidate
an otherwise supported return model; missing model inputs do. Do not invent numeric
ranges just to populate the TLDR.

## Consistency and updates

Store a structured `tldr` in the current snapshot alongside the Markdown:
`idea`, `decision_window` (anchor, earliest_check, latest_resolution, success_condition),
`supporting_evidence` (at most three, with claim, role, rationale, source URL/locator),
`countercase`, and `targets`. Each target carries identity, `price`, `ratings`,
`aoi_score`, and `annual_return` with numeric endpoints and model/duration references,
or an explicit unavailable reason and next check. Cite underlying evidence rather
than copying private account or source-capture data into this public summary.

Refresh the TLDR on every update, including invalidation, changed targets or blocked
coverage. Reconcile it with the current snapshot, score authority, index and return
calculations; preserve the original forecast and prior summaries in history. Do not
advance the summary's successful research cutoff when a source search fails. Check
the public export and rendered page retain all three TLDR parts and their caveats.
