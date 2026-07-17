# Prediction: denied

I assign a 0.05% probability to any grant and predict denial. I do not predict individual votes: certiorari votes are not public absent a recorded statement, and the record supplies no sound basis to attribute a vote to any Justice.

## Record and legal question

The July 17 snapshot identifies a paid petition from an unpublished Ninth Circuit disposition in a pro se employment dispute. It shows the petition filed on May 5, 2026 and distributed for the September 28 conference, with no response, amicus filing, CVSG, or prior conference distribution reflected in the provisioned docket. I used `data/cases/scotus/73318133/record/snapshots/2026-07-17.json` and the complete, non-truncated 60-page text in `record/documents/petition.txt`.

The petition presents nine questions. They range from whether federal marijuana law and several constitutional clauses apply to California and Boeing, to penalties for alleged workplace drug use, threats, and nondisclosure; Boeing's market position and FAA delegation; the Ninth Circuit's characterization of the action; and the availability of a nationwide injunction. The petition also seeks sweeping remedies including invalidation of state cannabis laws, injunctions, government seizure of aircraft, dissolution of Boeing business units, employment restrictions on individuals, and a monetary award. Its reasons-for-granting section invokes Boeing safety concerns, federal supremacy, retaliation, and Justice Thomas's criticism of the McDonnell Douglas framework.

## Certiorari standard and application

Under the Court's ordinary discretionary-certiorari criteria, a petition is strongest when it identifies a square conflict among appellate courts, an important recurring federal question, or a serious departure from accepted judicial practice. Four votes are required. Mere factual error or disagreement with an unpublished application of settled law is ordinarily insufficient, and vehicle defects weigh heavily against review.

This petition has exceptionally weak grant characteristics:

- It does not identify a developed split on a clean legal issue. Its questions largely request fact-specific penalties or remedies rather than frame a rule of federal law that the Court can resolve.
- The case comes from an unpublished decision reviewing summary judgment in an individual employment dispute. The petition's arguments predominantly challenge the lower courts' reading of evidence, characterize opposing factual assertions as false, and seek correction of alleged case-specific errors.
- The proposed remedies extend far beyond the parties and claims described in the record, creating severe preservation, standing, redressability, and vehicle concerns.
- The petition invokes many constitutional provisions, statutes, regulations, and precedents without connecting them to a focused holding below. The CourtListener search confirmed that *Ames v. Ohio Department of Youth Services*, 605 U.S. 303 (2025), contains the quoted criticism of McDonnell Douglas, but that observation does not itself create a split or make this state-law retaliation dispute a suitable vehicle.
- The snapshot shows none of the usual positive docket signals: no CVSG, no amicus support, no response, and no relist. The petition has merely been distributed for its first conference.

## Calibration

The committed statpack estimates a 2.5% grant rate across 2025 Term paid and IFP petitions, a 5.36% rate for paid petitions specifically, a 3.0% rate for modern petitions from the Ninth Circuit, and a 0.8% rate for petitions with no relist. The corpus examples also illustrate that recent grants commonly carried repeat distributions and specialist Supreme Court counsel, while denial remained possible even in salient, heavily supported disputes. Those are contextual signals rather than matched-case evidence. The defects here justify a much larger downward adjustment than any paid-filing uplift.

There is no plausible intervening authority in the consulted material that would make a GVR the leading disposition. Denial at or shortly after the first conference is overwhelmingly most likely.

## Significance

The 0.60 big-case score is separate from grant probability. A merits ruling on federal preemption of state cannabis regimes, aviation-safety oversight, or whistleblower standards involving Boeing could attract substantial national attention. The diffuse questions and poor vehicle reduce the likely doctrinal significance of any decision, but they do not erase the stakes of the subject matter if the Court actually reached it.
