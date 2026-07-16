# Retrieval log — claude-baseline / 20260716T205846Z

## Corpus tooling

1. `uv run fedcourts query --court scotus --citation "Thornburg v. Gingles" --citation "52 U.S.C. § 10301" --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
2. `uv run fedcourts query --court scotus --citation "478 U.S. 30" --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
3. `uv run fedcourts query --court scotus --topic "voting rights" --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
4. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   → 5 rows (recent grants/denials; no VRA/redistricting priors surfaced).
   stderr: `ranged corpus reads: 418 GET(s), 109576192 byte(s)`

Base rates: committed `metrics/statpack.md` (modern discretionary-cert slice;
relist and CVSG cuts; per-Term table). Note: the "Segment base rate by salience
band" table referenced in the prompt is not present in the committed statpack.

## CourtListener MCP

None — the provisioned snapshot and filed-document texts covered the docket, so no
MCP lookups were needed.

## Web searches (engine-surfaced)

1. WebSearch: `Louisiana v. Callais Supreme Court decision holding Voting Rights Act Section 2`
   → confirmed *Callais* decided 4/29/2026 (146 S. Ct. 1131, 6–3): Louisiana's
   second majority-minority district held an unconstitutional racial gerrymander;
   §2 vote-dilution reconstrued to require proof of race-based motive. Sources:
   supremecourt.gov slip opinion (24-109), SCOTUSblog, Congress.gov LSB11431,
   Wikipedia, Campaign Legal Center, Brennan Center.
2. WebSearch: `Supreme Court GVR "in light of" Callais redistricting petitions June 2026`
   → May 2026 GVR wave: Mississippi and North Dakota map cases plus *Allen v.
   Caster* (Alabama) GVR'd in light of *Callais*, Sotomayor/Kagan/Jackson
   dissenting; Volokh Conspiracy post (5/18/2026) on the breadth of the GVR
   practice. Sources: reason.com/volokh, Wikipedia, NPR, electionlawblog.org.
3. WebSearch: `"Garcia v. Hobbs" Supreme Court cert petition 2026 Washington redistricting mootness`
   → companion petition *Garcia v. Hobbs*, No. 25-901, filed 1/23/2026 (mootness
   of the racial-gerrymander challenge to original LD-15); Washington State
   Standard headline (6/2/2026): "WA urges US Supreme Court to take redistricting
   case." Sources: thearp.org, democracydocket.com, washingtonstatestandard.com.
4. WebSearch: `Washington attorney general brief Trevino Supreme Court "Soto Palmer" Callais grant vacate remand state urges`
   → the State of Washington's 6/2/2026 response brief (StateBOR.pdf, docket
   25-918) asks the Court to grant, vacate, and remand for the Ninth Circuit to
   apply *Callais*. Sources: supremecourt.gov docket PDFs, thearp.org.
5. WebFetch: KUOW, `us-supreme-court-may-look-at-wa-redistricting-case`
   → observers frame the options as deny / GVR under *Callais* / plenary grant;
   Secretary Hobbs opposed disrupting the map before the August 2026 primary;
   plaintiffs' counsel argues the remedial map reflects a community of interest.
6. WebFetch attempts that failed with HTTP 403/429 (no content retrieved):
   washingtonstatestandard.com, newsfromthestates.com, columbian.com,
   sunnysidesun.com article copies, and the supremecourt.gov StateBOR.pdf.

No search sought this petition's own disposition (none exists; it is distributed
for the 9/28/2026 conference).
