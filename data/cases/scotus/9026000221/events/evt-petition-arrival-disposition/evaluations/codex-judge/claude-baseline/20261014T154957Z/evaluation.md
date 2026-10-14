# Evaluation: claude-baseline

## Blocking record mismatch

The event title and claude-baseline's prediction concern Nathan v. Alamo Heights Independent School District, Texas Ten Commandments classroom displays, and a Fifth Circuit en banc decision. The provisioned October 13, 2026 snapshot instead identifies Theodore James Purdy v. Kansas, No. 26-221, from the Kansas Court of Appeals, with a petition denial that day. The petition and questions-presented text independently identify Purdy and a Confrontation Clause issue; the documents manifest records an October 5, 2026 fetch.

claude-baseline describes a 314-page Nathan petition and an August 21 prediction-time snapshot. That original snapshot is not staged here. The current petition manifest says 140 pages. This is an incompatible record association, not grounds to conclude that the candidate fabricated its inputs. I cannot locate the cause or determine Nathan's outcome from the permitted record. A cell-level blocker flag requests repair and reevaluation.

## Mechanical scores only

The supplied outcome says `denied` and `actual_granted = 0`; claude-baseline says `granted` at 0.72. Thus `correct = 0` and Brier = `(0.72 - 0)^2 = 0.5184`. Those fields preserve the mandated comparison to the supplied JSON, but are not defensible matched-case performance measures until the identity conflict is resolved.

The frozen baseline band and `sal-v3` version leave the stamped segment base rate, basis, and skill to the harness. No replacement baseline is calculated or quoted. This is a cert cell: no vote accuracy, judgment accuracy, or semantic grades are scored. The structured quantitative claims and forecast document are not graded here.

## Reasoning assessment withheld

`reasoning_quality` is null rather than a punitive zero. The rationale distinguishes an arrival prior from later docket signals and discusses percolation, defensive denial, interlocutory posture, absent opposition, and dependence on petitioners' framing. It also makes strong generalizations about review rates in precedent-defiance cases and about effectively shared incentives to seek review without demonstrating a suitable empirical reference class. These observations concern the analysis itself, not its separate forecast or claim probabilities. A substantive numerical quality grade would nevertheless require a compatible record against which to assess the asserted facts and outcome. Purdy's denial supplies no evidence that Nathan's asserted certworthiness was mistaken. The optional case-significance grade is likewise withheld.

## Leakage

Both frozen context and log say forward. Capture coverage is 1.0. The Nathan lower-court query carries a retrieved-document date of April 21, 2026; the other query concerns companion Roake. The retrieval note describes those as metadata checks, and no logged query or reasoning passage supplies this petition's eventual disposition. The log contains digests, not complete returned texts, so the assessment does not claim independent access to every result. There is no affirmative evidence of a decided case being provisioned forward: retrieved outcome material is false, influence `not_applicable`, suspicion false. The separate identity blocker is not a leakage exclusion.
