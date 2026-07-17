# Retrieval log — scotus/73281346, evt-petition-disposition, claude-baseline, 20260717T000329Z

Forward-mode cell; retrieval beyond the provisioned inputs listed below.

## Corpus / statpack

- Read the committed `metrics/statpack.md` (and section listing of
  `metrics/statpack.json`) for the modern discretionary-cert base rates, the
  originating-circuit (ca10), relist-count, CVSG, and per-Term cuts. No
  salience-band section exists in the committed statpack.
- `uv run fedcourts query --court scotus --citation "City of Tahlequah v. Bond" --citation "Kisela v. Hughes" --citation "Graham v. Connor" --era 2020s --limit 8`
  → 0 rows. `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
- `uv run fedcourts query --court scotus --citation "595 U.S. 9" --citation "584 U.S. 100" --citation "490 U.S. 386" --citation "471 U.S. 1" --era 2020s --limit 8`
  → 0 rows. `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  → 5 rows, but all with null caption/topic/dates — not usable as similar
  priors. `ranged corpus reads: 145 GET(s), 37879808 byte(s)`

## CourtListener MCP

- `search(type=o, q="Burke v. Pitts qualified immunity", court=ca10, filed 2025-10-01..2025-12-31)`
  → confirmed the decision below: *Burke v. Pitts*, No. 24-5134, filed
  2025-11-04, Published (opinion id 10730384). No information about this
  petition's disposition was sought or surfaced (the petition is pending,
  distributed for the 9/28/2026 conference).

## Web searches

None.
