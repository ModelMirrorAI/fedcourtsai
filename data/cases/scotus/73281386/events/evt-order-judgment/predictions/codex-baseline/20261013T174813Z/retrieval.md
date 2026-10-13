# Retrieval beyond the provisioned inputs

## Committed base-rate material

- Read the merits section of `metrics/statpack.md` and the corresponding `merits.terms` entries of `metrics/statpack.json`.
- Selected `2016 <= term < 2026` and summed the rows with `jq`: 377 disturbed, 540 parsed, 590 granted, and 66 excluded; disturbed rate 0.6981481481481482. No target-case outcome was read from these aggregates.
- No `fedcourts query` or `fedcourts open-events` call was made; there are no ranged-corpus transfer lines to report.

## Web attempts

1. Search: `site.law.cornell.edu/supct/html 03-475 Cheney 542 U.S. 367 2004`.
2. In the same call, search: `site.supremecourt.gov about biographies current members Supreme Court`.
3. Attempted to open the Cornell Cheney opinion page, identified by path `/supct/html/03-475.ZO.html`.

These tool calls returned no usable content. They supplied no substantive evidence or target-case information.

## CourtListener MCP

1. `search(type="o", citation="542 U.S. 367", num_results=1)`: returned an irrelevant Singleton v. Astrue hit through the loose citation search. Disregarded; did not open that opinion or paginate the results.
2. `search(type="o", q="caseName:Cheney", court="scotus", filed_after="2004-06-23", filed_before="2004-06-25", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: identified *Cheney v. United States District Court for District of Columbia*, decided June 24, 2004, 542 U.S. 367; combined opinion 136997 and lead opinion 9434668.
3. `search_document(opinion_id=136997, query="vacat", snippet_size=750)`: checked the precedent's vacatur-and-remand remedy and the distinction from directing issuance of mandamus.
4. `search_document(opinion_id=9434668, query="necessary precondition", snippet_size=1700)`: checked the discussion at pp. 390–392 concerning separation of powers, privilege, and further appellate consideration.

All external substantive material concerned a historical precedent, not this case's subsequent history. No eventual target judgment, opinion, or coverage was sought or encountered.

## Operational reads

Read the task instructions and artifact schemas; used `fedcourts paths` to confirm the case/event locations. The first CLI attempt failed because the default uv cache was read-only; rerunning with a writable temporary cache succeeded. Schema and artifact validation are operational checks, not additional forecasting evidence.
