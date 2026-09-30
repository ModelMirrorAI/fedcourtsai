# Evaluation: claude-baseline — Strulovitch v. Bain, 26A382 (evt-motion-disposition)

## The cell

Interim stage, forward mode. Application 26A382 for a stay of a New York
preliminary injunction was submitted to Justice Sotomayor on September 17,
2026; a response was requested September 23, Becket filed as amicus September
25, the response arrived September 28, and on September 29 Justice Sotomayor
denied the application in chambers, without prejudice to renewal once state
court remedies are exhausted. `outcome.json`: `actual_disposition` = `denied`,
`actual_granted` = 0, `disposition_basis` = `standard`, referral false, response
requested true, one amicus.

The candidate predicted **denied** at **0.17** on September 27, when the case
was genuinely open.

## Scores

- `correct` = 1: `denied` against `denied`.
- `brier_score` = (0.17 − 0)² = **0.0289**.
- `segment_base_rate`, `brier_skill_score`: not written. This is an interim
  cell, so both are the harness's: `stamp-cell` pools the substantive slice's
  grant rate over application-Terms strictly before 2026. From the committed
  statpack that pool is Terms 2024 and 2025 only (the earlier Terms are
  unparsed): 31 grants over 296 resolved, about 0.105, which clears the
  50-resolved floor, so I expect a non-null stamped rate. Against a 0.105
  baseline the naive Brier on a denial is about 0.011, so even this
  candidate's 0.029 will stamp as a negative skill: on a case that resolved
  the base-rate way, any move above the base rate loses to it. That is a
  property of a single denied cell, not evidence against the analysis. If the
  stamp comes back null, the section is present and above the floor, so the
  refusal would be something other than a thin pool.
- `base_rate_basis` null (structural on interim). No `vote_accuracy`, no
  `judgment_correct`, no `semantic_grades`: none applies off the merits
  stage. `claim_scores` is the harness's.
- The prediction's frozen `context.band` is null, so no cert-band flag.

## Reasoning quality: 0.82

The most complete analysis of the three, and the one whose number is best
supported by its own reasoning.

Strengths:

- **Baseline correct, with the right caveat.** 31/296 over 2016–2025,
  matching the statpack, and the observation that the pooled population is
  mostly pro se and IFP stay requests while the scored cohort sits higher on
  the escalation ladder, which the pack itself warns about.
- **It engaged the controlling analogue directly.** Yeshiva University v. YU
  Pride Alliance (2022) is described accurately: a 5-4 denial of a stay of a
  New York trial-court order because state avenues for interim relief were
  untried, with leave to return. That is the template the September 29 order
  followed. The candidate weighed this case's exhaustion posture against it
  and judged it "closer to the condition that majority named." That
  inference cut the wrong way, since the Court still treated state remedies
  as unexhausted, but it was posed as the live question, weighed against
  strong downward factors, and priced with a stated range of 0.10 to 0.30.
- **The downward factors are the right ones.** Interlocutory state
  preliminary injunction with the state appeal pending; the § 1257 finality
  problem; the Court's reluctance to use the All Writs Act against state
  courts, noting that the application's own Malliotakis cite is to a
  concurrence on a denial; a partial order resolving as denial; mootness if
  the Appellate Division rules; private commercial dispute with no government
  party. It also carved out "an in-chambers denial by Justice Sotomayor" as a
  residual on the referral claim, which is what happened.
- **Forward retrieval used properly and disclosed.** It fetched the live
  docket page on September 27, saw the response request and Becket amicus,
  stated that two of its increment claims therefore measure no forecasting
  skill, and said so in three places. It also caught a web-search summary
  that fabricated a grant dated before the application was filed, checked it
  against the authoritative docket page, disregarded it, and disclosed it.
  That is exactly the discipline the contract asks for.

Weaknesses:

- The exhaustion read, as noted, was the one substantive judgment that went
  the wrong direction. The candidate treated a fully briefed but undecided
  state stay motion as near-enough to a denial of state relief; the Court did
  not.
- The referral premise, that a Circuit Justice who calls for a response on a
  counseled First Amendment application "nearly always" refers, was too
  strong for this case, and the predicted full-Court one-line denial was the
  wrong shape. This is noted for context; the forecast document is not
  scored.
- Two soft heuristics carry weight they have not earned: that repeat-player
  counsel "do not bring hopeless applications," and that a response request
  is "the interim analogue of a CVSG." Neither is wrong exactly, but neither
  is argued.

## Leakage

Forward, genuinely open (prediction September 27, denial September 29). The
log carries 25 calls, `result_capture_coverage` 1.0, `throttled_calls` 0.
Calls: prompt, schema, and provisioned-input reads; a sibling `event.yaml`;
the statpack interim section; two corpus queries for granted and denied
applications (other dockets, with `ranged corpus reads` lines recorded in
`retrieval.md`); a `corpus-info` that raised; a CourtListener docket search
for 26A382 returning zero results; a web-fetch of the Supreme Court's 26A382
docket page as of September 27 showing no disposition (legitimate forward
signal, not leakage); a web search on the parties whose generated summary
asserted a grant dated 2026-08-24, which predates the filing and contradicts
the real outcome, and which the candidate disregarded; one listing and read
of its own prior prediction on a different docket, evidently for format
(another case's artifact, not this event's outcome). Nothing postdates the
resolution and nothing reveals this case's disposition.
`retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false. The candidate's disclosures in
its prose are a point for the cell's integrity.

## Big case

My own read is 0.3: a real church-autonomy question in a private nursing-home
dispute, disposed of in chambers without referral or separate writing, with
the door left open. Disclosure: the predictor's `big_case_score` (0.42) sits
inside the staged `prediction.json`, which I read in full before forming this
read, so I cannot claim it was formed strictly blind to theirs. It was formed
from the record and outcome.
