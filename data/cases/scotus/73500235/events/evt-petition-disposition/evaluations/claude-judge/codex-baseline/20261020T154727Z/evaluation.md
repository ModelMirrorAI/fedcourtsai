# Evaluation — codex-baseline

**Cell:** scotus/73500235 (Walid bin ‘Atash v. United States), `evt-petition-disposition`, stage `cert`. **Outcome:** `denied` on 2026-10-19 (`actual_granted` 0, no noted dissent from denial, three distributions).

**Baseline:** the scored prediction froze band `elevated` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I left them null and quote only "the stamped segment base rate". `correct` and `brier_score` are written as my independent read; the stamp recomputes both. Votes are not scored on a cert cell, and no semantic set is declared, so no `semantic_grades` block is written. The claims block is scored in code and is not graded here.

**Prediction:** `denied`, P(grant) = 0.18. **correct** = 1, **Brier** = (0.18 − 0)² = 0.0324.

## Reasoning quality: 0.76

A careful, well-sourced analysis. It pools the elevated-band reached rate correctly and transparently: 17.24% over 2,810 weighted petitions, OT2017–OT2024, with the per-Term rows listed. It treats the distribution count as reschedules. It also checks *Dean* in the primary source (67 M.J. 227–28) instead of taking either brief's word, which strengthens its account of the conflict. It sets out the government's vehicle objections accurately: the repealed court-martial rule, exclusive D.C. Circuit jurisdiction, and misapplication of the mandamus standard rather than a dispute over the standard itself.

Its weakness is the netting. It identifies the same non-recurrence and vehicle problems that make a split-driven grant unlikely, then calls them roughly offset by the stakes and lands slightly *above* the anchor. Its own analysis (no recurring conflict, interlocutory mandamus, a fact-bound application) pointed below the band rate. It acknowledges the adjustments are judgmental. The 0.30 dissent-from-denial estimate was reasonable but did not occur. Disclosure of the information boundary and retrieval is exemplary.

## Leakage

Forward. Retrieval covered *Dean* via CourtListener and two uncaptured web searches. Their queries target general Supreme Court Rule 10 material, not this case. One `find` excluded `data/qp-topics` with `-not -path`, which opens nothing there and is not a read. `not_applicable`, not suspected.
