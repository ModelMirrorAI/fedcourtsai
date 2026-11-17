# Evaluation — claude-baseline

**Cell.** `scotus/9026000427`, `evt-petition-disposition`, stage `cert`, forward. Outcome: petition **denied** on 2026-11-16 after a single distribution, no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.004 → `correct` = 1, Brier = 0.004² = 0.000016. Base rate, basis and skill are the harness's to stamp; I wrote none.

## Reasoning (`reasoning_quality` 0.72)

Sound and well-calibrated but thin. It picks the right anchor (the frozen band's reached rate, about 5%) and the right downward factors: pro se, SG waiver with no call for a response, fact-bound QPs 1 and 3, a nonprecedential decision, and no claimed split. Two observations are sharper than its length suggests: that the cafc originating-court row is dominated by counselled patent petitions and so should not lift this one, and (in the forecast) that near-exclusive Federal Circuit jurisdiction makes a split structurally hard to show.

What costs it:

- It says plainly that it read only the petition's front matter and questions, not the appendix. So it has no account of the decision below — the timing of the disclosures against the pay decision, or the alternative ground — which is where the vehicle problems actually sit. The disclosure is to its credit, but the analysis is shallower for it.
- "Essentially the pro se paid rate" is asserted with no figure behind it.
- The summary-route reasoning contradicts its number: it says any grant "would most likely be a GVR/summary vacatur" while assigning 0.3.

The sal-v4 baseline figures it quotes (2025: 4.0%, n=1314; 2024: 5.9%, n=1274) match the build it was placed against (`statpack-at`, build `7bcde3b105cb`, landed 2026-10-28); today's committed pack has been refreshed and differs, which is not the candidate's error.

## Predicted reasoning (`predicted_reasoning_quality` 0.8)

Central claims: denial at the November 13 conference without a relist and with no further distribution; no CVSG; no noted dissent or statement. All borne out by the docket and outcome. The document is short and commits cleanly, including the reasoning that a call for a response was the only realistic path to a second conference. It stays below 1.0 because these were the strongly favoured calls on this record. The QP 2 narrowing and the summary-route remark are conditional on a grant and are neither credited nor penalised.

## Leakage

Forward; `not_applicable`. Every call is captured: provisioned record, statpack, and generic corpus queries. No CourtListener or web call, nothing aimed at this petition's disposition, no document dated on or after resolution.

## Big case

My read: 0.04. An individual pro se federal employee's pay and position-description dispute, dismissed on jurisdictional pleading grounds in a nonprecedential decision, with no amicus interest and a denial without comment.
