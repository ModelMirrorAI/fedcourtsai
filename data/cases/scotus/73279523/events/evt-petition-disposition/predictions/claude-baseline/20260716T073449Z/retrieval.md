# Retrieval log — scotus/73279523 · evt-petition-disposition · claude-baseline · 20260716T073449Z

Mode: `forward` (record/context.json) — retrieval unrestricted; nothing
postdating the 2026-07-16 snapshot was used.

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "TransUnion LLC v. Ramirez" --citation "594 U.S. 413" --corpus-backend ranged`
   - stderr: `ranged corpus reads: 417 GET(s), 109117440 byte(s)`
   - Returned no rows.
2. `uv run fedcourts query --court scotus --disposition dismissed --era 2020s --corpus-backend ranged`
   - stderr: `ranged corpus reads: 232 GET(s), 60620800 byte(s)`
   - Returned dismissed-petition priors; used *Elephant Insurance Co. v.
     Holmes* (scotus/73281371, No. 25-1085, dismissed 2026-05-21 without
     conference action) as a settlement-dismissal pattern match.

## Base rates

- Committed `metrics/statpack.md`: modern discretionary-cert grant rate
  (~2.5–3% recent Terms), CA6-originating cut (granted 3.5%), relist-count
  cuts (2-relist bucket granted 33.6%), per-Term table. (No
  salience-band table is present in the committed statpack.)

## CourtListener MCP

- None used (provisioned documents and snapshot were sufficient; budget
  conserved).

## Web

1. WebSearch: `Cleveland Pickett water lien settlement Supreme Court petition defer 2026`
   - Surfaced SCOTUSblog case page, supremecourt.gov filings, NAACP LDF case
     page, and Cleveland Scene settlement report.
2. WebFetch: https://www.clevescene.com/news/cleveland-news/cleveland-water-lawsuit-settelment/
   - Article dated **May 7, 2026** (pre-snapshot): Cleveland agreed to a
     $3M settlement ($1.8M class damages, $1.2M fees, $14K per named
     plaintiff); Law Director stated commitment on the record in district
     court; details being finalized. This predates the snapshot and does not
     reveal the (still-nonexistent) petition disposition; treated as
     legitimate forward signal and flagged as decisive in flags.json.
