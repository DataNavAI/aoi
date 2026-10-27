---
name: aoi-send-daily-report
description: Prepare and send AOI daily investment research email using evaluated idea updates and reviews and verified delivery records.
---

# aoi-send-daily-report

Prepare and deliver AOI's daily research report.

1. Read [the research contract](../../docs/research-contract.md). Load the reporting date/timezone, intended recipients, user delivery authorization, latest discovery/update/review manifests, and evaluations. Missing inputs must appear as gaps. Failed or unreviewed research must be labeled and excluded from vetted recommendations.
2. Write a concise report: as-of/cutoff and coverage; strongest new ideas; material changes with supporting/opposing evidence; likelihood and trend; target equities; bear/base/bull and expected ROI for today/later with horizon and conditions; invalidations and risks; matured paper outcomes and learnings; next checks. Link to detailed snapshots and sources. A quiet day may have no new ideas; do not manufacture activity.
3. Freeze subject, recipients, body, attachments/links, report ID, and content hash. Use `aoi-send-daily-report-eval` in pre-send mode. Repair and reevaluate until passed; retain a reviewable draft if blocked. Verify private links are accessible to intended recipients without broadening access automatically.
4. Send only with explicit user instruction or applicable standing authorization for these recipients and cadence. If authorization or recipients are absent, finish the draft and request only the missing delivery information. Use the connected email tool and its actual capabilities; never claim a send from a draft ID.
5. Use a stable delivery key (reporting date/timezone + recipient set + report edition). Check the delivery ledger and Sent mail before sending to avoid duplicates. Record send intent before the call and provider message/thread ID and timestamp afterward. On timeout or uncertain result, reconcile Sent mail before any retry; remain delivery-unknown if it cannot be resolved. A revised resend needs an explicit revision label and applicable authorization.
6. Run post-send evaluation using the provider receipt and sent content. Report sent, draft-ready, blocked, or delivery-unknown accurately. Provider acceptance is not proof of inbox delivery. Do not activate a recurring schedule unless separately requested.
