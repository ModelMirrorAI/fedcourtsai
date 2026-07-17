# Retrieval log — scotus/73272491 · evt-petition-disposition · claude-baseline · 20260717T180352Z

## Provisioned inputs (read first)

- `record/snapshots/2026-07-17.json` (baseline snapshot)
- `record/documents/questions-presented.txt`, `record/documents/petition.txt`
  (221 pp., truncated), `record/documents/documents.json` — no
  brief-in-opposition provisioned (respondent waived; response now due
  2026-08-14 after a granted extension)
- `record/context.json` (mode: forward)
- Committed base rates: `metrics/statpack.md` and `metrics/statpack.json`
  (per-Term paid/IFP grant rates; relist and CVSG cuts; note: this build has no
  salience-band section)

## Corpus lookups (`fedcourts`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   — stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
   (recent granted-petition priors: distribution/relist patterns preceding
   grants, e.g. 3–4 distributions typical before a grant order)

## CourtListener MCP lookups (forward mode — unrestricted)

1. `search` (opinions, scotus, filed after 2025-10-01):
   `Ellingburg restitution "criminal punishment"` → confirmed *Ellingburg v.
   United States*, No. 24-482, decided 2026-01-20 (cluster 10776751)
2. `get_endpoint_item` clusters/10776751 → majority author Brett Kavanaugh;
   no syllabus text in the record
3. `search` (opinions, scotus): `"Burnett v. United States"` after 2025-06-01
   → 0 results (dissents from cert denial not indexed as opinions)
4. `search` (opinions, scotus): `Libretti forfeiture Apprendi denial certiorari`
   → 0 results

No web searches. No lookup touched this petition's own disposition (none
exists; the case is pending with the BIO due 2026-08-14).
