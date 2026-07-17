# Retrieval log — scotus/73298285 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Mode: `forward` (retrieval unrestricted; nothing outcome-revealing exists — the
petition is pending, response due Aug. 17, 2026).

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition",
  originating-circuit, relist, CVSG, and per-Term tables.
- `metrics/statpack.json` — per-Term fee-class detail (paid est. grant rate:
  5.4% Term 2025, 6.9% Term 2024). No "Segment base rate by salience band"
  section is present in the committed statpack.

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
   - 10 granted 2020s SCOTUS rows returned; captions empty on live-channel
     rows, so of limited use beyond confirming corpus reachability.

## CourtListener MCP lookups

1. `search(type=o, court=scotus, q="Bivens", filed_after=2025-01-01, order_by="dateFiled desc")`
   - 7 results: Cisco Systems v. Doe (24-856, decided 2026-06-23), Hencely v.
     Fluor (24-924, 2026-04-22), Goldey v. Fields (24-809, 2025-06-30,
     summary reversal), Martin v. United States (24-362, 2025-06-12).
   - Confirms no plenary merits decision yet on the Fourth Amendment
     new-context split; Goldey is the most recent Bivens-restricting signal.

## Web searches

1. `Supreme Court cert petition Bivens "new context" circuit split 2026 Arias Herzon Schwartz Miller`
   - Surfaced Nielsen v. Watanabe (25-417) cert petition and SCOTUSblog relist
     coverage; indicated the Court granted review in Nielsen.
2. `"Nielsen" "Watanabe" Supreme Court cert granted 25-417 Bivens`
   - Confirmed grant in Nielsen v. Watanabe (25-417), from the Ninth Circuit's
     Watanabe v. Derr: whether a federal prisoner may sue under Bivens for
     deliberate indifference; alternative-remedies/step-one and
     injury-severity questions. Sources: SCOTUSblog case page
     (https://www.scotusblog.com/cases/nielsen-v-watanabe/), supremecourt.gov
     docket 25-417.
3. `SCOTUSblog "Supreme Court agrees to hear case on the ability to sue federal officials" Nielsen Watanabe June 2026 Mohan`
   - Confirmed the June 2026 grant for OT2026
     (https://www.scotusblog.com/2026/06/supreme-court-agrees-to-hear-case-on-the-ability-to-sue-federal-officials-/)
     and that Mohan v. Watkins (25-952, the Seventh Circuit companion) is being
     held pending Nielsen — the SG's own filings recommended granting Nielsen
     and holding Mohan.

None of the searches surfaced any disposition of this petition itself (none
exists). Total retrieval: 1 corpus query + 1 MCP search + 3 web searches,
well within budget.
