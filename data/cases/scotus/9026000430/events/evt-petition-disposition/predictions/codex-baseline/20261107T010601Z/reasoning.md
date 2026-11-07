# Rationale

## Target and information state

I predict denial, with **P(any grant) = 0.18**, for No. 26-430 itself, not for the related petitions challenging HISA's enforcement structure. This is a cert-stage distribution cell. I read the case-level snapshot `record/snapshots/2026-11-07.json`, the event definition, `context.json`, the questions presented, petition, opposition, reply, document manifest, and relevant portions of the appendix. The snapshot records **one distribution**, entered November 4 for the **December 4, 2026 conference**, no relist, and no CVSG. It records three amicus briefs: Repole Stable on October 22, and the racetrack veterinarians and Scott Dilworth on October 30. The null amicus count in context is not treated as zero.

The caption is private: the National Horsemen's association and its affiliates are not sovereign petitioners. Texas's intervention in the underlying litigation does not make this caption a state petition. I retain the harness's `baseline` band and `sal-v7` version rather than replacing them with a band inferred from subject-matter importance.

## Anchor and calibration

The frozen `context.cert_anchor.rate` is **0.051512996760685784**, approximately **5.15%**, using its specified ten-Term lookback. This is the operative baseline-band risk-set anchor. The matching sal-v7 table in `metrics/statpack.md` shows the relevant strictly-prior rows, 2017–2025; the 2026 row is not an anchor. I use the frozen exact figure rather than reconstructing it from rounded displayed percentages. The broad modern-cert disposition table is much lower, about 2.8% for granted plus GVR, and is not a substitute for this selected population.

The paid-segment signal cuts provide context, not independent factors to multiply:

- Terminal relist 0: resolved n=10,204, granted 1.3% plus GVR 0.5%; relist 1: n=2,532, 8.3% plus 5.2%; relist 2: n=495, 28.3% plus 12.9%; relist 3+: n=482, 23.0% plus 14.1%. These are terminal buckets, not the hazard of another distribution from today's count of one.
- No CVSG: n=13,549, 4.1% granted plus 2.3% GVR; CVSG: n=164, 29.3% plus 5.5%. This petition is in the former observed state, and the latter figure is not its anchor.
- Three docketed amici place it in the 2+ group: **resolved n=1,446**, 18.2% granted plus 4.5% GVR. There is no displayed unknown-count bucket in this table. This terminal, marginal cut suggests genuine salience, but does not measure an increment over the related-litigation signals and may contain support arriving later than this cell's moment.
- The broader originating-circuit cut for CA5, n=5,456 resolved, is 1.5% granted plus 2.2% GVR. Its mixed population makes it a weaker comparator than the frozen anchor.

## Why above the anchor, but still denial

The petition's own QP is labeled Question Presented #2: whether private rules may enter force when the supervising agency cannot contemporaneously revise or reject them. Its footnote supports review of a different, executive-enforcement question in the Authority's and FTC's petitions. **Agreement that those lead petitions deserve review does not establish agreement that this cross-petition does.** (Questions-presented text; petition pp. 1, 3–8.)

There are substantial reasons to move above 5.15%. The Fifth Circuit again invalidated the enforcement provisions after a prior Supreme Court remand, and the same federal-supervision provision, 15 U.S.C. § 3053(e), bears on both enforcement and rulemaking. The reply makes the strongest grant argument: resolving the entire supervisory relationship together could avoid artificially separating intertwined powers. Three amici reinforce that the dispute matters to the regulated industry. (Appendix pp. 2a–5a; petition pp. 5–7; reply pp. 7–8.)

The strongest negative is **the lack of a rulemaking split**. The Fifth Circuit opinion reproduced in this petition's appendix is the June 11, 2026 judgment identified in the snapshot, not merely the vacated 2024 opinion. It agrees with the Sixth Circuit that the amendment cured the rulemaking defect while disagreeing on enforcement. The Authority's BIO identifies agreement among the Fifth, Sixth, and Eighth Circuits on the amended rulemaking arrangement. The reply presses novelty and interdependence, not an opposing rulemaking holding. (Appendix pp. 10a–15a; BIO pp. 12–15; reply pp. 1–8.)

The parties also dispute the QP's premise. Petitioners say consistency review is mandatory and independent policy revision can occur only afterward. Respondents point to the FTC's independent rulemaking, control of proposal publication, and ability to postpone effective dates. The appendix itself discusses those safeguards. That statutory dispute weakens the claim that a clean constitutional timing question must be added to an already substantial enforcement controversy. (Petition pp. 8–13; BIO pp. 22–25; reply pp. 2–6; appendix pp. 11a–15a.) I do not resolve that merits dispute to forecast certiorari.

Consumers' Research is pre-prediction legal context, not this event's outcome. The provisioned papers explain both its supervisory-control framework and the earlier GVR in this litigation. The targeted corpus lookup confirms the FCC precedent's separate docket and 2025 merits judgment, but supplies no opinion body. The broader granted-priors query returned two substantive applications and a cert grant; those are not matched cross-petition comparators and receive no quantitative weight. No additional outcome frequency is estimated from this handful.

My 18% judgment represents a real possibility of companion review, tempered by the ability to grant the enforcement petitions without enlarging review to a question the circuits answer uniformly. The key uncertainty is the Court's appetite for that enlargement, not whether the industry dispute is important. A denial here would not imply that the enforcement petitions also lose.

## Other forecasts and significance

I put further distribution at **45%**: coordination with related petitions makes delay materially more plausible than for a routine baseline case, but no relist is observed yet. The modal path is no further distribution; conditional on further distribution, one or two additional entries are more plausible than a long series. I put a new CVSG at **1%**, because federal respondents already participated and their memorandum is docketed; this is not a claim about what their unavailable memorandum recommends.

Conditional on a grant, **20%** goes to a cert-order disposition, chiefly a later GVR tied to a companion decision; **80%** goes to plenary review. The Fifth Circuit has already reconsidered Consumers' Research, so a mechanical repeat GVR under that same existing precedent is not the main route. Conditional on denial, a dissent or statement has probability **3.5%**. The unconditional per-Justice writing probabilities are separately reported and allow overlap; they are not votes or a probability distribution that must sum to one.

The significance score is **0.70**, independent of grant probability: industry-wide safety and anti-doping regulation and the permissible role of private regulators have substantial stakes, with possible implications for analogous regulatory frameworks. The specific rulemaking-timing question is narrower than the whole delegation controversy.

## Limits and integrity

`documents.json` reports nonempty petition, opposition, and reply texts, and a truncated appendix. The relevant Fifth Circuit rulemaking discussion is available; later appendix materials are not assumed complete. The BIO file contains the Authority's brief, not the separately docketed October 13 federal memorandum. I did not infer that memorandum's recommendation. Attempts to retrieve it and independent official precedent through the web tool produced no usable content. This limited input gap is recorded in `flags.json`.

`same-question.json` contains no matches; its November 8 metadata cutoff is later than this snapshot, so it supplies no affirmative signal and I make no timing inference from it. The filed documents themselves establish the related-petition posture; no companion docket was independently inspected. I neither sought nor encountered this petition's disposition, subsequent history, another cell's forecast, or an evaluator outcome. The 2024 stay and 2025 GVR in the appendix are earlier procedural history, not the disposition being forecast.
