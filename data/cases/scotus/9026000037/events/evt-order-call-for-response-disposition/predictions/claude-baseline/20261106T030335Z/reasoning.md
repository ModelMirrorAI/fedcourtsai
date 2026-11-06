# Reasoning — New Mexico v. Neal, No. 26-37 (response-requested moment)

**P(grant, any form) = 0.11.**

## Record read
- Snapshot `2026-08-27.json` (date cut at 2026-08-27; forward mode). Paid petition by the State of New Mexico from the New Mexico Supreme Court (decided April 6, 2026). Respondent waived on July 24; the petition was distributed for the 9/28/2026 conference on Aug 19; the Court called for a response on Aug 26 (due Sept 25). One distribution, no CVSG, no amici on the record. Respondent's counsel of record is a well-known Supreme Court appellate firm, so expect a serious brief in opposition.
- `questions-presented.txt` and `petition.txt` (truncated at the cap; appendix cut). No BIO yet, which is what this moment means. `same-question.json` lists no matching petitions. No related dockets beyond the extension application 26A24.

## Anchor
- `context.json`: band `state` (sal-v7), `cert_anchor.rate` = 0.233 (10-Term lookback, strictly prior Terms). That matches the statpack's `state` bracketed reached rates for OT2017–OT2025 (roughly 14–39% per Term, n≈30–96 each). That is the rate for paid state-petitioner petitions in the scored segment, and it is the yardstick.

## Adjustments
- **Up, a little, for the call for a response.** The call shows that at least one chambers read the petition. But a state petitioner whose respondent waives routinely draws a call, so it adds less here than it would for a private petition. Much of the state-band rate already reflects this.
- **Down for the vehicle and jurisdiction.** (1) In the multiple-punishment setting the Double Jeopardy question is legislative intent (Missouri v. Hunter). A state high court's reading of what its own legislature intended binds this Court, so much of what the New Mexico court did reads as state law. (2) The decision below cites both the Fifth Amendment and the New Mexico Constitution (art. II, § 15). The petition spends a section on Michigan v. Long and Glossip to head off an adequate-and-independent-state-ground problem. That is a fight the opposition will press, and the Court tends to avoid vehicles like that. (3) The "split" really sets one outlier state (New Mexico's fact-intensive test) against everyone else. The middle line (Sixth and Eighth Circuits, Texas, Connecticut) versus the abstract-elements line is older and shallow. (4) The petition asks only to restore one conviction for a violent crime. Error correction for a state prosecutor sometimes draws a summary reversal, but the state-law entanglement makes that awkward here.
- **Up for the question itself.** What a court may consult under Blockburger has been left open since Dixon split. Some Justices (notably Gorsuch and Thomas) have shown interest in Double Jeopardy first principles.

On net I land below the band anchor, around 0.11.

## Other claims
- relist-increment 0.97: masked at this moment. The petition will be redistributed once the response is in.
- cvsg-increment 0.02: state criminal case with no federal party; a CVSG would be very unusual.
- summary-disposition-route 0.20 given a grant: state-petitioner error-correction grants sometimes ride a per curiam. A plenary grant on the methodology question is the likelier route.
- dissent-from-denial 0.07: possible from a Justice interested in Double Jeopardy doctrine, but unlikely.

## Caveats
- I have not seen the brief in opposition. It is the main driver of what happens next. A strong adequate-and-independent-state-ground argument would push the outcome toward denial, and a weak one would leave the petition near the band rate.
- The petition text is truncated, and I did not verify the New Mexico Supreme Court opinion (CourtListener's coverage of state high courts was not checked).
