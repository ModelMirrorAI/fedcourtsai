# Prediction

I predict a **granted-side disposition**, most likely a summary vacatur and remand rather than plenary review, with `P(granted) = 0.88`.

## Leakage and input limitation

The provisioned July 13, 2026 snapshot contains an explicit May 11, 2026 disposition and a dissent lineup even though `event.yaml` says the event is unresolved and `record/context.json` labels the cell `forward`. That material was impossible to unsee. I quarantined it from the analysis below and did not use the disclosed lineup to predict votes, but its presence can still bias this forecast; `flags.json` records the problem for evaluation.

No filed-document text or `documents.json` was provisioned. The exact questions in the jurisdictional statement and the appellees' motion to affirm therefore were unavailable. The legal question can be stated only at a reliable high level: whether the three-judge district court's May 8, 2025 congressional-redistricting judgment against Alabama should stand under the Voting Rights Act and constitutional limits on race-conscious districting.

## Governing law

This is a paid direct appeal from a three-judge district court, presented by a statement as to jurisdiction rather than an ordinary certiorari petition. On such an appeal the Court can summarily affirm, dismiss, note probable jurisdiction, or vacate and remand when an intervening or closely related ruling changes the governing framework.

The principal pre-existing authority is *Allen v. Milligan*, 599 U.S. 1 (2023), which applied the familiar *Thornburg v. Gingles* framework to an Alabama congressional map. A Section 2 vote-dilution claimant generally must establish a sufficiently large and geographically compact minority population capable of forming a majority in an additional reasonably configured district, political cohesion, and usually defeating majority-bloc voting, followed by the totality-of-circumstances inquiry. If race predominates in drawing a district, strict scrutiny separately asks whether the use of race serves a compelling interest, including supported Voting Rights Act compliance, and is narrowly tailored.

## Docket signals available before disposition

The snapshot shows several signals that sharply distinguish this matter from a routine cert petition:

- Alabama filed its jurisdictional statement in August 2025 after receiving an extension; appellees responded with a motion to affirm, and Alabama replied.
- The matter was distributed for the November 21, 2025 conference but remained pending for almost six months. A long hold in a closely related redistricting dispute strongly suggests that another matter may supply the controlling rule and make a later summary order appropriate.
- The docket is linked to No. 25-273, and numerous filings are marked `VIDED`, reinforcing that the cases are being managed together.
- Alabama moved to expedite on April 30, 2026, filed an emergency stay application on May 8, and obtained a requested response and conference distribution. This late cluster of emergency activity makes a passive denial or indefinite hold less likely and an imminent merits-affecting order more likely.

The committed statpack reports only a 4.9% grant rate for the modern discretionary-cert slice, but that is not the proper baseline here: this is a paid direct appeal already held and coordinated with related litigation. The case-specific procedural signals overwhelm that generic cert prior. The main residual possibilities are summary affirmance, dismissal for want of jurisdiction, or a grant of plenary consideration. Given the long hold and coordinated emergency posture, I assign the largest mass to a grant-side summary vacatur/remand and predict `granted` at 0.88.

I omit individual votes. Any lineup inferred from the explicit post-disposition text would be leakage, while the clean pre-disposition record does not support a sufficiently reliable justice-by-justice forecast.
