# Evaluation of `codex-baseline` (`scotus/9026000427` / `evt-petition-disposition`)

## Outcome and Quantitative Summary

- **Stage / moment:** `cert` (`petition`, `moment: distribution`)
- **Predicted vs. actual disposition:** `denied` (`probability = 0.005`, `granted = 0`) vs. `denied` (`actual_granted = 0`, resolved November 16, 2026, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`)
- **Accuracy (`correct`):** `1`
- **Brier score (`brier_score`):** `0.000025`
- **Baseline and skill:** Cert-stage `segment_base_rate`, `base_rate_basis`, `brier_skill_score`, and `claim_scores` are harness-stamped from committed artifacts rather than hand-computed here; relative to the stamped segment base rate, `codex-baseline`'s `0.005` forecast beats the prior by a wide margin.

## Reasoning Quality (`0.86`)

`codex-baseline` produced a methodologically rigorous `reasoning.md` with standout doctrinal verification, held back from the very top tier primarily by overlooking one salient docket fact:

1. **Methodological rigor on base rates:** Checked against `codex-baseline`'s contemporaneous statpack build via `fedcourts statpack-at` (`build_sha = 7bcde3b105cb212283905eda17b827efc188e80c`, `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`), every prior-Term pool (`n = 12,913` across OT2017–OT2025 on the `sal-v4` `baseline` `reached` column) and paid-segment cut (`relist_bucket`, `cvsg`, `cert_amicus`) matches that build exactly. `codex-baseline` was particularly careful in explaining why terminal relist/CVSG/amicus cuts describe terminal populations rather than forward hazard multipliers, why `context.amicus_briefs: null` is distinct from a measured zero, and why three filtered prior-Term corpus rows should not be used to estimate grant frequency.
2. **Independent verification of *Bosley*:** `codex-baseline` went beyond the petition text to retrieve and read *Bosley v. Merit Systems Protection Board*, 162 F.3d 665 (Fed. Cir. 1998) (`opinion_id = 759750`), via CourtListener MCP. That check paid off: `codex-baseline` verified that *Bosley* distinguished continuing paycheck effects of a pre-effective-date quality-step denial from separately alleged post-effective-date reprisals (vacating and remanding on the latter), and caught the petition's chronological error in claiming that the 1998 *Bosley* decision applied *National Railroad Passenger Corp. v. Morgan*, 536 U.S. 101 (2002).
3. **Solid appendix engagement:** `codex-baseline` read the attached Federal Circuit nonprecedential opinion (App. 1–8), noting both the Administrative Judge's unreached alternative ground rejecting the protected-disclosure showing and the appendix's distinct causation finding on the later-numbered disclosures tied to the April 2015 position-description reassignment claim.
4. **Key omission—missed *pro se* posture:** Neither `reasoning.md` nor `predicted_reasoning.md` recognized that Petitioner Richard W. Coleman, Jr. proceeded *pro se* (`"Attorney": "Richard W. Coleman Jr.", "IsCounselofRecord": true` in `2026-10-30.json`, and `Petitioner, Pro Se` on the cover and signature block of `petition.txt`). On the paid certiorari docket, *pro se* status is one of the strongest empirical downward drivers on both cert grants and calls for a response, and missing it explains why `codex-baseline` retained somewhat more residual probability for a CFR/relist (`0.04`), grant (`0.005`), and stakes (`0.19`) than a *pro se* MSPB filing warrants.

## Predicted reasoning (`0.74`)

`codex-baseline`'s `predicted_reasoning.md` accurately anticipated the Court's handling of the petition:

- **Resolved central claims (all borne out):** It forecast that (1) the Court would deny certiorari in an orders list following the November 13, 2026 conference ("approximately in mid-to-late November") with zero additional distributions and the government's October 23 waiver standing without further briefing (`Nov 16 2026: Petition DENIED.`, `signals.distribution_count = 1`); (2) the Court would not issue a CVSG (`signals.cvsg_date = null`); and (3) the denial would be unexplained with no noted dissent or statement respecting denial (`noted_dissent_from_denial = false`).
- **Conditional claims (`unresolved`):** Its conditional predictions that any grant would narrow to QP2 rather than QPs 1 and 3 and take plenary review over summary disposition (85% vs. 15%) were untested once certiorari was denied.
- **Why `0.74`:** All resolved commitments held up, earning substantially more than a generic `0.50` call, though the prose relied on mild hedging ("most likely in an orders list... approximately in mid-to-late November", "waiver will most likely stand", "denial will most likely be unexplained") rather than committing unqualifiedly to the first post-conference orders list, and first-list denial on a government waiver in a nonprecedential MSPB appeal carries a natural ceiling on discriminating content.

## Leakage and Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected: false`):** `retrieval_log.json` confirms a `forward` run on October 30, 2026 (`20261030T011325Z`), seventeen days before the November 16, 2026 resolution. Thirty-five of 38 calls were `captured` (including local reads that explicitly excluded `data/qp-topics/**`, prior-Term corpus queries, and the *Bosley* CourtListener lookup), and the three `unobserved` web-search calls sought only Supreme Court Rule 10 / `2023RulesoftheCourt.pdf`. No outcome material existed at prediction time.
- **Big-case read (`0.04`):** My independent stakes assessment is `0.04`; `codex-baseline`'s `0.19` gave noticeably more weight to the abstract statutory question in QP2 than this *pro se*, nonprecedential, vehicle-flawed dispute warranted.
