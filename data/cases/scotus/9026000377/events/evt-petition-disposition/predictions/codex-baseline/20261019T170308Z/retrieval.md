# Retrieval log

No live corpus query or open-events call was made; there are no ranged-corpus transfer lines to report. No target-case outcome or subsequent-history lookup was made.

## Repository context

- Read the task contract, applicable repository instructions, prediction schema, and tooling/flags schemas.
- Read committed `metrics/statpack.md`: modern-cert, circuit, paid relist/CVSG, and sal-v4 reached-band tables. Read `metrics/statpack.json` for exact baseline risk-set rates and denominators for displayed Terms 2017-2025; pooled them with jq, yielding 644 / 12,883. This is the checked-in pack, not a refreshed corpus read.
- Ran `uv run fedcourts paths --court scotus --docket 9026000377 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; retrying with a writable temporary cache and `--no-sync` succeeded. The evaluator-only outcome was neither named nor opened.

## Web attempts

1. `web.run` search batch: `site.supremecourt.gov opinions Ruan United States 2022 20-1410` and `site.law.cornell.edu/supct/html Neder United States 527 U.S. 1 contested overwhelming evidence`. The tool returned no usable results or text.
2. `web.run` open of the official Ruan slip-opinion location, `https://www.supremecourt.gov/opinions/21pdf/20-1410_1an2.pdf`. The tool returned no usable text. No inference rests on this attempted retrieval.

## CourtListener MCP

1. `search(type="o", citation="527 U.S. 1", num_results=1)`. Returned an unrelated First Circuit labor case, UMass Memorial Medical Center, 527 F.3d 1 (2008). Disregarded; its opinion was not opened.
2. `search(type="o", case_name="Neder v. United States", court="scotus", filed_before="2000-01-01", num_results=2, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`. Located the June 10, 1999 merits decision, 527 U.S. 1, including lead opinion 9433818. The results also included Neder's 1998 cert-grant order; that concerns the historical precedent, not this cell's petition.
3. `search_document(opinion_id=9433818, query="contested", snippet_size=1100)`. Consulted the majority's discussion of the contested-element and rational-contrary-finding tests, especially page 19.
4. `search(type="o", case_name="United States v. Smithers", court="ca4", filed_after="2024-01-01", filed_before="2024-12-31", num_results=1, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`. Located United States v. Joel Smithers, 92 F.4th 237, decided February 2, 2024, opinion 9929725.
5. `search_document(opinion_id=9929725, query="copious", snippet_size=2200)`. Consulted the harmless-error analysis and its treatment of evidence supporting the defense despite powerful prosecution evidence, printed opinion pages 23-24 / reporter pages 251-52.

All external substantive material consulted predates the provisioned snapshot. No outcome-revealing material about this petition surfaced.
