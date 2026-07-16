# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially the modern discretionary-cert, originating-circuit, relist, CVSG, and per-Term sections. Relevant figures: Ninth Circuit modern cert petitions 3.0% granted; no-relist petitions 0.8% granted; CVSG petitions 27.1% granted among 59 resolved cases; Term 2025 overall petitions 2.5% granted.
- Consulted `metrics/statpack.json` for the Term 2025 paid-petition estimate: 5.364995602462621% granted.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --topic securities --era 2020s --limit 8`
- Result: failed before the corpus could be opened because the remote host could not be resolved. No result rows were returned and no `ranged corpus reads: ...` line was emitted.

## CourtListener MCP

- Opinion search for `"Item 303" "interim financial"` in the First, Second, Fifth, Ninth, and Eleventh Circuits, filed before February 5, 2026: no results.
- Opinion search for `"extreme departure"` in those circuits, filed before February 5, 2026: 38 results; the returned leaders were largely unrelated Eleventh Circuit opinions and did not materially inform the forecast.
- Opinion search for `"Item 303"` in those circuits, filed before February 5, 2026: four results, including *Oxford Asset Management Ltd. v. Jaharis*, 297 F.3d 1182 (11th Cir. 2002), already analyzed by both briefs.
- Opinion search for `"interim financial"` in the First, Second, Third, Fifth, Ninth, Tenth, and Eleventh Circuits, filed before February 5, 2026: one unrelated result.

No web searches were used, and no search targeted this case's disposition or subsequent history.
