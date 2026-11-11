# claude-baseline — evaluation

Cert-stage, arrival-moment, forward cell. Outcome: petition **denied** on 2026-11-09 (`actual_granted` 0) after a respondent waiver (Aug 25, 2026) and a single distribution for the 11/6/2026 conference; no CVSG, no relist, no noted dissent. The segment base rate, its basis and the skill score are the harness's to stamp; this write-up quotes no rate of its own. The claims block is scored in code and not graded here. No semantic set is declared on a cert cell.

## Score
- Predicted `denied` at P(grant) = 0.015 → `correct` = 1, `brier_score` = 0.000225.

## Reasoning quality — 0.80
A thorough and well-organized analysis. It gives an explicit anchor with its Term window and sample, then adjusts down for reasons that match the record:
- error-correction QPs, two of them aimed at the district court's judgment;
- no split alleged (it searched the petition text);
- an unreasoned unpublished per curiam with no en banc poll;
- the post-*Groff* posture;
- a discretionary Rule 56(d) ruling.

It also runs a timeliness check and candidly flags its thin retrieval. Its explanation for keeping the probability above a floor, a GVR tail from a possible intervening religious-accommodation decision, is coherent but speculative. That tail makes this the least sharp of the three numbers. The claim that the Court "has repeatedly denied" vaccine-mandate petitions rests on general knowledge rather than anything retrieved, and the document says so.

## Predicted reasoning — 0.62
The central claims were:
- a routine denial on an October or November order list (borne out: Nov 9);
- a waiver or short BIO, then one distribution with no relist (borne out: waiver Aug 25, single distribution);
- distribution for the late-September long conference, or failing that early October (not borne out: distributed Oct 14 for the 11/6 conference, despite the August waiver);
- no CVSG (borne out);
- no dissent from denial (borne out).

The document was more specific than its peers, and most of that specificity held. The one specific timing call failed, and it was secondary.

## Leakage
Forward (predicted 2026-08-16, resolved 2026-11-09). CourtListener searches by caption located the CA4 docket, which is pre-decision lower-court material. One corpus citation query returned nothing. No retrieved document post-dates the resolution. `not_applicable`, not suspected.

## Big case
0.12. This is a fact-bound private Title VII accommodation dispute with no split.
