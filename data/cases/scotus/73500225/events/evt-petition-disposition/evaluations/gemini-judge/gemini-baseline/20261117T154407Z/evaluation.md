# Evaluation of `gemini-baseline`

## Outcome and quantitative summary

On November 16, 2026, the Supreme Court denied certiorari in *Katherine Novotny, et al. v. Wes Moore, Governor of Maryland, et al.*, No. 25-1324 (`actual_disposition = "denied"`, `actual_granted = 0`), accompanied by a Statement of Justice Thomas respecting the denial of certiorari (`noted_dissent_from_denial = true`), after `distribution_count` rose from `2` at prediction time to `5` at resolution with no CVSG (`cvsg_date = null`).

`gemini-baseline` predicted `denied` (`correct = 1`) with `probability = 0.35`, yielding `brier_score = 0.1225`. This is a cert-stage evaluation; the stamped segment base rate, basis record, `brier_skill_score`, and `claim_scores` are computed by the harness.

## Reasoning quality (`0.42`)

`gemini-baseline`'s `reasoning.md` got the modal label right and identified a reasonable prior-Term starting range, but its brief two-paragraph analysis rests on a factual misreading of the docket and misses key record developments:

- **Base-rate reference.** Verified via `fedcourts statpack-at` against the prediction-time statpack build (`1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, carrying `sal-v4` rather than the currently committed `sal-v8` pack), `gemini-baseline`'s rounded citation of the prior-Term (`OT2017`–`OT2024`) `elevated` reached rate is a slight approximation of that build's prior-Term figures.
- **Misread procedural posture and double-counting.** `gemini-baseline` justified roughly doubling its baseline to `0.35` on the ground that the petition had been "relisted once" and that "surviving the initial conference is a significant positive signal." The `2026-10-05` snapshot clearly showed the opposite: the petition was distributed September 2 for the September 28 conference, *rescheduled* on September 24 (four days before conference), and redistributed October 5 for the October 9 conference. It had never been considered at or survived an initial conference, and `distribution_count = 2` was already what placed the petition into the `elevated` band—so treating it as an independent conference-survival signal both misread the docket and double-counted the band assignment against the stamped segment base rate.
- **Omission of record-central developments.** `reasoning.md` makes no mention of *Wolford v. Lopez* (decided June 2026 and discussed prominently in the Brief in Opposition), petitioners' alternative GVR request, the dismissal of Maryland's companion petition *Moore v. Kipke* (No. 25-1206), pending en banc Third Circuit review in *Koons*, or the vehicle difficulty posed by a single sweeping question across numerous heterogeneous location categories. Its reasoning on low CVSG risk and high separate-writing risk on denial was sensible, preventing a lower score, but the core grant-probability rationale was thin and factually flawed.

## Predicted reasoning (`0.58`)

`gemini-baseline`'s `predicted_reasoning.md` sits modestly above the `0.50` anchor (`0.58`):

- **What held up:** It unconditionally and accurately forecast at least one further relist (`distribution_count` rose from 2 to 5, including conference-to-conference relists across October 16, November 6, and November 13) and no CVSG (`cvsg_date = null`). Conditionally on denial, it predicted that a separate writing was highly probable and specifically named Justice Thomas or Justice Alito as the likely author—borne out when Justice Thomas issued a Statement respecting the denial of certiorari (`noted_dissent_from_denial = true`), though styled as a statement respecting denial rather than a dissent from denial.
- **What held the grade back:** Graded strictly on `predicted_reasoning.md` alone (apart from `prediction.json`), the document never commits unconditionally to whether certiorari will be granted or denied—framing both "If the Court grants review..." and "Should the Court deny the petition..." purely conditionally—and repeats the factual error that the petition had already been "relisted once" as of October 5. Having specific, borne-out procedural and separate-writing calls lifts it above `0.50`, while omitting a bottom-line disposition call in the forecast document itself keeps it well short of `0.75`.

## Leakage and stakes

This was a `forward` prediction (`run_id = 20261005T231540Z`) placed six weeks before the November 16, 2026 denial. In `retrieval_log.json`, all 32 calls carry `result_capture = "unobserved"` (`result_capture_coverage = 0.0`); graded on their queries, they read only provisioned inputs, `metrics/statpack.md`, a failed `fedcourts query` syntax attempt, and two CourtListener searches (`"Katherine Novotny" "Wes Moore"` and `Antonyuk`) while this petition was genuinely unresolved, with no `data/qp-topics/` access (`influenced_prediction = "not_applicable"`, `leakage_suspected = false`). My independent `big_case` stakes read is `0.78`.
