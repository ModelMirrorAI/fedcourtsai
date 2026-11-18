Beyond the provisioned event, snapshot, and context, I consulted the prediction contract, output schemas, and committed metrics/statpack.md and metrics/statpack.json. Local arithmetic pooled the sal-v8 baseline reached rates for OT2017–OT2025: 655/12,662 = 0.05172958458379403. I read the relist, CVSG, amicus, modern-cert, and originating-court cuts as described in reasoning.md. No web or CourtListener lookup was attempted.

CLI attempts, including setup failures:

1. `uv run fedcourts paths --court scotus --docket 9026000646 --event evt-petition-arrival-disposition --role predictor` failed before execution: uv could not initialize its cache under /home/codexcell/.cache/uv because that filesystem is read-only. No corpus result or transfer line.
2. `uv run fedcourts query --help` failed for the same read-only cache reason. No corpus result or transfer line.
3. `uv --no-cache run fedcourts paths --court scotus --docket 9026000646 --event evt-petition-arrival-disposition --role predictor` succeeded, resolving the case, corpus identifier, and event path; it did not expose an outcome path.
4. `uv --no-cache run fedcourts query --help` succeeded and documented the structured filters.
5. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 5` returned Martin Mizrahi v. United States (25-1238), Azadeh Khatibi v. Yip (25-1240), Caryn Devins Strickland v. Moritz (25-1303), Katherine Novotny v. Moore (25-1324), and Byron C. Farley v. Merit Systems Protection Board (25-7485), all recorded denied November 16, 2026, before this cell's November 18 baseline. The Term mask selects docket Terms before 2026; this is a forward cell. None contained an opinion body. This outcome-filtered sample was not used to estimate a denial frequency or treated as a set of substantive analogues.

   Transfer report: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`.

No own-case disposition or other forecaster's prediction was sought or encountered. The validation command is an output check, not case retrieval.
