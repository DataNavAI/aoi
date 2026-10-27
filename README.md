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

## Training a skill pair

Use [skill-trainer](skills/skill-trainer/SKILL.md) with a task skill path and a realistic task/input set. It runs a fresh task subagent, freezes its output, runs an independent evaluation subagent, and improves the task skill based on failures. It repeats until a verified pass, preserving iteration evidence and keeping the evaluator fixed. Training records stay outside this repository.

## v1 lineage

Inspected local AOI v1 at `/Volumes/Agent/Hermes/profiles/alphaaoi` (investment-research, portfolio-watch, and quant-for-agent skills) and `/Users/moonk/alpha-research-github`. V2 retains source traceability, falsifiable theses, and honest evidence gates. It does not import credentials, runtime state, broker execution, or the large qfa development workflow. V1 was left unchanged.
