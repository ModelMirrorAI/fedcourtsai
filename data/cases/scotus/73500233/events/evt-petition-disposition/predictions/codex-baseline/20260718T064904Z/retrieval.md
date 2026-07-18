# Retrieval

No lookup sought this case's disposition or subsequent history.

## Committed base rates

- Read `metrics/statpack.md`, especially modern discretionary-cert disposition, relist, CVSG, originating-court, and per-Term tables.
- Read the 2025 Term paid-petition detail and Wisconsin originating-court buckets in `metrics/statpack.json`.
- No `fedcourts query` or `fedcourts open-events` call was made, so there is no ranged-corpus transfer line.

## CourtListener MCP

- `search` (Opinions), query `"pending charges" "other acts" evidence constitutional right self-incrimination`, filed before 2026-07-18: 35 matches; reviewed the returned case list, including *State v. Barreau*.
- `search` (Opinions, semantic), query `admission of pending criminal charge as other acts evidence due process presumption of innocence`, filed before 2026-07-18: reviewed returned analogues.
- `search` (Opinions), query `Huddleston Dowling other acts pending prosecution Fifth Amendment right to remain silent testify`, filed before 2026-07-18: reviewed returned authorities.
- `search` (Opinions), case name `State v. Barreau`, Wisconsin Court of Appeals, filed before 2026-07-18: one result, 2002 WI App 198.
- `search` (Opinions) by citation for 493 U.S. 342, 485 U.S. 681, and 385 U.S. 554: identified *Dowling v. United States*, *Huddleston v. United States*, and *Spencer v. Texas*.
- `get_endpoint_item` (Opinions) for the lead/combined opinions in *Dowling*, *Huddleston*, and *Spencer*: reviewed the relevant opinion text on other-acts admissibility and due process.
- `search` (Opinions), query `"fundamental conceptions of justice" Dowling "Due Process Clause"`, Supreme Court: confirmed the *Dowling* result.
- `get_endpoint_item` (Opinions) for the *Dowling* lead opinion: reviewed the surrounding text for the fundamental-fairness standard.
- Three narrower `search` calls for combinations of `pending charges`, `pending prosecution`, `other acts`, and `presumption of innocence` returned HTTP 429 throttling responses. They yielded no content and did not affect the forecast.

No general web search was used.
