# Retrieval log — scotus/73331499 / evt-petition-disposition / claude-baseline / 20260718T000130Z

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  - stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
  - Purpose: recent resolved SCOTUS cert priors for context (dispositions,
    distribution counts, salience scores of granted vs. denied 2020s
    petitions). Broad filter only — the corpus carries no topic facet on
    SCOTUS rows, so no DNA/Fourth-Amendment-specific prior retrieval was
    possible through it.

## Base rates

- Read the committed `metrics/statpack.md`: "Modern discretionary-cert
  petitions by disposition", relist-count, CVSG, originating-court, and
  per-Term tables (Terms 2023–2025 est. grant rates 3.3% / 3.0% / 2.5%).

## CourtListener MCP

- `search(type=d, court=scotus, docket_number=25-1277)` — attempted twice
  (~00:03 and ~00:06 UTC), both returned HTTP 429 (rate limit exceeded:
  1200/day, shared quota). A third attempt after the throttle window cleared
  succeeded but returned 0 search-index hits for the docket.
- `call_endpoint(dockets, court=scotus, docket_number=25-1277)` — succeeded:
  returned docket id 73331499, "Scott R. Williams v. Pennsylvania",
  date_filed 2026-05-12, **date_terminated null** — confirming the petition
  is still pending (the forward cell is not mis-provisioned). CourtListener
  carries no SCOTUS docket-entry detail here, so the waiver/CFR question
  could not be resolved beyond the provisioned snapshot.

## Web searches

- None.
