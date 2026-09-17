# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   Returned mostly OT2025 substantive applications and a few granted paid
   petitions (Second Amendment and land-use dockets); no oath or warrant
   precedent. Did not inform the number.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned recent denied applications, largely capital stay applications. Did
   not inform the number.

## CourtListener MCP lookups (forward mode, unrestricted)

3. `call_endpoint docket-entries` for docket 73281687, newest first: 0 results
   (RECAP carries no entries for this supremecourt.gov docket).
4. `search type=d court=scotus` for petitions referencing *Jones v. United
   States*, "Oath or affirmation", hearsay, warrant, filed after 2024-01-01:
   0 results. No companion petition found.
5. `search type=d court=scotus docket_number=25-1205`: 0 results.
6. `search type=o court=ca10 case_name="Mendenhall v. City and County of
   Denver"` filed after 2025-12-01: 0 results (the order and judgment is
   unpublished; its content is summarised in the petition appendix references
   and the BIO).

None of the lookups surfaced this petition's disposition or any docket entry
after the provisioned snapshot.

## Committed base rates

`metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
"by originating circuit", "by relist count (paid scored segment)", "by CVSG
status (paid scored segment)", "by salience band", and "Segment base rate by
salience band (sal-v4)" pooled over Terms 2017 through 2024.

No web searches.
