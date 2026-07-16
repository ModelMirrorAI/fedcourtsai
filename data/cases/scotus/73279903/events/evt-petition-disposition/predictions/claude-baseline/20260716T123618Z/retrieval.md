# Retrieval log — scotus/73279903 / evt-petition-disposition / claude-baseline / 20260716T123618Z

## Provisioned inputs (baseline)

- `record/snapshots/2026-07-16.json` (supremecourt.gov docket JSON for No. 25-776, generated 2026-07-10)
- `record/documents/questions-presented.txt`, `petition.txt` (truncated at 186 pp.), `brief-in-opposition.txt`, per `documents.json`
- `events/evt-petition-disposition/event.yaml`, `record/context.json` (mode: forward)

## Corpus tooling

- `metrics/statpack.md` and `metrics/statpack.json` (committed) — modern discretionary-cert base rates, per-Term paid/IFP grant rates, relist-count and CVSG cuts, originating-circuit cuts.
- `uv run fedcourts query --court scotus --citation "582 U.S. 449" --citation "596 U.S. 767" --citation "565 U.S. 171" --citation "591 U.S. 732" --era 2020s`
  - stderr: `ranged corpus reads: 418 GET(s), 109510656 byte(s)` — returned no matching priors.
- `uv run fedcourts query --court scotus --era 2020s --limit 8 --topic "First Amendment"`
  - stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)` — returned no matching priors.

## CourtListener MCP lookups (forward mode; companion-case context only — never this case's own docket state or disposition)

1. `search` (type=d, court=scotus, docket_number=25-581) — 0 results (SCOTUS dockets sparse in search index).
2. `search` (type=d, court=scotus, case_name="St. Mary Catholic Parish") — 0 results.
3. `call_endpoint` dockets (court=scotus, docket_number=25-581) — found docket 73279026, *St. Mary Catholic Parish v. Roy*, filed 2025-11-17, `date_terminated: null`.
4. `call_endpoint` dockets (id=73279026, extended fields) — `date_cert_granted: null`, `date_cert_denied: null`, `date_argued: null`: the companion petition remains pending ~8 months after docketing.
5. `search` (type=d, court=scotus, q="Union Gospel Mission") — 0 results (checked whether Washington had petitioned from *Union Gospel Mission of Yakima v. Brown*, 162 F.4th 1190 (9th Cir. 2026); inconclusive, not pursued further).

## Web searches

None.
