# Retrieval log — scotus/73358839 evt-petition-disposition (claude-baseline, 20260718T000130Z)

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`. Used to eyeball
  recent granted-cert priors (distribution/relist counts on grants).

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition",
  originating-circuit, relist-count, CVSG, and per-Term tables. (This statpack
  version carries no "Segment base rate by salience band" table.)

## CourtListener MCP lookups

- `search` (type=d, court=scotus, docket_number=25-1201) — 0 results (SCOTUS
  companion docket not in RECAP).
- `search` (type=d, court=ca5, docket_number=24-40792) — Texas Top Cop Shop v.
  Blanche, CA5 docket 69450356, `dateTerminated: null` — the Fifth Circuit
  appeal is still pending, confirming the cert-before-judgment posture is live.

## Web searches (forward mode — unrestricted)

- "Supreme Court docket 25-1201 Corporate Transparency Act cert petition" —
  identified No. 25-1201 as National Small Business United v. Bessent (filed
  2026-04-15); Tax Notes, supremecourt.gov PDFs, CIR case page.
- "Texas Top Cop Shop Supreme Court 25-1290 rescheduled conference July 2026
  Corporate Transparency Act cert" — CIR case page reporting the Court is
  weighing the two CTA petitions together for next Term; no post-snapshot
  docket activity surfaced.
- "National Small Business United v. Bessent Eleventh Circuit Corporate
  Transparency Act decision 2026 cert petition" — Eleventh Circuit upheld the
  CTA on 2025-12-16 (Holland & Knight, Thomson Reuters, Transparency
  International summaries); Thomson Reuters: both CTA petitions still pending
  as the SCOTUS Term wrapped up.

No search surfaced any disposition of this petition itself; the cell is a
genuine forward prediction.
