# Evaluation of claude-baseline — scotus/73281388, evt-petition-disposition

**Outcome.** Cert stage. The petition (No. 25-1105, Thompson v. Wilson) was DENIED on
2026-10-05 after the 2026-09-28 long conference, with no noted dissent
(`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`,
`noted_dissent_from_denial: false`, `distribution_count: 2`).

**Scores.** `predicted_disposition: denied` matches, so `correct = 1`. P(grant) = 0.14,
Brier = (0.14 − 0)² = **0.0196**. Segment base rate: the prediction froze
`band: elevated` under `salience_version: sal-v4`, and the committed
`metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" carries the
same version in its heading, so the basis is `risk_set`. Pooling the bracketed
`reached` figure resolved-weighted over every rendered Term strictly before the case's
Term (OT2025) — OT2017 through OT2024, 484 / 2,810 — gives **0.1722**. The caption
renders 10 of 10 Terms, so the rendered window is the pack's whole window and no
window divergence needs flagging. Brier skill = 1 − 0.0196 / 0.1722² = **+0.339**:
the forecast beats the band baseline.

**What the prediction got right.** Everything on the disposition axis. It called a
plain denial on the October 5 order list following the long conference, which is
exactly what happened, and it put the right sign on the adjustment from the anchor.

**Reasoning quality: 0.88.** This is a careful, well-anchored rationale. It selects the
correct yardstick (reached elevated, strictly-prior Terms, version-checked against the
context), states the pooled number, and then makes its adjustments explicit in both
directions. Its single most important insight is that the frozen `distribution_count`
of 2 is a call-for-response redistribution, not a true relist, so the `elevated` band
overstates what the Court had actually signaled; it treats the response request as
real but weaker evidence than a post-conference relist, and that is what keeps the
number at or under the anchor rather than above it. The downward factors are
specific and checked against the briefs rather than asserted: the preservation
problem (the trespass-test framing as a cert-stage reframing of what the First
Circuit was asked), the thinness of the claimed split (each cited circuit case
described and distinguished on its own terms, with the BIO's account found accurate
against the petition's), the petitioner's concession that lobstering is closely
regulated, the maritime boarding tradition, and the state-respondent posture. The
upward factors (response request, repeat-player counsel, four amicus briefs,
originalist framing) are named and weighed rather than counted. The "where to
discount me" section is honest about not having read the First Circuit opinion or the
Richards decision and about the key judgment call on how informative a response
request is. What keeps it short of the top of the scale: the rationale did not read
the First Circuit opinion itself even though the preservation dispute turns on it and
the snapshot carried the link, and the write-up of the five minor claims is a
bit longer than its evidentiary basis warrants. These are small faults in a document
that otherwise models exactly the analysis the contract asks for.

**Leakage.** Forward cell (`context.mode: forward`, no cutoff), created 2026-09-17
against a petition that resolved 2026-10-05, so the case was genuinely open and the
`not_applicable` default applies. I confirmed rather than rubber-stamped it: the
captured log (`result_capture_coverage` 1.0) shows local reads, the statpack, two web
fetches of this docket's own July 20 reply and September 9 supplemental brief, one
CourtListener search for *Chatrie* with `retrieved_doc_date` 2026-06-29, and one
`fedcourts query` for recent granted priors. No call names this petition's
disposition, nothing is dated on or after the resolution, and there is no
`data/qp-topics/` read. The reasoning treats the petition as pending at the September
28 conference. `retrieved_outcome_material: false`, `influenced_prediction:
not_applicable`, `leakage_suspected: false`.

**Big case.** My own read, formed before consulting the candidate's score, is 0.40:
the doctrinal question could matter across closely regulated industries, but the
vehicle is a single state fisheries rule with a conceded closely-regulated status and
a contested preservation record, and the Court let it go silently at its first real
conference.

**Not scored here.** The claims block (`disposition`, `relist-increment`,
`cvsg-increment`, `summary-disposition-route`, `dissent-from-denial`) is scored in
code by the harness, and the forecast document `predicted_reasoning.md` was read for
context only. This is a cert cell, so no `vote_accuracy`, no `judgment_correct`, and
no `semantic_grades` are written; `record/opinion/` is absent, which is the ordinary
state of a denied petition.
