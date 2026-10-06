# Retrieval log

## Corpus lookups (`fedcourts`, read-only via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 48 GET(s), 12451840 byte(s)`
   Used for shape only (recent granted priors; mostly government-party and application rows).
2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr`
   stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   Surfaced hold-then-GVR priors (several Monsanto petitions GVR'd in the 2025 Term) as examples of the route this petition asks for.
3. `uv run fedcourts paths --court scotus --docket 9026000238 --event evt-petition-disposition --role predictor` (path resolution only).

## Committed base rates

- `metrics/statpack.md`: modern discretionary-cert petitions by disposition; by originating circuit; relist-count, CVSG-status, and salience-band cuts (paid scored segment); SCOTUS cert petitions by Term; segment base rate by salience band (`sal-v4`).

## Repository data read for forward context

- `data/cases/scotus/72483489/events/evt-order-judgment/event.yaml` — RiseandShine Corp. v. PepsiCo, certiorari granted 2026-06-29, merits event unresolved. Located with a grep over event titles under `data/cases/scotus/*/events/*/event.yaml`. Nothing under `data/qp-topics/` was read.

## CourtListener MCP

Two calls attempted, both refused with HTTP 429 (daily rate limit exceeded, availability about 50 minutes out):

1. `search` type `o`, court `ca2`, case name "Broadcast Music North American Concert Promoters", filed after 2026-01-01 — to read the Second Circuit opinion (168 F.4th 86).
2. `search` type `d`, court `scotus`, docket number `24-1016` — to check RiseandShine's argument status.

No REST fallback was attempted. No web searches.
