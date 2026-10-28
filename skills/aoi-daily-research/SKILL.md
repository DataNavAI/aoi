---
name: aoi-daily-research
description: Run AOI's daily investment research, independently evaluate candidate changes, and publish accepted idea pages to DataNavAI/aoi and GitHub Pages while preserving private source history.
---

# aoi-daily-research

Perform the research yourself using current sources. This routine orchestrates the existing task/evaluator pairs; rebuilding yesterday's files alone is not a research run.

## Operating context

- Checkout: `/Volumes/Agent/Codex/aoi`; remote: `https://github.com/DataNavAI/aoi.git`, branch `main`.
- Accepted private research and persistent article ledger: `/Volumes/Agent/AOI-data` and its `article-memory.sqlite3`.
- Private run records: `/Volumes/Agent/AOI-runs/<Pacific-date>-<unique-run-id>/`.
- Public reading library: `research/` in the checkout; site: `https://datanavai.github.io/aoi/`.
- Reporting timezone: `America/Los_Angeles`. Determine today's date at execution, including DST. This routine is scheduled daily at 07:00 local time, including weekends; retain the last completed market session when markets are closed.

The user authorizes recurring research, commits of accepted public idea updates, pushes to this remote, and Pages deployment. Private article history, raw source captures, receipts, extractions, account state, credentials and training records stay outside Git. No trading or new infrastructure purchases. Email is draft-only until recipients and standing delivery authorization are configured.

Read [the shared contract](../../docs/research-contract.md), [publication guide](../../docs/github-pages.md), and the task/evaluator skills for the phases below. Do not train or rewrite skills/evaluators during an ordinary daily run.

## Prepare and isolate

1. Verify the checkout/remote, source data and existing ledger. Check for an active daily run and skip overlap. Acquire a run lock in the private data root using atomic exclusive creation; record run ID/start time. Release it on completion; never remove another live run's lock. Investigate stale locks instead of guessing that a worker died.
2. Start a dated private run manifest with cutoff, overlap from each prior successful cutoff, expected idea inventory and original forecast references. Preserve immutable originals. If the private ledger is absent or unreadable, stop discovery rather than creating empty history.
3. Inspect Git status and fetch `origin/main`. Fast-forward only when safe; preserve unrelated user changes and stop publication if they prevent an isolated commit. Do not reset, force-push, or silently merge divergent research.
4. Create a candidate research workspace under the private run directory, seeded from accepted research and required supporting records. Never recursively copy the run directory or overwrite accepted current pointers during research. Use the **production** article ledger for real article claims/readings; do not clone it into an independent mining history. Save new extractions/results under durable private paths before recording them. Source readings and claims survive failed evaluations.

## Research and independently evaluate

- **Discover:** use [aoi-develop-ideas](../aoi-develop-ideas/SKILL.md) and [its evaluator](../aoi-develop-ideas-eval/SKILL.md). Observe Seeking Alpha's latest Trending Analysis listing; check canonical article IDs in the ledger before body reading. Mine only accessible thesis-bearing articles and reuse previously mined/rejected results. Do not originate seed theses. Zero new ideas can be correct. Retain listing/coverage and alias-deduplication evidence.
- **Update:** use [aoi-update-ideas](../aoi-update-ideas/SKILL.md) and [its evaluator](../aoi-update-ideas-eval/SKILL.md). Cover every active/pending idea, new primary filings/releases and contrary analysis. Reassess evidence direction/strength, likelihood trend, target equities and today/later ROI. Record per-idea search coverage and gaps. Unavailable prices or costs leave ROI unavailable; source failures do not advance successful cutoffs.
- **Review:** use [aoi-review-ideas](../aoi-review-ideas/SKILL.md) and [its evaluator](../aoi-review-ideas-eval/SKILL.md). Identify due/matured and relevant interim reviews; preserve original forecasts and execution records. Unknown execution status is not unexecuted. Record an honest empty/ineligible cohort when nothing qualifies, rather than manufacturing ROI or lessons.

Freeze each phase's candidate output with hashes and prior-source references. Give a fresh evaluator subagent the paired evaluator, frozen artifacts, raw source evidence and prior records; it must inspect them independently without modifying them. Delegation is explicitly part of this routine. If independent evaluation cannot run, save the candidate as unverified and do not publish it.

Repair demonstrated `revise` findings and freeze a new version; allow at most three evaluation attempts per phase in one daily run. Stop access-dependent retries on `blocked`. Never weaken the evaluator or treat a pending login as a passing zero-idea result. Accepted independent phases can proceed while a blocked phase remains excluded; evaluate the final combined publication so a failed discovery cannot leak candidate ideas into an accepted update.

If Seeking Alpha needs login, ask the user to sign in in their browser and confirm, with the relevant URL; never request secrets. Human verification requires user involvement according to the available tool policy. In an unattended run record the pending request, finish independent work and report the actionable blocker. Do not keep a run open indefinitely awaiting input or bypass access controls. On later runs recheck access before retrying blocked unread articles, and reuse persisted readings rather than mining twice.

## Reading library and publication

1. Generate candidate `INDEX.md`, one readable `ideas/<id>/IDEA.md` per idea, immutable snapshots, current index and score authority from the same accepted facts. Recompute rubric arithmetic with the existing scoring helper. Keep complete eligible scores separate from incomplete subtotals/ranges and ineligible ideas. Include material limitations beside each score/return. Preserve thesis/source attribution, evidence, countercase, next checks, source cutoff and original forecast lineage.
2. Export a candidate public bundle into a new empty directory with `scripts/export_idea_library.py --source <candidate-root> --output <run>/public`. Build with `scripts/build_idea_site.py --source <run>/public --output <run>/site`. Do not run an old fixed-date presentation script as if it performs fresh research.
3. Have an independent evaluator inspect the **final exported Markdown and generated site data**, inventory, scores/dates, links, private/public boundary and the phase verdicts. Save a publication verdict identifying hashes of the exact public files. Publish only when the combined artifact passes. A blocked phase may be excluded only if prior accepted ideas are retained and the publication accurately states its unchanged cutoff/coverage limitations.
4. Promote accepted private artifacts/current pointers with backups or atomic replacement, retaining prior immutable snapshots and all production ledger events. Promotion must preserve the evaluated bytes; if rendering changes them, freeze and evaluate again. Keep failed candidates and findings private.
5. Reconcile the evaluated public bundle into checkout `research/`; include deletions only for generator-owned paths proven removed by the accepted inventory. Inspect the complete diff and ensure only public research is staged. Run the repository tests and build the site from `research/`. If the public bundle is byte-identical, do not make an empty commit or advance dates merely to suggest freshness.
6. Commit only accepted `research/` changes with the run date and concise purpose. Push to `origin/main` with the authorized Git credentials. A normal authenticated Git push triggers `.github/workflows/pages.yml`. If using an Actions token or a push did not trigger deployment, dispatch that workflow explicitly for the accepted branch. Never force-push; on rejection, fetch and reconcile/re-evaluate instead of overwriting newer work.
7. Verify the matching commit's Pages workflow finishes successfully, then verify the public URL serves the expected accepted idea/version and project-relative assets. A pending deployment is pending, not published; retain its run ID for reconciliation. On failure retain last good site, record the error and surface the blocker. Do not claim the update is live based only on a local build or successful push.

## Finish

Save the run manifest, phase verdicts, source coverage/cutoffs, article ledger before/after references, changes/unchanged/blocked ideas, review cohort/exclusions, next checks and publication commit/workflow/URL/status. Update the last-run pointer without changing last-successful research cutoffs on failures. Release this run's lock.

Prepare a concise private daily report of material changes, new ideas, invalidations, review learnings and unresolved gaps; use the report pair only if composing its full deliverable. Sending requires configured recipients and applicable authorization; do not infer email permission from this schedule.

Report meaningful research/publication changes, failures or required user action. If evidence and published content are unchanged and no new actionable blocker exists, retain the private run record without a repetitive notification. Resume pending deployment reconciliation before starting duplicate work.
