# Retrieval log — scotus/73500218 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Forward-mode cell; retrieval unrestricted. Consulted beyond the provisioned
snapshot and event definition:

## Corpus tooling

- `uv run fedcourts query --court scotus --limit 8` (free-text stdin:
  "petition for writ of mandamus pro se extraordinary writ In re")
  - stderr: `ranged corpus reads: 432 GET(s), 113246208 byte(s)`
  - Result: surfaced recent salient cert cases (Monsanto, Petersen, ATF
    cases), no mandamus-alike priors — relevance ranking has no
    extraordinary-writ signal. Not used in the estimate.
- Committed `metrics/statpack.md` (base rates): modern discretionary-cert
  disposition split (~2.5–3% grant, Terms 2023–2025), relist-count buckets
  (relist-0: 97.3% denied / 0.8% granted), CVSG split, per-Term table. No
  salience-band section exists in this statpack build.

## CourtListener MCP

- `search(type=d, q="Joan Farr", order_by=dateFiled desc)` — free-text query;
  matches were mostly irrelevant (indexed-text hits). Not used.
- `search(type=d, party_name="Joan Farr", order_by=dateFiled desc)` —
  identified the underlying case *Farr v. Grant*, W.D. Mo. 4:24-cv-00439
  (§ 1983, filed 2024-07-01, terminated 2024-12-16; parties match this
  petition's respondents) and the petitioner's prior pro se suits
  (*Farr v. United States Government*, D. Kan. 2:21-cv-02183 and
  2:22-cv-02476; *Farr v. Curry*, D. Kan. 2:22-cv-02120). Used to establish
  posture and filer history. No information about this petition's own
  disposition was sought or surfaced.

## Web searches

None.
