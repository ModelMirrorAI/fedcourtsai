# Evaluation: codex-baseline — Strulovitch v. Bain, 26A382 (evt-motion-disposition)

## The cell

Interim stage, forward mode. Application 26A382 for a stay of a New York
preliminary injunction was submitted to Justice Sotomayor on September 17,
2026; a response was requested September 23, Becket filed as amicus September
25, the response arrived September 28, and on September 29 Justice Sotomayor
denied the application in chambers, without prejudice to renewal once state
court remedies are exhausted. `outcome.json`: `actual_disposition` = `denied`,
`actual_granted` = 0, `disposition_basis` = `standard`, referral false, response
requested true, one amicus.

The candidate predicted **denied** at **0.38** on September 27, when the case
was genuinely open.

## Scores

- `correct` = 1: `denied` against `denied`.
- `brier_score` = (0.38 − 0)² = **0.1444**.
- `segment_base_rate`, `brier_skill_score`: not written. This is an interim
  cell, so both are the harness's: `stamp-cell` pools the substantive slice's
  grant rate over application-Terms strictly before 2026. From the committed
  statpack that pool is Terms 2024 and 2025 only (the earlier Terms are
  unparsed): 31 grants over 296 resolved, about 0.105, which clears the
  50-resolved floor, so I expect a non-null stamped rate. Against a 0.105
  baseline the naive Brier on a denial is about 0.011, so this candidate's
  0.144 will stamp as a negative skill despite the correct label: it moved
  well above the base rate on a case that resolved with the base rate. If the
  stamp comes back null, the section is present and above the floor, so the
  refusal would be something other than a thin pool.
- `base_rate_basis` null (structural on interim). No `vote_accuracy`, no
  `judgment_correct`, no `semantic_grades`: none applies off the merits
  stage. `claim_scores` is the harness's.
- The prediction's frozen `context.band` is null, so no cert-band flag.

## Reasoning quality: 0.78

A careful, well-structured rationale that identified the mechanism of the
actual denial.

Strengths:

- **Baseline done correctly and candidly.** 31/296 over Terms 2016–2025,
  matching the statpack (17/226 for 2025, 14/70 for 2024), with the coverage
  caveats stated: the ten-Term window is effectively a two-Term sample, Term
  2024 is mostly unparsed, and the escalation columns are not forward
  transition rates. It also correctly declines to use the pack-level rate,
  which contains the case's own Term.
- **It named the obstacle that decided the case.** "The likely obstacle to
  immediate relief is the still-pending state appellate process," and it
  expressly anticipated "a short denial or denial without prejudice that
  permits further state action." That is the order that issued, almost
  verbatim.
- **It handled the record as advocacy.** Statements about the injunction,
  the appellate motion, and Yeshiva/Skokie are attributed to the application
  rather than adopted; it noted the respondent's account was still to come
  and why it could matter; it recognized the two provisions are separable and
  that a partial order resolves as a denial under the contract.
- It verified the general stay standard against Hollingsworth v. Perry
  through CourtListener rather than from memory, and said what that
  retrieval did and did not establish.

Weaknesses:

- **The number does not follow from the analysis.** Every factor the
  candidate lists under "denial remains more likely" is strong, the upward
  factors are merits-only, and it concedes the 0.38 is "a judgmental
  adjustment... not a fitted estimate." A 3.6-fold lift over baseline for a
  private applicant seeking to stay a state interlocutory order, with the
  state appeal pending, is more than the stated reasons support. The score
  reflects sound identification of the issues with a weakly justified
  magnitude.
- **Yeshiva University is the closest precedent and it is not analyzed.** The
  candidate mentions the application's distinction of Yeshiva but treats it
  only as "arguments made in the provisioned filing." Two searches for the
  opinion returned nothing and it left the analogue unexamined rather than
  reasoning from what it knew of the case. That precedent is the direct
  authority for the denial-without-prejudice shape it correctly predicted, so
  the mechanism was right but under-supported.
- The response-request and referral increments (0.82, 0.72) were formed
  without checking the live docket, which forward mode permitted. That is a
  legitimate choice and not penalized here; it is noted because the
  candidate's forecast of a full-Court disposition missed the in-chambers
  path that actually occurred.

## Leakage

Forward, genuinely open (prediction September 27, denial September 29). The
log carries 34 calls, `result_capture_coverage` 0.94. Calls: prompt, schema,
and provisioned-input reads; statpack reads and a `jq` pool over the interim
table; two web searches (unobserved, so graded on their queries) for general
stay precedent naming Hollingsworth and Skokie and no party or docket;
CourtListener searches for Hollingsworth v. Perry (`558 U.S. 183`, a passage
read at page 190) and two Yeshiva searches returning nothing; source-code
reads; the output writes. The candidate states it did not retrieve this
application's live docket, subsequent history, or outcome, and nothing in the
log contradicts that. One early shell call includes a `find` that names
`data/qp-topics/` only as a `-not -path` exclusion pattern; that is the
opposite of a read, and that directory encodes cert membership, which is
irrelevant to an interim event. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read is 0.3: a real church-autonomy question in a private nursing-home
dispute, disposed of in chambers without referral or separate writing, with
the door left open. Disclosure: the predictor's `big_case_score` (0.56) sits
inside the staged `prediction.json`, which I read in full before forming this
read, so I cannot claim it was formed strictly blind to theirs. It was formed
from the record and outcome.
