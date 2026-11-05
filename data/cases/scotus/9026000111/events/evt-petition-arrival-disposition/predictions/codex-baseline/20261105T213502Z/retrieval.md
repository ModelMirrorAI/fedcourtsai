# Retrieval record

## Provisioned baseline

Read the event definition, `record/snapshots/2026-07-24.json`, `record/context.json`, `record/documents/documents.json`, `questions-presented.txt`, the petition's argument and relevant bound appendix passages, and `record/same-question.json`. No other prediction, evaluation, own-case outcome, or own-case later docket was consulted. The context is forward; the July 24 baseline is not an external-retrieval clock.

## Local contract and tooling

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; inspected the committed statpack's relevant cert sections and its top-level JSON keys. No other cell outputs were read.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000111 --event evt-petition-arrival-disposition --role predictor`. It failed before execution because `/home/codexcell/.cache/uv` is read-only. Reissued as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000111 --event evt-petition-arrival-disposition --role predictor`; it resolved the case and event paths, with the outcome explicitly withheld.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help`, then repeated the help command with `head -65` and `head -55` to inspect the structured-filter usage after long output was truncated. These are tooling help, not corpus reads. No package was installed.
- Consulted `metrics/statpack.md`: paid-segment relist, CVSG, amicus-count, band, and sal-v7 per-Term reached tables. Used frozen baseline anchor 0.051512996760685784 from the context; the federal-class pool over displayed Terms 2017–2025 is a comparator, not a replacement band.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '606 U.S. 942' --decided-before 2026 --limit 3`

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

   No match. The CLI warned that only 200 in-scope rows had reporter citations and that citation coverage was sparse. Switched to CourtListener for the known case; did not interpret the empty result as absence of precedent.

2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition gvr --decided-before 2026 --limit 3`

   `ranged corpus reads: 30 GET(s), 7864320 byte(s)`

   Returned Burford German Funding, No. 25-1269; Roofing Designs by JR, No. 25-1367; and Silva Ochoa, No. 25-7569, recorded as GVRs. These are unrelated route examples, not matched Bivens precedents, and do not drive the numerical adjustment. Their docket Terms precede 2026, although disposition dates are in October 2026: the CLI's mask is by derived year/Term, not a strict July 24 date. This cell is forward and no result concerned its own outcome.

3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 25-417 --limit 1`

   `ranged corpus reads: 11 GET(s), 2883584 byte(s)`

   Returned Francis Nielsen v. Kekai Watanabe, case ID scotus/73278422: certiorari granted June 22, 2026; four distributions; a merits brief filed September 23, 2026; no merits judgment or merits decision date recorded. This independently supports the petition's identified lead-case grant. No Herzon lookup was made.

## CourtListener MCP

1. `search(type="o", citation="606 U.S. 942", num_results=3)`: three duplicate report versions of Goldey v. Fields, decided June 30, 2025; selected original opinion ID 11086520, docket 24-809.
2. `read_document(opinion_id=11086520)`: read the full Goldey opinion. It grants certiorari and summarily reverses recognition of an Eighth Amendment excessive-force Bivens action; used as doctrinal and procedural context, not as an on-point resolution of this petition's Fourth Amendment question.
3. `search(type="o", citation="72 F.4th 237", num_results=1)`: located Donald Snowden v. Jeremy Henning, Seventh Circuit, June 27, 2023, opinion ID 9410718.
4. `search_document(opinion_id=9410718, query="warrant", snippet_size=450)`: fifteen excerpts. Confirmed the arrest-warrant/hotel-lobby facts and the court's conclusion that warrant and location distinctions did not create a new context for that excessive-force claim. This independently corroborates one side of the asserted disagreement.
5. `search(type="o", citation="145 F.4th 516", num_results=1)`: no result for the Orellana citation. Did not infer that the cited case does not exist; its characterization remains attributed to the petition.

## Web attempts

All three calls returned no visible result or source text. None supplied evidence or exposed an outcome.

1. Search queries: `site.supremecourt.gov "Goldey" "Fields" "2025"` and `site.supremecourt.gov "Egbert" "Boule" "2022" opinion`.
2. Search queries: `Goldey Fields 606 U.S. 942 2025 Supreme Court opinion PDF` and `Egbert Boule 596 U.S. 482 2022 Supreme Court Bivens`.
3. Attempted opening the official Egbert PDF at `https://www.supremecourt.gov/opinions/21pdf/21-147_g31h.pdf`. No content returned. Successful primary-opinion retrieval was through CourtListener instead.

No credential lookup, direct CourtListener REST request, or package installation was attempted. Final cell validation is a local output check, not evidentiary retrieval.
