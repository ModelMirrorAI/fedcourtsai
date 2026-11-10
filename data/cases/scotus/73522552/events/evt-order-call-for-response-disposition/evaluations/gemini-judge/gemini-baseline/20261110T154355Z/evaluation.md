# Evaluation of `gemini-baseline` — *Eric Alan Isaacson v. Maribel Moses, et al.* (`scotus/73522552`, `evt-order-call-for-response-disposition`)

## Outcome and quantitative summary

- **Actual outcome**: `denied` (`actual_granted: 0`, `resolved_at: "2026-11-09"`, `noted_dissent_from_denial: false`, `signals.distribution_count: 2`, `signals.cvsg_date: null`).
- **Predicted disposition**: `denied` (`granted: 0`, `probability: 0.06`, `confidence: 0.85`).
- **Accuracy (`correct`)**: `1`.
- **Brier score**: `(0.06 - 0)^2 = 0.0036`.
- **Baseline and skill**: `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left null for harness stamping against the stamped segment base rate.
- **Statpack build graded against for base-rate use**: Reconstructed via `uv run fedcourts statpack-at` for `run_id: "20261029T142045Z"` as commit `7bcde3b105cb212283905eda17b827efc188e80c` (`sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `sal-v4`), which was in force when the candidate ran (as distinct from the currently committed `sal-v8` statpack).

## Reasoning quality (`reasoning_quality: 0.42`)

`gemini-baseline`'s `reasoning.md` identifies the core doctrinal tension (*Trustees v. Greenough* and *Central Railroad & Banking Co. v. Pettus* versus modern Rule 23 class-representative service awards and the Eleventh Circuit's holding in *Johnson v. NPAS Solutions, LLC*) and reaches a sensible final grant probability (`0.06`, slightly above the stamped segment base rate) by weighing the August 19, 2026 Call for a Response against the Court's repeated denials of certiorari on this exact question and the summary-order posture of *Moses II*.

However, `reasoning.md` suffers from severe evidence-grounding and base-rate fabrication errors that place it in the `0.4–0.5` rubric band:

1. **Fabricated statpack base-rate figures**: Inspection of `retrieval_log.json` shows that `gemini-baseline` issued a single unpaginated `file-read` on `metrics/statpack.md`, which truncated before line 196 (where the `Segment base rate by salience band (sal-v4)` table begins), and never read the remainder of `metrics/statpack.md`. In Section 2 of `reasoning.md`, `gemini-baseline` asserted that the `sal-v4` salience table "renders OT 2024 and OT 2025" and reported an OT 2024 `baseline` reached rate of `"2.1% (n=1,210; terminal rate 0.0%, n=1,179)"`, an OT 2025 `baseline` reached rate of `"4.6% on n=1,076"`, an overall modern discretionary-cert grant rate of `"4.0% across n=8,979"`, an originating-circuit `ca2` grant rate of `"3.3% on n=676"`, and a `0`-amicus rate of `"4.3% on n=1,846"`. Against the reconstructed statpack build in force when `gemini-baseline` ran (`7bcde3b105cb`, `sal-v4`)—as well as the committed `sal-v8` statpack—none of those numbers exist in the table (the `sal-v4` table rendered 10 Terms `2017–2026`, not two, and none of the quoted rates or denominators match any row or cut in `statpack.md`). Anchoring on a fabricated `2.1%` baseline and applying a 3x Call-for-Response multiplier to arrive at `0.06` fails the base-rate grounding check.
2. **Fabricated citations to `petition.txt` and misstated record dates**:
   - `gemini-baseline` wrote that "the petition itself candidly catalogues (Pet. 3, 21 & nn. 5, 65)" six prior Supreme Court cert denials on the *NPAS* split (*Johnson*, *Carson v. Hyland*, *Murray*, *Kazman*, *Isaacson v. Toy*, and *Dart v. Scott*). While those prior denials are real historical cases, the provisioned `petition.txt` is 20 pages long, contains only 7 footnotes in total, and does not cite those cert denials—so citing `"Pet. 3, 21 & nn. 5, 65"` fabricates page and footnote citations to the staged petition.
   - `gemini-baseline` misstated the date and Westlaw citation of the decision below (*Moses II*) as `"Dec. 17, 2025, Pet. App. 10a"` and `"2025 WL 3654242"`, whereas both `2026-08-20.json` and `petition.txt` (Pet. ii, 1, 6, 14, and Pet. App. 1a) explicitly state that the Second Circuit's summary order in *Moses II* was filed **February 10, 2026** (`2026 WL 364231`).
   - `gemini-baseline` misread the docket dates in `2026-08-20.json`, stating that respondents waived on July 14 and July 22, 2026 and that the petition was initially distributed on July 29, 2026, whereas `2026-08-20.json` records Moses's waiver on July 14, The New York Times's waiver on July 21, and initial distribution on August 5, 2026.
   - `gemini-baseline` also described the split as `"10–1 or 11–1"` across ten regional circuits plus the D.C. Circuit, whereas the petition and Question Presented frame the post-*NPAS* conflict as 5–1 (the Eleventh Circuit against the First, Second, Seventh, Ninth, and Federal Circuits).

## Predicted reasoning

Evaluated strictly on its own merits against the resolved record (`outcome.json` and `2026-11-09.json`), `gemini-baseline`'s `predicted_reasoning.md` (`predicted_reasoning_quality: 0.76`) performed well on every unconditional claim it committed to:

- **Procedural trajectory (`borne-out`)**: Correctly forecast that after the August 19, 2026 Call for a Response, respondents would file their opposition brief(s) (Sept. 18, 2026, after an extension was granted), petitioner would file his cert reply (Oct. 2, 2026), and the Clerk would re-distribute the petition once (`relist-increment: 0.98`, bringing total distributions from 1 to 2 on Oct. 7, 2026 for the Nov. 6, 2026 conference), followed by denial at that conference without a post-BIO conference relist. (The opening sentence of `predicted_reasoning.md` repeats the minor baseline-docket errors of citing July 29 instead of August 5 for the first distribution and swapping the two respondents' July waiver dates.)
- **CVSG (`borne-out`)**: Correctly forecast that no CVSG would issue (`cvsg-increment: 0.01`; `signals.cvsg_date: null`).
- **Disposition and separate writings (`borne-out`)**: Correctly forecast that certiorari would be denied (`disposition: 0.06`) without any noted dissent or separate statement (`dissent-from-denial: 0.04`; `noted_dissent_from_denial: false`), while keeping its discussion of a potential separate statement by Justice Thomas, Gorsuch, or Alito explicitly conditional.
- **Conditional merits and scope (`unresolved`)**: Properly framed its scope-of-review and plenary-versus-summary (`summary-disposition-route: 0.05`) discussion as conditional on a grant.

Because a cert denial with no separate writing tests only the unconditional claims, and `predicted_reasoning.md` called all of those specifically and accurately while keeping its grant/authorship sections conditional (with only minor date misstatements in its preamble), it earns `0.76`.

## Leakage and big-case read

- **Leakage (`not_applicable`, `leakage_suspected: false`)**: Forward prediction run on October 29, 2026, eleven days before the November 9, 2026 cert denial. `retrieval_log.json` confirms no post-cutoff or outcome-revealing material was accessed.
- **Big-case assessment (`evaluator_score: 0.35`)**: Forming an independent read of the case's stakes, a categorical Supreme Court ruling on *Greenough*/*Pettus* and Rule 23 service awards would reshape federal class-action settlement practice nationwide, though this specific dispute involves a pro se objector challenging a $5,000 award in private consumer litigation affirmed by summary order and ended in an unremarked cert denial.
