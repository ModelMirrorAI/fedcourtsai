# Retrieval log

Beyond the provisioned inputs (snapshot, `event.yaml`, `context.json`,
`petition.txt`, `questions-presented.txt`, `documents.json`) and the committed
`metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 5`
  - stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
  - Returned five recent resolved priors, mostly August 2026 substantive
    applications (all denied) — recency-ranked and not closely comparable to
    this cert petition; used only as a sanity check that recent low-salience
    SCOTUS matters resolve to denial. No `--full` hydration.

## CourtListener MCP lookups

- `search(type=o, court=ca4, docket_number=24-1166)` — 0 results: no opinion
  indexed for the decision below.
- `search(type=o, court=ca4, q="Defense Logistics Agency" Jones, filed_after=2025-01-01)`
  — 0 results: same check by party name.
- `search(type=d, court=ca4, docket_number=24-1166)` — 1 result: "William
  Jones v. Department of Defense", confirming the appeal below exists; its
  absence from the opinion index is consistent with an unpublished disposition.
- `search(type=d, court=vaed, case_name=Jones, q="Defense Logistics Agency")`
  — 4 results: the petitioner's EDVA suits (v. DLA 3:21-cv-00288, v. Austin
  3:22-cv-00118, v. Seiling 3:19-cv-00894, v. Del Toro 3:23-cv-00514),
  establishing a serial-litigant pattern.

## Web searches

None.

All retrieval was forward-legitimate pre-decision material; nothing about this
petition's own (nonexistent) disposition was sought or surfaced.
