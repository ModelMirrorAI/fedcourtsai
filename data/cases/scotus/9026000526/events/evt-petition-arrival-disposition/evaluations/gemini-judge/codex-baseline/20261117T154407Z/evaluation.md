# Evaluation of `codex-baseline` — `scotus/9026000526` (`evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** `cert` (`moment: arrival`)
- **Realized Outcome:** `denied` on `2026-11-16` (`actual_granted: 0`, `distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`)
- **Predicted Disposition / Probability:** `denied` (`probability: 0.04`, `correct: 1`, `brier_score: 0.0016`)
- **Base-Rate Verification:** Base-rate anchoring in `reasoning.md` was verified against historical statpack build `eb6830084a18` (`sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, `sal-v4`, landed `2026-10-19`) reconstructed via `fedcourts statpack-at`, rather than the later `sal-v8` statpack checked out at evaluation time. Skill is evaluated by the harness against the stamped segment base rate.

## Reasoning Quality (`0.87`)

`codex-baseline` delivered a rigorous, well-conditioned arrival analysis in `reasoning.md`:

1. **Disciplined Prior Conditioning:** Using build `eb6830084a18` (`sal-v4`), `codex-baseline` properly identified the private-petitioner `baseline` reached risk-set cohort across strictly prior Terms (OT2017–OT2025), explicitly distinguishing that reached population from both the `state`-petitioner floor (inapplicable where Mississippi is the respondent) and terminal low-distribution cohorts. It also accurately read the exclusive `2026-10-21` cutoff on the arrival snapshot and noted that Justice Alito's `26A324` time-extension grant was not a cert-merits signal. Its downward adjustment to `0.04` sits modestly below the stamped segment base rate for sound case-specific reasons.
2. **Targeted Primary-Source Verification of *Scott*:** Rather than relying solely on the petition's framing, `codex-baseline` checked *United States v. Scott*, 437 U.S. 82, 86–87, 97–101 (1978), via CourtListener MCP and verified that *Scott* itself involved a defense-requested dismissal entered *after the close of all evidence* on constitutional-prejudice grounds (preindictment delay). That directly neutralized petitioner's central attempt to distinguish *Scott* based on both sides having rested, and confirmed that the Mississippi Court of Appeals applied settled culpability-versus-procedure doctrine.
3. **Sound Vehicle and Split Assessment (with Minor Appendix Omissions):** `codex-baseline` accurately read the trial court's written order (App. E) as grounded in missing-witness/compulsory-process violations, deflated the petition's cross-jurisdictional split (*Kruelski* on limitations, *Karpov* on jurisdiction treated as an element), and flagged the complicating state-law appeal-statute and witness-imputation issues. The main limitation—candidly acknowledged in `reasoning.md` ("I did not read every appendix page")—is that `codex-baseline` missed two concrete record points in the appended opinions that further weakened the petition: (a) the trial court had *twice* explicitly denied Mitchell's directed-verdict motions on evidentiary sufficiency before granting the compulsory-process dismissal, and (b) Chief Judge Barnes's four-judge dissent in the Mississippi Court of Appeals rested on Mississippi's strict statutory limits on prosecution appeals (Miss. Code Ann. § 99-35-103) and expressly agreed (App. A ¶ 49) that the trial judge's order was not based on evidentiary insufficiency, making the 5-4 split much weaker evidence of federal constitutional division than `codex-baseline` credited. Its `0.39` stakes read also slightly overstated the broader procedural reach of an idiosyncratic trial order.

## Predicted reasoning (`0.65`)

`codex-baseline`'s `predicted_reasoning.md` committed to five central claims, ordered by the weight the document gave them:

1. **Certiorari denial without a separate writing (`borne-out`):** Forecast `denied` most likely without a noted dissent or statement, naming no Justice to write; the Court entered a bare `Petition DENIED.` order on November 16, 2026.
2. **Single conference distribution with no relist (`borne-out`):** Correctly distinguished `relist-increment` from `0` distributions (reaching conference at least once) from a post-conference relist, forecasting denial after the initial conference without an additional conference (`distribution_count: 1`).
3. **Post-deadline distribution and December 2026–February 2027 decision window (`not-borne-out`):** `codex-baseline` committed specifically to first distribution occurring *after* the November 19, 2026 response deadline and a decision in December 2026 through February 2027 ("allowing for ordinary response-related delay"). Because Mississippi waived its right to respond the day after docketing (October 21, 2026) and no response was requested, the petition was distributed on October 28, 2026 and denied on November 16, 2026—three days *before* the response deadline and ahead of the forecast window.
4. **No CVSG (`borne-out`):** Forecast no CVSG (`cvsg_date: null`).
5. **Conditional grant framing and plenary-over-summary route (`unresolved`):** Conditional claims about narrowing the QP and plenary versus summary reversal if granted were untested given the denial (and the bare denial order states no merits rationale).

Because the core disposition and single-conference/no-CVSG/bare-denial calls held on a modal baseline denial, while the explicit post-deadline timing commitment failed due to overlooking an immediate state waiver of response, the forecast document grades at `0.65` (between the `0.50` and `0.75` anchors).

## Leakage and Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected: false`):** Genuine forward run (`2026-10-20T19:17:47Z`) almost four weeks before the `2026-11-16` resolution. `retrieval_log.json` (33 calls, 93.9% result capture) shows clean forward discipline, pruning `data/qp-topics/*` and consulting external tools solely for general Supreme Court Double Jeopardy precedent (*Scott*, *Evans*, *McElrath*).
- **Big-Case Read (`0.12`):** Routine, fact-bound state non-capital criminal cert denial with no genuine doctrinal split, no amicus participation, an immediate state waiver of response, and no separate writing.
