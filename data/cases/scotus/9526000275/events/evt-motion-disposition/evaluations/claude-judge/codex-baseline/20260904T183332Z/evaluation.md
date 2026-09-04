# Evaluation of codex-baseline — scotus/9526000275, evt-motion-disposition

**Cell shape.** This is an **interim** cell (`event.yaml` `stage: interim`): an
emergency application for an injunction pending appeal, submitted to Justice
Kavanaugh 2026-08-31 and denied by the Circuit Justice 2026-09-03
(`actual_disposition: denied`, `actual_granted: 0`; signals: response
requested, not referred, zero amici at the order). Per the interim rules the
baseline and skill are the harness's: `stamp-cell` pools the statpack's
substantive-application grant rate over application-Terms strictly before
OT2026 and writes `segment_base_rate` and `brier_skill_score` itself. I write
neither and leave `base_rate_basis` null. For the reader: the committed pack's
strictly-prior rows are OT2025 (226 resolved / 17 granted) and OT2024 (70 / 14),
a pool of 296 that clears the registered floor of 50, so a non-null stamp is
expected; the harness's number governs. `claim_scores` is likewise the
harness's (`interim-v1`), no semantic set is declared on this stage so no
`semantic_grades` block is written, and `vote_accuracy` is omitted.

**Outcome match.** Predicted `denied` at P(grant) = 0.13; actual `denied`.
`correct = 1`, `brier_score = (0.13 - 0)^2 = 0.0169`. Both are my elicited
reads; the stamp recomputes them. Note for the skill reader: 0.13 sits *above*
the ~10.5% pooled baseline, so on a denial this forecast's Brier is worse than
the naive baseline's — a fact about the number, which the stamped skill will
carry; it is not what `reasoning_quality` grades.

**What the rationale got right.** This is the only candidate that read the
application itself (the 43-page PDF linked from the snapshot), and it shows:
the facts it relies on — the three-signature shortfall after the Board accepted
some affidavits and rejected nine others, the 2-2 deadlock, the September 4
settlement date — are exactly what the application pleads (I checked them
against the provisioned `record/documents/application.txt`, which was not
available to the predictors). Its institutional analysis is sound and is the
core of why the application failed: mandatory relief placing an initiative on
the ballot before *any* lower-court judgment, on a one-sided record built from
the applicants' presentation alone, days before ballot finalization. It
correctly pooled the strictly-prior Terms (31/296) and stated the pool's two
caveats (uneven parsing, a scored population selected higher on the ladder).

**Where it is weaker.** (1) The rationale pulls in two directions and does not
reconcile them. One paragraph "raises the estimate modestly above the pooled
baseline" because the injury is concrete and time-sensitive and the theory is
focused; the next says those same features are outweighed by the vehicle and
institutional problems. Salience, irreparable harm, and a focused theory are
good reasons to expect *escalation* (a response call, referral) — and the
candidate uses them for that too — but they are not reasons to raise
P(grant) above a pool that already includes far stronger applications. The
net upward move is the analytical error that produced the least calibrated
number of the three. (2) It never names the standard the application had to
meet — an injunction pending appeal requires an indisputably clear entitlement,
a materially higher bar than a stay — nor the Purcell timing concern, which
are the two doctrinal reasons a denial here was nearly certain rather than
merely likely. (3) The referral forecast (0.78) ran against the single-Justice
denial; the reasoning for it was reasonable and the increment itself is the
harness's to score.

**`reasoning_quality` = 0.70.** Best factual grounding of the three and a
correct institutional account, docked for the unreconciled upward adjustment
and for omitting the governing standard.

**Leakage.** Mode `forward`, `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, `leakage_suspected = false`. All ten
logged calls are timestamped 2026-09-01T02:52Z, two days before the denial;
coverage 0.6. The captured rows are reads of the committed statpack; two rows
are harness-redacted credential-shaped runs (`[redacted:fernet-token]`), which
read as removed text and not as outcome material. The three CourtListener
opinion searches and the application-PDF fetch the candidate describes in its
`retrieval.md` are **not in the log** — a capture gap on this engine's
telemetry, recorded in this cell's `flags.json` as information, and no mark
against the candidate. By its own account those calls returned no
case-specific opinion and the application filed 2026-08-31, which predates the
event. Nothing retrieved or written is a disposition of this application, and
the case was genuinely open when the cell ran.

**Big case.** My independent read is 0.4 (see `evaluation.json`). Caveat on
independence: the staged `prediction.json` carries the predictor's
`big_case_score` beside the fields I had to read first, so I saw it before
forming my own; my read is drawn from the record, not from that number.

**Retrieval.** None beyond the provisioned inputs and the committed statpack;
see `../../20260904T183332Z/retrieval.md`.
