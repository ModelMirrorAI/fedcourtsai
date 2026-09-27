# Retrieval log

Beyond the provisioned snapshot (`2026-09-23.json`), `context.json`, the
provisioned documents (`petition.txt`, `questions-presented.txt`,
`documents.json`), and the committed `metrics/statpack.md`:

## Corpus CLI

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 4`
  `ranged corpus reads: 10 GET(s), 2490368 byte(s)`
  Returned four 2025-Term emergency applications (DHS v. League of Women
  Voters; People Not Politicians v. Onder x2; NRCC v. Brown) — not comparable
  priors for a pro se paid cert petition. Not used.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 4`
  `ranged corpus reads: 0 GET(s), 0 byte(s)`
  Returned four September 2026 denied applications (Banks v. Brown; Downs v.
  Collins; Cheleden v. Florida DBPR; Ramey v. Texas). Not comparable; not
  used.

## CourtListener MCP (9 calls, 1 errored)

1. `search` (type `o`, court `ca6`, q "Lowery Cheboygan") — 0 results; the
   Sixth Circuit's disposition is not in the opinion collection.
2. `search` (type `d`, courts `mied`,`ca6`, q "Lowery Cheboygan") — 1 result:
   Sixth Circuit docket 25-1514, *Marlin Lowery v. Cheboygan, MI Area Public
   Schools*, CourtListener docket id 70639487.
3. `call_endpoint` `docket-entries` (docket 70639487) — 5 entries, empty
   descriptions: 2025-06-26 (#8), 2025-11-21 (#19), 2026-04-01 (#24, #25),
   2026-06-24 (#27).
4. `call_endpoint` `dockets` (court `mied`, docket 1:24-cv-11604) — *Lowery v.
   Cheboygan Area Public Schools*, docket id 68880369, Judge Linda V. Parker,
   filed 2024-06-20, terminated 2025-02-26, nature of suit "Constitutional -
   State Statute".
5. `call_endpoint` `recap-documents` (docket 70639487) — errored on an invalid
   `fields` value; retried as call 6.
6. `call_endpoint` `recap-documents` (docket 70639487) — document descriptions
   for the Sixth Circuit entries: #8 "ruling letter sent", #19 "clerk order
   filed", #24 "judge order filed", #25 "entry of judgment", #27 "judge order
   filed"; none available as text.
7. `call_endpoint` `docket-entries` (docket 68880369) — 10 most recent
   district entries; #39 (2025-07-21) is the order denying reconsideration;
   #40–#44 are appellate mailings through 2026-09-24.
8. `call_endpoint` `recap-documents` (docket 68880369, entries ≥ 33) —
   descriptions; #34 (2025-02-26, 5 pp.) and #39 (4 pp.) available as text.
9. `call_endpoint` `recap-documents` (id 431363864, `plain_text`) — the
   district court's February 26, 2025 opinion adopting the magistrate judge's
   report: § 1983 due process and CARES Act claims; motions to dismiss and for
   summary judgment granted; complaint dismissed sua sponte against all
   defendants for failure to state any federal claim.

All CourtListener material predates the petition's filing. No web searches.
No lookup of this petition's own disposition or of any post-docketing SCOTUS
activity beyond the provisioned snapshot.
