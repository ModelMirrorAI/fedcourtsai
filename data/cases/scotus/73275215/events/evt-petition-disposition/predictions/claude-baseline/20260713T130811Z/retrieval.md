# Retrieval log — scotus/73275215 / evt-petition-disposition / claude-baseline / 20260713T130811Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-07-13.json`,
`events/evt-petition-disposition/event.yaml`, `record/context.json`):

- **Committed statpack** — read `metrics/statpack.md` for SCOTUS base rates
  (modern discretionary-cert disposition split, per-Term table). Noted that no
  section covers mandatory § 1253 appeals, so the cert base rates were treated
  as context only.
- **Corpus priors (ranged)** —
  `uv run fedcourts query --court scotus --corpus-backend ranged --limit 8`
  → stderr: `ranged corpus reads: 408 GET(s), 106954752 byte(s)`.
  Returned recent resolved SCOTUS cert dockets (June 2026 grants/denials);
  none were mandatory appeals or redistricting holds, so they informed general
  disposition context only.
- **Repo source consulted for label conventions** (local files, not network):
  `src/fedcourtsai/pipeline/cert_signals.py` (GVR → `granted` mapping) and
  `src/fedcourtsai/pipeline/outcome.py` (decided-docket routing).

No CourtListener MCP calls, no REST fallback calls, and no web searches were
made. In particular, nothing was retrieved about this case's own disposition
or subsequent history: the disposition was already present in the provisioned
snapshot itself (disclosed in `reasoning.md` and `flags.json`).
