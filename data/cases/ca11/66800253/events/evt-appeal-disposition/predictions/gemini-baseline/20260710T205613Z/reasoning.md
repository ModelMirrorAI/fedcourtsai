# Reasoning: Marcellus Henderson v. United States (Eleventh Circuit, 21-11740)

## Disclosure of Inadvertent Knowledge
During the initial search to understand the nature of the case (since the provisioned snapshot only contained an "Opinion Issued" docket entry without the underlying documents or case details), a web search for "Marcellus Henderson v. United States 21-11740" was performed. The search results inadvertently revealed that the Eleventh Circuit affirmed the lower court's decision on April 10, 2025 (holding that the offense, armed bank robbery resulting in death, remained a crime of violence), and that the U.S. Supreme Court subsequently denied certiorari.

As instructed by the `predict.md` prompt: "If you already know the outcome... or encounter it inadvertently (a stray search result), say so explicitly in reasoning.md and add a flags.json note (category other) so the evaluation can discount the cell — then still reason from the pre-decision record only."

## Analysis from Pre-Decision Record and Base Rates
The case involves an appeal by the defendant, Marcellus Henderson, likely concerning a § 2255 motion to vacate his sentence or a direct appeal challenging his conviction under 18 U.S.C. § 924(c) in light of Supreme Court decisions like *United States v. Davis*. He argued that bank robbery resulting in death (18 U.S.C. § 2113(a), (d), and (e)) does not categorically qualify as a "crime of violence" under the elements clause.

Operating under the assumption that we are evaluating the likelihood of the Eleventh Circuit granting the defendant relief (e.g., reversing or vacating the conviction/sentence):
1. **Base Rates**: The Eleventh Circuit affirms the vast majority of appeals and denies most motions for relief. According to the `metrics/statpack.md`, the Eleventh Circuit has a base rate of "other" (which encompasses affirmances) at 95.6%, and "granted" at only 2.2%.
2. **Legal Context**: The categorical approach as applied to federal bank robbery (under § 2113(a) and (d)) has consistently resulted in findings that it constitutes a crime of violence across multiple circuits, including the Eleventh Circuit. A killing in the course of such a robbery (§ 2113(e)) further underscores the inherent force and violence of the offense. Therefore, legally, an appellant faces an extremely steep uphill battle.

## Prediction
Given the very high base rate of affirmance ("other") and the established precedent treating armed bank robbery as a crime of violence under the elements clause, the most probable outcome is that the court will deny the appellant's request for relief and affirm the lower court's decision. 

Therefore, `granted` is set to `0` (with a low probability of 0.04), and `predicted_disposition` is set to `other`.