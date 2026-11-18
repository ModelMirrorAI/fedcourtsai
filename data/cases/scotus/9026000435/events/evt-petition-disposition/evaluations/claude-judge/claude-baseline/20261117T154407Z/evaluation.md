# Evaluation: claude-baseline, scotus/9026000435, evt-petition-disposition

Cert-stage cell (moment: distribution). Outcome: petition **denied** on 2026-11-16 after a single distribution for the Nov 13 conference; no response requested, no CVSG, no noted dissent.

## Scores

- Predicted `denied` at probability 0.04; actual `denied` (`actual_granted` 0). `correct` = 1, `brier_score` = 0.0016.
- `vote_accuracy` omitted (cert stage). Segment base rate, skill and basis are the harness's to stamp; claim scores are computed in code.

## Reasoning quality: 0.7

A compact, sound rationale. It anchors on the baseline band's risk-set rate ("roughly 5%, about 4–6% per Term, each n about 1,200–1,700"), which matches the statpack build in force at its run (`statpack-at` build 7bcde3b105cb; bracketed rows 4.0% to 5.9%, n 1,196 to 1,740), and it correctly treats the relist-0 bucket (about 1.8%) as a terminal floor rather than the live rate. Adjustments run both ways and are weighed sensibly: the waiver, the unpublished order and the stale, fact-bound "split" push down; the "considerable deference" sentence and the Hospital Menonita GVR analogy push up; and it sees that Siren Retail cuts both ways, making the error look panel-specific while removing the need for review. Netting to 4%, just under the anchor, was a defensible call that the outcome did not contradict.

Limits: it says plainly that it did not read the Second Circuit's order in full, so it could not assess whether the deference sentence controlled the result, which was the question the grant probability most depended on. It checked no cited authority and gives Hospital Menonita's GVR as 2024 where the petition's citation is 145 S. Ct. 2831 (2025). The 15% relist increment was generous for a waived petition with no amici. Honest about its gaps, accurate on its numbers, thinner on the law than codex-baseline.

## Predicted reasoning: 0.75

Central claims: denial at the Nov 13 conference with no response requested; no further distribution; no CVSG; no dissent; a conditional GVR route. The unconditional claims were all borne out, and the lead claim is the most specific of the three because it commits to the mechanism (no call for a response) rather than only the result. It still describes the dominant path for a waived petition, so it stays at the 0.75 anchor rather than above it.

## Leakage

Forward cell: prediction created 2026-10-30 from the 2026-10-30 snapshot (last entry the Oct 28 distribution); the petition was denied 2026-11-16. Scanned the captured log and prose for this case's disposition surfacing as decided: no retrieved_doc_date on or after 2026-11-16, no query for a disposing order, no read under data/qp-topics/, and the reasoning treats the conference as pending. All results captured (coverage 1.0); retrieval was the provisioned record, the committed statpack and two corpus queries for GVR priors. No CourtListener or web retrieval. Graded `not_applicable`; `leakage_suspected` false.

## Big case: 0.15

A narrow, fact-bound labor dispute from an unpublished order, denied without comment. The Loper Bright question it invoked has broader reach than this vehicle did.
