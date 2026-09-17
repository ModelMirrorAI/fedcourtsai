# Retrieval

- Read committed metrics/statpack.md: modern discretionary-cert dispositions, paid scored-segment relist/CVSG cuts, and sal-v4 reached-band table. Anchored only on displayed Terms 2017–2024 for this Term-2025 cell. Computed an approximate denominator-weighted baseline rate from the printed cells using uv run python; no corpus query was involved.
- Web search attempted: `site.supremecourt.gov Rule 10 considerations governing review certiorari` and `site.loc.gov "Haines v. Kerner" "519"`. The tool returned no usable results.
- Web open attempted: Cornell's Supreme Court Rule 10 page. The tool returned no usable content; not used as evidence.
- CourtListener MCP search: type=o, citation="404 U.S. 519", num_results=1. Returned an unrelated Copy-Mor order; disregarded it.
- CourtListener MCP search: type=o, case_name="Haines v. Kerner", court=scotus, num_results=2. Identified the principal opinion and a rehearing entry. Did not rely on the search metadata's date for the principal decision.
- CourtListener MCP read_document: opinion_id=108432. Read Haines v. Kerner, 404 U.S. 519 (1972), especially pages 520–21, for the limited liberal-construction holding.
- Ran `uv run fedcourts paths --court scotus --docket 73246321 --event evt-petition-disposition --role predictor`; initial cache initialization failed, then succeeded with a temporary writable cache.

No fedcourts query or open-events calls; no ranged corpus reads line was emitted. No retrieval sought this petition's outcome, subsequent history, or another predictor's output. All case-specific substantive evidence came from the provisioned inputs.
