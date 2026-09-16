# Rationale for the numbers

**P(grant, any form) = 0.01; predicted disposition: denied.**

## What I read

- The provisioned snapshot `record/snapshots/2026-09-16.json` (paid docket 25-1289, OT2025). Three proceedings entries: petition filed April 29, 2026; the Department of Agriculture's waiver of response filed June 8, 2026; distribution for the conference of September 28, 2026 on June 17, 2026. One distribution, no relist, no response requested, no amicus filings.
- `record/context.json`: forward mode, `band: baseline` under `sal-v4`, `distribution_count: 1`, no CVSG, term 2025.
- `record/documents/questions-presented.txt` and `record/documents/petition.txt` (194 pages, `truncated: true` per `documents.json`; text extracted cleanly, not OCR). I read the question presented, the statement, the reasons for granting, and Appendix A. No brief in opposition exists because the government waived.

## Anchor

The statpack's sal-v4 band table matches the context's `salience_version`, so I anchored on the `baseline` band's bracketed `reached` rate pooled over Terms strictly before OT2025 (OT2017 through OT2024, all eight rows the table renders). Weighting each Term's reached rate by its risk-set n gives roughly 5.1% (about 593 grants over about 11,580 petitions). That is the grant-family rate for a private, paid petitioner that has been distributed at least once, and it is the yardstick this cell is scored against. The paid-segment relist cut puts the terminal relist-0 bucket at about 1.7% grant family (granted 1.2%, gvr 0.5%), and the originating-circuit cut for `cafc` at about 4.6% (granted 3.1%, gvr 1.5%) over all fee classes.

## Adjustments, all downward

1. **The Solicitor General waived a response and the Court did not call for one.** On the paid docket a government waiver followed by straight distribution is the strongest routine denial signal available: the Court almost never grants without at least a response, and the call-for-response step that would precede a serious look did not happen.
2. **The decision below is a Federal Circuit Rule 36 affirmance.** Appendix A is a one-line nonprecedential per curiam judgment after argument. There is no reasoning to review, no published holding, and no precedential effect, which the Court treats as a poor vehicle.
3. **No conflict of authority.** The petition alleges no circuit split. It cites the Fourth Circuit's *Flynn v. SEC* as an analogous remand but does not claim the Federal Circuit disagreed with it as a matter of law; it argues the Board misapplied settled law to this record. The All Circuit Review Act makes a real split possible, but none is presented.
4. **Error-correction posture.** The question is whether the Board adequately addressed one pleaded theory in a long fact-specific initial decision. The Board's decision (App. 3a to 119a) is described as engaging in detailed analysis of the violation-of-law theory; the claimed defect is that it did not separately analyze gross mismanagement. That is a record-review complaint under a substantial-evidence standard, not a question of law of general importance.
5. **Petition quality.** The petition contains internal inconsistencies (for instance it says the Board "failed to conduct any analysis" under subsection (i) when it means (ii), and it describes the petitioner as pro se on appeal although Appendix A shows argued counsel), typographical errors, and a Rule 36 target. These make a grant less likely still.

Nothing pushes the other way beyond the general salience of whistleblower protection, which is a policy interest and not a cert consideration in a case with no split and no reasoned opinion below.

Combining these, I moved from the class floor of about 5% to 1%. I did not go lower because the reached-rate population already includes many weak petitions, because a GVR or rare summary disposition is always a small residual possibility, and because a 1% floor keeps the number honest about my own uncertainty in reading a 194-page record from its text alone.

## The other claims

- **relist-increment 0.10.** From one distribution, the paid-segment cuts imply roughly a quarter of distributed petitions pick up another distribution entry, but that figure includes reschedules and petitions in which the Court had called for a response. With a waiver and no response requested, a first-conference denial is the norm. I set 10% to cover long-conference carry-over and rescheduling noise.
- **cvsg-increment 0.005.** The federal government is the respondent, so a CVSG is structurally impossible. I did not write zero only because the claim is banked and a hard zero states more certainty than any forecast should.
- **summary-disposition-route 0.55.** Conditional on a grant. Prior Terms' gvr share of the grant family sits between about 30% and 59% in Terms where the label existed. This petition's alleged error (a claim left undecided below) is the kind that a GVR remedies and plenary review does not need, so I sit a little above the middle of that range.
- **dissent-from-denial 0.03.** Conditional on denial. Statements respecting denial are rare on fact-bound petitions from Rule 36 affirmances; the whistleblower subject slightly raises the chance above the floor.
- **big_case_score 0.10.** Low stakes: a single employee's reprisal appeal, no split, and even a grant would produce a narrow procedural remand.

## Retrieval and its limits

- Two CourtListener MCP searches. A docket search for recent SCOTUS matters mentioning the Whistleblower Protection Act or § 2302(b)(8) returned nothing, which reflects CourtListener's thin SCOTUS docket coverage rather than an absence of petitions. An opinion search returned recent decisions (Margolin v. NAIJ, Riley v. Bondi, Feliciano, Harrow, Corner Post, Jarkesy) that match on incidental terms; none I recognize decides the reasonable-belief analysis under § 2302(b)(8)(A), so I found no intervening decision that would make this a hold or GVR vehicle. I did not open Margolin's opinion, so my read of it rests on its caption and my prior knowledge of the dispute; a reader should discount the GVR conditional accordingly.
- No `fedcourts query` call: the corpus filters are structural (court, disposition, era, judge, citation) and cannot isolate MSPB whistleblower petitions, so a query would have returned an untargeted sample of SCOTUS priors and added nothing the statpack cuts do not already give.
- I did not read the earlier predictions on this docket by any predictor, including my own July run.

## Where to discount me

The Board's initial decision (App. 3a to 119a) was in the petition text but I did not read it in full; if it in fact analyzes gross mismanagement separately, the petition's premise fails and the probability should be even lower, not higher. If a Justice has been looking for a vehicle to address Rule 36 practice or MSPB whistleblower review, a statement respecting denial is more likely than my 3%.
