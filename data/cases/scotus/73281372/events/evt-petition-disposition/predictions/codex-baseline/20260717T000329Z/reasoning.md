# Prediction

I predict that the Court will deny the petition, with a 10% probability of any grant. The most likely disposition is a conventional denial, not a GVR: the asserted errors concern the Second Circuit's construction of existing Bankruptcy Code provisions, and the record identifies no intervening decision or mootness event that would support summary vacatur.

## Question and governing standards

The provisioned `questions-presented.txt` asks whether 11 U.S.C. § 546(e), the safe harbor for specified securities-related transfers, applies through § 561(d) to prevent foreign liquidators in a Chapter 15 case from pursuing foreign statutory and common-law claims that would be cognizable abroad. On the merits, the petition invokes the presumption against extraterritoriality: absent a clear congressional indication of foreign reach, a federal statute ordinarily applies only domestically. Respondents answer that the relevant application is domestic because the liquidators invoked a U.S. bankruptcy court, and that § 561(d) expressly gives securities-contract provisions the same limiting effect in Chapter 15 as in Chapters 7 and 11.

At the certiorari stage, the central considerations are a square conflict, the importance and recurrence of the federal question, the clarity of the vehicle, and whether the decision below plausibly conflicts with this Court's precedents.

## Case-specific signals

The petition presents real grant-positive features. The issue is purely federal and text-centered. Petitioners argue that the Second Circuit used § 546(e) beyond its enumerated avoidance provisions, contrary to *Merit Management*, and that its extraterritorial reading conflicts with the Fifth Circuit's understanding of foreign-law avoidance powers in *Condor*. The dispute affects approximately $6 billion in Madoff-related redemption claims, hundreds of parties, and the operation of Chapter 15 in New York, a major cross-border financial forum. The petition is represented by experienced Supreme Court counsel and attracted two amicus filings supporting petitioners. These factors justify placing the case above an ordinary paid cert petition.

The brief in opposition, however, identifies substantial cert-stage weaknesses. It persuasively characterizes *Condor* as addressing § 1521(a)(7), not the extraterritorial reach of § 561(d), and says the Second Circuit is the first appellate court to decide the precise § 561(d) questions. The Seventh- and Eighth-Circuit cases on common-law claims reached the same practical result—those claims could not proceed—through implied preemption in domestic Chapter 11 cases, reducing the asserted conflict to reasoning and to the untested foreign-law distinction. Respondents also offer an alternative domestic-application rationale, point to New York contacts, and emphasize a sprawling record: roughly 300 adversary proceedings, more than 400 parties, multiple foreign-law claims, and alternative grounds for dismissal. The absence of a recorded dissent from denial of rehearing, the absence of a CVSG or relist as of the snapshot, and the Court's earlier cert denial in parallel Madoff litigation all weigh against review.

## Calibration

The committed corpus statpack reports a 5.36% estimated grant rate for paid 2025-Term petitions and a 5.41% grant rate for modern cert petitions originating in the Second Circuit. Petitions with no CVSG are granted about 3.0%; the no-relist bucket is lower, although this petition had not yet reached its first conference and therefore had no opportunity to be relisted. I adjust upward from the paid/Second Circuit baseline for the federal statutory issue, stakes, counsel, and plausible tension with other courts, but not to the level warranted by a clean, acknowledged appellate split. That produces a 10% grant probability.

The big-case score is 0.66. A merits decision could materially affect cross-border insolvencies, securities-transfer finality, and billions in recoveries from a notorious fraud, but the doctrinal field is specialized and the public-policy reach is narrower than a broad constitutional or regulatory case.

## Inputs and retrieval limits

I used the July 16, 2026 snapshot, the extracted questions presented, the petition, and the brief in opposition. `documents.json` marks the 345-page petition extraction as truncated, but the extracted file contains the complete cert petition through its conclusion; the missing material is within the appended volume. The live corpus-prior lookup failed because the runner could not resolve the remote corpus host, so no case-level corpus analogues informed the forecast. Targeted CourtListener searches supplied only the limited general context described in `retrieval.md` and did not search for or reveal this petition's disposition.
