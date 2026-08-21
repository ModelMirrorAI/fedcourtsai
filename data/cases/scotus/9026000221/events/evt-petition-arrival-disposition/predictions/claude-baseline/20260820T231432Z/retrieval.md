# Retrieval log (claude-baseline, run 20260820T231432Z)

Forward-mode cell; retrieval unrestricted. Beyond the provisioned inputs
(snapshot 2026-08-21, `event.yaml`, `record/context.json`, and the provisioned
`petition.txt` / `questions-presented.txt` / `documents.json`) I consulted:

## Committed base rates

- `metrics/statpack.md` (committed copy at HEAD) — salience-band segment
  table (sal-v3), modern discretionary-cert base rate, relist-count cut, CVSG
  cut, per-Term table.

## CourtListener MCP lookups (2 calls)

1. `search` (type=o, court=ca5, q=`Nathan "Alamo Heights" Ten Commandments`,
   fields restricted) — confirmed the en banc decision below exists as the
   petition describes: *Nathan v. Alamo Heights ISD*, No. 25-50695, decided
   2026-04-21, published; and surfaced *Roake v. Brumley*, No. 24-30706,
   decided 2026-02-20 (en banc, the Louisiana companion).
2. `search` (type=d, court=scotus, q=`Roake Brumley`) — 0 results
   (CourtListener does not index the SCOTUS docket for Roake's conditional
   petition, No. 25-1360); its status is taken from the petition's own
   footnote 1 instead.

Neither lookup sought or surfaced this case's own disposition — the petition
was docketed on 2026-08-20 and no disposition exists.

## Corpus tooling

- No `fedcourts query` / `open-events` calls (so no `ranged corpus reads`
  lines to record). The query surface filters on court/topic/judge/citation,
  none of which retrieves "Ten Commandments / school religious display"
  priors usefully, and the statpack carried the base rates the prompt
  anchors this cell on.

## Web searches

- None.
