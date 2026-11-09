# Retrieval record

## Provisioned and committed material

Read the prediction prompt and output schemas, the event definition, `record/context.json`, `record/snapshots/2026-11-09.json`, the document manifest, questions presented, the jurisdictional statement with embedded appendix, selected passages of the separate appendix, and `record/same-question.json`. Read relevant cert sections and prior-Term sal-v8 rows in `metrics/statpack.md`, then exact high-band risk-set values in `metrics/statpack.json`. The substantive response filings below were not provisioned. No target outcome, evaluation, other cell's forecast, or `data/qp-topics/` material was read.

## CLI setup and corpus lookups

Initial `uv run fedcourts paths --court scotus --docket 9026000117 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help` both failed because the default UV cache directory was read-only. Retried both with `UV_NO_CACHE=1 uv run --no-sync`; both succeeded. The paths command identified the event and marked the outcome evaluator-only. The help command was subsequently consulted again over a narrower displayed range. No packages were installed.

All four corpus requests used `UV_NO_CACHE=1 uv run --no-sync` as the execution prefix. This is a forward cell; `DECIDED_BEFORE` was unset, and the context's `decided_before` is null.

1. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --era 2020s --disposition gvr --limit 4`
   - `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Returned Heidi Cid, Burford German Funding, Roofing Designs, and Pedro Jose Silva Ochoa. These illustrate disposition vocabulary, not a substantive voting-rights comparison. No opinion bodies were requested.
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --citation '146 S. Ct. 1131' --limit 2`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned no cases. Coverage note: only 200 scoped rows had reporter citations; no inference of nonexistent precedent was drawn.
3. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --docket-number 26-116 --limit 1`
   - `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Returned pending Caster, three distributions, conference November 13, 2026, no disposition. Used to check the same-question entry against a docket row.
4. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --docket-number 26-118 --limit 1`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned pending Singleton with the same distribution count and conference date. This was a warm-cache response, not a missing transfer report.

## CourtListener MCP

One `analyze_citations` request supplied only `Louisiana v. Callais, 146 S. Ct. 1131 (2026). Allen v. Milligan, 146 S. Ct. 1377 (2026).` The second citation is the earlier interim order cited in the opening papers, not the pending direct appeal's eventual disposition. Job `a3e16b9a` reported both individual citations NOT FOUND, although its aggregate header said two verified. No verification was credited. There was no direct REST fallback or credential access.

## Web-tool attempts

The following attempts are disclosed even where the visible response supplied no independently usable text. The filings ultimately used were read through the pinned extractor as described next.

- One paired `web.search_query`: `site.supremecourt.gov/opinions "Callais" "2026"` and `site.supremecourt.gov "Abbott" "LULAC" "2026"`. These sought prior precedent, not the target appeal's outcome.
- One paired `web.search_query`: `"Louisiana v. Callais" "1131"` and `"Allen v. Milligan" "1377" "2026"`. Again, the Allen reporter citation identified the prior interim ruling supplied in the record.
- Three `web.open` attempts on the exact September 18 respondent-filing URL below.
- Two `web.open` attempts on the exact September 29 state-filing URL below.
- One attempted `web.find` for `moot` with an empty reference identifier; it supplied no usable retrieval and was not relied on.

No search requested the disposition, subsequent history, or coverage of the pending 26-117 appeal. No target disposition was used from any search result.

## Exact filed PDFs read

These URLs came directly from the provisioned snapshot, not from an outcome search:

Respondent, motion to dismiss or affirm, filed September 18, 2026:
`https://www.supremecourt.gov/DocketPDF/26/26-117/424850/20260918144144882_26-117%20-%20Motion%20to%20Dismiss%20or%20Affirm.pdf`

Appellants, opposition to motion to dismiss or affirm, filed September 29, 2026:
`https://www.supremecourt.gov/DocketPDF/26/26-117/425965/20260929142452533_2026.09.29%20-%20Ala.%20Opp.%20-%20Milligan%20-%20FINAL.pdf`

First attempted `curl -fsSL <respondent URL> | UV_NO_CACHE=1 uv run --no-sync fedcourts pdf-text /dev/stdin`, followed by a targeted text search. The extractor refused `/dev/stdin` as not a file; curl consequently reported a write failure. No text from that attempt informed the prediction.

Then made one public HTTPS GET per filing with Python `urllib.request`, held each PDF in an anonymous in-memory `os.memfd_create` descriptor, and passed its inherited `/proc/self/fd/<descriptor>` path to `uv run --no-sync fedcourts pdf-text` under `UV_NO_CACHE=1`. No PDF or extra artifact was written to the repository or to disk. The extractor reported:

- Respondent: `pdf-text: 48 page(s), 69742 character(s)`. Inspected targeted excerpts on mootness, jurisdiction, election timing, and the requested disposition, including pp. 11–14.
- Appellants: `pdf-text: 18 page(s), 25551 character(s)`. Inspected targeted excerpts on continuing relief, election certification, and alternative Munsingwear vacatur, especially pp. 1–4.

Also consulted `UV_NO_CACHE=1 uv run --no-sync fedcourts pdf-text --help` to use the provisioned extractor without installing anything. These exact pre-disposition filings, not a live target-docket refresh, informed the jurisdictional uncertainty in the forecast.

## Validation

The cell is checked with `UV_NO_CACHE=1 uv run --no-sync fedcourts validate data --cell data/cases/scotus/9026000117/events/evt-petition-disposition/predictions/codex-baseline/20261109T171058Z`. Validation is a local contract check, not substantive retrieval.
