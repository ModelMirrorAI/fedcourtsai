# Evaluation — codex-baseline, scotus/9026000290 (*Emberton v. Superior Court of California*), cert disposition

**Stage:** cert (forward, distribution moment). **Outcome:** denied on Nov 9, 2026, after one distribution (Nov 6 conference). No CVSG, no noted dissent.

## Scores
- `predicted_disposition` denied vs. actual denied → **correct = 1**.
- P(grant) 0.004 → **Brier = 0.000016**.
- The harness computes the base rate and skill and stamps them (frozen band `baseline`, sal-v4); I leave them to the stamped segment base rate. Cert votes are not scored. The claims block is scored in code.
- No semantic set is declared on a cert cell, so I wrote no `semantic_grades`.

## Reasoning quality: 0.80
The analysis holds up. It anchors on the pooled sal-v4 baseline-band reached rate. It correctly describes the relist/CVSG cuts as descriptive terminal cuts, not forward hazards. It then cuts down hard for sound reasons:
- the claimed "conflict" is between lines of this Court's own precedent, not a lower-court split;
- the vehicle looks interlocutory: summary writ denials from a demurrer sustained with and without leave to amend;
- the petition sweeps together many theories;
- the petitioner is pro se, with no response and no Court-requested adversarial development.

It is careful about epistemic limits. It separates the petitioner's characterizations from readable holdings, and it treats finality as a risk rather than a settled bar because the trial-court reasoning was not in the text. Small deductions:
- the stakes score (0.22) is somewhat high for a local dispute, though it is reasoned;
- the 35% conditional summary-route figure is loosely grounded.

## Predicted reasoning: 0.60
I treated these as central: denial; no further distribution; disposition on the order list after the Nov 6 conference; no CVSG; and an ordinary denial with no writing. Every one was borne out. But these are close to the default path for a pro se paid petition with no response, and a competent reader would rarely have called them otherwise. The document is specific but not discriminating, which puts it just above the 0.5 "right but generic" anchor. The conditional QP-narrowing and summary-route content was never tested (unresolved).

## Leakage
Forward cell; `influenced_prediction` = not_applicable. I checked for a mis-provisioned decided case and found none. The two web-search rows (Supreme Court Rule 10 query; Cornell rule page) returned nothing usable and do not concern this case's outcome. No retrieved document dates fall on or after the Nov 9 resolution, and nothing under `data/qp-topics/` was read.

## Big case
My own read is 0.04: one homeowner's code-enforcement dispute over a fence, with abstract Fourth Amendment framing.
