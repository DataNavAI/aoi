# TLDR training result — 2026-10-28

Both development and refinement passed independent evaluation against the fixed
[TLDR standard](idea-tldr.md) and existing [research contract](research-contract.md).
These are **offline synthetic fixture tests**, not live Seeking Alpha access,
current market verification, complete financial coverage or evidence of returns.

| Pair | Passing attempt | Tested behavior |
|---|---:|---|
| `aoi-develop-ideas` / `aoi-develop-ideas-eval` | 15 | Trending-listing mining, prior rejection and canonical alias deduplication, source attribution, evidence/score integrity, truthful missing-forecast handling, readable library and public website |
| `aoi-update-ideas` / `aoi-update-ideas-eval` | 2 | Updated evidence and price, annualized today/later returns, invalidation, stale/failed coverage, retained prior likelihood and consistent public TLDRs |

Each attempt used a fresh performer, then a different fresh evaluator. Raw inputs,
acceptance criteria and evaluation skills stayed fixed after the initial TLDR
update. Failed outputs were preserved; the parent did not repair generated outputs
to obtain a pass. New independent trials used isolated copies of the original seed
ledger; duplicate passes within each trial reused that trial's persistent ledger.

Training improved causal evidence explanations, precise source roles and clocks,
current-version reconciliation, immutable snapshot creation, full public snapshot
exports and downloaded calculation/source links. The website now places TLDRs
before detailed scores and renders structured decision windows readably.

Validation: 35 automated tests pass; skill structure/references, JavaScript syntax
and deployment workflow checks pass. The current exporter preserves the passing
refinement fixture's TLDR, scores, likelihood and applicable full research fields;
the current renderer rebuilds all three refinement examples with clean references.

The final development artifact has 122 hash-frozen files and the refinement artifact
57. Both retained development candidates remain incomplete and unranked: no supported
valuation bridge exists in the permitted fixture. Refinement includes a supported
annualized calculation; unavailable fields are explicit with next retrieval actions.

| Audit identity | SHA-256 |
|---|---|
| Development output manifest | `81f96ab3a746eda4f62cc9ffd728598363798f94ee06a02513b43a781e1d2a91` |
| Development evaluation Markdown | `d712b050face95e919a5284c843c16914c691fd096ba1170c70c05ada47451af` |
| Refinement output manifest | `a6dba9cabcf715973b4436eddce3273a0f929bf1cd9f45e6c038afd6c8122f47` |
| Refinement evaluation Markdown | `694a940eeb83e8e263de0948d966e56f200270a589e0fb4e1d94031ef7ef8cdc` |

Detailed frozen artifacts, reports, dependency hashes and failed attempts are retained
in the private training directory `AOI-training/tldr-20261028`, outside this repository.
No synthetic idea is published into `research/`. All 41 original production research
files and the production article-memory database retain their original hashes.
Existing real idea pages have not been backfilled by this training run. The daily
research skill now requires this standard for future development and refinement.
