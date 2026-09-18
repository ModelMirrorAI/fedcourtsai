# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned eight recent granted rows (four substantive applications, four cert petitions), none on Parker immunity; the corpus carries no text or topic filter on SCOTUS rows, so this served only as a sanity check on the shape of recent grants and did not move the forecast.

## CourtListener MCP

1. `search` type=o, court=ca4, q="Cherry Grove Beach Gear" — confirmed the decision below (cluster 10765510, No. 24-2161, filed 2025-12-23) is a **published** opinion.
2. `search` type=o, court=scotus, filed_after=2010-01-01, q=`"state-action immunity" OR "state action immunity" Parker "clear articulation"`, newest first — three hits: Jones v. Mississippi (false positive), N.C. State Bd. of Dental Examiners v. FTC (2015), FTC v. Phoebe Putney (2013). Confirms that the Court's Parker merits docket since 2010 consists of two FTC-brought cases.

No lookup of this docket's own CourtListener record and no web searches. Committed `metrics/statpack.md` read for base rates (not a retrieval call).
