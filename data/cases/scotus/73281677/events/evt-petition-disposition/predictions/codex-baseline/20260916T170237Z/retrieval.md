# Retrieval log

## Local reference material

- Read the prompt and the prediction, tooling, and flags schemas, plus the provisioned event, snapshot, context, document manifest, QP, petition, and opposition.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating courts, paid-segment relist/CVSG cuts, and the `sal-v4` per-Term segment table. Only baseline reached rows for 2017–2024 enter the anchor. Read only the top-level keys of `metrics/statpack.json`; they supplied no additional case facts.
- Executed a local weighted calculation from the displayed Markdown rows: weighted denominator 11,580 and approximate reached grant-family rate 5.1202504317789295%.
- Ran `uv run fedcourts paths --court scotus --docket 73281677 --event evt-petition-disposition --role predictor`. The default cache location was read-only; rerunning with a writable temporary cache succeeded. This resolves local paths, not case facts. Inspected local path/serialization API names and schemas for output-contract checking.

## Attempted web retrieval

All requests returned empty tool responses with no usable source text or search results. None informed the forecast.

1. Combined search for `site.supremecourt.gov "Clinton v. Goldsmith" "collateral"` and `site.uscode.house.gov "866" "error or excessive delay"`.
2. Search for `10 USC 866 d 2 courts criminal appeals error excessive delay`.
3. Open attempt for the official Section 866 page: `https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title10-section866`.

No CourtListener MCP lookup, `fedcourts query`, or `open-events` call was made; therefore no ranged-corpus transfer line was produced. No search targeted Myslow's disposition or subsequent history. The other petitions' prior denials used in the forecast were already described in the provisioned petition and opposition.
