# Evaluation — claude-baseline

Cell: scotus/9026000119 (Guam v. Ybanez, No. 26-119), `evt-petition-arrival-disposition`. This is a cert-stage arrival cell, and the prediction ran forward on 2026-08-16. Outcome: **denied** on 2026-11-09 (`actual_granted` 0). The petition was distributed once (the conference of 11/6/2026), with no relist, no CVSG and no noted dissent; one respondent waived a response on 2026-08-26. The harness stamps the segment base rate, the skill and the basis, so this note quotes no rate of its own.

**Score.** The prediction was P(grant) = 0.06 with a predicted disposition of `denied`, so it is correct (1) with a Brier score of 0.0036. That is the highest Brier of the three, because it placed the most mass on a grant.

**Reasoning quality: 0.7.** The case-specific analysis is good:
- the petition alleges no split and frames itself as a request to extend district-court authority;
- a government is an awkward due-process claimant;
- the vehicle is fact-bound, with unreported orders and a possible adequate territorial ground;
- the counsel are in-house rather than Supreme Court practitioners.

The counterweights (stark no-notice facts, the Limtiaco precedent for Guam cases) are real and kept modest. The weakness is the anchor. The rationale acknowledges that the arrival moment calls for the whole-segment fallback, but it builds a roughly 20% state-class prior out of nested risk-set and terminal figures and then discounts heavily from there. That inflated prior is what leaves the final number at about twice the other candidates'. The rationale is candid that this may be a miscalibration. The reasoning is otherwise transparent and careful.

**Leakage.** Forward, `not_applicable`. In the captured log the latest retrieved document date is 2026-08-09. Its CourtListener searches returned 2007 and 2026-02-03 material unrelated to this petition's disposition.

## Predicted reasoning

**Grade: 0.8.** This is the most specific forecast document. Its central claims, and how they held:
- Denial in October or November: borne out (2026-11-09).
- Respondents waive or file a short opposition, and the Court does not request a response: borne out (a waiver was filed 2026-08-26, and no response request appears).
- One conference with no relist: borne out.
- No CVSG and no dissent: borne out.

One secondary timing detail failed. It expected distribution for the late-September long conference or the first October conference, but the petition was distributed on 2026-10-14 for the 11/6/2026 conference. The waiver and no-response calls are discriminating content beyond the bare disposition, and that lifts this document above the others. The missed distribution timing keeps it below 1.0. Its content conditional on a grant (a reformulated question, a per-curiam possibility) earns neither credit nor penalty.

**Big case.** 0.15 (my own read).
