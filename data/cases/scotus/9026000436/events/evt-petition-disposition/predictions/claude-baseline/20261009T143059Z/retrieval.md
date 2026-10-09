# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 12` — twelve most recent resolved SCOTUS priors (eleven denials, mostly at distribution count 0-1, one GVR at count 3); used for the shape of the recent docket only, no filter matched this case's subject. stderr: `ranged corpus reads: 5 GET(s), 1245184 byte(s)`.
- `metrics/statpack.md` (committed) — modern discretionary-cert disposition section, originating-circuit cut (ca2), relist-count and CVSG cuts (paid scored segment), and the sal-v4 "Segment base rate by salience band" table (pooled `baseline` bracketed `reached` figures, OT2017-OT2025).

## CourtListener MCP (forward mode, no restriction; none sought this case's disposition)

1. `search` type=d court=scotus q="Lapham Walgreen" — 0 results (the RECAP docket index does not carry SCOTUS dockets).
2. `search` type=d court=scotus q='"FMLA" retaliation "but-for" causation' — 0 results (same reason).
3. `search` type=o court=ca2 q='"Woods v. START" "Loper Bright" FMLA causation' — 0 results.
4. `search` type=o court=scotus q="Lapham Walgreen" — 0 results.
5. `search` type=o court=ca2 case_name=Ramadei — 0 results (the summary order is not in the opinion index; read it from the petition appendix instead).
6. `search` type=o q='FMLA retaliation causation "Loper Bright" "but-for"' filed_after=2024-07-01 — 0 results.
7. `search` type=o court=ca11 citation="88 F.4th 879" — 1 result: Lapham v. Walgreen Co. (Dec. 13, 2023), cluster 9451563; confirmed the Eleventh Circuit decision the petition relies on exists as cited.
8. `search` type=o court=ca2 q="FMLA retaliation" filed_after=2025-06-01 — 1 result: Haran v. Orange Business Services, Inc. (Nov. 25, 2025, published), cluster 10742017.
9. `search` type=d court=ca2 docket_number=25-587 — 1 result: Ramadei v. Radiall USA, Inc., docket 72417495 (filed Mar. 13, 2025); confirmed the appellate docket.
10. `search` type=o court=ca2 case_name=Haran q='"motivating factor" OR "but-for" OR Woods OR "Loper Bright"' — 1 result (same cluster).
11. `search` type=o court=scotus q='"Family and Medical Leave Act" retaliation causation' filed_after=2023-01-01 — 0 results (no SCOTUS opinion or statement on FMLA causation since 2023).
12. `call_endpoint` opinions cluster=10742017 fields=id,type,plain_text — read the Haran opinion: it cites Woods for the FMLA framework and resolves retaliation at the pretext step without addressing the causation standard or Loper Bright; DOL appeared as amicus for the plaintiff.

## Web searches

None.
