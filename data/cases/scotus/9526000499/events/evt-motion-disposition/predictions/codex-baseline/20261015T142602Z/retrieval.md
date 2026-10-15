# Retrieval record

## Provisioned materials

Read the event definition, the October 10, 2026 snapshot, context, document inventory, and the application under this case's provisioned `record/`. No later docket or disposition of this case was sought or read. The application supplies all case-specific facts used here.

## Committed base-rate context

- Read `metrics/statpack.md`, principally “The interim docket (applications),” and the corresponding `interim.terms` counts in `metrics/statpack.json`. Used only application-Terms 2016–2025 for the Term-2026 anchor: 53 grants / 549 resolved substantive applications.
- Checked the statpack's last git change with `git log -1 --format='%h %cI' -- metrics/statpack.json`: `cf9ae960e`, October 13, 2026, 19:17:46 UTC. This is the pack's commit vintage, not a newly measured corpus freshness stamp.
- No `fedcourts query` or `open-events` calls; consequently no ranged-corpus transfer lines.

## General-authority web attempts

The following calls returned no usable content to this session. They supplied no factual basis for the prediction:

1. Search: `site.supremecourt.gov opinions Coinbase Bielski 2023 stay interlocutory appeal 22-105`.
2. Search in the same call: `site.supremecourt.gov vacate stay demonstrably wrong accepted standards Western Airlines Teamsters`.
3. Search: `Western Airlines Teamsters 480 U.S. 1301 vacate stay demonstrably wrong accepted standards`.
4. Attempted opening of the govinfo U.S. Reports PDF for volume 480, page 1301 (`USREPORTS-480-1301.pdf`).

None of these requests named the target case or sought its outcome.

## CourtListener MCP

1. `search(type="o", citation="480 U.S. 1301", num_results=1)` — returned Western Airlines v. Teamsters, April 2, 1987, opinion 111855.
2. `read_document(opinion_id=111855)` — read the returned opinion text; the displayed response was truncated.
3. `search_document(opinion_id=111855, query="demonstrably", snippet_size=1500)` — obtained the complete relevant vacatur-standard passage quoting Coleman v. Paccar. Used to distinguish eventual review-worthiness from emergency vacatur.
4. `search(type="o", citation="599 U.S. 736", num_results=1)` — returned Coinbase v. Bielski, June 23, 2023, opinion 10516266.
5. `search_document(opinion_id=10516266, query="contrary indications", snippet_size=1100)` — obtained the majority's automatic-stay reasoning and statutory qualification at page 744.
6. `search_document(opinion_id=10516266, query="Kavanaugh, J., delivered", snippet_size=1000)` — verified the Coinbase majority and dissent lineup. Used only as a caution against assuming a majority on the distinct remand question.

These are general authorities predating the cell's event, not later case-specific information. No target-case outcome material was encountered.

## Operational checks

Ran the prescribed `fedcourts paths` command using the authoritative identifiers. Its first attempt failed because the default uv cache was read-only; a writable temporary cache resolved that operational issue. Consulted the output schemas, path/ID utilities, and serialization helpers for artifact construction and validation, not substantive case information.
