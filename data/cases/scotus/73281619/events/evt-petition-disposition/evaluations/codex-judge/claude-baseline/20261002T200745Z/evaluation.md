# Evaluation: claude-baseline

## Outcome and quantitative score

The supplied cert outcome is `granted`, `actual_granted = 1`, with plenary
review, resolved October 1, 2026. The provisioned October 1 snapshot specifies
review limited to Question 1. The blinded prediction from run
`20260918T174135Z` called `denied` with P(grant) = 0.30. Thus exact-label
correctness is **0** and **Brier = (0.30 - 1)^2 = 0.49**. The partial scope of
the grant does not change this event's recorded binary target.

## Baseline

The prediction freezes band `elevated`, Term 2025, and version `sal-v4`, which
matches the committed `metrics/statpack.md` segment-table heading. I use the
bracketed reached rates on the `risk_set` basis, not the terminal population
or the evaluator's decided-docket context. The table displays all 10 of 10
Terms, 2017–2026; only the eight rows from 2017 through 2024 precede the case's
frozen Term and enter the calculation.

In chronological order, the printed percentage/weighted-resolved pairs are
17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300,
17.5%/354, and 17.9%/336. The weighted numerator reconstructed from these
rounded percentages is 484.386, with denominator 2,810, giving
**segment base rate = 0.172379359430605**. This is an approximate rate from the
required rendered surface, not an assertion of 484.386 observed grants.
The pack describes denial-reweighted live/historical-slice estimates; these
are committed-context figures, not a fresh corpus measurement. I did not query
the corpus.

The baseline Brier is 0.6849559246964957 and
**skill = 1 - 0.49 / 0.6849559246964957 = 0.2846255031415062**.
The forecast beats this baseline on the realized grant but misses the modal
label. Neither observation supports a broad performance claim from one case.

## Reasoning quality: 0.78

The rationale identifies a coherent group of upward and downward signals,
uses the right frozen-band prior, and explains the adjustment to 30%. It
recognizes that the response request and later briefing can explain the two
distributions rather than treating the count as straightforward post-briefing
relisting. It ties the claimed legal conflict to the two questions presented
and identifies concrete invited-error, comparator-record, and statutory-
coverage issues. The opposition at printed pages 27–28 and 35–36 substantiates
that these arguments were made. The analysis is also candid that the reply
and amicus briefs were not available as text, that the recent Anash holding
was inferred from the opposition rather than independently read, and that
the response-request weight is judgmental.

Several assertions exceed what the sources establish. The docket supports
caution about completed substantive consideration, not certainty that the
Court has never voted on the petition. The assertion that this amicus volume
is rare outside granted petitions is not paired with a measured comparison
group. Treating a response request as an analogue of a CVSG can also invite
overweighting unless the distinct selection mechanisms are kept clear.

Source quality is uneven on the related-case discussion. The staged retrieval
record discloses that the characterization of Grand's question came partly
from an earlier generated forecast, not its petition or a substantive court
opinion. That is weaker evidence than a primary source for the proposition
used in this rationale. The Anash lookup verifies metadata rather than the
full doctrinal characterization; the disclosure of that limitation is a
strength, but does not eliminate it. The rejection of the vehicle is also
phrased more confidently than the unresolved party dispute warrants, and the
specific 45–50% clean-vehicle counterfactual has no measured foundation.

Finally, the equal-terms preservation difficulty need not dispose of the
substantial-burden question. The actual Question-1-only grant illustrates that
distinction, but does not reveal why the Court granted or resolve any merits
issue. The grade reflects these analytical strengths and limits, not a
mechanical deduction for the denied label or a reward for conditional language
in the separate forecast document.

## Leakage and scope

The log identifies forward mode and captures all 45 call results (coverage
1.0). The September 18 prediction predates the October 1 disposition. External
queries concern Anash, Spirit of Aloha, and Grand; the legible decision dates
are July 30, 2026 and November 13, 2025. The generic corpus query and local
related-case reads do not show this petition's own resolution. The earlier
Grand forecast is not evidence of future-outcome knowledge about this case;
its provenance affects reliability of that argument, not the leakage bit.
No observed query or passage in the reasoning establishes that an already-
decided petition was routed forward. Outcome material is not shown as
retrieved, influence is `not_applicable`, and `leakage_suspected` is false.

The forecast document was read for context only and is not scored. The
structured quantitative claims remain the harness's responsibility. No vote
accuracy or semantic grades are written because this is a cert cell. The
optional independent stakes assessment is omitted.
