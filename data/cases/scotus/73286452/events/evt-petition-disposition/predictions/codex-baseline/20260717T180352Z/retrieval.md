# Retrieval beyond the provisioned inputs

## Corpus and base rates

- Read `metrics/statpack.md` and the 2025-Term paid-fee detail in `metrics/statpack.json`. The relevant anchors were a 5.36% estimated grant rate for paid 2025-Term petitions, a 3.0% modern-cert grant rate for Ninth Circuit origins, and the relist/CVSG cuts.
- Ran `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` (with the runner-local package cache redirected to `/tmp`). Output: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`. The returned sample supplied recent grant-side procedural priors; it did not include or prompt a lookup of this case.

## CourtListener MCP

All searches were limited to opinions and pre-disposition legal context; none sought this petition's Supreme Court docket or outcome.

- Searched SCOTUS opinions for *Chiles v. Salazar*, filed March 2026, and confirmed two versions dated March 31, 2026.
- Searched Ninth Circuit opinions for *Khatibi v. Hawkins* filed before 2026 and confirmed the July 25, 2025 panel opinion and December 29, 2025 rehearing order.
- Repeated the *Chiles* search requesting docket, cluster, and opinion metadata; identified docket 24-539 and opinion item 11297186.
- Searched the December 2025 *Khatibi* rehearing record for opinion metadata; identified opinion item 11232600.
- Ran a targeted *Chiles* opinion search for professional/private-speech language; the search returned no separately indexed hit.
- Ran a targeted July 2025 *Khatibi* panel-opinion search for government-speech, public-perception, control, and regulation terms; confirmed the panel opinion.
- Ran a targeted December 2025 *Khatibi* rehearing-opinion search for the dissent's “out of step” discussion; confirmed the rehearing opinion.
- Consulted the CourtListener `opinions` endpoint schema to request only needed opinion-text fields.
- Retrieved opinion item 11297186 and extracted the passages explaining that First Amendment protection extends to licensed professionals.
- Retrieved opinion item 11232600 and extracted the rehearing dissents' discussion of history, public perception, state control, and conflict with other precedent.
- Searched *Chiles* opinion metadata for author/panel information; confirmed Justice Gorsuch as author.
- Re-read the limited portions of opinion item 11297186 identifying the judgment and alignment: reversal and remand, with eight Justices joining the Court's opinion and Justice Jackson dissenting.
- Searched the July 2025 *Khatibi* panel record for opinion metadata; identified opinion item 11107766.

No web search was used.
