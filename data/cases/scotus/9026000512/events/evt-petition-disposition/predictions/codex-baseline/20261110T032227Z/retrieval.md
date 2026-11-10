# Retrieval log

## Corpus and local tooling

- Attempted `uv run fedcourts paths --court scotus --docket 9026000512 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help`. Both failed before execution because uv could not write its default cache at `/home/codexcell/.cache/uv/CACHEDIR.TAG`. No corpus records were returned.
- Repeated both commands with `UV_CACHE_DIR=/tmp/uv-cache`. Paths resolved correctly; the realized outcome remained explicitly evaluator-only and was not opened. Query help described the structured filters. These were setup calls, not prior retrievals, and printed no transfer lines.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era roberts --limit 3`. Rejected because `roberts` is not a valid decade token; the usage message supplied the valid vocabulary. No prior rows or transfer line returned.
- Successful lookup: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026-11-10 --limit 3`.
  - Stderr: `note: replay cutoff 2026-11-10 (from --decided-before) — priors that had not resolved by then are excluded, on top of any --decided-before Term`.
  - Transfer: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`.
  - Returned Robert J. Jesenik v. United States (25-7515), Andrew N. MacRitchie v. United States (25-7522), and Tauno Waidla v. Christopher Pierce, Warden (25-7555), each denied November 9, 2026. These are generic criminal denials, not issue-matched precedents. No opinion bodies were requested; no quantitative adjustment was based on this outcome-selected sample. This is a forward cell; the voluntarily supplied date limit was a precaution, not a claim that its mode is replay.
- Read committed `metrics/statpack.md`, specifically modern cert dispositions, paid-segment relist/CVSG/amicus cuts, and sal-v8 per-Term band rates. Used the provisioned context's frozen 5.1588% reached-band anchor. No corpus aggregate command or install was attempted.

## General legal research

- Web search batch attempted: `site.law.cornell.edu/uscode/text/28/1257 final judgments highest court state` and `site.supremecourt.gov/opinions "Currier" "2018" "issue preclusion"`. The tool returned no usable content. No claims were derived from it.
- Web open attempted for the Cornell page for 28 U.S.C. section 1257. The tool returned no usable content. No statutory verification is attributed to that attempt.
- CourtListener MCP `search(type="o", citation="431 U.S. 651", num_results=1)` returned an irrelevant first result, Kachina v. Roy, a 2013 denial. Disregarded; the citation-field lookup was not an exact case match.
- CourtListener MCP `search(type="o", case_name="Abney v. United States", court="scotus", filed_before="1978-01-01", num_results=1)` returned Abney v. United States, 431 U.S. 651 (1977), opinion 109677, decided June 9, 1977.
- CourtListener MCP `search_document(opinion_id=109677, query="1291", snippet_size=600)` confirmed that Abney addresses immediate federal appellate review of pretrial double-jeopardy orders, under section 1291.
- CourtListener MCP `search_document(opinion_id=109677, query="1257", snippet_size=1000)` supplied its discussion of state pretrial former-jeopardy rulings, Harris v. Washington, and the statutory finality language. This check prevents treating lack of sentencing as an invariably conclusive barrier in every double-jeopardy case.

No search sought this petition's disposition, current docket, subsequent history, or coverage of its outcome. No other prediction or evaluation was read.
