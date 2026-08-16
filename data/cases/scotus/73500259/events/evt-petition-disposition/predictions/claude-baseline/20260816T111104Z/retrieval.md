# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-16, event.yaml, context.json,
petition.txt, brief-in-opposition.txt, questions-presented.txt, documents.json)
and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "542 U.S. 155"` — attempted
   lookup of the Empagran prior (the controlling FTAIA precedent).
   - stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
   - Returned no rows; the tool's coverage note reported only 161 of 590,339
     scotus-scope rows carry citation data, so the empty result is a coverage
     gap, not an absence of the case.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted` —
   recent granted SCOTUS priors, for context on what distribution counts and
   docket shapes recent grants carried.
   - stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 20 rows (OT2025-era grants). Used only as shape context: several
     recent grants came at distribution counts 1–3 (e.g. Apple v. Epic,
     25-1311, granted at distribution_count 2), tempering the assumption that a
     grant always requires a further relist.

## CourtListener MCP

None. The provisioned documents were complete (petition, BIO, QP, full docket
to 2026-08-16) and the petition is pending until the 2026-09-28 conference.

## Web searches

None.
