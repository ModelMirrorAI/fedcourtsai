# Evaluation: codex-baseline — scotus/9026000004, evt-petition-disposition

**Outcome:** petition denied on November 16, 2026, with no noted dissent, no CVSG, and no distribution beyond the two already on the docket.

**Scores:** `correct` 1 (predicted `denied`), Brier 0.0064 (p = 0.08 against 0). This is a cert cell; the segment base rate, basis and skill are the harness's to stamp.

## Reasoning (`reasoning_quality` 0.8)

The rationale reads the docket accurately: distributions for 9/28 and 11/13, the response requested August 14, the brief in opposition filed October 14, and the reply filed but not provisioned. It correctly treats the second distribution as following the requested response and not as a substantive relist. The anchor is computed exactly, and it explains why the terminal relist, CVSG and amicus cuts cannot be stacked as independent multipliers.

The legal analysis is careful about attribution. Preservation is identified as the strongest obstacle, the alleged independent specific-jurisdiction basis (admissions) as a second, and the split as disputed; contested assertions are attributed to the brief in opposition and not treated as established. The 1985 registration date and the Cooper Tire prior are both right.

Weaknesses are modest. At 8% it kept the most probability on a grant of the three, giving the response request and the issue's importance somewhat more weight than the vehicle problems it had just catalogued would support. It also spends space on process caveats that do not bear on the forecast. Like the others, it could not read the reply and says so.

## Predicted reasoning (`predicted_reasoning_quality` 0.75)

Central claims: denial without a separate writing, the route (zero further distributions, denial after the November 13 conference, mid-to-late November), and no CVSG. All were borne out, and the timing was specific enough to have failed.

It sits a step below the top because the document hedges its horizon ("disposition by December 2026 is a reasonable central horizon") and gave the relist alternative 24%. The vehicle-based reason for denial cannot be checked against a bare denial order, so it is `unresolved`. The if-granted content is conditional and earns neither credit nor penalty.

## Leakage

Forward cell; `not_applicable`. Captured calls show the provisioned record, statpack and corpus queries, with legible document dates before the prediction. The two web searches are unobserved rows; their queries target the 2023 Mallory opinion, not this petition. Nothing in the reasoning presupposes the outcome.

## Big case

My own read is 0.35: a nationally relevant jurisdiction question in a poor, fact-bound vehicle, denied silently.
