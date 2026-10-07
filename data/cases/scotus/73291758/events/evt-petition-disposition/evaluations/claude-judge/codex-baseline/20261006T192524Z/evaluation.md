# Evaluation: codex-baseline — scotus/73291758, evt-petition-disposition

Cert-stage cell (event stage `cert`, moment `distribution`). Outcome: petition
**denied** 2026-10-05 after a single distribution for the 2026-09-28 long
conference, `actual_granted` 0, no noted dissent, no response ever requested.

## Quantitative

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.006 − 0)² = 0.000036.
- `segment_base_rate` = 0.0512 (`base_rate_basis` `risk_set`). Frozen
  `band: baseline`, `salience_version: sal-v4`; the statpack's segment table
  heading is "(sal-v4)", so the versions match. Pooled the bracketed `reached`
  figure weighted by `n` over OT2017–OT2024, every rendered Term strictly before
  Term 2025 (caption: 10 of 10 Terms rendered, no window divergence):
  593 / 11,580 = 0.05120; the unrounded JSON agrees at 0.05121 — which is the
  figure this candidate itself computed and reported.
- `brier_skill_score` = 1 − 0.000036 / 0.0512² = 0.9863.
- `vote_accuracy` omitted (cert cell).

## Reasoning quality: 0.82

A sound, well-bounded rationale. It states its information boundary precisely,
treats the petition's narrative as the petitioners' assertions rather than
findings, computes the anchor exactly (and from the unrounded pack, with the
per-Term denominators listed), and explicitly declines to substitute the
terminal relist-0 or terminal-band rates for the risk-set anchor — the error
gemini-baseline makes. The docket reading is correct: one distribution, no
response, no request for one, no amici, no CVSG.

On the law it identifies preservation as the strongest negative and treats it
as a vehicle risk rather than a holding, which is the honest framing given the
appellate order was not provisioned. The Rahimi discussion is accurate and
usefully limited: it notes what Rahimi did and did not decide and why it does
not supply a GVR hook (it predates the September 2025 appellate decision). The
fact-bound, diffuse character of the four questions and the single cited
authority are read correctly against Rule 10.

Deductions, modest: the rationale is more hedged than the record requires —
the petition's conceded forfeiture, in a state civil case, is a classic
adequate-and-independent ground and could have been stated with more force
(claude-baseline does); the civil-case ineffective-assistance point is left
implicit; and the mootness aside, while fair, is not developed into anything
that bears on the number. The treatment of the "constitutional interests" as
"real" reads slightly generous for a record this thin, but the rationale does
not let it move the probability much.

## Leakage

Forward cell; `influenced_prediction` `not_applicable`, `retrieved_outcome_material`
false, `leakage_suspected` false. Log coverage 0.906, 32 calls. Three web-search
rows are unobserved and graded on their queries: a Rule 10 phrase search and
two opens of the Court's rules-guidance page, none naming this case. Captured
external calls are an opinion search for United States v. Rahimi (bounded to
pre-2025 filings), a snippet search inside that opinion, and shell fetches of
the 2023 Rules of the Court PDF. No query touches docket 25-1245, the caption,
an order list, or any date after 2026-09-16. The candidate's `retrieval.md`
discloses the same set of lookups and states that no outcome material was
sought or encountered, which the log bears out.

## Big case

My independent read is 0.03 (see `big_case.notes`): a private family
protective-order dispute with no institutional party, no split, and forfeited
federal claims; the silent denial is consistent with that. (The candidate's
own stakes score is markedly higher; that disagreement is left to the
rank-agreement grading at leaderboard time and did not enter
`reasoning_quality`.)
