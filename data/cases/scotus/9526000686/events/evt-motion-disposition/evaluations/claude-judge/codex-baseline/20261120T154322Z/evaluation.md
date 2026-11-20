# Evaluation: codex-baseline, scotus/9526000686, evt-motion-disposition

**Outcome:** the application for a stay of execution was referred to the Court and denied on 2026-11-19, with certiorari denied in the same order (`interim_reading` `denied`, `interim_granted` 0).

**Scores:** predicted `denied` at P(granted) = 0.03, so `correct` = 1 and `brier_score` = 0.0009.

This is an interim cell. The baseline (`segment_base_rate`) and the skill derived from it are the harness's to stamp, so I left them and `base_rate_basis` null. I cannot see the stamp from here; the pool the candidate quotes (1,337 resolved over the ten prior Terms) is well above the registered floor, so I would not expect it to come back null. No `vote_accuracy` and no semantic grades apply on this stage.

## Reasoning (`reasoning_quality` 0.65)

The base-rate work is careful and correct: the 156/1337 anchor and the private x capital cell (10/288) match the committed statpack, and the document explains why it weighs the joint cell over either margin. The legal analysis is fair. It identifies irreparable harm as the applicant's only strong factor, notes that the application develops no conflict and does not separate federal defects from a state separation-of-powers dispute, and reads the *Woodard* concurrence accurately as a modest downward adjustment.

Two things cost it. First, it adds almost no case-specific adjustment below the cell (3.47% to 3%) while describing an application it found weak on every factor but harm; it retrieved nothing on how warrant-stage Florida applications actually fare. Second, the procedural read was wrong on the one rung that was open to judgment: it put 80% on a formal call for a response on the reasoning that "a prompt answer [is] useful", when in capital warrant practice the State files unprompted, which is what happened. The 12% amicus figure is also high for a five-day window. The document is candid about what it did not have.

## Predicted reasoning (`predicted_reasoning_quality` 0.60)

I treated as central the denial, the two procedural forecasts the document leads with (response call and referral), the amicus and timing forecast, and the no-writing forecast. The denial, the referral, zero amicus, the Nov 16-19 window and the absence of a writing all held. The response call did not: no request was docketed, and the document itself notes that an uninvited response would not count. That was a specific claim given weight at 80%, so it is more than a margin. The document does not forecast the linked cert petition's fate, and its doctrinal paragraph is conditional on an explanation the Court did not give. Right on the disposition, split on the procedural path.

## Leakage

Forward cell, run 2026-11-15, resolved 2026-11-19. Two web searches have unobserved results; graded on their queries, both target *Woodard*, not this docket. Nothing reaches this case's disposition. `not_applicable`.

## Stakes

My own read is 0.18: a routine warrant-stage capital stay application with no broader doctrinal reach.
