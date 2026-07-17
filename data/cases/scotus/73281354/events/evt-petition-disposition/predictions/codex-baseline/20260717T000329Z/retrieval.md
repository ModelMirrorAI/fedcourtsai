# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, especially modern discretionary-cert dispositions, originating circuit, relist, CVSG, and Term 2025 paid-petition rates.

## Corpus lookup

- `uv run fedcourts query --court scotus --citation 'Illinois Brick Co. v. Illinois, 431 U.S. 720' --citation 'Bell Atlantic Corp. v. Twombly, 550 U.S. 544' --limit 8`
  - Failed before returning priors because the ranged corpus remote could not be resolved. No `ranged corpus reads: ...` line was printed.

## CourtListener MCP

- Opinion search for `"Illinois Brick" "lost profits" indirect purchaser`, filed before July 17, 2026. Results included the Sixth Circuit's 2025 panel decision and January 2026 rehearing denial in *Academy of Allergy & Asthma v. Amerigroup Tennessee*, and the Third Circuit's *Howard Hess Dental Laboratories v. Dentsply*.
- Opinion search for `"opportunity to conspire" "trade association" plus factor`, filed before July 17, 2026. Results included antitrust decisions applying the plus-factor framework.
- Exact case-name search for *Academy of Allergy & Asthma*, limited to 2025–2026, to identify the panel opinion and rehearing-denial opinion.
- Retrieved CourtListener opinion 11240564, the Sixth Circuit's January 13, 2026 published order and separate statements denying rehearing en banc. It confirms that no judge requested an en banc vote, while Judges Bush and Murphy separately described the competing interpretations and the potential need for Supreme Court clarification.
- Appellate opinion search for `"opportunity to conspire" "trade association"` across the First, Third, Sixth, Ninth, Eleventh, and D.C. Circuits; it returned no results for that exact phrase combination.

No web search was used. No lookup sought or surfaced this petition's Supreme Court disposition.
