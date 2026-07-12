# Retrieval log

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.” Purpose: establish the modern cert baseline and the Ninth Circuit bucket. The rendered statpack reported a 4.9% overall modern grant rate and a 5.3% grant rate for the Ninth Circuit bucket; relist and CVSG values were unknown in this slice.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --era 2020s --citation 'District of Columbia v. Heller' --limit 8 --corpus-backend ranged`
  - Purpose: retrieve similar resolved modern Supreme Court priors citing *Heller*.
  - Result: failed because the runner could not resolve the remote corpus host. No prior rows were returned, and no `ranged corpus reads: …` line was emitted.

## CourtListener MCP

- Searched opinions for `"large-capacity magazines" Bruen -Duncan`, filed after January 1, 2024. Purpose: identify related post-*Bruen* magazine decisions without seeking this petition's disposition. Results included *Hanson v. District of Columbia* and other lower-court litigation.
- Searched opinions for `Benson "large-capacity magazine"`. Purpose: identify the decision referenced by the snapshot's March and April supplemental filings.
- Searched by case name for *Benson v. United States*, limited to January 1 through July 12, 2026. Purpose: confirm the court, date, docket number, and opinion identifier.
- Retrieved CourtListener opinion item 11270885, *Benson v. United States* (D.C. Mar. 5, 2026). Purpose: read the related court's holding and procedural context. The majority held the District's analogous magazine ban unconstitutional and reported that the United States conceded the point.
- Searched by case name for *Hanson v. District of Columbia*, limited to March 1 through July 12, 2026. Purpose: check publicly available procedural context following *Benson*.
- Retrieved CourtListener opinion item 11296664, *Hanson v. District of Columbia* (D.D.C. Mar. 30, 2026). Purpose: determine whether *Benson* was final. The opinion stated that en banc proceedings in *Benson* had not concluded as of March 30.
- Searched opinions for `"Tyree Benson"`, filed after March 5 through July 12, 2026. Purpose: check for a later published en banc opinion. No results were returned.

No web searches were used. I did not search for this case's own disposition or subsequent history.
