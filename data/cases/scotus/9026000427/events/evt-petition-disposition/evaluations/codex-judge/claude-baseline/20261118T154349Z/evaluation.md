# Evaluation: claude-baseline

The cert-stage prediction correctly called `denied`. The outcome records denial on November 16, 2026, with `actual_granted = 0`. Its grant probability of 0.004 gives `correct = 1` and Brier score `(0.004 - 0)^2 = 0.000016`.

Reasoning quality: **0.78**. The rationale identifies the right certworthiness considerations: a pro se individual petition, response waiver, nonprecedential decision, fact-specific questions, and no demonstrated circuit conflict. It distinguishes the potentially broader statutory QP2 from QPs 1 and 3. Those considerations support a probability below the stamped segment base rate without treating denial as a ruling on the merits.

The analysis is comparatively shallow about the actual jurisdictional holding. It expressly read only the front matter and questions closely, and does not work through the appendix's contributing-factor chronology or distinguish a new alleged refusal from continuing financial consequences. Descriptions of an essentially pro se grant rate and the composition of Federal Circuit petitions are unquantified judgments. The unrelated grant sample cannot validate the precise downward adjustment; the candidate appropriately disclaims reliance on it. These limitations, rather than its correct result, determine the rationale grade.

Base-rate use was checked against historical statpack build `7bcde3b105cb212283905eda17b827efc188e80c` (digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`), recovered with `fedcourts statpack-at` for this alias. It is the sal-v4 build available at prediction time, rather than the currently committed sal-v8 pack. The cited historical table entries agree with that build. The scored comparison uses the stamped segment base rate; the harness supplies that rate and Brier skill.

## Predicted reasoning

Forecast quality: **0.90**. The central procedural forecast was specific and borne out: denial in the first conference cycle, no further distribution, no CVSG, and no noted dissent. The docket's October 28 distribution for November 13 is followed directly by the November 16 denial; the outcome confirms one distribution, no CVSG, and no noted dissent. The reference to denial at the conference is read as the conference decision, not a claim that the public order would issue on November 13.

The conditional choice of QP2 and conditional summary-disposition discussion were never tested because review was denied, so they receive neither credit nor penalty. The broader prediction of no statement or separate writing cannot be conclusively checked: no order text or writings are staged, and the explicit outcome field establishes only the absence of a noted dissent. The procedural detail earns substantial credit; untested merits discussion and unavailable writing evidence do not supply additional credit.

Leakage: **not applicable; not suspected**. All 15 calls have captured results. The October 30 snapshot reads and general corpus query precede the November 16 resolution; no own-case disposition is evident. This cell's later, decided snapshot was not substituted for the candidate's information set. Its frozen cutoff is null, the ordinary forward distribution shape.

Cert votes are not scored. No semantic grades or quantitative claim scores are assigned; claim scoring and baseline stamping belong to the harness. The independent stakes read is 0.12 for a narrow individual dispute with a potentially broader whistleblower pleading question.
