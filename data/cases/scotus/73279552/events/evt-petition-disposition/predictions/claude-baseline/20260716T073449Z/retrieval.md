# Retrieval log — scotus/73279552 / evt-petition-disposition / claude-baseline / 20260716T073449Z

Mode: `forward` (retrieval unrestricted; nothing sought or surfaced about this
case's own disposition, which does not yet exist — the 2026-07-16 snapshot
shows it pending).

## Corpus lookups (`fedcourts`, ranged backend)

All `query` calls returned **zero rows** (the topic index is sparse for these
terms); base rates were taken from the committed `metrics/statpack.md` instead.

- `uv run fedcourts query --court scotus --topic "free exercise religion church COVID restrictions fines" --limit 8`
  — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — 0 rows
- `uv run fedcourts query --court scotus --topic "free exercise" --limit 8`
  — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — 0 rows
- `uv run fedcourts query --court scotus --topic "church" --limit 6`
  — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — 0 rows
- `uv run fedcourts query --court scotus --topic "religious" --limit 6`
  — `ranged corpus reads: 3 GET(s), 786432 byte(s)` — 0 rows

## Base rates

- Committed `metrics/statpack.md`: modern discretionary-cert base rate
  (grant ≈ 3.1%), relist-count cut (0 relists → 0.8% grant; 1 → 7.6%;
  2 → 33.6%), CVSG cut (n/a here), per-Term table (Term 2025: grant ≈ 2.5%,
  paid/IFP 1432/2702), originating-court cuts. No salience-band table is
  present in the committed statpack.

## Web searches (engine `WebSearch`)

- `St. Mary Catholic Parish v. Roy Supreme Court 25-581 certiorari granted`
  — confirmed cert **granted April 20, 2026** in No. 25-581 (Smith
  general-applicability QP; merits briefing into August 2026, OT2026
  argument). Sources: [SCOTUSblog case page](https://www.scotusblog.com/cases/st-mary-catholic-parish-v-roy/),
  [Oyez](https://www.oyez.org/cases/2026/25-581),
  [SCOTUS docket 25-581](https://www.supremecourt.gov/docket/docketfiles/html/public/25-581.html),
  [SCOTUSblog coverage](https://www.scotusblog.com/2026/04/supreme-court-will-hear-religious-liberty-case-on-catholic-preschools-and-lgbtq-families/).
- `"Calvary Chapel San Jose" Supreme Court 25-703 petition held St. Mary conference`
  — background/advocacy coverage of the petition only
  ([ACLJ](https://aclj.org/religious-liberty/aclj-files-petition-at-the-us-supreme-court-defending-church-against-unconstitutional-million-dollar-fines),
  [Advocates for Faith & Freedom](https://faith-freedom.com/press-release-ca-fines-church-for-worship/),
  [Liberty Justice Center](https://libertyjusticecenter.org/amicus/calvary-chapel-san-jose-v-california/));
  no commentary confirming or denying a hold, and nothing about a disposition.
  The hold inference rests on the docket pattern in the provisioned snapshot.

## CourtListener MCP

- None used (the schema was loaded but no MCP call was needed; the provisioned
  snapshot was fresher than any secondary docket source).

Total external retrieval: 4 corpus queries + 2 web searches — within budget.
