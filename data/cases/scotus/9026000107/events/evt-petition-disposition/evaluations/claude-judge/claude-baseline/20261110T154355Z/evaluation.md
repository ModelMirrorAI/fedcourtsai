# Evaluation — claude-baseline

Cell: scotus/9026000107 (*Walls v. Prince George's County*, No. 26-107), `evt-petition-disposition`, stage **cert**. Outcome: **denied** on 2026-11-09 after one redistribution (for the 11/6/2026 conference), no CVSG, no noted dissent.

## Scores

- Predicted disposition `denied`, P(grant) = 0.22. `correct` = 1; `brier_score` = (0.22 − 0)² = 0.0484.
- Segment base rate, skill and basis are the harness's stamp (the prediction froze band `baseline` under `sal-v4`); I quote no rate of my own — compare against the stamped segment base rate.
- No vote accuracy (cert stage; votes are never scored here). No semantic grades (cert stage declares no semantic set).

## Reasoning quality (0.75)

Strong rationale. Anchored on the frozen band's bracketed `reached` (risk-set) figure for `baseline` under `sal-v4`, the right population for a frozen-band cell, then made explicit, well-reasoned upward adjustments (CFR after waiver, six amici discounted as a coordinated campaign, repeat-player counsel, companion petition, thin BIO) and equally concrete downward ones (unpublished per curiam, divergent lower-court grounds, a contested factual predicate on whether a waiver application was ever made, a split resting mostly on old state intermediate-court decisions, the Court's reluctance to settle prudential ripeness). The vehicle problems it names are exactly the reasons a petition like this is denied. The 0.22 is high relative to the anchor; the CFR and amicus uplift is not quantified from the pack, which the candidate itself discloses. The companion-petition argument overweighted the chance the Court would treat the pair as a unit, but it was framed with its own discount. Scored 0.75.

## Predicted reasoning (0.6)

Central claims: denial (borne out), a further distribution (borne out), the hold-with-Tedford's timing path to a December/January decision (not borne out — the Court redistributed once and denied on Nov 9, which the document had named as the main alternative), no CVSG (borne out), silent denial most likely (borne out). Specific and mostly right, but the most distinctive, discriminating call — the companion-hold timing — failed, while what held is largely the modal path for any CFR'd paid petition. Conditional grant-branch content (which QP, summary route, merits) is unresolved and earns nothing either way. Graded 0.6.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false. Forward cell (snapshot 2026-10-05, cutoff null). All 30+ calls ran 2026-10-06, more than a month before the 2026-11-09 denial. Web fetches of this case's and the companion's public dockets returned the docket as of Oct 6 (no entry after the Oct 1 BIO, per the candidate's own disclosure); no retrieved_doc_date on or after resolution; no qp-topics read. Disclosed retrieval honestly in retrieval.md. Companion-docket and practitioner-blog material is legitimate forward signal.

## Big case

My own read: 0.35 — A Fourth Circuit unpublished per curiam in a single-lot well-and-septic dispute raising legislative-exhaustion and prudential-ripeness questions for takings claims; doctrinally meaningful to the land-use bar and drew an organized property-rights amicus slate, but low public salience, and the Court denied silently after one redistribution.
