# Evaluation: codex-baseline, scotus/9026000435, evt-petition-disposition

Cert-stage cell (moment: distribution). Outcome: petition **denied** on 2026-11-16 after a single distribution for the Nov 13 conference; no response requested, no CVSG, no noted dissent.

## Scores

- Predicted `denied` at probability 0.07; actual `denied` (`actual_granted` 0). `correct` = 1, `brier_score` = 0.0049.
- `vote_accuracy` omitted (cert stage). Segment base rate, skill and basis are the harness's to stamp; claim scores are computed in code.

## Reasoning quality: 0.8

The most thorough rationale of the three. It read the appended Second Circuit order rather than only the petition's account of it, and found the point that matters: the same page that carries the "considerable deference" sentence also states de novo review of legal conclusions, and the operative analysis rests on record-specific evidentiary gaps. It checked the two authorities the petition leans on (Loper Bright's fact/law distinction and Multimedia KSDK) and correctly reported that KSDK does not establish a categorical rule for television producers. It was careful about what it had not verified (Siren Retail taken only as the petition's account; appellate briefs not reviewed for preservation).

Base-rate use checks out against the statpack build in force at its run (`statpack-at` resolved build 7bcde3b105cb, not the committed pack): the relist-0, relist-1/2/3+, CVSG, zero-amicus and ca2 figures it quotes match that build's tables, and its pooled baseline risk-set figure of about 5.1% is consistent with the build's per-Term bracketed rows (4.0% to 5.9%). It correctly distinguished the risk-set anchor from terminal-bucket cross-checks.

What costs it: having marshalled the reasons the petition was weak (unpublished order, no clean split, the circuit's own later correction, a waiver with no response call), it still moved the number *above* its anchor to 7% and gave 20% to a further distribution. The analysis it wrote supports a number at or below the anchor; the upward adjustment for the GVR hook was not well reconciled with its own finding that the hook likely did not control the judgment. The petition was denied at first conference with no response requested.

## Predicted reasoning: 0.7

Central claims: denial without writing on the order list after the Nov 13 conference; no further distribution as the modal path; no CVSG; a conditional GVR route. The first three were borne out exactly, including the timing. The document committed to the modal path while hedging the relist branch at 20%, heavier than the other candidates, and a good share of its length is conditional on a grant that did not occur (no credit, no penalty). Specific on path and timing, but the path it called was the base-rate-dominant one, so it sits just below the 0.75 anchor.

## Leakage

Forward cell: prediction created 2026-10-30 from the 2026-10-30 snapshot (last entry the Oct 28 distribution); the petition was denied 2026-11-16. Scanned the captured log and prose for this case's disposition surfacing as decided: no retrieved_doc_date on or after 2026-11-16, no query for a disposing order, no read under data/qp-topics/, and the reasoning treats the conference as pending. Retrieval beyond the record was Loper Bright and Multimedia KSDK (8th Cir. 2002) via CourtListener, plus one hosted web search for Loper Bright context whose result was unobserved; graded on its query, it targets a 2024 opinion, not this petition. Graded `not_applicable`; `leakage_suspected` false.

## Big case: 0.15

A narrow, fact-bound labor dispute from an unpublished order, denied without comment. The Loper Bright question it invoked has broader reach than this vehicle did.
