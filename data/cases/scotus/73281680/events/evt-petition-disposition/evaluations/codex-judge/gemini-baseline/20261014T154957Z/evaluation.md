# Evaluation: gemini-baseline

## Outcome and quantitative score

This is a cert-stage evaluation. The controlling `outcome.json` records denial
on October 13, 2026, with `actual_granted = 0`; the provisioned October 13
snapshot also contains that denial entry. gemini-baseline predicted `denied` with
grant probability 0.02. Thus `correct = 1` and the Brier score is
`(0.02 - 0)^2 = 0.0004`. A correct denial forecast does not establish that the
Court accepted the candidate's account of the jurisdictional issue.

The prediction freezes `context.band = baseline`, `salience_version = sal-v4`,
and Term 2025. The stamped segment base rate and its skill comparison belong
to the harness. I leave the baseline, basis, and skill fields absent and do
not independently pool or quote a replacement rate. Cert votes are not scored;
no semantic grading set applies. The forecast document was read for context
only; its procedural forecasts and the quantitative claims are not graded here.

## Reasoning quality: 0.64

The rationale identifies an intelligible cert-stage mechanism: it describes a
jurisdictional statutory dispute, distinguishes the appellate judgment from
the discretionary decision to grant review, and links the claimed lack of a
conflict and possible vehicle limitations to a low grant probability. It starts
from the appropriate kind of frozen-band, prior-Term risk-set anchor rather
than treating all petitions alike. It also candidly states that the opposition
text was unavailable and frames a possible government concession as uncertainty.

The principal weakness is overstatement relative to the evidence described.
Finding several circuits taking the same approach does not by itself establish
the categorical assertion that there is no circuit split. The rationale does
not explain the scope or continuing force of potentially contrary authority,
or distinguish an issue left open by precedent from one already resolved by it.
Its substantial downward adjustment rests heavily on a categorical pro-se
vehicle discount without petition text, a measured subgroup rate, or analysis
of preservation and the petition's actual presentation. Inferring the
government's position from the filing of an opposition is labeled as inference,
but cannot substitute for its contents. These limits reduce the soundness
score despite the very small realized Brier loss. The score evaluates the
analysis in `reasoning.md`, not the success of the separate forecast document.

## Leakage assessment

The harness log records forward mode and 34 calls on October 3, ten days before
resolution. It includes a live lookup of this petition's Supreme Court docket,
as well as searches for the underlying appellate decision and general
jurisdictional authorities. That live lookup is legitimate while this petition
is unresolved; an underlying appellate judgment is not the cert outcome.

All call results are marked `unobserved`, so capture coverage is 0.0. I assess
the queries and prose, not nonexistent captured results, and do not interpret
null document dates as proof that searches returned nothing. They contain no
indication that this petition's own disposition had surfaced as already decided.
Accordingly, `retrieved_outcome_material = false`, influence is
`not_applicable`, and `leakage_suspected = false`. This is a timing- and
record-based assessment, not a claim to have inspected the uncaptured bodies.
