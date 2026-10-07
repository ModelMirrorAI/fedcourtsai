# Evaluation — claude-baseline — scotus/9026000066, evt-petition-arrival-disposition

**Cell.** Cert stage, arrival moment, forward mode. The petition (pro se, from an
unpublished Arizona Court of Appeals memorandum affirming a divorce decree) was
distributed once, for the September 28, 2026 conference, and **denied** on
October 5, 2026 with no noted dissent. `actual_granted` = 0.

**Scores.**

| field | value | note |
| --- | --- | --- |
| `correct` | 1 | predicted `denied`, outcome `denied` |
| `brier_score` | 0.000025 | (0.005 − 0)² |
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

**What the prediction got right.** The disposition, and the path to it: one
distribution, a denial at the first conference, no relist, no CVSG, no
separate writing. That is what happened. The rationale states its anchor
precisely (the `sal-v3` baseline band's bracketed `reached` rate pooled over
OT2017–OT2025, n = 13,163 weighted, about 6.5%), explains why the arrival
moment takes the risk-set figure rather than the relist-zero terminal cut, and
then lists concrete downward adjustments each tied to something in the
provisioned record: the attorney block showing the petitioner as his own
non-counsel-of-record, the unpublished memorandum decision, the Arizona
Supreme Court's denial of review, the absence of any alleged conflict despite
the *Lee v. Kemna* / *Michigan v. Long* framing, and the petition's own
account of missing transcripts as a vehicle problem. It also names the
terminal baseline-band grant-family rate (about 1.2%) as an upper bound on the
realistic pool and places the petition below it, which is how a reader can
check the size of the adjustment.

**What drove `reasoning_quality` = 0.85.** This is a complete, checkable
rationale. The calibration logic is explicit at every step, the uncertainty
section correctly locates the residual risk in the tail (dismissal or
withdrawal before conference) rather than in the disposition, and it is candid
that the corpus query returned nothing useful. Two small deductions. The claim
that "the statpack's state-court originating rows show sub-1% grant rates" is
loosely sourced: the originating-court table has no state-court row as such,
and the nearest proxy, the `(none)` row, shows granted 0.5% and GVR 0.8%, so
the figure is right in spirit but the row is not what the prose says. And the
rationale does not test the first question's "not strictly or regularly
followed" prong against the petition's content, which codex-baseline did and
which is the sharpest doctrinal point available on this record. Neither
affects the conclusion.

**Leakage.** Mode `forward`; the event was unresolved when the cell ran
(2026-08-16). All 22 calls are captured (coverage 1.0). The only
outward-looking calls are two `fedcourts query` runs for recent 2020s SCOTUS
denials; the one legible `retrieved_doc_date` is 2026-08-09, on an unrelated
row and before this event's resolution. No query named this docket or caption,
no MCP or web call. `retrieval.md` discloses the same query and nothing else.
`retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false.

**Big case.** My independent read, formed before looking at the candidate's
score: 0.02. A private dissolution dispute with no reach beyond the parties.
The candidate's 0.02 matches.

**Not graded here.** The `claims` block and `predicted_reasoning.md` are
outside this evaluation; the harness scores the claims in code. No
`semantic_grades` block: a cert cell declares no semantic set.
