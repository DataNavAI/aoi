# AOI v2 — Alpha Obsessed Investor

A personal investment research agent skill library: four task skills paired with four outcome evaluators.

| Requirement | Task | Evaluation |
| --- | --- | --- |
| Develop ideas | [aoi-develop-ideas](skills/aoi-develop-ideas/SKILL.md) | [aoi-develop-ideas-eval](skills/aoi-develop-ideas-eval/SKILL.md) |
| Update ideas daily | [aoi-update-ideas](skills/aoi-update-ideas/SKILL.md) | [aoi-update-ideas-eval](skills/aoi-update-ideas-eval/SKILL.md) |
| Review unexecuted ideas | [aoi-review-ideas](skills/aoi-review-ideas/SKILL.md) | [aoi-review-ideas-eval](skills/aoi-review-ideas-eval/SKILL.md) |
| Send daily email | [aoi-send-daily-report](skills/aoi-send-daily-report/SKILL.md) | [aoi-send-daily-report-eval](skills/aoi-send-daily-report-eval/SKILL.md) |

Every AOI skill uses the shared [research contract](docs/research-contract.md). Keep this repository layout intact when loading skills; copying a skill folder alone omits that dependency. Point the agent at the relevant SKILL.md and evaluate its frozen output with the paired evaluator. A revision creates a new version and evaluation.

Daily flow: discover → evaluate; update all tracked ideas → evaluate; review eligible past forecasts → evaluate; compose email → pre-send evaluation → authorized send → delivery verification. Discovery need not produce a new idea every day. Research and evaluation artifacts belong in a separate private data root.

Before unattended use, configure the equity universe, investment constraints, data root, source access, market-data providers, benchmark/return conventions, reporting timezone, recipients, delivery authorization, and schedule. Missing research inputs remain explicit; missing delivery configuration leaves a complete draft. This repository does not install jobs, connect accounts, send messages, or trade.

Idea discovery mines only Seeking Alpha’s latest trending analysis. It keeps article-ID history outside Git to avoid mining an analysis twice and scores ideas using a fixed evidence-linked rubric. Default local data root: `/Volumes/Agent/AOI-data`; training uses a separate declared ledger.

The human-readable research library starts at `<data-root>/INDEX.md`, with one `ideas/<idea-id>/IDEA.md` per retained idea. The index separates complete scores from incomplete subtotals and links directly to each idea’s thesis, evidence, score, risks and next checks.

## Training a skill pair

Use [skill-trainer](skills/skill-trainer/SKILL.md) with a task skill path and a realistic task/input set. It runs a fresh task subagent, freezes its output, runs an independent evaluation subagent, and improves the task skill based on failures. It repeats until a verified pass, preserving iteration evidence and keeping the evaluator fixed. Training records stay outside this repository.

## v1 lineage

Inspected local AOI v1 at `/Volumes/Agent/Hermes/profiles/alphaaoi` (investment-research, portfolio-watch, and quant-for-agent skills) and `/Users/moonk/alpha-research-github`. V2 retains source traceability, falsifiable theses, and honest evidence gates. It does not import credentials, runtime state, broker execution, or the large qfa development workflow. V1 was left unchanged.

## Static idea browser

Build an offline-capable website from the Markdown idea library with Python 3.10+ and no extra packages:

```bash
python3 scripts/build_idea_site.py --serve
```

Defaults: source `/Volumes/Agent/AOI-data`, output `/Volumes/Agent/AOI-data/site`. `--serve` prints a local browser URL (default `http://127.0.0.1:8000`) and serves only the generated directory on loopback; Ctrl-C stops it. Use `--port 0` for an available port. Omit `--serve` to generate files only; you can open `index.html` directly in a regular browser. Browser-tool QA used localhost because its URL policy blocks direct `file://` navigation. Search covers ticker, thesis, evidence and risks; filters separate eligible, incomplete, ineligible and closed ideas. Select an idea to read it, jump between sections, download its source note, or print it. Hash links preserve the selected idea/section. Incomplete subtotals remain explicitly incomplete and are never substituted for full scores.

For another library/output location:

```bash
python3 scripts/build_idea_site.py --source /path/to/research --output /path/to/generated-site
```

The builder reads `ideas/*/IDEA.md`, optional `current-snapshot-index.json` (or `current-idea-index.json`), current snapshots and `score-table.json`. Without score metadata it shows “Not scored.” It supports headings, paragraphs, lists, tables, links, emphasis, code and quotes; raw HTML is escaped. Referenced local Markdown is rendered into reading pages; supported JSON/text/CSV/PDF references are copied inside the generated site. References outside the source root and unsupported URL schemes are blocked. No external JavaScript, fonts, telemetry or background data fetching is used; all application assets ship with the generated site. Clicking external source links still opens their websites.

Rebuild after updating ideas. Source research is read-only. An atomic build replaces only a generator-owned output directory; it refuses to overwrite unrelated output files. Keep generated research sites outside Git. Generated sites contain private research copies—this script performs no upload or hosting.

Run the behavioral checks with `python3 -m unittest discover -s tests -v`.
