# Evaluation of `gemini-baseline` — *Novotny v. Moore* (`scotus/73500225`, `evt-order-relist-disposition`)

## Outcome and Quantitative Summary

On November 16, 2026, following the November 13 conference (the petition's fifth recorded distribution entry and first post-conference relist), the Supreme Court denied certiorari without calling for the views of the Solicitor General or relisting the petition again (`actual_disposition = "denied"`, `actual_granted = 0`, `signals.distribution_count = 5`, `signals.cvsg_date = null`). Justice Thomas issued a detached *Statement respecting the denial of certiorari* (`noted_dissent_from_denial = true`).

`gemini-baseline` called `"denied"` (`correct = 1`) with `probability = 0.22`, yielding `brier_score = 0.0484`—substantially below the stamped segment base rate and the sharpest calibration of the cohort on this resolved denial.

## Analysis of `reasoning.md` (`reasoning_quality = 0.82`)

`gemini-baseline`'s `reasoning.md` delivers a well-structured, institutionally grounded ex-ante rationale for adjusting downward from the stamped segment base rate to `0.22`.

**What worked well:**
- **Docket-mechanics decomposition:** `gemini-baseline` carefully separated the three pre-conference `Rescheduled` entries (`Sep 24`, `Oct 6`, `Oct 13`) from the single genuine post-conference relist (after the `Nov 6` conference, redistributed `Nov 9` for `Nov 13`). That distinction rightly explained why `distribution_count = 5` mechanically placed the petition in a higher salience cohort than a typical first-relist paid petition.
- **Base-rate verification:** Graded against the statpack build in force when the candidate ran (`ca0c9e1a49e292692bdc5b092cd9f868561169b8`, reconstructed via `fedcourts statpack-at`), `gemini-baseline`'s marginal statpack figures (`relist_bucket = 1` at `13.5%` across `n = 2,532`, `relist_bucket = 3+` at `37.3%` across `n = 483`, `cert_amicus = 1` at `14.9%` across `n = 1,159`, `ca4` paid rate at `2.6%` across `n = 3,425`) match the prediction-time build accurately. (One minor cohort slip: when cross-checking the stamped segment base rate by hand in `statpack.md`, `gemini-baseline` summed `OT2017–OT2025` rather than strictly prior docket Terms `OT2017–OT2024` for this `term: 2025` docket, though it properly anchored its actual baseline on the frozen context figure.)
- **Post-*Wolford* institutional and vehicle read:** `gemini-baseline` accurately integrated *Wolford v. Lopez* (May 2026), Maryland's ensuing Rule 46 dismissal of cross-petition *Moore v. Kipke* (No. 25-1206), the April 2026 denial in *Schoenthal v. Raoul* (No. 25-541), and pending Third Circuit en banc proceedings in *Koons*. It also identified the core vehicle defect in petitioners' sweeping facial theory—conditioning sensitive-place status on armed government entry screening—under *United States v. Rahimi*, 602 U.S. at 693, and correctly tracked the 3–0 vs. 2–1 voting split on the Fourth Circuit panel (Judge Agee concurring on government buildings, school grounds, and healthcare facilities while dissenting on the remaining six categories).

**Where `reasoning.md` fell short:**
- **Misread of the petition on public demonstrations:** `gemini-baseline` stated parenthetically that petitioners "do not press the public-demonstration provision in the body of their Petition." In fact, `petition.txt` explicitly challenges and argues the public-demonstration restriction (Pet. 5, 9, 13, 18–19), citing the Ninth Circuit's decision in *Wolford*, 116 F.4th at 998, as a conflict on permitted public gatherings.
- **Overbroad "no circuit split" framing:** Adopting the BIO's framing a bit too uncritically, `gemini-baseline` asserted there was "no circuit split on any of the nine challenged locations across the 2d, 3d, 4th, 7th, and 9th Circuits," glossing over the narrow tensions between the Fourth Circuit below and the Ninth Circuit's preliminary-injunction rulings in *Wolford*, 116 F.4th at 997–1002, on healthcare facilities, permitted public gatherings, and unloaded-firearm transit rules (even though the BIO persuasively explained why posture and statutory differences made this petition a poor vehicle for them).
- **Minor statutory/citation slips:** `gemini-baseline` described all nine challenged categories as enacted in Maryland's 2023 SB 1 (whereas the public-transit, public-demonstration, and state-park/forest bans predated *Bruen* and SB 1, Pet. 5–6; BIO 3–4) and cited the decision below as `165 F.4th 459` rather than `165 F.4th 194` (Pet. 3).

## Predicted reasoning (`predicted_reasoning_quality = 0.78`)

`gemini-baseline`'s `predicted_reasoning.md` structured its forecast around four sections: (1) procedural trajectory (further relists and CVSG), (2) disposition route (denial vs. plenary grant vs. GVR/summary reversal), (3) conditional scope and merits posture if granted, and (4) separate writings on denial.

The three central non-conditional claims that carried the weight of the document were specific, discriminating, and fully borne out by the staged record:
1. **Immediate post-relist resolution without further relists:** `gemini-baseline` leaned against an additional relist (`38%`), predicting resolution directly out of the November 13, 2026 conference or at most one more. The Court denied certiorari on November 16, 2026 with `distribution_count` unchanged at `5`.
2. **No CVSG:** `gemini-baseline` assigned `2%` to a CVSG for sound institutional reasons; no CVSG occurred (`cvsg_date = null`).
3. **Outright denial rather than plenary review or a *Wolford* GVR:** `gemini-baseline` committed decisively to denial (`78%`) and ruled out a GVR or summary reversal because *Wolford* had already aligned with the Fourth Circuit's invalidation of the private-property default rule. Certiorari was denied outright.

The conditional merits section (`Section 3`) was never triggered by the denial and neither helps nor hurts the grade. On the secondary separate-writing forecast (`Section 4`), `gemini-baseline` leaned slightly the wrong way on existence (`42%` probability of a separate writing vs. `58%` silent denial), which keeps the document below the top anchor; however, it specifically singled out **Justice Thomas** as the dominant author if a writing appeared and explicitly anticipated a **statement respecting the denial of certiorari** alongside a dissent from denial—matching the November 16 docket entry (`Statement of Justice Thomas respecting the denial of certiorari`). The substantive points predicted for Justice Thomas's detached statement cannot be checked because `record/opinion/` carries no staged text.

## Leakage Audit (`influenced_prediction = "not_applicable"`, `leakage_suspected = false`)

`retrieval_log.json` confirms `mode = "forward"`, with all 48 tool calls executed between `2026-11-09T21:59Z` and `2026-11-09T22:12Z`—four days before the November 13 conference and seven days before the November 16 denial order. Because `result_capture_coverage = 0.0` (every call logged as `outcome_only`), `reasoning.md` and `retrieval.md` were weighted heavily per protocol: all corpus and CourtListener MCP queries targeted pre-existing dockets (`25-1206`, `25-541`, *Wolford*, and open `25-1324`) and Second Amendment appellate precedents, `retrieval.md` matches the harness log, and no post-2026-11-09 facts appear anywhere.

## Big-Case Assessment (`evaluator_score = 0.52`)

Independently of the predictors' scores, *Novotny v. Moore* sits at `0.52`: it is a high-profile, final-judgment Second Amendment challenge to nine sweeping categories of public-carry restrictions litigated by national gun-rights counsel against a state Governor and Attorney General that drew a partial Fourth Circuit dissent, a relist, and a detached Statement of Justice Thomas respecting the denial of certiorari—placing it well above routine cert petitions, while bounded ex post by the denial of certiorari leaving no binding national merits precedent.
