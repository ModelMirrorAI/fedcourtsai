# Retrieval record

## Committed base-rate inputs

- Read `metrics/statpack.md`: modern cert, originating circuit, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table.
- Read relevant `metrics/statpack.json` fields for exact prior-Term baseline reached rates and denominators. Pooled all displayed 2017–2024 rows with `jq`: 593 / 11,580 = 0.05120898100172712.
- `git log -1 --format='%cs %h' -- metrics/statpack.md` returned `2026-09-14 55121cdb8`; this dates the committed file, not the corpus's newest pull.

## Corpus tools

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`: failed because the service backend has no client-side connection. No corpus-wide pull or stored-snapshot vintage was returned.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '455 U.S. 209' --decided-before 2025 --limit 1`: no prior returned.
  - Exact transfer line: `ranged corpus reads: 1357 GET(s), 355663872 byte(s)`.
  - Coverage note: only 200 of 590919 SCOTUS rows in scope carry citation data; the filter is for a case's own citations, not a citing-case graph. No sparse-filter retries were made.

## CourtListener MCP

1. `search(type="o", citation="503 F.3d 755", num_results=2)`: found *Fields v. Brown*, decided September 10, 2007, with lead opinion 9565854.
2. `search_document(opinion_id=9565854, query="similar", snippet_size=700)`: reviewed majority discussion of the similar-experience argument and the circuit's extreme-circumstances approach. Some multi-match output was truncated; no claim relies on unseen text.
3. `search_document(opinion_id=9565854, query="We decline", snippet_size=1300)`: read the majority's refusal to imply bias and its discussion of honest disclosure and follow-up.
4. `search(type="o", citation="455 U.S. 209", num_results=1)`: returned unrelated *DIRECTV, Inc. v. Trone* metadata, not the intended precedent; not used substantively.
5. `search(type="o", case_name="Smith v. Phillips", court="scotus", num_results=3)`: returned similarly named cases' metadata, not the intended 1982 opinion; not used substantively.
6. `search(type="o", case_name="Smith v. Phillips", court="scotus", filed_after="1982-01-01", filed_before="1982-12-31", num_results=3)`: identified the February 22, 1982 decision, opinion 110645, 455 U.S. 209.
7. `search_document(opinion_id=110645, query="extreme", snippet_size=800)`: read Justice O'Connor's concurrence describing extreme cases of implied bias.

## Web attempts

- Searched `site.gov "Smith v. Phillips" "455" "209"` and `site.ca9.uscourts.gov "Fields v. Brown" "503" "755" "bias"`. The tool returned no usable content.
- Attempted to open `https://tile.loc.gov/storage-services/service/ll/usrep/usrep455/usrep455209/usrep455209.pdf`. The tool returned no usable content. No web-derived substantive evidence entered the prediction.

## Local operations

Read the task instructions and output schemas, resolved the event with `fedcourts paths --court scotus --docket 73500216 --event evt-petition-disposition --role predictor`, and read the provisioned inputs. The first unmodified `uv run` failed because its default cache was read-only; subsequent commands used a writable temporary cache. These operations did not retrieve any case outcome. No live lookup targeted this petition's current state or subsequent history.
