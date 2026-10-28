# GitHub Pages publication

The public reading library is `research/`: one Markdown page per idea, current snapshots,
score authority and a reading index. The private data root remains separate. Generate a
fresh public export into an **empty** staging directory with:

```sh
python3 scripts/export_idea_library.py --source /Volumes/Agent/AOI-data --output /tmp/aoi-public-export
python3 scripts/build_idea_site.py --source /tmp/aoi-public-export --output /tmp/aoi-public-site
```

Inspect and reconcile the export into `research/` before committing. The exporter copies
only declared reading pages, a reduced current snapshot, score authority and an index.
It does not copy the SQLite ledger, extractions, receipts, training files or authentication
state. Links to excluded supporting files become text marked private; original research
is unchanged. Never replace good research with a partial/failed export.

## Deployment

`.github/workflows/pages.yml` tests and builds on pushes to `main`, builds without deploying
on pull requests, and supports manual invocation. Select **GitHub Actions** as the Pages
publishing source in repository Settings → Pages. GitHub returns the deployed URL in the
`github-pages` environment. The generator uses relative assets and supports project URLs
such as `https://OWNER.github.io/aoi/` without a hardcoded domain.

The reusable workflow accepts a `research_commit` SHA so an automated updater can deploy
the exact accepted commit directly. This is necessary when the updater commits using
`GITHUB_TOKEN`: such a push does not trigger another push workflow. Never assume that
pushing with the Actions token alone redeploys Pages.

## Daily research and publishing

Research runs in the existing Codex conversation using
[the daily routine](../skills/aoi-daily-research/SKILL.md), every day at **07:00
America/Los_Angeles**, including weekends. It uses the current Codex environment;
no GitHub-hosted model job or additional OpenAI API key is required. Keep the
research computer on, the app running and its local data paths available.

Private accepted research and durable article history stay in `/Volumes/Agent/AOI-data`.
Dated candidates, source records and independent evaluations stay in `/Volumes/Agent/AOI-runs`.
The routine mines accessible Seeking Alpha Trending Analysis, updates tracked ideas, reviews
eligible forecasts, evaluates frozen candidates, and exports only accepted public pages
to `research/`. It commits/pushes those changes to `DataNavAI/aoi` on `main`; Pages CI
builds and deploys the corresponding commit. It verifies deployment before claiming
that the new content is live. No empty daily commits or fabricated freshness dates.

The user authorizes daily research and publication of accepted public idea updates.
Credentials, browser sessions, source captures and private ledger data are never uploaded.
A source-login or human-verification challenge is reported for user action; affected
mining and its successful cutoff remain blocked. Independent research can continue.
Failed evaluations preserve candidate history and prior accepted ideas. Article readings
remain recorded even when publication fails.

Scheduled execution uses the Codex automation facility, not a GitHub Actions cron.
GitHub hosts the static site continuously; it remains reachable when the research
computer is offline, but research runs require that computer and Codex to be available.
Email is not sent until recipients and standing delivery authorization are configured.

Repository: `DataNavAI/aoi`; published URL: `https://datanavai.github.io/aoi/`.
