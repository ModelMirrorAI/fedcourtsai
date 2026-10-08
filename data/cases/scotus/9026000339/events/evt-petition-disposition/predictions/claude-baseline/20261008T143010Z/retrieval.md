# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 9026000339 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  `ranged corpus reads: 28 GET(s), 7274496 byte(s)`
  Returned eight recent OT2025/OT2026 grants (three cert dockets and five
  application dockets); none concerned diversity jurisdiction or a comparable
  posture. Used to confirm the corpus service was live and that the surface
  carries no topical filter for this question; no prior informed the number.
- `metrics/statpack.md`: modern discretionary-cert by disposition, by
  originating circuit (ca4 row), relist-count and CVSG cuts, the per-Term
  table, and the sal-v4 segment base rate by salience band (baseline column,
  Terms 2017 through 2025, pooled on the bracketed `reached` figures).
- `docs/salience.md` (sal-v1 feature list, carried into sal-v4): confirmed the
  band keys on relist count, CVSG, and originating circuit only, so the call
  for a response is not in the band.

## CourtListener MCP

- `search` type=o, q="FS Medical Supplies" Tanner Pharma, court=ca4 — found
  the published Fourth Circuit opinions (clusters 10881161 and 10881160,
  June 25, 2026).
- `search` type=o, q="1332(a)(3)" "Tango Music" "additional parties", filed
  after 2003 — seven results: the two Fourth Circuit opinions, Tango Music
  itself, and Eighth, Sixth, and S.D. Ohio decisions that cite it on other
  (a)(3) questions; used only to gauge how often Tango Music is cited on this
  point.
- `read_document` opinion 11348682 — the full Fourth Circuit opinion in
  No. 25-2199 (panel, reasoning, footnotes on the third suit and on (a)(1)
  and (a)(2)).
- `read_document` opinion 784045, chunk 0 — the opening of Tango Music, LLC v.
  DeadQuick Music, Inc., 348 F.3d 244 (7th Cir. 2003), to check how squarely
  it decided the question presented here.

## Web

- WebSearch: `"FS Medical Supplies" Tanner Pharma certiorari 26-339 diversity
  jurisdiction LLC foreign member` — surfaced the Justia and CourtListener
  copies of the Fourth Circuit opinion, the WLF case page, a civil-procedure
  blog post on the decision, and a trade-press story on the underlying suit.
  Nothing about a disposition of the petition appeared (the petition is
  pending; the response is due November 5, 2026).
- WebSearch: `Supreme Court petition "1332(a)(3)" dual citizen LLC foreign
  member "additional parties" certiorari denied OR granted` — found no prior
  Supreme Court petition on this question; results were lower-court decisions
  and practitioner articles.
- WebFetch `wlf.org/case/fs-medical-supplies-v-tanner/` — WLF's summary of its
  October 6, 2026 amicus brief supporting the petition; no status beyond the
  filing.
- WebFetch `tlblog.org/fourth-circuit-answers-civ-pro-hypothetical/` — a
  civil-procedure academic's post on the decision below; neutral on the
  holding, questions the court's refusal to drop the foreign defendant, no
  mention of the petition.
- WebFetch of the petitioner's September 22, 2026 letter to the Clerk
  (`supremecourt.gov/DocketPDF/26/26-339/425248/...Letter re Distribution...pdf`);
  the fetcher could not read the PDF, so I extracted its text locally with
  pypdf (one page): petitioner asked that the petition be distributed for a
  conference after the October 14 amicus deadline because WLF intended to
  file in support.

Retrieval total: 2 corpus commands (1 real query), 4 CourtListener MCP calls,
2 web searches, 3 web fetches, 1 local PDF extraction.
