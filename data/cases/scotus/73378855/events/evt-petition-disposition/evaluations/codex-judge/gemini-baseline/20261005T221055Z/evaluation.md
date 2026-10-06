# Evaluation: gemini-baseline

## Outcome and scores

This cert-stage event resolved as denied on October 5, 2026, with actual_granted = 0. The supplied outcome agrees with the "Petition DENIED" entry in the October 5 snapshot. gemini-baseline predicted denied with grant probability 0.01, so correct = 1 and Brier = (0.01 - 0)^2 = 0.0001. The correct label does not establish that the Court used the rationale offered in the prediction.

## Matched baseline

The prediction froze baseline under sal-v4 and Term 2025. The committed statpack heading matches that version. I use its bracketed reached rates on a risk_set basis, not terminal rates or a re-derived post-disposition band. The table shows 10 of 10 Terms, of which eight precede 2025: baseline reached percentages and weighted resolved denominators are 2024: 5.7%, 1271; 2023: 5.9%, 1312; 2022: 5.8%, 1192; 2021: 5.6%, 1500; 2020: 4.5%, 1739; 2019: 4.6%, 1399; 2018: 4.6%, 1524; 2017: 4.7%, 1643.

Pooling these displayed rounded percentages yields approximately 592.925 / 11580 = 0.05120250431778929. The numerator is not an integer grant count. Skill is 1 - 0.0001 / 0.05120250431778929^2 = 0.961856758794282. The candidate's approximate 5.1% anchor is consistent with this population. There is no omitted-pack-Term window discrepancy to flag. The estimates describe the committed denial-reweighted live/historical slice, not a freshly queried corpus; no current corpus vintage is asserted.

## Reasoning quality: 0.48

The short rationale identifies the correct salience population, the relevant strictly-prior Terms, and the petition's challenge to an unexplained appellate affirmance. It makes a coherent qualitative argument that this record is an unattractive vehicle and does not confuse a denial with an affirmance on the merits. Those are meaningful strengths, and brevity itself is not penalized.

However, almost the entire downward adjustment rests on a categorical assertion about the absence of a reasoned opinion. Calling review "nearly impossible" is insufficiently supported by the material the candidate discusses. The questions presented specifically ask whether unexplained affirmance satisfies due process; simply treating the absence of reasons as disqualifying bypasses that asserted procedural question. The rationale does not analyze the petition's competing position, identify a conflict or its absence from the arguments, or explain the evidence of review at the trial level.

The provisioned opposition includes the remittitur transcript, which records substantive discussion of the conduct and the damages ratio, and quotes TXO concerning an adequate hearing despite an unexplained trial ruling. Those materials offer a much more case-specific way to evaluate the petition's asserted absence of meaningful review. The candidate's rationale does not engage them, and its logged read queries show the questions presented and snapshot but no petition or opposition read. This is an evidentiary limitation, not a penalty for declining optional outside research. Listing precedents without explaining how they bear on the actual hearing or the appellate-explanation distinction does little to justify a reduction from approximately 5.1% to 1%. The correct result therefore receives full quantitative credit while the thin analytical support receives a substantially lower qualitative grade.

Only reasoning.md is graded for analytical quality. The forecast document was read for context, and neither it nor the structured quantitative claims is scored here.

## Leakage and scope

The harness records forward mode and 25 calls on September 17, well before the October 5 resolution. Result-capture coverage is 0.0: every result is unobserved. Null result dates and digests are therefore not evidence that queries returned nothing. Assessment rests on the queries and rationale: they identify ordinary local provisioned inputs, statpack context and output production, with no external query or request for this petition's outcome. The rationale treats the event as pending, and nothing in it presupposes the denial. The available record supports retrieved_outcome_material = false and the forward assessment not_applicable, with leakage_suspected = false; this is not a claim to have audited unseen result bodies. Zero capture coverage alone is not a defect to flag.

Vote accuracy and semantic grades are absent because this is cert-stage. Mechanical claim scoring and provenance/context stamps belong to the harness. No independent big-case assessment is supplied, and no durable flag is necessary.
