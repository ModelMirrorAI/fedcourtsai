# Evaluation of `codex-baseline` (`scotus/9026000087` — `evt-petition-disposition`)

## Outcome and Quantitative Scoring

The Supreme Court denied certiorari on November 9, 2026 (`actual_disposition: "denied"`, `actual_granted: 0`), following the November 6, 2026 conference after a single distribution (`distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).

- **Predicted disposition:** `denied` (`correct: 1`)
- **Predicted grant probability:** `0.008` (`brier_score: 0.000064`)
- **Base rate and skill:** Left for the harness (`stamp-cell`) to compute against the stamped segment base rate. Using `uv run fedcourts statpack-at`, `codex-baseline` ran against statpack build `0918fb18e74f` (`sha256:63295af7c6e50f69b51af1f372c8a86dd6e8a398f9e6bc408c56fd8af8ccaf4d`), whose `sal-v4` table matches the committed pack.

## Reasoning Quality (`0.95`)

`codex-baseline` produced the most thorough and record-grounded legal analysis in the panel (`reasoning.md`):
1. **Exact base-rate methodology:** `codex-baseline` properly distinguished between the bracketed `reached` (risk-set) rate and the terminal rate for `sal-v4` `baseline`, pooled the nine strictly prior Terms (2017–2025) weighted by their denominators (`12,871`), and arrived at ~4.99%, while explicitly noting why terminal relist and CVSG buckets cannot be substituted for the reached-band anchor.
2. **Deep engagement with the Fifth Circuit opinion and briefing:** Rather than relying on surface indicators alone, `codex-baseline` verified the petition's premises against Appendix C and the BIO:
   - Pointed out that Appendix C (pp. 32–35) explicitly recited the four *Geiserman* factors and rested on the petitioner's failure to explain missing expert reports and the district court's prejudice finding—directly undercutting QP 1's premise that the lower courts refused to consider prejudice or explanation.
   - Identified the chronological defect in QP 2's narrative: the BIO showed that partial summary judgment on policy valuation (actual cash value) and the motel roof exclusion preceded the expert exclusion by more than six months, and Appendix C affirmed those coverage and evidentiary rulings independently.
   - Analyzed the factual dispute over whether the Dropbox link contained compliant Rule 26 expert reports or ordinary discovery materials, and noted the BIO's specific preservation objections.
3. **Careful handling of docket provenance:** It flagged the September 6, 2025 vs. July 21, 2026 date discrepancy without over-inferring a jurisdictional defect.

## Predicted Reasoning (`0.85`)

In `predicted_reasoning.md`, `codex-baseline` laid out a clear, well-structured forecast of the Court's action:
- Accurately predicted that the Court would deny certiorari in the orders following the November 6, 2026 conference, during November 2026, without a separate writing.
- Accurately predicted zero additional distributions (relists) and no CVSG.
- Grounded the forecast in the specific mismatch between the petition's broad due-process framing and the Fifth Circuit's unpublished application of the multifactor *Geiserman* standard alongside independent insurance-policy rulings.
- Clearly separated its conditional merits/route expectations (narrowed QP 1 on Rule 37(c)(1) findings; 15% summary route vs. 85% plenary review if granted) from its primary denial forecast.

## Leakage Assessment

- **Mode:** `forward` (prediction placed October 12, 2026; event resolved November 9, 2026).
- **Assessment:** `retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`.
- **Notes:** `retrieval_log.json` shows local reads of the provisioned record and `statpack.md`, one CourtListener lookup for `"R & R Sails"` (a cited Ninth Circuit case), and unobserved web searches for general Supreme Court Rules pages (`Rule 10`, `2019RulesoftheCourt.pdf`, `rules_guidance.aspx`), all of which were candidly documented in `retrieval.md` and occurred nearly a month before the case was decided.
