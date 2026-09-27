# Retrieval log

## Provisioned record

Read only this cell's event definition, `record/context.json`, `record/snapshots/2026-09-11.json`, and the manifest, petition, and questions-presented text under `record/documents/`. The source URLs in the manifest were not followed. No outcome file, other predictor output, or labeling artifact was read.

## Context beyond provisioned inputs

- Read the committed `metrics/statpack.md` modern-cert, paid-segment relist/CVSG, originating-court, and prior-Term salience tables. Inspected `metrics/statpack.json` term and baseline-risk-set fields and calculated the 2017–2025 `sal-v4` private-caption pooled reached rate with `jq`: weighted grants 638, weighted resolved 12,720, rate 0.05015723270440252. A file-history lookup, `git log -1 --format='%h %cI' -- metrics/statpack.md`, returned `96ebdd342 2026-09-26T12:03:37Z`. This dates the committed artifact, not the underlying corpus's last refresh.
- Web search attempted: `site.supremecourt.gov Rule 10 considerations governing review certiorari state court federal appeals important federal question`. The tool returned no usable result or source text. No case-specific search was attempted.
- Web open attempted for the general rules PDF at `https://www.supremecourt.gov/ctrules/2023RulesoftheCourt.pdf`. The tool returned no usable content. No proposition in the forecast depends on this attempted retrieval.
- No CourtListener MCP calls. No `fedcourts query` or `open-events` calls, so no ranged-corpus transfer lines were produced.

## Contract and local checks

Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, tooling, and flags schemas. Used `fedcourts paths --court scotus --docket 9026000328 --event evt-petition-arrival-disposition --role predictor` for path confirmation. The initial `uv run` attempt could not write the default cache; retrying with a temporary writable cache succeeded. These operations supplied no additional case facts.
