# Evaluation of codex-baseline (`scotus/73522552`, `evt-petition-disposition`)

## Quantitative Summary

- **Top-level disposition**: Predicted `granted = 0`, `predicted_disposition = "denied"`, `probability = 0.28`. Actual outcome: `actual_granted = 0`, `actual_disposition = "denied"` (resolved `2026-11-09`).
- **Scores**: `correct = true`, `disposition_exact = true`, `brier_score = 0.0784`, `log_loss = 0.328504`.
- **Scored claims**:
  - `disposition` (`p = 0.28`, actual `0`): `correct = true`, Brier `0.0784`, log-loss `0.328504`.
  - `relist-increment` (`p = 0.92`, actual `1`, as `distribution_count` rose from `1` to `2` on October 7, 2026): `correct = true`, Brier `0.0064`, log-loss `0.083382`.
  - `cvsg-increment` (`p = 0.025`, actual `0`): `correct = true`, Brier `0.000625`, log-loss `0.025318`.
  - `dissent-from-denial` (`p = 0.10`, actual `0`): `correct = true`, Brier `0.0100`, log-loss `0.105361`.
  - `summary-disposition-route` (`p = 0.08`): Not evaluable because certiorari was denied (`actual_granted = 0`).

## Reasoning and Calibration Assessment (`reasoning_score = 0.78`)

### What held up well
1. **Rigorous base-rate anchoring**: `codex-baseline` properly anchored on the `sal-v4` `baseline` bracketed `reached` figures in the statpack build in force at prediction time (`1c4f550b7b75`), pooling strictly prior Terms OT2017–OT2024 (`593 / 11,580 = 5.1209%`) and excluding OT2025 (the petition's own docket-number Term). It also explicitly distinguished forward risk-set rates from terminal relist and CVSG cuts.
2. **Accurate procedural reading of `relist-increment`**: `codex-baseline` recognized that the single distribution recorded in the October 6 snapshot (August 5, for the September 28 Long Conference) had been overtaken by the August 19 call for a response, September 18 briefs in opposition, and October 2 reply. It therefore assigned `0.92` to `relist-increment` on the ground that placing the newly completed briefing before a conference required an additional distribution even if the Court ultimately denied certiorari without a substantive relist. That exact sequence occurred: the petition was distributed a second time on October 7 for the November 6 conference and denied on November 9.
3. **Careful engagement with provisioned briefs**: `codex-baseline` cited specific pages of `petition.txt` and both respondents' oppositions in `brief-in-opposition.txt`, accurately contrasting the conceded 5–1 circuit split over *Greenough*/*Pettus* and the August 19 response request against the unpublished Second Circuit summary order, the uncontested reasonableness of the $5,000 service award, and Respondent New York Times's finality objection.

### Where calibration was overly generous on grant probability
- While `codex-baseline` correctly predicted denial, its `0.28` grant probability was the highest in the cell (resulting in a `0.0784` Brier score versus `0.0400` for `gemini-baseline` and `0.0100` for `claude-baseline`).
- Because `codex-baseline` did not conduct external docket research on prior petitions raising the same *Greenough*/*Pettus* class-representative service-award question, it missed that the Court had repeatedly denied review on this exact split in recent Terms—including in *Isaacson v. Meta Platforms*, No. 24-259, where the same petitioner received a call for a response after initial waivers and was denied at the first post-briefing conference without a relist. With that context, the upward adjustment from `5.1%` to `28%` overweighted the August 19 response request.

### Forecast document review

`codex-baseline`'s `predicted_reasoning.md` addressed all five required cert-stage items clearly and specifically:
1. **Relists**: Forecast at least one additional distribution (`P = 0.92`, expecting one or two additional distributions and a decision between late October and December 2026) specifically to put the completed post-CFR briefing before a conference rather than necessarily reflecting a substantive relist. This matched the actual trajectory closely (one additional distribution on October 7 for the November 6 conference, followed by denial on November 9).
2. **CVSG**: Forecast no CVSG (`P = 0.025`) because private class-action settlement awards under *Greenough*, *Pettus*, and Rule 23 do not require executive-branch input. Matched outcome (`cvsg_date = null`).
3. **Questions presented if granted**: Conditionally forecast that the Court would take the categorical *Greenough*/*Pettus* question as framed rather than reviewing the reasonableness of the $5,000 award or unrelated class-certification issues. Conditional on a grant that did not occur, this was sound.
4. **Summary disposition**: Conditionally assigned `P = 0.08` to the summary route, explaining that no intervening Supreme Court decision supported a GVR and resolving competing readings of 19th-century precedent would require plenary review. Sound conditional reasoning (unscored given denial).
5. **Dissent from denial**: Assigned `P = 0.10` to a noted dissent or statement respecting denial and predicted none would issue. Matched outcome (`noted_dissent_from_denial = false`).

## Big-Case Score Assessment

- `codex-baseline` assigned `big_case_score = 0.55` with a concise rationale noting the nationwide impact on class-action settlement practice balanced against the modest $5,000 vehicle and limited broader public salience. I mark `big_case_agreement = "agree"`.

## Leakage Check

- **Mode**: `forward` (`2026-10-06` prediction run; `2026-11-09` resolution).
- **Audit**: `retrieval_log.json` (`result_capture_coverage = 0.93`) records only local workspace reads and two general Supreme Court Rules queries (`site.supremecourt.gov rule 10...` and `2023RulesoftheCourt.pdf`) that returned no case-specific data. `reasoning.md` and `predicted_reasoning.md` strictly reflect the October 6, 2026 docket state. No leakage detected or confirmed.
