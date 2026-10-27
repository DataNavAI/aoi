# Persistent article memory

Use `scripts/article_memory.py --db <data-root>/article-memory.sqlite3 ...`. The database is durable state, not an ephemeral per-run list. All operations normalize Seeking Alpha article IDs, so tracking parameters, title edits, or URL slug aliases cannot bypass deduplication. No credentials or full copyrighted article bodies belong in the ledger; keep a concise extraction and lawful source locators in the private data root.

Commands:

- `list`: export current entries for coverage and before/after evidence.
- `claim URL --run RUN_ID`: atomically reserve an unseen article. A duplicate returns `claimed: false` and the existing record. An unread blocked article is retried only with `--retry-blocked` after an access change; do not repeatedly hammer a paywall.
- `read URL --run RUN_ID --record PATH`: mark body read and store the durable JSON extraction path. The JSON must include `article_id`, `read_at`, `body_access` (`full` or `sufficient-body`), `author_thesis`, `locators`, and `ideas` (possibly empty). `sufficient-body` means the actual thesis-bearing body and its qualifying context were read, not a public teaser. Preserve the original extraction; do not overwrite it later.
- `finish URL --run RUN_ID --status mined --record PATH`: the durable JSON result must include `article_id`, `idea_paths` (existing files, nonempty), and `reason`. Use `--status rejected` with a reason when no usable ideas exist; rejected may also terminate an unread article proven out of scope from the listing without claiming it was read.
- `finish URL --run RUN_ID --status blocked --record PATH`: save a reason for unread access failure. Blocking an already-read article is not allowed: resume from its extraction instead.

Inspect the returned state every time; do not infer a claim succeeded from exit status. Only the owning run may advance its claim. On restart, inspect `claimed` and `read` entries. A `read` entry resumes its owner run from the immutable extraction; an already `mined`/`rejected` entry is reused by reference without a new mining event. A stale claim requires explicit recovery of the original run after checking that no worker is active; never delete history or reset a read/mined record to unseen. Shared SQLite transactions coordinate local workers; do not put the database on a filesystem without reliable SQLite locking.

Also compare mined thesis/equity/horizon against prior idea inventory: distinct articles can repeat the same investment idea. Retain each source attribution, but link to an existing idea when the thesis matches. A material article revision keeps its article ID and goes through evidence-update handling; it does not count as a fresh discovery. Record first/last observation separately from first reading and completed mining.

Before release, prove repeated-run behavior by rechecking IDs (including at least one URL alias) after completion: each returns `claimed: false`, retained result paths are reused, and terminal event counts remain unchanged. This is a read-only deduplication check, not a second mining run. Save database exports and event history alongside the output for independent evaluation. Training uses one persistent isolated ledger across attempts; later attempts regenerate output from cached extractions/results and mine only genuinely unseen eligible articles.
