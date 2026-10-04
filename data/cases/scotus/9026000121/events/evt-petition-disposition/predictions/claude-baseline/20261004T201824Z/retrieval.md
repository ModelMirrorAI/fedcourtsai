# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   Returned eight rows, mostly 25A/26A substantive applications and two cert
   dockets (one federal-petitioner immigration case, one private family-law
   case). Not a comparable set for a private state-court Caperton petition;
   used for shape only.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 8`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned eight rows, all substantive applications. Not used beyond
   confirming the filter's coverage.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
  "Cert petitions by relist count (paid scored segment)", "Cert petitions by
  CVSG status (paid scored segment)", "Petitions by originating court (incl.
  state courts)", "SCOTUS cert petitions by Term", and "Segment base rate by
  salience band (sal-v4)". Anchor: `baseline` bracketed `reached` rate pooled
  over OT2017-OT2025, about 5.0 percent.

## CourtListener MCP

1. `search type=d court=scotus docket_number=26-121` — 0 results; the docket is
   not yet indexed on CourtListener.
2. `search type=o court=scotus q='Caperton "due process" recusal "senior judge" OR "retired judge" certiorari' filed_after=2016-01-01` — 1 result,
   Williams v. Pennsylvania, 579 U.S. 1 (2016), already cited in the petition.
3. `search type=o court=[md, mdctspecapp] case_name=Basso filed_after=2017-01-01` —
   1 result: Basso v. Campos, 233 Md. App. 461 (2017), the published reversal
   of the first directed verdict. The 2025 unreported Appellate Court
   opinion and the 2026 Maryland Supreme Court per curiam dismissal are not
   indexed, so the account of the decisions below rests on the petition and
   its appendix as provisioned.

No web searches. Nothing retrieved surfaced this case's disposition.
