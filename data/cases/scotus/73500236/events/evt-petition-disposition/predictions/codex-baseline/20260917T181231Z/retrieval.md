# Retrieval log

## Committed aggregate context

- Read metrics/statpack.md: modern discretionary-cert dispositions, paid-segment terminal relist and CVSG cuts, Term table and grant/GVR warning, and sal-v4 reached-band table.
- Read metrics/statpack.json structure and baseline prefix rates/weighted denominators for displayed Terms 2017–2024. Computed sum(rate × denominator) / sum(denominator) = 593 / 11,580 = 0.051208981. No individual case rows or outcomes were retrieved.
- Ran git log -1 --format='%h %cI' -- metrics/statpack.json to identify the committed aggregate artifact's vintage: 55121cdb8, September 14, 2026, 11:02 UTC. This does not establish corpus pull freshness.
- No fedcourts query or open-events lookup; consequently no ranged-corpus-transfer line was emitted.

## General web attempts

- web.run search_query: `site.supremecourt.gov Rule 10 considerations governing review certiorari` and `site.supreme.justia.com Palazzolo Rhode Island 533 606 notice acquisition` in one call.
- Two web.run open attempts at the Supreme Court's official filing-and-rules guidance page.
- These calls returned no usable visible content. No rule text or case-specific result was relied upon. None requested this petition's disposition or subsequent history.

## CourtListener MCP

1. search(type="o", citation="533 U.S. 606", num_results=1): returned Palazzolo v. Rhode Island, decided June 28, 2001; cluster 118459 and its opinion identifiers. This is general precedent, not the target litigation.
2. search_document(opinion_id=[9434149,9434150], query="notice", snippet_size=1100): returned five excerpts from the lead opinion on purchasers' notice and no literal matches in the concurrence. Read the lead-opinion passages corresponding to 533 U.S. 626–630. Used the rejection of a categorical notice bar only as an analogy; did not treat the concurrence's search miss as substantive evidence.

## Local contract tools

Read AGENTS.md, the prediction prompt and output schemas, followed by the cell's event, context, snapshot and document inputs. Resolved paths with `uv run fedcourts paths --court scotus --docket 73500236 --event evt-petition-disposition --role predictor`; the first attempt failed because the default cache directory was read-only, and the temporary-cache retry succeeded. No evaluator-only file was read.
