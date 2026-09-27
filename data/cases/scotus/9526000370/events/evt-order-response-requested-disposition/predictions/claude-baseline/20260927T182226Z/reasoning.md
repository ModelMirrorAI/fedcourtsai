# Reasoning — why P(grant) = 0.20 and the other numbers

## Cell and inputs

- Stage `interim`, moment `response-requested`, event opened 2026-09-18. Mode **forward**; `context.json` freezes `response_requested: true`, `referred_to_court: false`, `amicus_briefs: 0`, `band: null`, `signals_observable: true`, cutoff 2026-09-19 under a `date` cut. Band is null as the prompt says is normal for an interim cell, so no cert band anchor and no caption-class floor apply.
- Snapshot read: `record/snapshots/2026-09-18.json`. It shows two entries: the stay application submitted to Justice Kagan on September 16 and Kagan's September 18 call for a response due September 25.
- Provisioned document: `record/documents/application.txt` (189 pages, `truncated: true`, `empty_text: false`). The truncation cut only the district-court appendix; the full application (statement, both merits sections, equities, conclusion) and the Ninth Circuit's September 1 order with Judge Forrest's partial dissent were intact and I read them.
- Retrieved beyond the record (forward mode, unrestricted): the application's own live docket page (response filed September 25; no referral, no amici, no disposition as of September 27), the respondents' 40-page opposition (fetched as PDF and extracted locally), the Ninth Circuit dockets 26-1746 and 26-5060 and the D. Ariz. docket via the CourtListener MCP, and corpus priors via `fedcourts query`. Details in `retrieval.md`. Nothing outcome-revealing surfaced; the cell is genuinely pending.

## Anchor: the statpack interim section

`metrics/statpack.md`, "The interim docket (applications)". Application-Term 2026 is mine, so the pool is Terms strictly before it within ten Terms with parsed rows: 2025 (17 granted / 226 resolved) and 2024 (14 / 70). Pooled: **31 / 296 = 10.5%**, which clears the 50-resolved floor, so a published baseline exists and this is the yardstick my skill is scored against. The section's caption is the current estimator caption (it calls the rows the ground of the scored base rate, not descriptive-only). Caveats I read with it: Term 2024 has 972 unparsed applications beside 70 substantive, so the pool blends a fully covered Term with a partially covered one whose parsed slice grants at 20% against 2025's 7.5%; and the escalation-signal columns (response requested 64, referred 178, amicus 65 across 367 substantive) are terminal and right-censored, so they describe shape only.

## Conditioning on the escalation rung (my own computation, not a published rate)

The prompt says the pool is unconditioned on the ladder while this cell is selected on it, so I built the conditioned cut from corpus rows. Across 99 resolved substantive applications the corpus service returned (decided 2025-05-27 to 2026-09-25; 9 granted, 84 denied, 6 withdrawn):

| Slice | n | granted | rate |
| --- | --- | --- | --- |
| all resolved substantive | 99 | 9 | 9.1% |
| response requested | 20 | 8 | 40% |
| response requested, never referred | 5 | 0 | 0% |
| response requested and referred | 15 | 8 | 53% |
| no response requested | 79 | 1 | 1.3% |

The 40% headline is the right starting point for a response-requested cell, but the composition matters more than the number. Every one of the 8 grants was either a federal-government applicant (Trump v. California, National Park Service, DHS v. League of Women Voters) or an election-timing application (Allen v. Milligan x3, NRCC v. Brown, People Not Politicians v. Onder). Among response-requested applicants that were **neither the federal government nor in an election posture** the tally is 0 for 5 (Roy Moore, Students Engaged v. Paxton, CCIA v. Paxton, Alabama v. California, M.W. v. Superior Court). Alabama v. California is the closest analogue, a State seeking a stay of a lower-court order against it outside the election context, and it was denied with five amici on file. Five is a tiny sample and I do not treat 0% as the rate, but it tells me that a response request is close to routine for any competently filed application and is not by itself a grant signal outside the federal-applicant and Purcell categories.

## Case-specific adjustments

Up from the pooled 10.5%:

- A State applicant with elite counsel and a bipartisan executive posture (Democratic Governor and Attorney General defending a receivership challenge), asking for a bounded stay through the Ninth Circuit's expedited December argument.
- The remedy is genuinely extraordinary: a private receiver with authority over the Department's health-care budget, staff, contracts, and the ability to seek waiver of Arizona statutes, for a minimum of five years. The current Court's majority is attentive to federalism and to *CASA*-style limits on equitable remedies, and the PLRA's "least intrusive means" text gives a statutory hook rather than a purely equitable one.
- Judge Forrest would have granted an administrative stay and referred the motion to the merits panel, so the State has a dissent below to point to.
- The "transfer and transfer back" argument has practical force: the receivership begins October 19 and a Ninth Circuit decision may not arrive until early 2027.

Down:

- Both lower courts denied a stay; the Ninth Circuit expedited the appeal and reserved the stay question to the merits panel. The Court has repeatedly said stays on matters pending before a court of appeals are rarely granted, and this record fits that description exactly.
- The dispute is abuse-of-discretion on a fourteen-year record with two contempt findings, over $2 million in fines, monitors' reports of preventable deaths, and a staffing pilot that met 22% of its requirements. Even if the Court thought the district court moved too fast, that is error correction, not certiorari material.
- The one arguably certworthy question (CASA and equitable authority over state institutions) was not raised below and the application disclaims the need to resolve it.
- Irreparable harm is weak on this record: the State nominated the receiver, the underlying injunction was stipulated, the receiver must follow state law absent the district court's leave, and the costs are for compliance the State owes anyway. The opposition also notes the $2.2 million contempt-fine balance is earmarked for the receiver's expenses.
- The conditioned corpus cut for a non-federal, non-election applicant with a response requested is 0 for 5.

Net: **0.20**. That is roughly double the pooled baseline, reflecting that this application is far stronger than the median substantive application (many of which are pro se or capital-eve filings), but well under the headline response-requested rate, whose grants come from categories this case does not belong to.

## The other three claims

- `response-requested-increment` **0.02**: the rung has already fired, so the harness will resolve this as vacuous. The number is my honest probability of a second call for a response (a supplemental filing request), which is rare.
- `referral-increment` **0.78**: 15 of 20 response-requested applications in the corpus were referred; the 5 that were not were mostly low-salience matters denied quickly. Kagan denying this one in chambers is possible (she could point to the expedited appeal) but the current practice on a State's application with a response in hand is referral.
- `amicus-increment` **0.50**: 18 of the 20 response-requested resolved applications carried at least one amicus, and Arizona's legislative leaders already filed as amici in the Ninth Circuit, so filers exist. Against that, eleven days have passed with zero amicus entries on this docket while the response has come in, and the reply will close briefing shortly; application-stage amici usually file within the first week. I treat the two as roughly offsetting.

## Big-case score

0.55. A federal receivership over a State's entire prison health system is a major federalism and institutional-reform event and would be widely covered if the Court grants, but it is one system's fact-bound remedy rather than a national rule; a denial will get a news cycle in Arizona and among prison-litigation specialists, not more.

## Where to discount me

- The conditioned cut rests on 20 response-requested rows and a 5-row sub-slice; the composition argument is qualitative.
- I read the respondents' opposition, which the sibling `evt-brief-response-disposition` cell is the declared moment for. Forward mode permits it and I have disclosed it in `flags.json`; a reader comparing the two moments should know this cell was not blind to the response.
- I have no reliable prior on how the current Court treats State applications against structural prison remedies specifically; the nearest historical in-chambers analogue (Atiyeh v. Capps, where a stay of a prison order was granted) is decades old and cuts the other way from the Alabama v. California denial I leaned on.
- No engine-side base rate exists for the three increment claims; those numbers are banked, not scored.
