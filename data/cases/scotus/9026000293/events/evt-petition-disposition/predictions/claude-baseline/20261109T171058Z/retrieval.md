# Retrieval log

- WebFetch: supremecourt.gov docket 26-292 (Havlish). Live entries through Nov 9, 2026 ("DISTRIBUTED for Conference of 11/13/2026").
- WebFetch: supremecourt.gov docket 26-293 (this case). Entries through the Nov 9 redistribution; no disposition.
- WebSearch (standard): "Exxon Mobil v. Corporación CIMEX Supreme Court decision 2026 foreign state FSIA holding". Decided June 23, 2026, 6-3 (Kavanaugh): Helms-Burton abrogates Cuban instrumentalities' immunity.
- WebSearch (standard): "Havlish v. Taliban petition certiorari Da Afghanistan Bank Supreme Court 26-292". Docket and filing links only. No disposition of this case surfaced.
- WebFetch: Faegre Drinker summary of *CIMEX*. Says nothing about who decides "foreign state" status.
- WebFetch: Havlish Oct 30, 2026 motion and supplemental brief PDF (binary), then extracted locally with `uv run fedcourts pdf-text`. Says the Taliban waived; argues a CA9/CA11 split and answers Faiq on vehicle issues.
- Corpus: `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` was a usage error (unknown flag), and I re-issued it without `--era`.
- Corpus: `uv run fedcourts query --court scotus --disposition gvr --limit 5`. `ranged corpus reads: 37 GET(s), 9699328 byte(s)`. Generic GVR priors, none comparable.
- Read `metrics/statpack.md` (relist, CVSG and amicus cuts; sal-v8 band table).
- No CourtListener MCP calls.
