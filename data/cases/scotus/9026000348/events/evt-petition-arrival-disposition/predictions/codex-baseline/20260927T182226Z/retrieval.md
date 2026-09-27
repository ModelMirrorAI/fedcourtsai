# Retrieval record

## Provisioned materials

Read the event definition, `record/context.json`,
`record/snapshots/2026-09-15.json`, and the document manifest, questions
presented, main petition, and selected appended-opinion passages. The
petition text is truncated as disclosed by its manifest. No outcome file,
other predictor's output, or labeling-measurement artifact was consulted.

## Beyond provisioned case materials

- Read the committed `metrics/statpack.md`: modern discretionary-cert
  disposition context, paid-segment relist/CVSG cuts, and the sal-v4
  per-Term reached-rate table.
- Read the structure of `metrics/statpack.json` and used its sal-v4 federal
  segment fields for Terms 2017-2025 to compute a weighted anchor of
  143/202 = 0.7079207921. No case-level historical lookup was made.
- Web search attempted: `site.uscode.house.gov 5 USC 3347 exclusive means
  3348 function duty`. The tool returned no usable results or source text.
- Web open attempted for the official U.S. Code Section 3347 page:
  `https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title5-section3347&num=0&edition=prelim`.
  The tool returned no usable content. Neither attempt searched for this
  case, its outcome, or the companion's current status; neither informed
  a factual assertion in the prediction.

No CourtListener MCP lookup, `fedcourts query`, or `fedcourts open-events`
call was made. Consequently there is no ranged-corpus transfer line.

## Local contract and validation tooling

Read AGENTS.md, the prediction prompt, relevant output schemas, and local
path/serialization interfaces. Ran `fedcourts paths --court scotus --docket
9026000348 --event evt-petition-arrival-disposition --role predictor`.
The first invocation could not initialize the default read-only uv cache;
the retry with a writable temporary cache and `uv run --no-sync` succeeded.
These operations supplied no additional case facts.
