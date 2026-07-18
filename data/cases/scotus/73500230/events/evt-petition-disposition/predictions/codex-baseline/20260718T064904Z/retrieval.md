# Retrieval

The following sources were consulted beyond the provisioned event, snapshot, document manifest, questions presented, petition, and context file. No search targeted this case's disposition or post-snapshot history.

## Corpus and base rates

- Read `metrics/statpack.md`, especially the modern discretionary-cert, originating-circuit, relist, CVSG, and per-Term sections. Read the 2025 paid fee-class entry in `metrics/statpack.json`. Relevant estimates were 5.36% for 2025-Term paid petitions, 3.0% for modern petitions from the Ninth Circuit, 0.8% for zero-relist petitions, and 3.0% without a CVSG.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
  - `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
  - Returned ten recent grants. The records reinforced that many grants carried repeated distributions, a CVSG, or unusually salient federal questions; this case currently has none of those developed docket signals.

## CourtListener MCP

- Opinion search for `anti-SLAPP "Shady Grove" "Rule 56"`, limited to filings before 2026-07-18. Returned 34 matches and confirmed leading split authorities including *Klocke* and *Carbone*.
- Opinion search for `Gopher Media v. Melone`, limited to filings before 2026-07-18. Returned the Ninth Circuit's 2025 panel and en banc opinions.
- Narrowed opinion search for the post-September-2025 *Gopher Media* opinion. Returned the October 9, 2025 en banc opinion, docket 24-2626.
- Supreme Court docket search for related petition No. 25-1067, limited to filings before 2026-07-18. Returned no indexed result; no status was inferred.
- Opinion search for `Berk v. Choy`, limited to filings before 2026-07-18. Returned the Supreme Court's January 20, 2026 opinion, docket 24-440.
- Opinion endpoint lookup for *Berk*, opinion id 11243340. Consulted its syllabus and holding that Delaware's affidavit-of-merit requirement was displaced by the Federal Rules under the *Shady Grove* framework.

No general web search was used.
