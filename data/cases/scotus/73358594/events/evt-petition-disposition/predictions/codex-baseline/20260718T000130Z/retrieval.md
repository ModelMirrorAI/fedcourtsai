# Retrieval

## Corpus and base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, specifically modern discretionary-cert disposition, originating-circuit, relist, CVSG, per-Term, and paid/IFP cuts.
- Ran `uv run fedcourts query --court scotus --era 2020s --limit 10` (with the runner cache redirected to `/tmp`).
  - `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
  - The results supplied recent resolved SCOTUS priors and their procedural-signal fields; no result concerned this case.

## CourtListener MCP

- Searched opinions for `"5 U.S.C. § 2302(b)(8)"`, restricted to SCOTUS and filed before July 18, 2026. The two results were *Department of Homeland Security v. MacLean* (2015) and *Garcetti v. Ceballos* (2006).
- Searched opinions for `"gross mismanagement" AND "2302(b)(8)(A)(ii)"`, filed before July 18, 2026. The results included MSPB and Federal Circuit applications but revealed no square Supreme Court authority on the petition's claimed omission.
- Looked up `877 F.3d 200`, identifying *Flynn v. United States Securities & Exchange Commission*, Fourth Circuit, December 7, 2017, and opinion ID 4226778.
- Looked up `880 F.3d 913`, identifying *Adam Delgado v. Merit Systems Protection Board*, Seventh Circuit, January 29, 2018, and opinion ID 4239969.
- Retrieved the opinion text for CourtListener opinion ID 4226778 to examine *Flynn*'s issue and disposition.
- Retrieved the opinion text for CourtListener opinion ID 4239969 to examine *Delgado*'s exhaustion holding and circuit identity.

No web search was used, and I did not search for this petition's disposition or subsequent history.
