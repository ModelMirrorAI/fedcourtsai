# Evaluation of `codex-baseline` — `scotus/9026000372` (`evt-petition-disposition`)

## Stage and Quantitative Summary

- **Stage:** `cert` (`kind: petition`, `moment: distribution`)
- **Outcome:** `denied` (`actual_granted: 0`, `resolved_at: 2026-11-16`, `distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`)
- **Prediction:** `predicted_disposition: "denied"`, `probability: 0.04`
- **Accuracy & Proper Score:** `correct = 1`, `brier_score = 0.0016` (`(0.04 - 0)^2`). `segment_base_rate`, `brier_skill_score`, `base_rate_basis`, `base_rate_salience_version`, and `claim_scores` are left unset for the harness stamp; relative to the stamped segment base rate on the frozen `baseline` risk-set band, `codex-baseline`'s `0.04` forecast adjusts modestly in the right direction.

## Base-Rate Verification (`statpack-at`)

`codex-baseline` ran on `2026-10-31` (`run_id: 20261031T173439Z`) under `sal-v6` against statpack build `dedb32b153e6` (`sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`), reconstructed via `uv run fedcourts statpack-at`. Every statpack count and percentage cited in `codex-baseline`'s `reasoning.md` matches `dedb32b153e6` to the digit (`cert_anchor.rate` `0.0518752467429925`, `1,274` grant-family out of `44,770` modern cert resolutions, relist buckets `10,204` / `2,532` / `495` / `482`, CVSG buckets `13,549` / `164`, zero-amicus bucket `11,109` resolved / `11,414` total, and `ca2` `2,101` resolved). Its methodological hygiene—refusing own-Term 2026 data, refusing to substitute the terminal `baseline` rate, explaining why terminal relist/CVSG/amicus cuts are non-independent cross-checks rather than multipliers, and assigning zero quantitative weight to its disposition-filtered corpus sample—is exemplary.

## Rationale Quality (`reasoning_quality`: 0.88)

`codex-baseline`'s `reasoning.md` combines rigorous statistical discipline with balanced, epistemically careful legal analysis, falling only slightly behind `gemini-baseline` on targeted docket retrieval and internal probability calibration:

- **Strengths:**
  - **Substantive engagement with both sides of the record:** Fairly credits petitioners' distinction between curing jurisdiction during an active appeal and resurrecting a vacated judgment after appellate finality (*Pennoyer*, *Calderon*, *Plaut*), while accurately extracting from `appendix.txt` (pp. 16a–27a) every reason the Second Circuit's opinion blunted cert-worthiness—distinguishing judicial recall discretion from legislative reopening under *Plaut*, noting the 2016 vacatur was *without prejudice*, and highlighting plaintiffs' already-filed second action so petitioners were seeking a new trial rather than immunity from the claims.
  - **Epistemic discipline:** Rightly distinguishes petitioners' foreign-policy/fiscal advocacy (relying partly on a 2015 statement) from verified current facts, notes that an unrecorded en banc vote does not disclose individual judicial votes, notes the August 2026 stay denial (`petition.txt` p. 6) while observing that interim relief carries extra requirements beyond cert-worthiness, and cleanly distinguishes a party CFR to the Solicitor General from a CVSG.
- **Limitations:**
  - **Missed targeted corpus lookups (`19-764` and `26A141`):** Whereas `codex-baseline` ran a generic `--disposition denied --decided-before 2026` corpus query returning four unrelated OT2025 petitions, querying this litigation's own prior dockets (`19-764` and `26A141`) would have surfaced both that the 2020 GVR vacated the 2019 recall-denial order while the recall motion remained live and that Justice Sotomayor denied stay application `26A141` in four days without calling for a response or referring it to the Court.
  - **Mild tension between `relist-increment` (`0.12`) and `probability` (`0.04`):** Because modern Supreme Court practice virtually never grants plenary review after double respondent waivers without first calling for a response (and `codex-baseline` put summary disposition given grant at only `0.15`), a `0.12` further-distribution probability alongside a `0.04` grant probability implies roughly a one-in-three conditional grant rate given a response request/relist—generous for a splitless post-*Fuld* sequel where the Solicitor General waived.

## Predicted Reasoning (`predicted_reasoning_quality`: 0.92)

Grading `predicted_reasoning.md` strictly against the staged record (`outcome.json` and `record/snapshots/2026-11-16.json`):

- **Specific, low-hedge central claims borne out:** `codex-baseline` led cleanly with the exact realized action: certiorari denied in the order list immediately following the November 13, 2026 conference (`2026-11-16`) without an explanatory opinion, zero additional distributions and no response request (`88%` modal commitment; `distribution_count: 1`), no new CVSG (`0.5%`; `cvsg_date: null`), and no dissent or statement respecting denial (`2.5%`; `noted_dissent_from_denial: false`). Committing at 88% against even a call for a response or relist in a $655.5 million follow-on to *Fuld* was specific and discriminating.
- **Conditional content (`unresolved`):** Its conditional forecast of a narrowed PSJVTA mandate-recall question (excluding Fifth Amendment validity settled in *Fuld* and trial-expert issues) and an 85%/15% plenary-over-summary split if granted was never tested (`actual_granted: 0`) and receives neither credit nor penalty, placing the document at `0.92`.

## Big-Case Read (`evaluator_score`: 0.32)

Assessed independently of the candidates' scores, *PLO v. Sokolow* (No. 26-372) sits at **0.32**: while the underlying $655.5 million ATA judgment against the PLO and Palestinian Authority and the post-*Fuld* finality framing carry genuine financial and diplomatic weight, this cert petition presented a sui generis mandate-recall postscript under PSJVTA § 903(d)(2) (with a parallel 2018 action stayed below), drew waivers from both private respondents and the Solicitor General with zero amicus briefs, and was summarily denied at its first conference without dissent.

## Leakage Assessment (`not_applicable`, `leakage_suspected: false`)

`retrieval_log.json` confirms `mode: "forward"` (`result_capture_coverage: 0.971`, with 34 of 35 calls captured and one hosted `web-search` call marked `unobserved`). All calls ran between `2026-10-31T17:44:31Z` and `2026-10-31T17:47:49Z`, sixteen days before the `2026-11-16` denial. Grading the single `unobserved` web search on its query (`site.supremecourt.gov opinions 2024 Fuld Palestine Liberation Organization 24-20 June 20 2025`), it targeted only the June 2025 *Fuld* opinion; the `rg --files` check for `AGENTS.md` properly passed `-g '!data/qp-topics/**'` without opening files there; and the case was genuinely open when predicted.
