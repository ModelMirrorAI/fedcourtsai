# Evaluation of gemini-baseline

## Quantitative summary

- **Stage:** `cert` (`evt-petition-disposition` in `scotus/9026000249`, *Randy Quaid, et ux. v. Craig Granet, et al.*, No. 26-249).
- **Predicted disposition / probability:** `denied` (`probability = 0.005`, `granted = 0`).
- **Actual outcome:** `denied` (`actual_granted = 0`, resolved `2026-11-09`).
- **Correct:** `1` (`predicted_disposition == actual_disposition`).
- **Brier score:** `0.000025`.
- **Segment base rate and skill:** Left to the harness stamp (`stamp-cell` pools the stamped segment base rate and `brier_skill_score` from the committed statpack). To evaluate `gemini-baseline`'s base-rate usage against the pack in force when the prediction ran (`20261015T142602Z`), I reconstructed statpack build `886549a3ac32bdba039691b6d2ca7dc57bb72561` (`sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, which differs from the currently committed `metrics/statpack.md`) via `uv run fedcourts statpack-at`.

## Reasoning quality (`0.62`)

`gemini-baseline` reached a well-calibrated headline probability (`0.005`, `denied`) and correctly identified the core reasons why the petition was uncertworthy, but `reasoning.md` had notable methodological and analytical gaps:

1. **Base-rate anchoring error:** Evaluated against statpack build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, `gemini-baseline` stated that the `baseline` grant rate for recent Terms was "approximately 0.9-1.3%". Those numbers correspond to the unbracketed *terminal* band rates in recent Terms rather than the bracketed `reached` (risk-set) rate that governs a cell with a frozen `baseline` band (and underpins the stamped segment base rate). Moreover, `gemini-baseline` eyeballed a recent-Term range rather than pooling strictly prior Terms.
2. **Limited engagement with the provisioned filings:** As reflected in both `reasoning.md` and the retrieval log, `gemini-baseline` read `questions-presented.txt` and only the first 20 lines of `appendix.txt`, without reading `petition.txt`, `brief-in-opposition.txt`, or the substance of the Ninth Circuit and district court orders in the appendix. Consequently, `reasoning.md` missed the specific vehicle defects developed in the record (such as the separate Government Claims Act dismissal of the County defendants and the service dismissal of the sheriff's employee who allegedly accessed the database) and slightly misstated the vexatious-litigant ruling as deeming "one of the plaintiffs" a vexatious litigant (the district court declared both Randy and Evgenia Quaid vexatious litigants, App. 2).
3. **Omission of secondary claim rationale:** `reasoning.md` asserted that there was a very low probability of a relist or CVSG, but gave no explanation for the specific probabilities assigned to `relist-increment` (`0.05`), `cvsg-increment` (`0.01`), `summary-disposition-route` (`0.05`), or `dissent-from-denial` (`0.02`), and left `big_case_rationale` null in `prediction.json`.

Despite those limitations, `gemini-baseline` accurately captured the decisive points: an unpublished Ninth Circuit memorandum ("Not for Publication"), a state-law dispute over California Civil Code § 47(b) with no federal circuit split, and a poor vehicle.

## Predicted reasoning (`0.70`)

In `predicted_reasoning.md`, `gemini-baseline` committed to five main claims:
1. **Denial of certiorari:** Borne out (`actual_disposition: "denied"`).
2. **No further relists before decision:** Borne out (`signals.distribution_count: 1`).
3. **No CVSG:** Borne out (`signals.cvsg_date: null`).
4. **No separate writing or dissent from denial:** Borne out (`noted_dissent_from_denial: false`).
5. **Conditional on grant, plenary focus on limits of state litigation privileges in federal court rather than a summary disposition / GVR:** Unresolved because certiorari was denied.

All four testable claims on the denial path were borne out. The document is concise and accurate in direction, though slightly more generic than peers (it does not reference the November 6, 2026 conference schedule or the specific gravamen/futility framing of the question presented), placing it at `0.70`.

## Leakage assessment

- **Mode:** `forward` (predicted `2026-10-15`, resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`. All 22 tool calls in `retrieval_log.json` are `unobserved` (`result_capture_coverage: 0.0`, the engine's standing telemetry shape). Graded on the queries, every call targeted local prompt/record/statpack files plus a single CourtListener search for `"Randy Quaid" "Craig Granet"` (which `retrieval.md` notes located the C.D. Cal. district court docket) while the Supreme Court petition remained genuinely open.
