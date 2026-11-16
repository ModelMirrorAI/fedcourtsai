# Retrieval record

## Provisioned and repository sources

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and the tooling/flags schemas. Read this event's `event.yaml`; the case-level `record/context.json`; `record/snapshots/2026-11-16.json`; `record/documents/documents.json`, `questions-presented.txt`, selected substantive portions of `petition.txt`, the appellate opinion and dissent in `decision-below.txt`, `lower-court-docket.txt`, and the opening/index and matching-opinion portion of `appendix.txt`; and `record/same-question.json`. The future-dated same-question cutoff was not used as substantive evidence. Consulted the committed `metrics/statpack.md` modern-cert, circuit, paid-segment relist/CVSG/amicus, and prior-Term salience tables. Did not read another prediction, any outcome file, or topic-label artifacts.

## CLI attempts and corpus lookups

1. `uv run fedcourts paths --court scotus --docket 9026000400 --event evt-petition-disposition --role predictor` failed before execution because the default uv cache was on a read-only filesystem. No corpus transfer was reported.
2. `UV_NO_CACHE=1 uv run fedcourts paths --court scotus --docket 9026000400 --event evt-petition-disposition --role predictor` succeeded and identified the case and event paths. The evaluator-only outcome was neither named nor read.
3. `UV_NO_CACHE=1 uv run fedcourts query --help` and a second rendering with `COLUMNS=130` were consulted for structured-filter syntax. No corpus transfer was reported.
4. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --citation '605 U.S. 333' --decided-before 2026 --limit 3` returned no matching rows, with a note that only 195 in-scope rows carry reporter citations and empty results are not evidence of nonexistence. This was a pinpoint used in the petition; the earlier Labcorp case's starting page was subsequently verified as 327 through MCP. Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
5. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --disposition granted --decided-before 2026 --limit 3` returned Robinhood Markets v. Sodha (25-944), Goldman Sachs Bank USA v. Brown (25-1408), and U.S. DOGE Service v. U.S. District Court (25-1103). Their records are sparse and were not used as issue-matched analogues or as rate estimates. The forward-mode lookup's Term mask did not exclude their recorded 2026 grant dates. Transfer: `ranged corpus reads: 36 GET(s), 9371648 byte(s)`.

## Web attempts

Each returned no visible source content, so none supplied evidence:

1. Search query: `site.supremecourt.gov opinions 2024 Laboratory Corporation Davis 605 Kavanaugh dismissed improvidently granted`.
2. Open attempt: `https://www.supremecourt.gov/opinions/24pdf/605us1r40_7m58.pdf` (an unverified candidate address, not a source relied upon).
3. After MCP supplied the actual official download address, open attempt: `https://www.supremecourt.gov/opinions/24pdf/24-304_3e04.pdf`.

None of these requests concerned the disposition or a forecast of Nestlé v. Falcone.

## CourtListener MCP

1. `search(type="o", court="scotus", case_name="Laboratory Corporation of America Holdings v. Davis", filed_before="2026-01-01", num_results=3)` returned zero results.
2. `search(type="o", court="scotus", q='"Labcorp"', filed_before="2026-01-01", num_results=3)` returned the relevant Laboratory Corp. of America Holdings v. Davis, 605 U.S. 327, decided June 5, 2025, cluster 10599006, opinion 11065594, alongside two older Metabolite matters. Only the Davis result informed the forecast.
3. `read_document(opinion_id=11065594)` supplied the earlier per curiam dismissal and Kavanaugh dissent. Used to distinguish a prior grant on the certification question from a merits resolution and to assess the particular writing interest. This is a different, earlier case, not the target petition's outcome.

## Completion check

The cell is checked with `UV_NO_CACHE=1 uv run fedcourts validate data --cell data/cases/scotus/9026000400/events/evt-petition-disposition/predictions/codex-baseline/20261116T161636Z`. This is local validation, not additional legal retrieval.
