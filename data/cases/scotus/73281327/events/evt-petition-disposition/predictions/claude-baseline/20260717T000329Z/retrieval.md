# Retrieval log — scotus/73281327 / evt-petition-disposition / claude-baseline / 20260717T000329Z

Mode: `forward` (per `record/context.json`); retrieval unrestricted.

## Corpus tooling

- `uv run fedcourts query --court scotus --topic "Video Privacy Protection Act" --limit 5`
  → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- `uv run fedcourts query --court scotus --topic "privacy" --limit 5`
  → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- `uv run fedcourts query --court scotus --topic "held pending" --limit 5`
  → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- `uv run fedcourts query --court scotus --topic "statutory interpretation" --limit 3`
  → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- `uv run fedcourts open-events --court scotus --docket 73281327`
  → `evt-petition-disposition` (confirms the open event).
- Read the committed `metrics/statpack.md` for base rates: modern
  discretionary-cert grant rate ~2.5–3% (per-Term table, Terms 2023–2025);
  D.C. Circuit-originating petitions granted 11.8% (denial-reweighted cut);
  relist-count and CVSG cuts noted (0 relists parsed for this docket; no CVSG).

## CourtListener MCP

- `search(type=d, court=scotus, docket_number="25-459")` → 0 results
  (CourtListener does not index this SCOTUS docket).
- `search(type=d, court=scotus, q="Salazar Paramount")` → 0 results.
- `search(type=d, q="Salazar v. Paramount Global")` → 48 results; confirmed the
  Sixth Circuit docket (23-5748) and the M.D. Tenn. origin (3:22-cv-00756).
  No SCOTUS-side status available via CourtListener; the *Salazar* cert grant
  (Jan. 26, 2026) is instead confirmed on the face of both provisioned briefs.

No web searches. No retrieval touched this case's own post-snapshot docket
state or disposition.
