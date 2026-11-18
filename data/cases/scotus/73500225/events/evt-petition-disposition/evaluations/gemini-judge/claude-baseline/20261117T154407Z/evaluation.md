# Evaluation of `claude-baseline`

## Outcome and quantitative summary

On November 16, 2026, the Supreme Court denied certiorari in *Katherine Novotny, et al. v. Wes Moore, Governor of Maryland, et al.*, No. 25-1324 (`actual_disposition = "denied"`, `actual_granted = 0`), with a Statement of Justice Thomas respecting the denial of certiorari (`noted_dissent_from_denial = true`). From the October 5, 2026 prediction-time snapshot (`distribution_count = 2`, no CVSG), the petition went through three further distributions (October 13, November 2, and November 9, reaching `distribution_count = 5`) without a CVSG (`cvsg_date = null`).

`claude-baseline` predicted `denied` (`correct = 1`) with `probability = 0.18`, yielding `brier_score = 0.0324`. This is a cert-stage evaluation; the stamped segment base rate, basis record, `brier_skill_score`, and `claim_scores` are computed by the harness.

## Reasoning quality (`0.86`)

`claude-baseline`'s `reasoning.md` delivers the strongest and best-calibrated analysis on this cell:

- **Base-rate discipline.** Because the committed statpack has advanced to `sal-v8` since the October 5 run, `claude-baseline`'s base-rate figures were verified via `fedcourts statpack-at` against the prediction-time statpack build (`1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`), which carried `sal-v4`. Every prior-Term (`OT2017`–`OT2024`) `elevated` reached figure and paid-segment cut in `reasoning.md` matches that build accurately, and `claude-baseline` properly treated terminal relist and CVSG cuts as descriptive cross-checks rather than compounding multipliers on the stamped segment base rate.
- **Procedural and doctrinal insight.** `claude-baseline` accurately read the `2026-10-05` snapshot to see that the September 24 entry was a pre-conference reschedule before the September 28 Long Conference rather than a post-conference relist. Crucially, `claude-baseline` identified the strongest concrete evidence cutting against both plenary review and an alternative GVR in light of *Wolford v. Lopez* (June 25, 2026): the Court had confined its *Wolford* grant to the private-property default rule while leaving sensitive-places questions out, and had denied *Schoenthal v. Raoul* (a final-judgment Seventh Circuit transit ban) in April 2026 *while Wolford was pending* rather than holding it for *Wolford*. Combined with active percolation (including *Koons* pending en banc in the Third Circuit and *Christian v. James* in the Second Circuit) and the sprawling eight-category question presented, that explained why the upward vehicle factors roughly cancelled the downward reluctance and percolation signals, keeping `probability` tightly anchored at `0.18`.
- **Where the rationale erred.** `claude-baseline` read selected slices of `brief-in-opposition.txt` and skipped the procedural history around page 6, missing footnote 4—which reported that after *Wolford*, Maryland had already moved to dismiss its cross-petition in *Moore v. Kipke* (No. 25-1206) and that the Court had already granted the dismissal. Relying instead on CourtListener's un-updated docket shell for No. 25-1206, `claude-baseline` mistakenly inferred that the September 24 reschedule likely paired No. 25-1324 with No. 25-1206 for the October 9 conference. That factual oversight is real but peripheral to the main sensitivity analysis on No. 25-1324 itself, meriting a modest deduction from an otherwise exemplary rationale.

## Predicted reasoning (`0.75`)

`claude-baseline`'s `predicted_reasoning.md` sits right on the `0.75` rubric anchor (specific central claims mostly borne out, with modest hedging on two secondary probabilities and one failed secondary companion-petition claim):

1. **Disposition (central, borne out):** Confidently predicted denial (`P(any grant) = 0.18`).
2. **Distributions and timing (central, borne out):** Correctly noted that the petition had not yet been considered at conference, forecast further distribution (`P = 0.50`, hedged at even odds), and specifically projected "one to three further distributions, then an order by late November" if relisted—matching the exact realized path of three further distributions and a November 16 order.
3. **CVSG (central, borne out):** Forecast no CVSG (`P = 0.04`).
4. **Separate writing on denial (central, borne out with a hedged probability):** Forecast a "reasonable chance of a dissent from denial or statement respecting denial (P = 0.45), most plausibly from Justice Thomas." Justice Thomas indeed issued a Statement respecting the denial of certiorari (`noted_dissent_from_denial = true`), matching both the named author and form, though `P = 0.45` hedged just below 50%.
5. **Companion petition (secondary, not borne out):** Forecast that Maryland's petition in No. 25-1206 would be denied at the same conference, whereas `brief-in-opposition.txt` (p. 6 n.4) shows No. 25-1206 had already been dismissed months earlier. (Conditional grant-route and merits claims were untested by the denial and are neither credited nor penalized.)

## Leakage and stakes

This was a `forward` prediction (`run_id = 20261005T231540Z`) placed six weeks before the November 16, 2026 disposition. All 38 calls in `retrieval_log.json` are captured (`result_capture_coverage = 1.0`); every retrieved document predated the snapshot (latest `2026-06-25`, *Wolford v. Lopez*), no `data/qp-topics/` paths were touched, and no outcome material existed (`influenced_prediction = "not_applicable"`, `leakage_suspected = false`). My independent `big_case` stakes read is `0.78`.
