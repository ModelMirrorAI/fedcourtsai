# Retrieval log

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-10-14.json`, `record/documents/documents.json`, `questions-presented.txt`, and selected petition/appendix passages described in `reasoning.md`. All are inputs to this cell, not external retrieval.

## Committed general context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist/CVSG cuts, and the `sal-v4` per-Term salience table. Read the federal segment entries of `metrics/statpack.json` to compute the unrounded 2017–2025 pooled reached rate: 143/203 = 0.7044334975. No Term-2026 observation entered the anchor.
- Read the task contract, output schemas, and path/serialization helpers for artifact construction. The paths command initially failed because its default cache directory was read-only; it succeeded with a writable temporary cache. This involved no corpus lookup.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer line was produced.

## Web attempts

1. `web.run` search query: `site.supremecourt.gov opinions 24pdf Trump CASA 2025 APA vacatur footnote 10`. No usable content returned.
2. `web.run` search query: `site.supremecourt.gov "24a884" "pdf" "2025"`. No usable content returned.
3. `web.run` open attempt: `https://www.supremecourt.gov/opinions/24pdf/24a884_new2_0pl1.pdf`. No usable content returned. This candidate address was not verified and supplied no evidence.

## CourtListener MCP

1. `search(type="o", case_name="Trump v. CASA", filed_before="2025-07-01", court="scotus", num_results=3)`. Returned historical CASA opinions, including cluster 10776816, opinion 11243403, decided June 27, 2025, reported at 606 U.S. 831. Query ID: `f7670514`.
2. `search_document(opinion_id=11243403, query="Administrative Procedure", snippet_size=900)`. Returned two excerpts, including Kavanaugh's concurrence discussing APA relief and a dissent's historical discussion. Used the former only to confirm the distinct APA context; the latter did not affect the estimate.
3. `search_document(opinion_id=11243403, query="vacate", snippet_size=550)`. Returned the majority's footnote 10 at 606 U.S. 847 expressly reserving whether the APA authorizes vacatur of federal agency action. This verified the petition's characterization of the issue as left open.

No target-case outcome or subsequent history was requested or encountered. No direct CourtListener REST request was made.
