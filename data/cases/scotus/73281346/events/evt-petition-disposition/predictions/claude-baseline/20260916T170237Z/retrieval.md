# Retrieval log

## Corpus (read-only, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal`
   No rows returned. stderr: `ranged corpus reads: 764 GET(s), 200081408 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   Eight rows read (recent OT2025 grants and substantive applications; none topically similar to a qualified-immunity petition). stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`

Base rates: read the committed `metrics/statpack.md` sections "Modern discretionary-cert petitions by disposition", "by originating circuit", "by relist count", "by CVSG status", "by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)".

## CourtListener MCP

1. `search` (type `o`, court `ca10`, filed after 2025-10-01, query `"Burke v. Pitts" OR ("Pitts" AND "Bartlesville" AND "qualified immunity")`) to confirm the Tenth Circuit opinion is published (Burke v. Pitts, No. 24-5134, filed 2025-11-04, status Published).

## Web searches (engine-surfaced, forward mode)

1. `"Pitts v. Burke" Supreme Court 25-1062 qualified immunity petition` — only the Tenth Circuit opinion and a training-industry summary of it; no commentary on the cert petition and no disposition.
2. `Supreme Court certiorari granted "officer-created danger" OR "provocation" Barnes v. Felix reserved question 2026` — background on Barnes v. Felix (2025) and its reserved footnote; no grant on that question found.
3. `Supreme Court summary reversal qualified immunity excessive force per curiam 2025 2026` — Zorn v. Linton, No. 25-297, per curiam summary reversal 6-3 on 2026-03-23.
4. `Zorn v. Linton 25-297 docket "response requested" OR relisted ...` — Zorn's docket path: waiver 2025-09-16, response requested 2025-10-02, reversal 2026-03-23.
5. `Supreme Court denies certiorari police officers qualified immunity excessive force petition 2026 ...` — Crockett v. Krueger and Craig v. Krueger (Tenth Circuit qualified-immunity petitions) denied 2026-03-23.
6. `"Pitts" "Burke" Bartlesville Supreme Court petition certiorari September 2026 conference qualified immunity` — nothing about this petition beyond the Tenth Circuit decision.
7. `"Crockett v. Krueger" 10th Circuit qualified immunity Supreme Court docket ...` — confirmed fully briefed and denied 2026-03-23.
8. `SCOTUSblog relist watch 2026 qualified immunity officer petition "Tenth Circuit" ...` — Reinink v. Hart (25-179), an officer qualified-immunity petition relisted repeatedly in March and April 2026; Crockett/Craig denials.
9. `Barnes v. Felix Kavanaugh concurrence officer "created" danger reserved ...` — confirmed the reservation and the four-Justice concurrence (Kavanaugh, joined by Thomas, Alito, Barrett).

None of the retrieval surfaced this petition's disposition; the conference is 2026-09-28.
