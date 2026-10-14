# Retrieval beyond provisioned case inputs

- Read the committed `metrics/statpack.md` modern discretionary-cert, originating-circuit, paid relist/CVSG and salience-band sections, and `metrics/statpack.json` for unrounded prior-Term state reached-rate pooling. Used jq to pool sal-v4 state prefix rates for Terms 2017–2025: 99 implied grants / 421 weighted resolved = 0.23515439429928742. No individual corpus cases were queried.
- Ran `git log -1 --format='%cs %h' -- metrics/statpack.md` to identify the committed pack's latest change: October 13, 2026, commit cf9ae960e. This is file vintage, not a fresh corpus read.
- Web search attempt 1: `Pitchess v Davis 421 U.S. 482 1975 conditional writ habeas retrial jurisdiction exhaustion` and `Gentry v Deuth 456 F.3d 687 conditional writ compliance jurisdiction`. The tool returned no visible results; no material from these searches informed the forecast.
- Web search attempt 2: `site.supreme.justia.com Pitchess Davis 421 482`. Again no visible results.
- CourtListener MCP `search(type="o", citation="421 U.S. 482", num_results=1)`: unexpectedly returned an unrelated Seventh Circuit Medtronic opinion, 421 F.3d 482. Disregarded it; did not read its full text.
- CourtListener MCP `search(type="o", case_name="Pitchess v. Davis", court="scotus", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])`: identified Pitchess, decided May 19, 1975, opinion 109256.
- CourtListener MCP `read_document(opinion_id=109256)`: consulted the opinion's facts and holding concerning the new unexhausted claim and the restriction on continuing supervision following a conditional writ. This is an unrelated historical precedent, not the present Davis/Smith petition.

No `fedcourts query` or `open-events` calls were made, so there are no ranged-corpus transfer lines. No current target docket, target disposition, subsequent history, other predictor output, or labeling-measurement artifact was retrieved.

Administrative reads covered the task instructions and output schemas. `uv run fedcourts paths --court scotus --docket 9026000176 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only; it succeeded with `UV_CACHE_DIR=/tmp/uv-cache`. This command resolves local paths rather than retrieving case facts.
