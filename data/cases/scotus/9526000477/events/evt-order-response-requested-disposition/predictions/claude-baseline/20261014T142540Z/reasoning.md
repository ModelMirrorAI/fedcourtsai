# Rationale — P(unqualified grant) = 0.72

**Inputs read.** Snapshot `2026-10-08.json` (one proceedings entry: the stay
application, submitted to The Chief Justice, Oct. 8, 2026); `context.json`
(forward mode, interim, `band: null`, `response_requested: false`,
`referred_to_court: false`, `amicus_briefs: 0`, term 2026); the provisioned
application text (`application.txt`, 114 pp., truncated per `documents.json`;
I read the application body — statement of the case and the opening of the
argument — not the appendix).

**Anchor.** The statpack's "The interim docket (applications)" section, pooled
over application-Terms strictly before 2026 within ten Terms: 2023–2025 carry
substantive counts (2016–2022 are fully unparsed and contribute nothing):
granted 18 + 18 + 17 = 53 over resolved 127 + 196 + 226 = 549 → **9.65%**,
clearing the floor of 50. The section's caption describes it as grounding the
scored base rate (the current caption, not the older descriptive-only one).

**Adjustments (large, and I own that).** This is far from a typical
application:
1. *Same case, same panel, prior stay granted.* The Court already found a
   likelihood of no jurisdiction and irreparable harm in Brown I one month
   earlier. The applicants' theory — mandamus cannot aid a jurisdiction the
   court likely lacks, and the writ end-runs the stay — maps directly onto
   that holding. Prior-ruling-in-same-case applications grant at rates far
   above the pool.
2. *Response requested* (per the event's own definition) — the strongest rung
   of the ladder; the population that reaches it grants several times the pool
   rate.
3. *The FCC itself sought a stay below*, so the federal agency appears aligned
   with applicants on interim relief (I infer this from the application; I did
   not see the FCC's papers).
4. *Election proximity* — the Court's Purcell-flavored concern for stability
   runs in applicants' favor here, since the status quo is the existing rule.

**Discounts.** (a) Mootness risk around the Oct. 9 noon deadline if no
administrative stay issued in time, or the FCC acted; (b) a partial or
tailored order reading as a denial; (c) the mandamus orders the agency only to
*decide*, which some Justices may see as less harmful than vacatur of the
rule; (d) I cannot see the respondents' answer. Together these keep me well
below 0.9.

**Increments.** The context's frozen `response_requested: false` conflicts
with the event's `moment: response-requested` (opened Oct. 8) — the request
apparently landed after the snapshot's poll. I set 0.95 because the event's
existence implies the request occurred; see `flags.json`. Referral 0.80;
amicus 0.35 (short timetable).

**Retrieval.** One CourtListener docket search returned nothing for this
docket; I relied on provisioned inputs and the statpack.

**Votes.** Not forecast.
