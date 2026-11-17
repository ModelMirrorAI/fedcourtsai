# Evaluation of `codex-baseline` — *Novotny v. Moore* (`scotus/73500225`, `evt-order-relist-disposition`)

## Outcome and Quantitative Summary

On November 16, 2026, immediately following the November 13 conference, the Supreme Court denied certiorari without any further relist or CVSG (`actual_disposition = "denied"`, `actual_granted = 0`, `signals.distribution_count = 5`, `signals.cvsg_date = null`), accompanied by a detached *Statement of Justice Thomas respecting the denial of certiorari* (`noted_dissent_from_denial = true`).

`codex-baseline` called `"denied"` (`correct = 1`) on the binary side, but assigned `probability = 0.44` to a grant/GVR, producing `brier_score = 0.1936`—higher (worse) than a naive forecast anchored at the stamped segment base rate.

## Analysis of `reasoning.md` (`reasoning_quality = 0.80`)

`codex-baseline`'s `reasoning.md` exhibits the strongest factual precision and statistical verification in the cohort, paired with an internally strained upward probability adjustment that hurt its calibration.

**What worked well:**
- **Exact record and statpack fidelity:** Graded against the prediction-time statpack build (`ca0c9e1a49e292692bdc5b092cd9f868561169b8`, reconstructed via `fedcourts statpack-at`), `codex-baseline` reproduced the stamped segment base rate cleanly from the strictly prior `OT2017–OT2024` Terms (explicitly noting why `OT2025` and `OT2026` are excluded for this `term: 2025` docket) and accurately cited every relevant marginal rate (`13.5%` one-relist paid rate, `37.3%` `3+` `dist-v2` rate, `14.9%` one-amicus rate, `2.6%` Fourth Circuit paid rate).
- **Balanced reading of the alleged splits and vehicle flaws:** Unlike briefer summaries that either dismissed all circuit conflict outright or glossed over the briefs, `codex-baseline` accurately identified the specific circuit tensions petitioners pressed on pp. 17–21 of `petition.txt` (medical facilities, demonstrations, unloaded transit exceptions, and government-proprietor reasoning vis-à-vis *Wolford*) and explained why Maryland's BIO (pp. 26–30) showed those tensions were narrow, posture-dependent, or poor fits for Maryland's statutory text (such as the police-dispersal predicate in Maryland's demonstration statute and the unanimous 3–0 panel ruling on healthcare facilities), alongside the *Rahimi* facial-challenge obstacle to petitioners' armed-security rule.
- **Thorough docket context:** Accurately integrated *Wolford v. Lopez* (May 19, 2026), the June 1, 2026 dismissal of *Moore v. Kipke* (No. 25-1206), the April 6, 2026 denial of *Schoenthal v. Raoul* (No. 25-541), and Third Circuit en banc rehearing in *Koons*.

**Where `reasoning.md` fell short:**
- **Upward probability adjustment contradicted its own reschedule-inflation diagnosis:** `codex-baseline` observed that this private petition entered the `high` salience band *because* `distribution_count = 5`, and demonstrated that three of those five distributions were pre-conference reschedules leaving only one genuine post-conference relist (`13.5%` marginal paid grant+GVR rate; `37.3%` even in the unadjusted `3+` bucket). Adjusting nearly ten percentage points *above* the stamped segment base rate to `0.44` double-counted case stakes while under-weighting its own finding that the band-defining distribution count was reschedule-inflated.
- **Overstated post-*Wolford* GVR probability (`16.7%`):** Allocating `16.7%` unconditional probability (more than a third of its `0.44` grant mass) to a summary order/GVR in light of *Wolford* was poorly supported by the record: *Wolford* was decided in May 2026—three months *before* the BIO (`Aug 17, 2026`) and Reply (`Sep 2, 2026`) were filed—resolved only the private-property default rule that the Fourth Circuit had already unanimously invalidated, and was affirmatively relied upon by the BIO (`146 S. Ct. at 2044, 2053`) to defend the Fourth Circuit's historical-principles approach. Neither party suggested a *Wolford* GVR.

## Predicted reasoning (`predicted_reasoning_quality = 0.66`)

`codex-baseline`'s `predicted_reasoning.md` led with its disposition and procedural calls (denial at `56%`, further relists at `58%`, CVSG at `3%`), devoted two middle sections to conditional grant paths (a *Wolford* GVR path and a narrowed plenary-review path), and closed with its separate-writing forecast on denial (`51%`, led by Justice Thomas).

Checking the central claims against the staged record yields a mixed-positive result:
- **Disposition and no-CVSG calls borne out, though heavily hedged on disposition:** The petition was denied (`actual_disposition = "denied"`) with no CVSG (`cvsg_date = null`), matching `codex-baseline`'s headline calls, though its disposition prose was notably hedged (`56%` denial vs. `44%` grant/GVR, devoting roughly half the document to conditional GVR and plenary-grant scenarios that never materialized).
- **Central procedural relist forecast failed:** `codex-baseline` committed explicitly that "The docket will probably show at least one further relist after November 9 (58%)," reasoning that another conference was needed to prepare a GVR, consolidate a grant, or circulate a separate writing. Instead, the Court denied the petition immediately out of the November 13 conference on November 16, 2026 with zero additional relists (`distribution_count = 5`).
- **Separate-writing call borne out:** `codex-baseline` leaned just across the line (`51%`) toward a noted dissent or statement respecting denial and named **Justice Thomas** as the leading author, explicitly noting the writing could take the form of a cautionary statement respecting denial—both borne out by the November 16 docket entry (`Statement of Justice Thomas respecting the denial of certiorari`). The conditional grant sections and the un-staged text of Justice Thomas's detached PDF remain `unresolved`.

Because the document got the disposition direction, absence of CVSG, and Justice Thomas's separate writing right, but missed its explicit `58%` further-relist commitment and hedged heavily toward unreached GVR/grant paths, it sits between the `0.50` and `0.75` anchors at `0.66`.

## Leakage Audit (`influenced_prediction = "not_applicable"`, `leakage_suspected = false`)

`retrieval_log.json` confirms `mode = "forward"`, running between `2026-11-09T21:59Z` and `2026-11-09T22:10Z`—seven days prior to the November 16, 2026 resolution. Result capture coverage is `0.955` (`21/22` calls fully captured with digests, with only an internal planning call uncaptured). The candidate made zero web or MCP calls, restricted corpus queries to pre-existing Second Amendment dockets with `retrieved_doc_date <= 2026-06-01`, and accurately logged every query in `retrieval.md`.

## Big-Case Assessment (`evaluator_score = 0.52`)

Independently of the predictors' scores (and noting `codex-baseline`'s `0.86` explicitly priced what a *merits ruling* could have done nationwide), *Novotny v. Moore* sits at `0.52` ex post: a prominent, final-judgment Second Amendment challenge across nine public-carry categories that drew a Fourth Circuit partial dissent, a relist, and a detached Statement of Justice Thomas respecting the denial of certiorari, but ended in a cert denial without establishing national Supreme Court merits precedent.
