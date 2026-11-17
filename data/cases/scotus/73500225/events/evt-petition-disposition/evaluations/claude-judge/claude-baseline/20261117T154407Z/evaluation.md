# Evaluation — claude-baseline

**Cell.** Cert stage, `moment: distribution`, forward. Outcome: petition **denied** on 2026-11-16 after five distributions, with a statement of Justice Thomas respecting the denial; no CVSG.

**Scores.** `predicted_disposition` denied vs. actual denied → `correct` 1. Probability 0.18 against `actual_granted` 0 → Brier 0.0324. No vote accuracy on a cert cell. Segment base rate, skill and basis are the harness's and left null; claim scores are computed in code.

## Reasoning (`reasoning.md`) — 0.82

The strongest rationale of the cell. It pooled the frozen elevated-band rate over strictly prior Terms and then actually argued both directions from the record, ending at the anchor because the adjustments cancelled rather than because it declined to analyse. What held up:

- It identified the Court's revealed reluctance on this exact question (the partial grant in *Wolford* that left sensitive places behind, the *Antonyuk* and *Schoenthal* denials) as the dominant consideration, and drew the right inference that *Schoenthal* being denied rather than held undercut the GVR route. The denial is consistent with that reading.
- It read the second distribution correctly as a pre-consideration reschedule, not a relist, and treated the petition as never yet considered.
- It took the BIO's percolation and vehicle-breadth points seriously (eight location categories under one broad question).
- It disclosed its uncertainties candidly, including what it could not verify.

What did not hold up:

- It inferred that the reschedule was pairing with Maryland's own petition, No. 25-1206, and said it could not confirm that petition's status. The brief in opposition it lists as read in full says Maryland moved to dismiss that petition after *Wolford* and the Court granted the motion. That is a miss on a provisioned fact, though it carried little weight in the number.
- Splitting the grant family evenly between plenary review and GVR gave the GVR route more than its own *Schoenthal* argument supported.

I did not rebuild the statpack the candidate ran against; its pooled figure (about 17.2% over 2,810) agrees with the other candidates' independent readings of the same table, and I take it as read rather than as verified.

## Predicted reasoning — 0.85

Central claims, in the document's order of weight: denial; at least one further distribution with "one to three further distributions, then an order by late November"; a writing on denial most plausibly from Justice Thomas; no CVSG; the companion petition denied at the same conference. The first four were borne out, and two of them were specific in ways a reader could have called otherwise: the docket shows exactly three further distributions and an order on November 16, and the separate writing came from Justice Thomas. Those two were held at 0.50 and 0.45, so they are leanings rather than confident calls, which keeps the document short of the top anchor. The companion-petition claim failed against the candidate's own provisioned record (No. 25-1206 had already been dismissed). The conditional content on question reformulation, the GVR route and the merits ground was never tested and earns neither credit nor penalty.

## Leakage

Forward; `not_applicable`. The log is fully captured and nothing in it post-dates the run or concerns this petition's disposition. *Wolford* (June 2026) is forward signal about another case, and the candidate disclosed it.
