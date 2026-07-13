# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted the paid-fee-class detail in `metrics/statpack.json`. The incomplete 2025-Term sample reports an estimated 7.2% grant rate for paid petitions (10 grants among 139 estimated resolved paid matters).

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --era 2020s --citation 'Kisor v. Wilkie, 588 U.S. 558 (2019)' --citation 'Stinson v. United States, 508 U.S. 36 (1993)' --limit 10 --corpus-backend ranged`
- Purpose: retrieve resolved SCOTUS priors sharing the petition's principal authorities.
- Result: failed before returning priors because the ranged corpus remote could not be resolved or reached. No `ranged corpus reads: …` line was emitted.

## CourtListener MCP

- Opinion search: `Kisor Stinson Sentencing Guidelines commentary deference circuit split`, limited to federal courts of appeals and opinions filed before 2026-07-13. Purpose: identify general appellate authority on the split without searching this docket or its disposition. The result identified *United States v. Curtis Jenkins*, 50 F.4th 1185 (D.C. Cir. 2022).
- Exact opinion search: *United States v. Vargas*, Fifth Circuit, 2023. Purpose: verify a representative decision continuing broader *Stinson* deference. The result identified 74 F.4th 673, filed July 24, 2023.
- Exact opinion search: *United States v. Dupree*, Eleventh Circuit, 2022–2023. Purpose: verify a representative contrary en banc decision applying *Kisor*. The result identified 57 F.4th 1269, filed January 18, 2023, and the superseded panel decision.
- Exact opinion search: *United States v. Riccardi*, Sixth Circuit, 2020–2021. Purpose: verify another decision applying *Kisor* to Guidelines commentary. The result identified 989 F.3d 476, filed March 3, 2021.

No web searches or direct REST calls were used. No lookup sought this case's disposition or subsequent history.
