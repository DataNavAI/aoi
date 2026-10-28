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

## Daily research prerequisites

Publishing existing research needs no model key. New research needs an agent runtime,
lawful source access and persistent article history. A GitHub-hosted runner cannot inherit
a desktop Seeking Alpha session, and Actions alone does not perform investment research.
The supported hosted Codex action needs the `OPENAI_API_KEY` repository secret (separate
API usage), plus any approved research-source integrations. Do not upload desktop cookies,
passwords or a Codex authentication directory. If Seeking Alpha requires sign-in or human
verification, stop affected mining, preserve the prior successful cutoff and request
interactive access. Do not substitute teasers or independently invented ideas.

For subscription-dependent research, a dedicated self-hosted research runner with durable
private state may be more practical. Pages deployment can still run on GitHub's hosted
runners, and the website remains reachable when the research runner is offline.

A daily pipeline must: load the prior durable ledger → perform develop/update/review →
freeze candidate output → independently evaluate → publish only accepted research → push
idea changes → invoke the reusable Pages workflow. Persist reading history even when an
evaluation fails; do not rely on an expiring Actions cache as the only ledger. A failed
research or evaluation run leaves the last successful website online. Keep research
cutoffs distinct from build/deployment time. Sending email requires its separate delivery
configuration and is not implied by a website publishing workflow.

Repository: `DataNavAI/aoi`; published URL: `https://datanavai.github.io/aoi/`.

Pending configuration: hosted API versus self-hosted research runtime, approved Seeking
Alpha access method, durable private ledger location, daily time.
No daily research schedule is enabled until these dependencies are configured.
