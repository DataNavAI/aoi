---
name: aoi-evaluate-daily-report
description: Evaluate an AOI daily email report before sending and verify sent-content and provider receipts after sending.
---

# aoi-evaluate-daily-report

Read [the research contract](../../docs/research-contract.md), especially the evaluation protocol. Obtain the frozen task output, raw sources, and relevant prior records. Audit the following requirements and produce an evidence-linked verdict; do not merely grade the performer’s summary.

Choose pre-send or post-send mode explicitly; a pre-send pass never certifies delivery.

Pre-send:
- Reconcile the reporting date, timezone, cutoffs, idea coverage, and source manifests. Verify displayed evaluations apply to the exact referenced artifact versions/hashes.
- Trace material claims to snapshots and sources; reproduce sampled calculations and every high-impact changed number. Check likelihood versus confidence, ROI horizons/scenarios/entry conditions/downside, paper outcome labeling, risks, and gaps.
- Verify all four workflow sections are present or explicitly have no activity/incomplete coverage. Ensure the summary does not elevate failed/unreviewed work into vetted advice.
- Inspect the exact subject/body/attachments, recipient set, current authorization, privacy, and link accessibility. Check the delivery key/ledger for duplicate or unresolved attempts. Missing authorization permits a draft-quality assessment but blocks a send-ready verdict.

Post-send:
- Match provider Sent message/receipt to report content, recipients, edition, and delivery key. Confirm message ID and timestamp; a draft or queued attempt is not sent.
- Check duplicate sends, uncertain attempts, revised-edition labeling, and ledger reconciliation. State provider-accepted, draft-only, failed, or unknown; do not infer inbox delivery.

Return separate content, send-readiness, and delivery statuses with findings; do not send or retry email as an evaluator.

Output: artifact identity/hash, cutoff, checks and evidence, findings with repair actions, pass/revise/blocked verdict, and remaining limitations. A pass requires every applicable requirement above and in the contract; do not modify the artifact.
