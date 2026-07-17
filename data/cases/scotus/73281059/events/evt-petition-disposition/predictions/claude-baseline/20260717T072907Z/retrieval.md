# Retrieval log — scotus/73281059 evt-petition-disposition (claude-baseline, 20260717T072907Z)

Forward-mode cell; retrieval unrestricted per the contract. The CourtListener
MCP server was configured but not used — SCOTUS cert-stage dockets are better
served by the provisioned supremecourt.gov snapshot, and the decisive
companion-case signal came from the open web.

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --citation "Arizona v. Inter Tribal Council of Ariz., Inc., 570 U.S. 1" --citation "Brnovich v. Democratic National Committee, 594 U.S. 647" --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --topic election --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --citation "570 U.S. 1" --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`

Base rates came from the committed `metrics/statpack.md` (modern
discretionary-cert disposition, relist-count, CVSG, circuit, and per-Term
tables). The salience-band table named in the prompt is absent from the
committed statpack version.

## Web searches

1. `Supreme Court 25-1017 25-1019 25-1022 Mi Familia Vota cert petition Arizona proof of citizenship conference`
   — identified companions: RNC v. Mi Familia Vota (25-1017), Arizona v.
   Promise Arizona (25-1022); surfaced SCOTUSblog Relist Watch and press.
2. `Supreme Court grants certiorari "Republican National Committee v. Mi Familia Vota" 25-1017 Arizona proof of citizenship July 2026`
   — confirmed cert granted in companion 25-1017 (Cronkite News 2026-06-29,
   AZ Capitol Times 2026-07-01, Ballotpedia 2026-07-02/07, Washington
   Examiner; NBC affiliate: Court took up "part of" the dispute).
3. `"Petersen v. Mi Familia Vota" OR "25-1019" cert petition held OR denied OR relisted after RNC grant July 2026`
   — no report of any action on 25-1019 after the RNC grant; consistent with
   the snapshot (held).

## Web fetches

1. https://www.scotusblog.com/2026/06/penultimate-relists-papers-parents-and-procedural-puzzles-/
   — Relist Watch (2026-06-25): all three petitions first relisted after the
   June 18 conference; SG supported the RNC petition and opposed 25-1019 and
   25-1022.
2. https://www.nbcnews.com/politics/supreme-court/supreme-court-weigh-arizonas-proof-citizenship-voting-law-rcna351239 — HTTP 403, not retrieved.
3. https://www.supremecourt.gov/RSS/Cases/JSON/25-1017.json — HTTP 403, not retrieved.
4. https://www.supremecourt.gov/RSS/Cases/JSON/25-1022.json — HTTP 403, not retrieved.

All companion-case information used predates the provisioned snapshot
(2026-07-17) and concerns companion dockets, not this petition's own
disposition, which remains undecided. Disclosed as decisive forward signal in
`flags.json`.
