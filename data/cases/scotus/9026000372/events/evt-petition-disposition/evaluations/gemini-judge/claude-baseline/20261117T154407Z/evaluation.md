# Evaluation of `claude-baseline` — `scotus/9026000372` (`evt-petition-disposition`)

## Stage and Quantitative Summary

- **Stage:** `cert` (`kind: petition`, `moment: distribution`)
- **Outcome:** `denied` (`actual_granted: 0`, `resolved_at: 2026-11-16`, `distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`)
- **Prediction:** `predicted_disposition: "denied"`, `probability: 0.04`
- **Accuracy & Proper Score:** `correct = 1`, `brier_score = 0.0016` (`(0.04 - 0)^2`). Because `segment_base_rate`, `brier_skill_score`, `base_rate_basis`, `base_rate_salience_version`, and `claim_scores` are harness-owned on cert cells, they are left to `stamp-cell`; relative to the stamped segment base rate on the frozen `baseline` risk-set band, `claude-baseline`'s downward adjustment to `0.04` moves in the right direction.

## Base-Rate Verification (`statpack-at`)

`claude-baseline` ran on `2026-10-31` (`run_id: 20261031T173439Z`) under `sal-v6` against statpack build `dedb32b153e6` (`sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`), reconstructed via `uv run fedcourts statpack-at` rather than the working tree's later `sal-v8` statpack. Against `dedb32b153e6`, `claude-baseline` accurately read its frozen `cert_anchor.rate` (`0.0519`) and accurately described the prior-ten-Term `sal-v6` `baseline` reached range (`4.1%` to `6.1%`, summarized as "roughly 4–6% per Term").

## Rationale Quality (`reasoning_quality`: 0.76)

`claude-baseline`'s `reasoning.md` is concise, factually accurate on everything it cites, and anchored on the right risk-set prior, but leaves notable analytical value on the table compared to a fuller reading of the provisioned record:

- **Strengths:**
  - Correctly identifies the absence of any circuit conflict and the sui generis procedural posture behind petitioners' reliance on *Pennoyer*, *Calderon*, and *Plaut*.
  - Makes good use of its corpus check on No. `19-764` and the Second Circuit opinion (`171 F.4th 575`) to highlight a telling flaw in petitioners' "reopened final case" premise: plaintiffs moved to recall the 2016 mandate in 2018, and the Supreme Court's 2020 GVR vacated the 2019 recall denial in light of the PSJVTA, meaning the recall motion was still live and remanded by this Court itself.
  - Notes both the unanimous 2025 decision in *Fuld v. PLO* upholding PSJVTA jurisdiction and the Solicitor General's waiver of a response.
- **Limitations:**
  - **Omitted downward signals in the provisioned filings:** `reasoning.md` overlooks two concrete points prominent in `petition.txt` and `appendix.txt`. First, `petition.txt` (p. 6) reported that Justice Sotomayor had already denied petitioners' stay application (`No. 26A141`) in August 2026—a quick, unreferred, no-response denial (`scotus/9526000141`) testing the same finality theory. Second, `appendix.txt` (pp. 16a n.3, 20a–22a) explained that the 2016 jurisdictional dismissal was *without prejudice* and that plaintiffs had a parallel protective 2018 action (*Sokolow*, No. 18-cv-12213) stayed in S.D.N.Y., showing mandate recall spared a repeat seven-week trial rather than stripping substantive repose.
  - **Modest downward calibration despite double waivers:** Given waivers by *both* private respondents and the Solicitor General, zero amicus briefs, no response request on file (when modern practice virtually never grants plenary review without first calling for a response), and two prior Supreme Court remands in this same recall proceeding, `claude-baseline`'s ~1-in-3 estimate for a call for a response (`relist-increment: 0.38`) and small net step from the anchor to `0.04` underweighted how dead-on-arrival the petition looked procedurally.

## Predicted Reasoning (`predicted_reasoning_quality`: 0.84)

Grading `predicted_reasoning.md` strictly against the staged record (`outcome.json` and `record/snapshots/2026-11-16.json`):

- **Central claims borne out:** `claude-baseline` specifically and accurately called the modal outcome—"a plain denial on the November 16 order list with no further distribution"—matching `actual_disposition: "denied"` on `2026-11-16` with `distribution_count: 1`. It also accurately forecast no CVSG (`cvsg_date: null`, largely structural given the federal respondent caption) and no separate writing or dissent from denial (`noted_dissent_from_denial: false`).
- **Specificity vs. hedging:** While the modal November 16 plain-denial call was specific and discriminating, `predicted_reasoning.md` hedged substantially on the procedural trajectory, devoting most of its **Relists** section to a "one in three" call-for-response scenario redistributing in January–February 2027. Under the forecast-document rubric, that hedge keeps a wholly borne-out forecast below the very top of the scale (`0.84`).
- **Conditional content (`unresolved`):** Its discussions of which Question Presented the Court would take if granted and why summary disposition would be unlikely were conditioned on a grant that never occurred (`actual_granted: 0`) and receive neither credit nor penalty.

## Big-Case Read (`evaluator_score`: 0.32)

Assessed independently of the candidates' scores, *PLO v. Sokolow* (No. 26-372) sits at **0.32**: the underlying $655.5 million Anti-Terrorism Act judgment against the PLO and Palestinian Authority carries major financial and diplomatic stakes as the post-*Fuld* sequel, but at the cert stage it presented a case-bound procedural postscript under PSJVTA § 903(d)(2) (with a parallel 2018 suit stayed below) that drew respondent waivers from both private plaintiffs and the Solicitor General, zero amicus filings, no call for a response, and a summary first-conference denial without dissent.

## Leakage Assessment (`not_applicable`, `leakage_suspected: false`)

`retrieval_log.json` confirms `mode: "forward"` with `result_capture_coverage: 1.0`. Every tool call executed between `2026-10-31T17:43:52Z` and `2026-10-31T17:45:16Z`—sixteen days before the November 16, 2026 denial and two weeks before the November 13 conference. Corpus queries touched only `19-764`, `24-151`, and a failed `--era modern` syntax attempt; no `data/qp-topics/` paths were accessed and the case was genuinely unresolved when predicted.
