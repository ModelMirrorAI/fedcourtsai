# Why 0.57

## Anchor

The context froze `band: elevated` under `sal-v4`, `distribution_count: 2`, no CVSG, Term 2025, `mode: forward`. The statpack's "Segment base rate by salience band (sal-v4)" table matches the context's salience version, so the anchor is the bracketed `reached` figure for `elevated` pooled over the Term rows strictly before 2025 that the table renders (2017 through 2024). Weighting each Term's reached rate by its reached denominator gives roughly 17 percent over about 2,800 weighted petitions (per-Term reached rates run 13.8 to 20.5 percent). That is the yardstick the evaluator scores this cell against.

For shape only: the paid-segment relist cut puts a two-distribution petition at about 28 percent granted plus 13 percent GVR at terminal count, and the CVSG cut's `none` bucket at 4 percent granted. Neither is as-at-prediction, and I did not anchor on them.

## Adjustments up from the anchor

- **The Court called for a response.** Respondents waived on June 3; the Court requested a response on June 15, pulling the petition off the June 25 conference. A call for response is the Court's own signal of interest and sits well above the elevated band's average trajectory. The band in the context is still `elevated`, so this signal is not already priced into the anchor.
- **The Court has taken this exact question before, in this exact case's orbit.** In OT2022 the Court called for the Solicitor General's views in *Flagstar v. Kivett* (No. 22-349) and *Cantero*, granted *Cantero*, decided it in 2024 without resolving preemption, and GVR'd this case. The Solicitor General's 2023 brief, which both sides quote, recommended granting Flagstar as the better vehicle. The Court knows this case and has already vetted it.
- **A real, acknowledged three-way split.** The petition (Reasons I) lays out the First Circuit (*Conti*, not preempted), the Second Circuit on remand (*Cantero*, May 2026, preempted), and the Ninth Circuit below (not preempted, relying on pre-*Cantero* circuit precedent in *Lusnak*). The BIO does not deny the conflict; it argues it is "minor and transient" and confined to three cases (BIO at 3, 14-16). A conceded conflict on the regulation of national banks is close to the paradigm Rule 10 case.
- **Vehicle quality.** Final money judgment plus an ongoing injunction; the Ninth Circuit's affirmance rests solely on preemption (Pet. Reasons IV). Even the BIO says that if the Court takes the issue, this is the best vehicle of the three (BIO at 21-23). That matters for the conditional: if the Court takes the question at all, this petition is very likely granted in some form.
- **Institutional support.** Amicus brief from the Bank Policy Institute, American Bankers Association, Chamber of Commerce and Mortgage Bankers Association; petitioner's counsel is an experienced Supreme Court practice; the OCC has repeatedly called the question exceptionally important.

## Adjustments back down

- **The Court denied *Conti* earlier in 2026.** The BIO reports certiorari denied in *Citizens Bank v. Conti*, No. 25-1004, with a rehearing petition pending. CourtListener shows that docket was last modified the same day this one was redistributed, consistent with the rehearing petition being on the same conference. The denial is the strongest negative signal: the Court passed on the issue once this year. I discount it because *Conti* arose on a motion to dismiss with no record, which is the vehicle defect the Solicitor General flagged in 2023, and because the Court called for a response here at about the same time, which reads as choosing this vehicle over that one rather than as disinterest.
- **The new OCC rule.** The OCC's May 19, 2026 final rule preempts state interest-on-escrow laws prospectively from June 19, 2026 (BIO at 10-11). Respondents argue this makes the question non-recurring. The Court could accept that and let the legacy cases lie, or could see a nationwide rule now in force, sure to be challenged, as raising the stakes of settling the statutory standard. I weight this as a genuine reason for denial but not a dominant one.
- **The BIO's narrowness argument has some force.** Twelve States have such laws, most reportedly inert, and all mortgage servicers except Flagstar comply with California's law. A Court that granted *Cantero* to fix the Second Circuit's categorical test may feel it has already given the guidance it intended to give.
- **Companion-vehicle risk.** The Court may prefer the *Cantero* plaintiffs' petition as the lead and hold this one. A hold that ends in a denial (if New York's law is held not preempted) is a denial for this event, though a hold ending in a GVR counts as a grant.

## Putting it together

I put P(the Court takes the interest-on-escrow question this Term in some vehicle) near 0.65 and P(this petition is granted in some form, including a later GVR, given that) near 0.85, plus a small residual, giving 0.57. The `disposition` claim restates that number. `predicted_disposition` is `granted` because plenary review is the modal grant form; `summary-disposition-route` at 0.20 covers the hold-then-GVR path.

## Other claims

- `relist-increment` 0.72: frozen count is two distributions (June 25 and September 28 conferences, the latter after a reschedule). Almost every grant now follows at least one relist, and coordination with *Conti*'s rehearing petition and the *Cantero* petition adds to it. Most of the complement is a straight denial off the long conference.
- `cvsg-increment` 0.22: the government's views are already on file from 2023 and now embodied in a rule, which argues against a second CVSG; the open question of the rule's effect on recurrence argues for one.
- `dissent-from-denial` 0.15: a denial here would most plausibly rest on the OCC rule having mooted the question going forward, which does not invite a separate writing; *Conti* drew none.
- `big_case_score` 0.45: important to the national banking system and the mortgage market, and the Court has treated the question as cert-worthy once, but the subject is technical and the affected laws are few.

## What I read and did not read

Provisioned: the 2026-09-17 snapshot, `context.json`, `questions-presented.txt`, the petition (198 pages, `truncated: true`, so the appendix was cut; I read the QP, introduction, statement of related proceedings, and Reasons I, III and IV), and the brief in opposition (32 pages, complete; read in full at the argument level). The reply brief filed August 19 is on the docket but was not provisioned and I did not fetch it. The Bank Policy Institute amicus brief was not provisioned and not fetched.

Retrieval beyond the record: two `fedcourts query` pulls for the row shape of recent granted and GVR priors (not case-matched; the corpus query is a structured filter and has no topic column for banking preemption), and seven CourtListener MCP calls to confirm this docket's metadata and locate the companion dockets. The docket number stamped on the BIO's filename (25-1230) resolves to an unrelated case, *Google v. VirtaMove*, so I treated it as a filing artifact, not a companion. CourtListener carries no docket entries or search hits for the SCOTUS *Conti* or *Cantero* dockets, so the *Conti* denial and rehearing status rest on the BIO's account, and I could not confirm the *Cantero* plaintiffs' petition number or conference date.

## Where to discount me

The core judgment is how to weigh a call for response plus a prior grant on the same question against a denial in a sister case and an intervening agency rule. Reasonable forecasters would land anywhere from 0.35 to 0.7. I have no information about the September 28 conference beyond the docket, and no view of the reply brief. Nothing I retrieved disclosed this petition's disposition; it is pending.
