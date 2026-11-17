# Evaluation — `claude-baseline` (`scotus/9526000680`, `evt-motion-disposition`)

## Outcome & Mechanical Summary

- **Realized outcome (`outcome.json` & `record/snapshots/2026-11-16.json`)**: On November 13, 2026 (`resolved_at: "2026-11-13"`), Justice Sotomayor denied Application `26A680` in chambers via a one-line docket entry (`"Application (26A680) denied by Justice Sotomayor."`), with no response requested (`response_requested: false`), no referral to the full Court (`referred_to_court: false`), zero amicus briefs (`amicus_briefs: 0`), and no separate writing (`actual_disposition: "denied"`, `interim_reading: "denied"`, `interim_granted: 0`).
- **Prediction**: `predicted_disposition = "denied"` (`granted = 0`), `probability = 0.01` (`correct = 1`, `brier_score = 0.0001`). Against the 10-Term finer interim grant rate (`156 / 1,337 = 0.116679`), `brier_skill_score = 0.9927`.

## Reasoning Assessment (`reasoning.md` — `0.72`)

`claude-baseline` delivered a concise, well-calibrated structural read of the stay application, but left significant detail in the provisioned 38-page filing unexamined:

1. **Strengths in calibration and base-rate framing**: `claude-baseline` cited the exact scored 10-Term finer interim pool (`11.7%`, `156/1337`) and the `private` / `unmarked` applicant-class cell (`7.0%`, `63/906`) from `metrics/statpack.md`, then clearly explained the sharp compositional divide within `private` / `unmarked` between counselled institutional/constitutional emergency applications and pro se foreclosure/eviction stay filings. It correctly spotted doubtful finality under 28 U.S.C. § 1257 (noting Applicant's reliance on *Cox Broadcasting*), the absence of any circuit split, and the silent escalation ladder, arriving at a realistic `0.01` grant probability while transparently noting OCR provenance and mootness conditioning.
2. **Thin record inspection and missing angles**: `retrieval_log.json` (`head -c 9000 data/cases/scotus/9526000680/record/documents/application.txt`) shows that `claude-baseline` read only the first 9,000 bytes (~3 pages out of 38) of `application.txt` and did not consult CourtListener. Because it stopped near page 3, `reasoning.md` never engages the concrete procedural record set out in pages 4–38: it does not name *Hollingsworth v. Perry* or analyze why Connecticut's *Frimberger* foreclosure-finality rule (liability-only summary judgment entered December 1, 2025, prior to debt determination, strict-foreclosure judgment, or law days) defeats *Cox* finality; it misses the 28 U.S.C. § 2101(c) timeliness discrepancy between the June 2, 2026 certification denial in `PSC-250444` (>90 days before filing) and the September 11/15, 2026 reconsideration order in `SC 250398`; and it overlooks Judge Nagala's November 9, 2026 District of Connecticut TRO/PI denial (`ECF 133`/`134`). In addition, `referral-increment = 0.07` (3.5× its `response-requested-increment = 0.02`), premised on a hypothetical post-denial renewal to a second Justice despite acknowledging the imminent November 16 hearing would likely overtake renewal, is internally somewhat high.

## Forecast Document Assessment (`predicted_reasoning.md` — `0.93`)

Graded on its own terms against `outcome.json` and `record/snapshots/2026-11-16.json`, `claude-baseline`'s `predicted_reasoning.md` is crisp, unhedged, and accurate across every observable commitment:

- Single-Justice denial by Justice Sotomayor in a one-line docket entry with no opinion or separate statement from any Justice, and no interim administrative stay (**borne out**: one-line November 13, 2026 denial by Justice Sotomayor, `interim_granted: 0`, `writing_roles: null`).
- No response requested (**borne out**: `response_requested: false`), no referral to the full Court (**borne out**: `referred_to_court: false`), and zero amicus filings (**borne out**: `amicus_briefs: 0`).
- Timing within about a week of submission, most likely on or shortly before November 16, 2026 (**borne out**: denied November 13, 2026, two days after submission and three days before November 16; its parenthetical remark that post-denial renewal would be unlikely because the November 16 hearing "will already have passed" assumed slightly later pre-hearing action than November 13, though no renewal occurred through the November 16 snapshot).
- Its final two-sentence conditional paragraph on what a contrary favorable action would look like is proportional and untested by the unexplained denial (`unresolved`, not a miss).

## Big-Case Stakes Read (`0.03`)

Independently assessed at **`0.03`** (`0.00–0.15` routine fact-bound band): a single-property pro se Connecticut foreclosure stay request turning on case-specific state trial-management and interlocutory finality rulings, with zero external attention and a routine one-line chambers denial. (`claude-baseline`'s pre-registered `big_case_score = 0.03` matched this read.)

## Leakage & Forecast-Exposure Check

- **Mode & timing**: `mode = "forward"`, `run_id = "20261114T033825Z"` (2026-11-13 22:38 EST), provisioned with `2026-11-12.json` (`snapshot_provenance: "truncated"` at `cut_anchor_index: 0`). Audited against `resolved_at: "2026-11-13"`.
- **Audit result**: Clean (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`). `result_capture_coverage` is `1.0` across all 10 logged tool calls, with zero CourtListener MCP or web calls. Only provisioned files, `metrics/statpack.md`, and two generic `fedcourts query` calls for recent denied dockets (which did not include `26A680` at prediction time) were accessed, and `claude-baseline`'s reasoning treats `26A680` as pending ahead of November 16, 2026. No external or sibling forecast exposure occurred.
