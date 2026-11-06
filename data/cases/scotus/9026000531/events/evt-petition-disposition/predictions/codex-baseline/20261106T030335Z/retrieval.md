# Retrieval record

## Provisioned material and local references

Read the prediction prompt and prediction schema before the per-case record. Read `event.yaml`, `record/snapshots/2026-11-06.json`, `record/documents/documents.json`, `questions-presented.txt`, the petition including its appendix, `context.json`, and `same-question.json`. Read the relevant cert sections of committed `metrics/statpack.md` and `schemas/agent_tooling.schema.json`. No other prediction, evaluation, outcome file, or topic-label artifact was read. No live docket lookup for this petition was attempted.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000531 --event evt-petition-disposition --role predictor` failed before execution because uv could not open its default cache's `CACHEDIR.TAG` on the read-only filesystem. No case data returned.
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 9026000531 --event evt-petition-disposition --role predictor` succeeded and resolved the case and event paths; its outcome line was an evaluator-only placeholder, not an outcome path or record.
3. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` displayed the structured-filter interface.
4. `COLUMNS=140 UV_NO_CACHE=1 uv run --no-sync fedcourts query --help | head -65` reread the initial help and options with wider columns.
5. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --citation '537 U.S. 522' --decided-before 2026 --limit 3` returned no rows and explicitly warned that only 200 scoped rows carry reporter citations; this is sparse coverage, not absence of the precedent.

   Exact transfer report: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.

The historical cutoff was used voluntarily on this forward cell to keep the known-precedent lookup away from current-Term outcomes. No dependency installation or synchronization was performed. The final validation command is `UV_NO_CACHE=1 uv run --no-sync fedcourts validate data --cell data/cases/scotus/9026000531/events/evt-petition-disposition/predictions/codex-baseline/20261106T030335Z`; it is a local completeness check, not a precedent lookup.

## Web attempts

Every web call below returned no usable output in the tool response; no fact or forecast rests on them.

1. Batched search queries: `site.supremecourt.gov Clay United States 537 522 finality certiorari 2003` and `site.supremecourt.gov Slack McDaniel 529 473 procedural certificate appealability 2000`.
2. Batched search queries: `Clay v United States 537 U.S. 522 Supreme Court opinion 2003` and `Slack v McDaniel 529 U.S. 473 Supreme Court opinion 2000`.
3. Open attempt: the historical U.S. Reports PDF at `https://www.govinfo.gov/content/pkg/USREPORTS-537/pdf/USREPORTS-537-522.pdf`.
4. Find attempt on the same URL for `Finality attaches`.

These attempts concerned historical general precedent, not this petition or its disposition.

## CourtListener MCP

1. `search(type="o", citation="537 U.S. 522", num_results=1)` returned Clay v. United States, decided March 4, 2003, opinion ID 122265, docket 01-1500. The server reported three matches; only the first result was requested and read. No pagination was used.
2. `search_document(opinion_id=122265, query="Finality attaches", snippet_size=900)` returned two excerpts, including the postconviction finality discussion at 537 U.S. 527. This confirmed general doctrine already quoted in the provisioned petition; no current-case facts were retrieved.
3. `search(type="o", citation="529 U.S. 473", num_results=1, fields=["caseName","citation","dateFiled","opinions","absolute_url"])` returned Slack v. McDaniel, decided April 26, 2000, combined-opinion ID 118359, with metadata and snippets for the separate historical opinions. No pagination was used.
4. `search_document(opinion_id=118359, query="a plain procedural bar", snippet_size=600)` returned one excerpt at 529 U.S. 484–85, explaining the two-part certificate threshold and the effect of a plain procedural bar.

No current-case disposition, subsequent history, or outcome-revealing material was retrieved. The historical direct-review denials already in the petition appendix concern different events and are part of the provisioned record.
