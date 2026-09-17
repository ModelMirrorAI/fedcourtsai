# Retrieval log

## Provisioned inputs

- Read the event definition, `record/context.json`, and `record/snapshots/2026-09-15.json` for this cell.
- Read `record/documents/documents.json`, `questions-presented.txt`, and substantive excerpts from `petition.txt` and `brief-in-opposition.txt`. No independent retrieval of the reply, appendix, or amicus texts.

## Statistical context beyond provisioned case inputs

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cuts, paid-segment relist and CVSG cuts, and the per-Term sal-v4 segment table.
- Read the corresponding fields in `metrics/statpack.json`. Pooled elevated-band reached numerators and denominators for every displayed prior Term, 2017–2024: 484 / 2,810. Did not use this case's Term or later Terms as the anchor.
- No `fedcourts query` or `open-events` lookups were made, so there are no ranged-corpus transfer lines.

## External retrieval attempts

1. Web search: `site.loc.gov "Bethel School" "478 U. S. 675"`. No usable result content returned.
2. Web open: `https://supreme.justia.com/cases/federal/us/478/675/`, attempted twice. Neither attempt returned usable content. This was a historical precedent lookup, not a search for this petition or its outcome.
3. CourtListener MCP `search`: `type="o"`, `citation="725 F.3d 293"`, `num_results=2`, fields `id`, `caseName`, `dateFiled`, `citation`, `opinions`, `absolute_url`. Intended to examine the preexisting B.H. precedent cited by both briefs. Returned HTTP 429 (300/hour limit, indicated wait 1,057 seconds); no opinion content received. No REST fallback or repeated MCP retry.

No case-outcome retrieval was attempted, and no external substantive evidence was added.

## Local tooling

- Initial `uv run fedcourts paths --court scotus --docket 73281630 --event evt-petition-disposition --role predictor` failed because the default cache location was read-only.
- Re-ran successfully with caching disabled and the existing environment, using `uv run --no-sync fedcourts paths` with the same identifiers. The evaluator-only outcome was not opened.
