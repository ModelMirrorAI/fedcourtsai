# Retrieval log

Beyond the provisioned inputs (snapshot, questions-presented, petition, BIO,
event definition) and the committed `metrics/statpack.md`:

1. Corpus query for recent granted-petition priors, to compare this case's
   signal profile against what recent grants look like:

   ```
   uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5
   ```

   stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`

   Result: five recent grants (Monsanto v. Salas, Monsanto v. Johnson,
   Petersen v. Doe, Davis v. United States, Viramontes v. Cook County) — all
   with multiple conference distributions and/or prominent Supreme Court
   counsel, consistent with the statpack's relist-count signal. Used as
   contrast for the negative signals in this petition.

No CourtListener MCP lookups and no web searches were made — the provisioned
record (petition, BIO with the remittitur-hearing transcript, docket snapshot)
was complete and sufficient, and the case's conference date (2026-09-28)
post-dates this run.
