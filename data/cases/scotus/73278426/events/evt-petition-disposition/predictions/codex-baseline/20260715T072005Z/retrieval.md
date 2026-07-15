# Retrieval

## Committed base rates

- Read `metrics/statpack.md` and the Term 2025 paid-fee detail in `metrics/statpack.json`. Used the modern cert-petition, originating-circuit, relist-count, and Term/fee-class rates for calibration.

## Corpus lookup

- `uv run fedcourts query --court scotus --era 2020s --citation '554 U.S. 570' --citation '597 U.S. 1' --limit 12 --corpus-backend ranged` — attempted to retrieve similar resolved SCOTUS priors. The lookup failed before any result or ranged-read statistic because the remote corpus host could not be resolved. No `ranged corpus reads: ...` line was printed.

## CourtListener MCP

- Opinion search for `"Snope v. Brown" AR-15`, limited to SCOTUS opinions filed from 2024 through July 15, 2026 — no results.
- Opinion search for `Snope Brown assault weapons` over the same period — surfaced related lower-court opinions, including the Second Circuit opinion in this litigation, *Duncan v. Bonta*, and July 9, 2026 Seventh Circuit opinions in the *Barnett/Harrel* litigation. I did not seek or retrieve this petition's disposition.
- Opinion search for `Barnett v. Raoul`, limited to July 1–15, 2026 — confirmed July 9 opinions in Seventh Circuit docket 24-3060 and returned opinion identifiers 11392780 and 11392781.
- Opinion endpoint lookups for identifiers 11392780 and 11392781 — the requested opinion-text fields were empty; only metadata was available.
- Separate opinion searches for `"CALEB BARNETT" "REVERSED"`, `"CALEB BARNETT" "AFFIRMED"`, and `"CALEB BARNETT" "Second Amendment"`, limited to July 8–15, 2026 — the first and third returned the July 9 related opinions; the second returned none. Because the snippets contained no holding, I used only the fact that a new appellate decision exists, not its result or reasoning.
- SCOTUS docket searches for docket 25-198, `Gator's Custom Guns`, and `Banta Ferguson`, limited through July 15, 2026 — no results.
- Opinion citation search for `145 S. Ct. 1534` — no results.

No general web search was used.
