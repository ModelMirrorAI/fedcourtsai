# Evaluation of `gemini-baseline` — `scotus/9026000435` (`evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Outcome**: Certiorari `denied` on `2026-11-16` (`actual_granted = 0`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`). The Solicitor General waived the right to respond on October 23, 2026; the petition was distributed once on October 28, 2026 for the November 13, 2026 Conference and denied without separate writing on November 16, 2026.
- **Prediction**: `predicted_disposition = "denied"` (`correct = 1`), `probability = 0.12`, `brier_score = 0.0144`. Skill against the baseline is recorded mechanically by the harness against the stamped segment base rate.
- **Base-rate build graded against**: Reconstructed via `fedcourts statpack-at` at build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5` (`sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, landed `2026-09-28`), which carried the `sal-v4` segment table matching `gemini-baseline`'s frozen `context.salience_version` rather than the later committed pack.

## Reasoning Quality (`reasoning.md` — `0.30`)

`gemini-baseline`'s reasoning is superficial and omits examination of the provisioned petition text and lower-court opinion (`record/documents/petition.txt`), leading to an ungrounded upward probability adjustment and a conceptual error on the distribution-increment claim.

**What `gemini-baseline` got right:**
- Correctly placed Nexstar in the `private` petitioner class (`band: baseline`) rather than mistaking a federal respondent for a federal petitioner, and accurately pooled the `sal-v4` `baseline` bracketed `reached` rate over strictly prior Terms OT2017–OT2025 in statpack build `1c4f550b7b75` (`~5.0%`).
- Correctly noted that because the NLRB is the respondent represented by the Solicitor General, `P(CVSG)` is effectively zero (`0.01`).

**Major analytical failures:**
1. **Failure to examine `petition.txt` and the Second Circuit order (`App. 1a–13a`)**: `gemini-baseline`'s single-paragraph `reasoning.md` relies solely on `questions-presented.txt`. It explicitly speculates that *"we have not yet seen the government's response (or whether they might point to vehicle issues, such as the lower court ruling resting on factual rather than legal deference)"* — treating as an unknown future possibility what was directly observable in the provisioned appendix! Had `gemini-baseline` read `petition.txt`, it would have seen that:
   - the decision below was an **unpublished summary order** (`App. 1a`) that explicitly stated *"We review the NLRB's legal conclusions de novo"* (`App. 3a`), treated supervisory status under 29 U.S.C. § 152(11) as a question of fact (`App. 5a`), and affirmed on concrete **substantial-evidence** gaps across each producer group (`App. 5a–8a`);
   - the Second Circuit had **already disclaimed NLRB legal deference** in a published opinion two months later (*Siren Retail Corp. v. NLRB*, Sept. 2, 2026), disclosed on pages 3 and 13–14 of the petition itself;
   - the Eighth Circuit's *Multimedia KSDK* decision was a record-specific finding on one station's broadcast producers rather than a categorical legal split; and
   - the petition's own primary ask was a *Loper Bright* GVR on analogy to *Hospital Menonita* (`Pet. 4, 14–17`).
2. **Unsubstantiated upward adjustment (`5.0% -> 12%`)**: Taking the Questions Presented's framing ("direct defiance of ... *Loper Bright*" and a circuit split) at face value led `gemini-baseline` to more than double the risk-set base rate for a weak, non-precedential substantial-evidence petition, producing a worse Brier score (`0.0144`) than the stamped segment base rate.
3. **Misread `relist-increment` at arrival (`0.28`)**: At `moment: arrival` (`distribution_count = 0`), `relist-increment` (`distribution_count` increasing by at least 1) is satisfied as soon as the petition is distributed for its *initial* conference, which occurs for virtually every paid petition not withdrawn or dismissed before conference (as happened here on Oct. 28, 2026 when `distribution_count` went from `0` to `1`). `gemini-baseline` conflated an initial distribution increment from zero with a post-conference relist and assigned `0.28`. Its low conditional `summary-disposition-route` (`0.10`) and inflated `dissent-from-denial` (`0.15`) similarly reflected not having read the petition's GVR request or the summary order below.

## Forecast Document Quality (`predicted_reasoning.md` — `0.35`)

Graded strictly on `predicted_reasoning.md` against the staged record (`outcome.json` and `record/snapshots/2026-11-16.json`), `gemini-baseline` called the ultimate denial right (and the structurally entailed absence of a CVSG), but its specific procedural and separate-writing predictions failed:

- **Borne-out**: Ultimate disposition (`denied`) and absence of a CVSG (`cvsg_date = null`).
- **Not borne-out — relist forecast**: The document leads with *"Expect one relist before a decision on the petition, as the question presented directly addresses whether the Second Circuit defied Loper Bright..."* In fact, the petition was distributed once on October 28, 2026 for the November 13, 2026 Conference (`distribution_count = 1`) and denied on November 16, 2026 with **zero relists**.
- **Not borne-out — government brief forecast**: Asserted that the federal respondent *"will file a brief expressing the government's views."* In fact, the Solicitor General filed a waiver of the right to respond on October 23, 2026 (`2026-11-16.json`), and the Court never requested a response.
- **Not borne-out — dissent-from-denial prospect**: Suggested a *"reasonable prospect of a dissent from denial from one of the conservative Justices"*; the denial was routine and unexplained (`noted_dissent_from_denial = false`).
- **Unresolved**: Its conditional grant forecast (plenary review of QP 1 favored 90% over a 10% summary route) was untested given the denial.

## Leakage Audit (`not_applicable` / `leakage_suspected = false`)

This was a `forward` prediction made on `2026-10-01` (`run_id: 20261001T215439Z`), long before the `2026-10-23` waiver and `2026-11-16` denial. Although `result_capture_coverage` is `0.0` (an engine standing shape), inspection of all 21 call queries in `retrieval_log.json` confirms exclusively local reads of prompt, schema, `event.yaml`, `context.json`, `2026-10-02.json`, `documents.json`, `questions-presented.txt`, and `metrics/statpack.md`, with zero external lookups and zero touches of `data/qp-topics/`.

## Big-Case Read (`evaluator_score = 0.18`)

Independent of the candidates' scores, this case carries low significance (`0.18`): it is a single-station technical refusal-to-bargain dispute resolved by an unpublished summary order on record-specific substantial-evidence grounds after the Second Circuit had already adopted non-deferential *Loper Bright* review in *Siren Retail*, drawing an SG waiver, zero amicus briefs, one distribution, and a routine denial.
