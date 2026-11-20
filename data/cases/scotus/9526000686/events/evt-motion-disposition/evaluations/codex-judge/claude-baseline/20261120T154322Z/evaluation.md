# claude-baseline on Overton’s application for a stay

The Court denied the stay on November 19, 2026. claude-baseline predicted denial and assigned 1.00% to relief. With `interim_granted` equal to 0, the disposition is correct (1) and the Brier score is 0.0001. The harness computes the interim baseline and Brier skill score from prior application Terms.

## Reasoning quality

**0.78.** The private-capital application cohort is a sensible starting point. The four-page application incorporated the certiorari petition for its substantive argument, identified no conflict itself and gave little detail about the alleged denial of process. The rationale usefully connects those features to the difficulty of attracting four votes for review and to the minimal clemency safeguards discussed in *Woodard*. The move down to 1% relies partly on a recollection about Florida stays and a procedural bar inferred without the state decision. The unrelated grants returned by the corpus query provide little support for the size of that adjustment. The candidate acknowledges both limits.

## Predicted reasoning

**0.98.** The forecast called the most distinctive feature of the order. Justice Thomas referred the stay, and the full Court denied both the stay and certiorari in the same entry. Florida filed on November 17 without a formal request, and no amicus appeared. The order gives no reasons and records no dissent. November 19 was inside the predicted date window. The docket gives no hour of issuance, so the afternoon deadline remains open. The forecast’s discussion of possible state-law grounds earns no additional credit from the unexplained order.

## Leakage

Forward forecast made November 15. All ten logged calls have captured results. They concern the opening record, statpack, tooling, an unrelated grant-filtered corpus query and the candidate’s output. The rationale describes the November 14 submission and treats the decision as pending. Nothing points to retrieval of the November 19 order.
