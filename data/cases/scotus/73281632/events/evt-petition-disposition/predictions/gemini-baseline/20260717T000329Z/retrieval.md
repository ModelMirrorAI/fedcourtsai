# Retrieval Log

**CourtListener MCP Searches:**
- `search` for `"Federal Housing Finance Agency" AND "Appropriations Clause"`
- `search` for `"Federal Housing Finance Agency" AND "Appropriations Clause" AND "Collins v. Treasury"`
- `search` for `"Federal Housing Finance Agency" AND "Appropriations Clause"` with `filed_after="2024-05-16"`
- `call_endpoint` on `opinions` for `id=11234854` to read the lower court's opinion in *Daisey Trust*.

**Corpus CLI Queries:**
- Attempted `uv run fedcourts query --court scotus "Federal Housing Finance Agency funding constitutionality appropriations clause"`, which failed due to incorrect syntax.
- Attempted `uv run fedcourts query --court scotus "CFPB v. CFSA Appropriations Clause"`, which failed similarly.
- `uv run fedcourts query --help` to check syntax.
- Read `metrics/statpack.md` using `cat metrics/statpack.md | grep -A 30 "Modern discretionary-cert petitions"` to obtain base rate statistics for the Ninth Circuit.

No other retrieval was performed beyond the provisioned inputs and the searches listed above.