# Evaluation — codex-baseline

**Cell.** Cert stage, `moment: distribution`, forward. Outcome: petition **denied** on 2026-11-16 after five distributions, with a statement of Justice Thomas respecting the denial; no CVSG.

**Scores.** `predicted_disposition` denied vs. actual denied → `correct` 1. Probability 0.38 against `actual_granted` 0 → Brier 0.1444, the weakest of the cell. No vote accuracy on a cert cell. Segment base rate, skill and basis are the harness's and left null; claim scores are computed in code.

## Reasoning (`reasoning.md`) — 0.55

Methodologically careful and well sourced, but its conclusion does not follow from its own analysis.

What was sound: it pooled the frozen elevated-band rate over strictly prior Terms and said plainly that the figure was reconstructed from rounded rates. It refused to treat terminal relist-bucket figures as forward hazards. It read the second distribution correctly as a pre-conference reschedule and discounted it. It caught from the brief in opposition that Maryland's companion petition had been dismissed after *Wolford*. It set out the opposition's percolation and vehicle points fairly and noted that *Wolford*'s private-property question differs from the sensitive-places questions here. Its disclosure of limits is thorough.

What was not: having listed downward considerations that it called important (a reschedule rather than a relist, a broad and awkward vehicle, a GVR hook it described as substantially limited), it still more than doubled the anchor to 38%. Most of that mass went to a GVR route (about 23%) that its own text had just argued against, and it did not weigh the Court's prior treatment of this same question (the partial grant in *Wolford*, the earlier denials the petition itself discusses). It also put only 22% on a separate writing at denial in a major Second Amendment case, without considering the recent pattern of such writings; that judgment proved wrong, though it is the claims block's to score. The process was disciplined; the calibration was not.

## Predicted reasoning — 0.30

Central claims: denial; narrowly no further distribution; no writing on denial; no CVSG. The disposition held, but at 38% for a grant the document's lean was soft. Its two other committed calls about the path both failed: the petition was distributed three more times, and the denial carried a Thomas statement, which the document had put at 22% while declining to name any Justice. The CVSG call held but was the least contestable claim in the cell. A correct disposition with both procedural calls wrong sits just above the 0.25 anchor. The GVR-route and question-reformulation content was conditional on a grant and is not graded.

## Leakage

Forward; `not_applicable`. Two web searches are unobserved in the log; their queries target *Wolford* and *Bruen* on the Court's site, and the candidate reports they returned nothing usable. Nothing sought or reflects this petition's disposition.
