# Retrieval record

## Local contract and calibration material

Read AGENTS.md, .github/prompts/predict.md, schemas/prediction.schema.json, the tooling and flags schemas, and the case-level provisioned record. Read metrics/statpack.md and the relevant sal-v4 term-segment fields in metrics/statpack.json; pooled the displayed strictly prior Terms 2017–2024 using their exact reached-baseline counts. Also inspected the local paths and serialization helpers to honor the output contract. No other cell's predictions or evaluations, outcome file, or topic-label artifacts were read.

Administrative CLI calls: the initial `uv run fedcourts paths --court scotus --docket 73522552 --event evt-order-call-for-response-disposition --role predictor` failed before execution because uv's default cache location was read-only. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; it resolved the case and event and withheld the evaluator-only outcome. Queried `fedcourts query --help` twice, once with a wider terminal, to inspect supported structured filters. No remote retrieval results came from those calls.

## Corpus query

Executed:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025 --limit 4
ranged corpus reads: 72 GET(s), 18874368 byte(s)
```

Returned RiseandShine v. PepsiCo (24-1016), Chaney v. United States (24-6543), Monsanto v. Durnell (24-1068), and Hikma v. Amarin (24-889). These were generic modern grant priors, not subject-matched examples. I used no full opinion bodies and derived no rate from this grant-filtered sample. The four-digit clock is a docket-Term filter: the returned grant dates can fall in a later calendar year. None is this petition. No open-events query was made.

## CourtListener MCP

Attempted `search(type="o", citation="975 F.3d 1244", num_results=2)` for Johnson v. NPAS Solutions. Returned HTTP 429: daily rate limit exceeded, expected available in 12,784 seconds. No opinion text was returned. No REST fallback or token retrieval was attempted.

## Web tool calls

1. Search batch: `site.ca11.uscourts.gov "Johnson" "NPAS" "1244"`; `site.ca2.uscourts.gov "Moses" "New York Times" "2023"`. No results were surfaced by the tool.
2. Search batch: `Johnson NPAS Solutions 975 F.3d 1244 incentive awards Greenough Pettus opinion`; `Murray Grocery Delivery 55 F.4th 340 incentive awards opinion`. No results were surfaced by the tool.
3. Search batch: `site.supremecourt.gov "NPAS" "2023"`; `site.supremecourt.gov "Dart" "incentive awards"`. Returned official docket results for 22-389 and 22-517 and a petition PDF associated with 24-798. The returned batch also included an unrelated public prediction snippet about a different Tenth Circuit service-award dispute despite the requested site restriction. That non-primary snippet was not opened or used; no own-case disposition appeared. The 24-798 PDF was not opened.
4. Opened the official Supreme Court docket for **22-389**, Johnson v. NPAS Solutions. Its entries show the response request on December 13, 2022, denial on February 21, 2023, and rehearing denial on April 17, 2023. Used the first two as a prior procedural analogue, not as legal endorsement of either side.
5. Opened the official Supreme Court docket for **22-517**, NPAS Solutions v. Johnson. Its entries show opposition and reply, distribution, and denial on April 17, 2023. Used as older procedural context for the incentive-award litigation. Neither official page concerns the target petition.

## Freshness checks

Inspected `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info --help`. A first combined shell command intended to invoke corpus-info failed to parse because a later jq expression was improperly quoted; no corpus read occurred in that failed command. Then executed `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info --corpus-backend service`: refused with `Unsupported --corpus-backend 'service'; choose local, ranged.` Executed `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` without an explicit backend: failed because the configured service backend has no client-side connection, and only query/open-events forward to it. Neither call reported a transfer line or freshness date. No attempt was made to acquire cloud credentials or pull the corpus locally.

The committed pack's build vintage and the live corpus-wide newest pull/snapshot dates could not be verified; the provisioned snapshot's own date and cutoff are reported in reasoning.md. Schema and artifact validation are local checks, not substantive retrieval.
