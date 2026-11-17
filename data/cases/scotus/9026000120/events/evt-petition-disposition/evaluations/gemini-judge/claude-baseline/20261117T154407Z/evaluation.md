# Evaluation of `claude-baseline` — `scotus/9026000120` (`evt-petition-disposition`)

## Outcome and Quantitative Summary

On November 16, 2026, the Supreme Court denied certiorari in *Gays Against Groomers, et al. v. Garcia, et al.* (No. 26-120) directly off the November 13, 2026 conference without any further relist (`distribution_count = 2`), CVSG (`cvsg_date = null`), or noted dissent (`noted_dissent_from_denial = false`).

- **Stage:** `cert` (`moment: distribution`). Baseline and skill fields (`segment_base_rate`, `brier_skill_score`, `base_rate_basis`) are left null for the harness to stamp from the committed statpack.
- **Disposition accuracy (`correct`):** `1` (`denied` vs. `denied`).
- **Probability / Brier (`brier_score`):** `P(grant) = 0.12` → `(0.12 - 0)^2 = 0.0144`.
- **Statpack build verified against:** `ca0c9e1a49e292692bdc5b092cd9f868561169b8` (`sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`), reconstructed via `fedcourts statpack-at`. All statpack and `amicus-line.json` numbers `claude-baseline` cited match that pinned build.

## Reasoning Quality (`reasoning.md` — `0.72`)

`claude-baseline` produced a well-calibrated probability (`0.12`, substantially beating the stamped segment base rate) backed by sensible statistical adjustments, but made a notable procedural misread of the record below by skimming rather than reading the Tenth Circuit opinion bound into `petition.txt`:

- **Strengths (base-rate calibration and primary doctrine):** `claude-baseline` properly anchored on the prior-Term `elevated` risk-set figures in the pinned statpack (`ca0c9e1a49e2`), accurately explained why `distribution_count = 2` via a November 5 pre-conference `Rescheduled` entry is a much weaker signal than a post-conference relist, avoided double-counting the four amicus briefs against `amicus-line.json` (`14.7%`), and correctly identified that *Supreme Court of Virginia v. Consumers Union* (1980) already extends legislative immunity to equitable claims while `Minton` and `Schmidt` n.10 are municipal/dicta authorities rather than a square state-legislator split.
- **Factual / procedural error on mootness:** Under *Vehicle / posture*, `claude-baseline` wrote that *"The district court gave an alternative ground: the prospective claims were moot. That would complicate review."* While the district court had ruled in the alternative on mootness (BIO p. 6; Pet. App. 54a–59a), the Tenth Circuit's published opinion—provisioned directly in Appendix A of `petition.txt` (Pet. App. 3a, Part II, joined by Judge Carson as well)—**expressly addressed jurisdiction and held that the case is not moot and remains justiciable**, and Respondents did not renew mootness as an obstacle in the Brief in Opposition. Because `claude-baseline` read only lines 1–400 of `petition.txt` and two excerpts of `brief-in-opposition.txt`, it treated a resolved district-court ruling as a live vehicle problem while missing the actual vehicle issue Respondents pressed (that Petitioners sued only five state legislators and named no non-legislator enforcement officer such as a sergeant-at-arms under *Powell* / *Kilbourn*). `claude-baseline` also slightly muddled the relationship between *Ex parte Young* and § 1983 on Question 1 (*Consumers Union* itself addressed prospective § 1983 relief).

## Predicted reasoning (`predicted_reasoning.md` — `0.68`)

`claude-baseline`'s forecast document is a brief five-bullet summary whose modal procedural calls were borne out:

1. **Disposition (`borne-out`):** Forecast `denied`, matching `actual_disposition = "denied"`, though its one-sentence rationale repeated the mistaken premise that *"a mootness holding below is a vehicle problem."*
2. **Conference resolution without further relist (`borne-out`):** Committed at ~80% confidence to no further distribution past the November 13, 2026 conference, matching `signals.distribution_count = 2` and resolution on November 16, 2026.
3. **No CVSG (`borne-out`):** Assigned ~1% to a CVSG, matching `signals.cvsg_date = null`.
4. **Separate writings (`borne-out`):** Treated no separate writing as modal (~70%) while hedging with a ~30% conditional chance of a separate writing respecting or dissenting from denial by Justice Thomas, Alito, or Gorsuch; the order issued with no separate writing (`noted_dissent_from_denial = false`).
5. **Conditional grant scope (`unresolved`):** Forecast a clean plenary grant on both questions if granted, which was left untested by the denial.

The document lands between the `0.50` (correct direction, brief/generic) and `0.75` (specific central claims mostly borne out) anchors at `0.68`: its concrete call of immediate resolution off the November 13 conference without a relist or CVSG held up cleanly, tempered by its terse bullet format, its 30% separate-writing hedge, and its inaccurate mootness-vehicle statement.

## Leakage Assessment

`claude-baseline` ran in `forward` mode on November 9, 2026 (`20261109T171058Z`), prior to the November 13 conference and November 16 denial. All 8 tool calls in `retrieval_log.json` were captured (`result_capture_coverage = 1.0`) and consisted exclusively of local file reads and pre-resolution corpus queries (`retrieved_doc_date <= 2026-10-16`), with no web or CourtListener queries (`retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`).
