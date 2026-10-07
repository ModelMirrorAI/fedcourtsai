# Retrieval log — claude-baseline, scotus/73522552, evt-petition-disposition, run 20261006T142731Z

Mode: `forward` (no retrieval clock). Nothing retrieved concerned this case's own disposition; the live docket (fetched October 6, 2026) ends at the October 2 reply.

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   `ranged corpus reads: 28 GET(s), 7208960 byte(s)` — a sample of recent grants for shape; no incentive-award analogue surfaced (the filters cannot express the topic on SCOTUS rows).
2. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache) — recent OT2026-resolved rows, mostly October 5, 2026 denials; used only as a sanity check on the live slice.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition"; "by originating circuit" (ca2 row); "by relist count (paid scored segment)"; "by CVSG status (paid scored segment)"; "SCOTUS cert petitions by Term"; "Segment base rate by salience band (sal-v4)" — pooled the `baseline` bracketed `reached` figures over OT2017–OT2024.

## CourtListener MCP

Four `search` calls (type `d`, court `scotus`: "NPAS Solutions"; "Isaacson"; "National Veterans Legal Services Program"; "Scott v. Dart" OR "incentive award" OR "service award"). **All four returned HTTP 429** (daily rate limit 1400/day exhausted; reset in ~3,340 s). No MCP data was obtained; no REST fallback was attempted.

## Web searches (engine WebSearch)

1. `Johnson v. NPAS Solutions certiorari denied Supreme Court incentive award` — confirmed cert denied April 17, 2023 (No. 22-389).
2. `National Veterans Legal Services Program v. United States incentive awards Federal Circuit 2026 petition certiorari` — surfaced the companion petition No. 26-302 (filed September 3, 2026).
3. `Isaacson v. Moses 25-1411 Supreme Court incentive awards Chamber of Commerce amicus` — confirmed the Chamber as the amicus filer; surfaced Rules suggestion 26-CV-4.
4. `Supreme Court "incentive awards" class representatives circuit split cert petition 2025 OR 2026 Dickenson OR "Scott v. Dart"` — surfaced Nos. 24-259 and 24-464.

## Web fetches (engine WebFetch, supremecourt.gov and uscourts.gov)

1. Docket 25-1411 (this case) — entries through October 2, 2026; no later entry.
2. Docket 26-302, *Isaacson v. National Veterans Legal Services Program* — petition filed Sept 3, 2026; federal respondent waived Sept 23; respondents' time extended to Nov 9, 2026.
3. Docket 24-259, *Isaacson v. Meta Platforms* — waivers; response requested Oct 21, 2024; BIOs Dec 20, 2024; redistributed Jan 8, 2025; denied Jan 27, 2025.
4. Docket 24-464, *Dart v. Scott* — DRI amicus; BIO Jan 14, 2025; distributed Jan 29, 2025; denied Feb 24, 2025.
5. Docket 22-389, *Johnson v. Dickenson* — four distributions with reschedules; denied Apr 17, 2023.
6. Chamber of Commerce amicus brief in 25-1411 (PDF; text extracted locally with pypdf) — interest statement, summary of argument, opening of Part I.
7. Petitioner's reply brief in 25-1411 (PDF; extracted locally) — pp. 1–7, including the footnote naming No. 26-302.
8. Rules suggestion 26-CV-4 (COSAL letter of Feb 13, 2026 to the Standing Committee) — proposes amending Rule 23 to expressly permit service awards.
