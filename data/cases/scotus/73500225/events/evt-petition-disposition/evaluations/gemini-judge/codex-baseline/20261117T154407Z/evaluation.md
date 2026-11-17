# Evaluation of `codex-baseline`

## Outcome and quantitative summary

On November 16, 2026, the Supreme Court denied certiorari in *Katherine Novotny, et al. v. Wes Moore, Governor of Maryland, et al.*, No. 25-1324 (`actual_disposition = "denied"`, `actual_granted = 0`), with a Statement of Justice Thomas respecting the denial of certiorari (`noted_dissent_from_denial = true`), following three additional conference distributions (`distribution_count = 5`, up from `2` at prediction time) and no CVSG (`cvsg_date = null`).

`codex-baseline` predicted `denied` (`correct = 1`) with `probability = 0.38`, yielding `brier_score = 0.1444`—the highest (worst) Brier score among the three candidates on this cell. This is a cert-stage evaluation; the stamped segment base rate, basis record, `brier_skill_score`, and `claim_scores` are computed by the harness.

## Reasoning quality (`0.74`)

`codex-baseline`'s `reasoning.md` combines the most thorough factual reading of the provisioned briefs with an over-aggressive upward probability jump that conflicted with its own best analytical points:

- **Exemplary record reading and base-rate discipline.** Checked via `fedcourts statpack-at` against the prediction-time statpack build (`1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, carrying `sal-v4` rather than the currently committed `sal-v8` pack), `codex-baseline` accurately pooled the strictly prior (`OT2017`–`OT2024`) `elevated` reached rows without leaking later Terms or compounding terminal relist/CVSG cuts against the stamped segment base rate. On the filings, `codex-baseline` was the **only** candidate to catch Brief in Opposition p. 6 n.4—recording both the intervening decision in *Wolford v. Lopez*, 146 S. Ct. 2032 (2026), and the prior dismissal of Maryland's separate petition in *Moore v. Kipke*, No. 25-1206—while also recognizing that the September 24 entry was a pre-conference reschedule rather than a conference relist and noting the April 15 vs. May 20 petition-date metadata discrepancy.
- **Internal tension in the jump to `0.38`.** Despite showing that (1) the second distribution followed a pre-conference reschedule and was therefore *weaker* evidence of active judicial interest than a true relist inside the `elevated` band, (2) *Wolford* resolved the distinct private-property consent rule (already reflected in the dismissal of No. 25-1206) rather than sensitive places, (3) *Koons* remained pending en banc in the Third Circuit, and (4) the single sweeping question presented was an unwieldy vehicle, `codex-baseline` still more than doubled its prior-Term anchor to `0.38`—including a `~22.8%` unconditional probability of a summary disposition/GVR. Over-pricing a *Wolford* GVR when *Wolford* did not address sensitive places drove its poor calibration on the realized denial, and `reasoning.md` similarly under-weighted the likelihood that a final-judgment post-*Bruen* sensitive-places denial would be held across additional conferences for a separate statement.

## Predicted reasoning (`0.50`)

`codex-baseline`'s `predicted_reasoning.md` matches the `0.50` rubric anchor ("a specific forecast is split between borne out and not"):

1. **Disposition (central, borne out):** Correctly forecast denial (`actual_disposition = "denied"`), though with substantial grant weight (`38%`).
2. **Further distributions (central, not borne out):** Narrowly forecast *no* further distribution (`52%` none vs. `48%` further) and stated that if redistributed, "one or two further distributions are more likely than a long sequence." In fact, the petition was distributed three more times (October 13, November 2, and November 9, reaching `distribution_count = 5`).
3. **CVSG (central, borne out):** Correctly forecast no CVSG (`1%`).
4. **Grant route and narrowing (conditional, unresolved):** Conditional on grant, forecast a `60%` summary/GVR route vs. `40%` narrowed plenary review; untested because certiorari was denied.
5. **Separate writing on denial (central, not borne out):** Confidently forecast "no noted dissent or statement respecting denial (78%; some such writing 22%)," whereas Justice Thomas issued a Statement respecting the denial of certiorari (`noted_dissent_from_denial = true`).

## Leakage and stakes

This was a `forward` prediction (`run_id = 20261005T231540Z`) placed six weeks before the November 16, 2026 denial. In `retrieval_log.json`, 26 of 28 calls are captured (`result_capture_coverage ≈ 0.93`); the two unobserved `web-search` calls queried *Wolford v. Lopez* (`No. 24-1046`) and the 2022 *Bruen* slip opinion PDF, its `find` call excluded `data/qp-topics/*` via `-not -path` without opening files there, and no outcome material existed (`influenced_prediction = "not_applicable"`, `leakage_suspected = false`). My independent `big_case` stakes read is `0.78`.
