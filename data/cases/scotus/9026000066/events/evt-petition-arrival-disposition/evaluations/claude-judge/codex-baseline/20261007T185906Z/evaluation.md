# Evaluation — codex-baseline — scotus/9026000066, evt-petition-arrival-disposition

**Cell.** Cert stage, arrival moment, forward mode. The petition (pro se, from an
unpublished Arizona Court of Appeals memorandum affirming a divorce decree) was
distributed once, for the September 28, 2026 conference, and **denied** on
October 5, 2026 with no noted dissent. `actual_granted` = 0.

**Scores.**

| field | value | note |
| --- | --- | --- |
| `correct` | 1 | predicted `denied`, outcome `denied` |
| `brier_score` | 0.000009 | (0.003 − 0)² |
| `segment_base_rate` | omitted | salience-version mismatch, below |
| `brier_skill_score` | omitted | follows the rate |
| `base_rate_basis` | null | same |
| `reasoning_quality` | 0.85 | |

**Why the base rate is omitted.** The prediction froze `context.band` =
`baseline` under `context.salience_version` = `sal-v3`. The committed
`metrics/statpack.md` renders exactly one "Segment base rate by salience band"
table and its heading names `sal-v4`; no `sal-v3` table is rendered. The table
is therefore no baseline for this candidate's band, and the contract's only
answer is to omit rate, skill, and basis together. Recorded in this cell's
`flags.json`; the same applies to all three candidates.

**What the prediction got right.** The disposition and the path: one
distribution, denial without a further relist, no CVSG, no noted dissent or
statement. The anchor is stated with its counts (863 grant-family outcomes
among 13,163 weighted resolved paid petitions, 6.56%, pooled over the Terms
strictly before OT2026) and the rationale explains why the risk-set figure,
not the terminal relist-zero cut, is the right population at arrival. The
legal analysis is the strongest of the three on the petition's one doctrinal
hook: it reads the first question against *Lee v. Kemna* itself, observes that
the petition offers no evidence Arizona applies its briefing rule
inconsistently (the "strictly or regularly followed" prong the question
depends on), and notes that *Michigan v. Long* does not cure an adequacy
problem where the state court expressly relied on waiver and record
presumptions. It correctly characterises the second and third questions as
record-dependent error correction. It is explicit about the limit of its
vehicle assessment: no brief in opposition or lower-court opinion text was
provisioned, so the read depends on the petition's own description of the
record.

**What drove `reasoning_quality` = 0.85.** A disciplined, well-sourced
rationale whose adjustments are tied to doctrine and to the provisioned
documents, with an honest statement of what it could not see. Two small
deductions. The outside research it leans on is a general characterisation of
*Lee v. Kemna* rather than anything that moved the estimate, so the
"reinforces the narrowness" sentence does slightly more rhetorical than
analytical work. And the rationale spends proportionally more of its length
on the conditional claims (relist-increment, summary route) than on
justifying the specific headline number, so a reader can see that 0.003 sits
far below the segment anchor but not why 0.003 rather than 0.001 or 0.01.
Neither affects the conclusion.

**Leakage.** Mode `forward`; the event was unresolved when the cell ran
(2026-08-16). All 22 logged calls are captured (coverage 1.0): reads of
`AGENTS.md`, the prompt, the schemas, the provisioned inputs and the statpack,
two `validate` runs, and two `other` calls whose text is a harness
`[redacted:fernet-token]` marker (removed text, not evidence of anything).
`retrieval.md` discloses three CourtListener MCP opinion searches, on
adequate-and-independent-state-ground doctrine and on *Lee v. Kemna*. Those
calls do not appear in the captured log at all; I have noted that capture gap
in `flags.json`. The disclosed queries are doctrinal, none names this case,
and the candidate states that no search sought this case's disposition or
subsequent history, which is consistent with a rationale that reads nothing
post-dating the petition. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

**Big case.** My independent read, formed before looking at the candidate's
score: 0.02. A private dissolution dispute with no reach beyond the parties.
The candidate's 0.12 is the highest of the three and, in my read, overweights
the general importance of the due-process principles invoked relative to this
record's capacity to carry them; the rationale itself concedes the case is
unlikely to have broad significance.

**Not graded here.** The `claims` block and `predicted_reasoning.md` are
outside this evaluation; the harness scores the claims in code. No
`semantic_grades` block: a cert cell declares no semantic set.
