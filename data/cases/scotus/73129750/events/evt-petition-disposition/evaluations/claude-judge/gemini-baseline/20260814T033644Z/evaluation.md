# Evaluation: gemini-baseline — evt-petition-disposition (scotus/73129750)

## Outcome and scores

Cert-stage cell (kind `petition`, no recorded stage). Realized outcome:
`granted` (certiorari before judgment granted 2025-12-05, `actual_granted` = 1).
The candidate predicted `granted` at p = 0.99, so `correct` = 1 and
`brier_score` = (0.99 − 1)² = 0.0001. No votes were predicted and the outcome
records none, so `vote_accuracy` is null.

**Base rate.** The prediction carries no frozen `context` block (an older-shape
record; this one also omits `confidence`), so per the fallback rule I derived
the band now and used the table's *leading* (terminal) figure, recording
`base_rate_basis` = `terminal`. The terminal band is `federal` (sal-v2).
Pooling the leading figures resolved-weighted over Terms strictly before 2025
(2017–2024; the caption renders 9 of 9 Terms, so the rendered window is the
full pack and matches the configured 10-Term lookback — no window divergence to
flag) gives ≈ **0.7063**. `brier_skill_score` = 1 − 0.0001/(1 − 0.7063)² ≈
**0.9988** — read under the leakage grading: the cell's outcome was in its
provisioned input.

## Leakage

The cell ran `forward` per its retrieval log, but the event resolved
2025-12-05, seven months before the 2026-07-14 run — a decided case was
provisioned forward. The candidate acknowledges the snapshot contained the
outcome entries and says it filed a flag (predictor flags are not staged, so
this reaches me only through its prose). Its staged retrieval log is heavily
degraded — nearly every call row carries a null query, digest, and (for most)
timestamp, with only tool classes surviving — so the retrieval grading leans on
the prose and its `retrieval.md`, which discloses three CourtListener MCP
searches: this case's own SCOTUS docket (25-365) and caption, both returning 0
results, and the First Circuit companion docket 25-1861, returning the docket
identity. Querying the case's own docket after decision could have reached
outcome material, but the empty results mean nothing additional arrived that
way; the outcome came from the provisioned snapshot regardless.
`influenced_prediction` is `likely`: the candidate admits knowing the outcome,
and its 0.99 with "certain to grant" language is hard to credit as a blind
estimate, notwithstanding its claim that the number rests purely on the
pre-decision record.

## Reasoning quality: 0.55

Directionally sound but materially the weakest of the three. Credits: it
identifies the correct grant drivers (SG petitioner defending a major enjoined
executive order, a request to revisit a landmark precedent, exceptional
national importance, heavy amicus attention), engages the BIO's Wong Kim Ark
argument, anchors on the statpack (~3%), and discloses the leakage. Debits:
factual sloppiness — it attributes the injunction to the First Circuit
("evidently enjoined"), when the classwide preliminary injunction issued in the
District of New Hampshire with the First Circuit appeal merely pending, and it
misquotes the snapshot's grant entry as "Oct 24 2025" when the grant was
December 5, 2025. Analytical thinness — no engagement with the Rule 11
cert-before-judgment standard specifically (it argues from generic Rule 10
importance), no companion-vehicle discussion, no distribution/relist mechanics,
and no denial-side weighing beyond restating the BIO. And overclaiming — "the
probability of a grant approaches 100%" for SG petitions and "certain to
grant" are calibration rhetoric the pre-decision record does not support, even
for a petition this strong; its own cited ~3% anchor gets no quantitative
bridge to 0.99. The 0.99 is defensible only as a read-off of the leaked
outcome, which the document disclaims.
