# Retrieval record

## Provisioned inputs

Read `event.yaml`, `record/context.json`, `record/snapshots/2026-09-16.json`, and the provisioned `documents.json`, `questions-presented.txt`, and `petition.txt`. No other prediction, evaluation, target outcome, or labeling-measurement artifact was read. Lower-court history mentioned in the petition was treated as pre-decision history, not as the disposition being forecast.

## Local context beyond the provisioned record

- Read the task instructions and prediction/tooling schemas, and inspected path/serialization helpers for output handling.
- Ran `uv run fedcourts paths --court scotus --docket 73391039 --event evt-petition-disposition --role predictor`. The first attempt failed at the default cache; retrying with a temporary cache and `--no-sync` succeeded. The command displayed only an evaluator-only placeholder for the outcome, not outcome contents.
- Read the modern discretionary-cert, originating-circuit, paid-segment relist/CVSG, and sal-v4 segment sections of `metrics/statpack.md`. Read the matching `metrics/statpack.json` segment rows. Used jq to pool the baseline reached rates for Terms 2017–2024: estimated numerator 593, weighted denominator 11,580, rate 0.05120898100172712. The same-Term and later-Term rows were not used in the anchor.
- Ran `git log -1 --format='%cs %h' -- metrics/statpack.md` to establish file vintage: September 14, 2026. This is not a live corpus freshness measurement.
- No `fedcourts query` or `open-events` calls; consequently no ranged-corpus transfer lines were emitted.

## External legal context

CourtListener MCP calls:

1. `search(type="o", citation="559 U.S. 260", num_results=1)` returned United Student Aid Funds, Inc. v. Espinosa, decided March 23, 2010, opinion 1727.
2. `search_document(opinion_id=1727, query="Rule 60(b)(4) applies", snippet_size=2000)` returned the discussion of exceptional jurisdictional/due-process defects, the distinction between voidness and error, and the limited role of collateral review. This was the substantive external authority used.

Web requests attempted the following general-precedent searches:

- `site.supremecourt.gov opinions 09pdf 08-1134 Espinosa Rule 60 void`
- `site.supremecourt.gov rules Rule 10 rarely granted misapplication properly stated rule law`
- `United Student Aid Funds Espinosa 559 U.S. 260 2010 Rule 60 b 4 opinion`
- `site.supremecourt.gov "Espinosa" "08-1134"`
- `site.supremecourt.gov/opinions/09pdf/08-1134.pdf`

There were also repeated open attempts for the official opinion paths `https://www.supremecourt.gov/opinions/09pdf/08-1134.pdf` and `https://www.supremecourt.gov/opinions/25pdf/24-808_lkgn.pdf`. These web calls yielded no usable source text in this session; no holding was inferred from the latter path. The successful Espinosa MCP excerpt, not an unverified web result, supplied the legal analysis. No search targeted this petition's disposition or subsequent history.
