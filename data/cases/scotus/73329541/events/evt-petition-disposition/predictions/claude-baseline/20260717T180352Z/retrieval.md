# Retrieval log — scotus/73329541 evt-petition-disposition (claude-baseline, 20260717T180352Z)

Mode: `forward` (retrieval unrestricted; nothing outcome-revealing exists yet).

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 5` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:`
  line was printed (the query never reached the corpus). No retry; degraded to
  the committed statpack per the prompt contract.
- Read the committed `metrics/statpack.md` and `metrics/statpack.json`
  (per-Term fee-class detail: Term 2025 paid grant rate ~5.4%, IFP ~1.1%;
  originating-circuit, relist, and CVSG cuts). Note: the statpack contains no
  "Segment base rate by salience band" table.

## CourtListener MCP lookups (4 calls)

1. `search(type=o, court=scotus, q="Bowe v. United States 2244 2255", filed_after=2025-10-01)`
   → confirmed *Bowe v. United States*, No. 24-5438, decided 2026-01-09,
   Published. Verifies the petition's central authority and its date.
2. `search(type=o, court=ca10, q="St. Clair certificate of appealability 2241 executive agreement", filed_after=2025-01-01)`
   → 0 results; the Tenth Circuit's unpublished COA-denial order (No. 24-7090)
   is not in the opinions index. Relied on the petition and its appendix
   description for the decision below.
3. `search(type=d, court=scotus, docket_number=25-1274, q="St. Clair")`
   → 0 results; the SCOTUS docket is not in RECAP, so the provisioned
   snapshot is the docket state of record for this cell.
4. `search(type=o, court=scotus, case_name="Bowe v. United States", q="Bowe")`
   → majority author Sonia Sotomayor; the indexed syllabus field was empty,
   so *Bowe*'s holding is taken from the petition's characterization plus
   model knowledge (the certiorari-bar provision of § 2244 does not apply to
   § 2255 proceedings).

No web searches were used. No lookup touched this case's own disposition
(none exists; the petition is pending, distributed for the 2026-09-28
conference).
