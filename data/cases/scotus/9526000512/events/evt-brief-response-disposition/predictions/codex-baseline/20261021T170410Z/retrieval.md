# Retrieval log

## Provisioned baseline

Read the event definition, October 19, 2026 snapshot, context, document manifest, application, and application response for this cell. No other event's prediction or realized outcome was read.

## Committed base-rate context

Read `metrics/statpack.md`, principally the interim-docket section. Inspected only the top-level key names in `metrics/statpack.json`; no figures were taken from that JSON file. A local Python calculation parsed the Markdown's per-Term table, selected 2016 <= Term < 2026, and summed the substantive-resolved and granted columns: 51 grants / 547 resolutions = 0.09323583180987204. No corpus service or CourtListener request was made, so there is no ranged-corpus transfer line.

Pack provenance: `git log -1 --format='%h %cI' -- metrics/statpack.md` returned `ac757d745 2026-10-19T05:54:06Z`. SHA-256 of `metrics/statpack.md`: `a04f8745186adfe006877e2d86392073a3ab039e564af8bdc2fd795272bf6127`. This is committed-artifact provenance, not a live corpus refresh timestamp.

## Web retrieval: general precedent only

1. Search: `site.supremecourt.gov opinions Purcell Gonzalez 2006 06a375`.
2. Search: `site.supremecourt.gov opinions Merrill Milligan Kavanaugh 2022 Purcell clearcut`.
3. Opened the official Supreme Court PDF of Merrill v. Milligan, Nos. 21A375 and 21A376, February 7, 2022, including Justice Kavanaugh's concurrence and Justice Kagan's dissent: `https://www.supremecourt.gov/opinions/21pdf/21a375_d18f.pdf`.

The searches returned general election-litigation material, including an unrelated Supreme Court docket result. That docket was not opened or used. No search named this application, its parties, its docket number, or its outcome. No own-case disposition or subsequent history surfaced in the consulted material. The official Merrill opinion supplied general legal context only; its competing views reinforce uncertainty about how election proximity and implementation concerns are weighed.

## Operational reads

Read the task instructions, artifact schemas, and local path/serialization helpers for output compliance. Ran `uv run fedcourts paths --court scotus --docket 9526000512 --event evt-brief-response-disposition --role predictor` successfully after selecting a writable temporary cache. No corpus query, open-events, live CourtListener MCP lookup, or current-case web retrieval was used.
