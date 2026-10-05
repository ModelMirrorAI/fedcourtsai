# Retrieval log

Forward-mode cell; nothing retrieved concerned this petition's own disposition
(the response is not yet due).

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "144 S. Ct. 551"`
   (lookup of Anibowei I's denial) — stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`;
   returned no rows, with the note that only 200 SCOTUS rows carry any citation.
2. `uv run fedcourts query --court scotus --citation "141 S. Ct. 2858" --citation "141 S. Ct. 2840"`
   (lookup of the Cano / Merchant denials) — stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`;
   returned no rows, same coverage note.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   — stderr: `ranged corpus reads: 40 GET(s), 10289152 byte(s)`; returned the
   most recent granted SCOTUS rows (mostly OT2025–OT2026 grants and substantive
   applications). None was a border-search or Fourth Amendment petition; used
   only as a sanity check on what recent grants look like (several carried
   distribution counts of 2–5), not as case priors.

## CourtListener MCP (`mcp__courtlistener__search`)

4. type `d` (dockets), court `scotus`, q `Anibowei` — 0 results.
5. type `o` (opinions), court `scotus`, q `"border search" "cell phone" certiorari denied dissenting OR "statement respecting"` — 0 results.
6. type `o`, q `Anibowei` (all courts) — 7 results; the relevant one is
   *Anibowei v. Morgan*, 70 F.4th 898 (5th Cir. 2023), the earlier
   preliminary-injunction appeal. Not opened; the petition already summarizes it.
7. type `o`, court `scotus`, q `"border search" phone warrant Riley`, filed after 2019-01-01 — 0 results.
8. type `d`, court `scotus`, q `Merchant Mayorkas OR Cano OR Alasaad` — 0 results.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
  "by originating circuit", "by relist count", "by CVSG status", "by salience
  band", "SCOTUS cert petitions by Term", and "Segment base rate by salience
  band (sal-v4)".

No web searches.
