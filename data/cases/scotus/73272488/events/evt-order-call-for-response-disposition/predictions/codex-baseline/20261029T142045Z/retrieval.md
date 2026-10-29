# Retrieval record

## Provisioned and committed inputs

Read the event definition, case-level context, `record/snapshots/2026-06-10.json`, document manifest, extracted question presented, petition argument, and relevant lower-court appendix passages. Read the stable prompt, AGENTS.md, output schemas, and the committed `metrics/statpack.md`; used `metrics/statpack.json` only for unrounded prior-Term sal-v4 baseline risk-set arithmetic. No other cell's prediction or evaluation, case outcome, or labeling-measurement artifact was read. No current docket lookup for Abrams was made.

The statpack arithmetic pooled OT2017–OT2024 only: 607 / 11,599 = 0.05233209759462023. This is a committed-pack calculation, not a fresh corpus-state measurement. File/model/path helper reads and output-validation commands were local tooling inspection, not additional case evidence.

## Corpus CLI

Initial `uv run fedcourts paths --court scotus --docket 73272488 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` both failed because the default uv cache was on a read-only filesystem. Both succeeded after setting `UV_CACHE_DIR=/tmp/uv-cache`. The query help was subsequently repeated with wider terminal columns to read the filter definitions. Paths only returned identifiers and paths, not an outcome.

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025 --limit 3`

   Stderr: `ranged corpus reads: 72 GET(s), 18874368 byte(s)`

   Returned RiseandShine v. PepsiCo (24-1016), Devin Chaney v. United States (24-6543), and Monsanto v. Durnell (24-1068). These are selected granted examples, not an estimate of grant probability or factually matched preservation cases. The Term-year mask admits older docket Terms even where their grant dates fall in 2026; no strict-before-June-2026 chronology is claimed for them, and no fact about these examples drives the forecast. No opinion bodies were requested.

2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '598 U.S. 729' --decided-before 2025 --limit 2`

   Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

   Returned no rows. The warning said only 200 scoped SCOTUS rows carry reporter citations and an empty result likely reflects missing coverage. This was an attempted lookup of Dupree v. Younger, not evidence that the precedent does not exist. Did not retry the sparse filter or use a remembered holding as retrieved evidence.

## CourtListener MCP

Attempted opinion search with `citation="679 F.3d 544"`, `type="o"`, `num_results=2`, fields `caseName,dateFiled,citation,absolute_url,id,snippet`, seeking the historical Hosseini opinion cited in the petition. Received HTTP 429, daily rate limit exceeded, expected availability after 2,049 seconds. No opinion was returned. Did not attempt REST, obtain credentials, or retry the throttled server.

## Web attempts

All were directed at general preservation precedent or Tovar, a different petition identified in the provisioned argument. None sought Abrams's disposition. No usable substantive source content appeared in the web tool responses available for this run, so the forecast does not claim these attempts independently verified the petition's legal assertions. The attempted PDF URL below is recorded as an attempted address, not as verified source attribution.

1. Search batch: `United States Hosseini 679 F.3d 544 general Rule 29 motion specificity sufficiency preserved`; `Supreme Court Rule 29 general motion acquittal circuit split Tovar 2014 United States opposition`.
2. Search batch: `site.justice.gov "25-6344" "Tovar"`; `site.ca7.uscourts.gov "Hosseini" "679" "544"`.
3. Attempted PDF open: `https://www.supremecourt.gov/DocketPDF/25/25-6344/403828/20260407130647497_Tovar%20Opp%2025-6344.pdf`.
4. Malformed open attempt with an empty reference; supplied no evidence.
5. Search: `site.justice.gov "Tovar" "25-6344" "2026"`.
6. Repeated the same PDF-open attempt.
7. Attempted find for `conflict` on that PDF address.

## Independent read-only assessment

A subagent reviewed only the provisioned petition/appendix for alternative grounds and vehicle concerns. It identified the panel's strong-evidence findings and the distinction between first-prong no-error reasoning and lack-of-plainness reasoning. I inspected the material supporting passages before using the vehicle discount. It made no retrieval calls, numeric forecast, or file edits.
