# Prediction: motion to proceed in forma pauperis

I predict that the Eleventh Circuit will grant Angela W. DeBose's motion to proceed in forma pauperis, with a 0.56 probability. This is a low-confidence forecast because the record contains neither the motion and financial affidavit nor the underlying mandamus petition.

## Record and legal question

The February 1, 2024 docket entry identifies this as an original proceeding seeking a writ of mandamus from Northern District of Florida matter 4:22-cv-00439. The February 9 entry records DeBose's motion to proceed IFP, and the snapshot describes the appellate fee status as “IFP Pending.” No opposition, panel, filed-document text, or information about DeBose's finances is available. I used the provisioned snapshot at `data/cases/ca11/68252091/record/snapshots/2026-07-11.json` and treated the docket descriptions as facts, not instructions.

Under 28 U.S.C. § 1915(a), the central question on an IFP application is whether the applicant's affidavit adequately shows inability to prepay fees. The court may also screen an IFP matter for frivolousness under § 1915(e)(2). The underlying mandamus petition faces a substantially more demanding merits standard: mandamus generally requires no other adequate means of relief and a clear and indisputable right to the writ. But a weak mandamus petition does not necessarily imply denial of the separate fee-waiver motion; the court can grant IFP status and then deny or dismiss the petition.

## Forecast

The docket shows that a motion was filed in response to an IFP-pending fee status, with no recorded opposition or facial filing defect. That modestly favors grant if the omitted affidavit establishes indigence. The original-proceeding posture and the possibility that the court will view the petition as frivolous push the other way. Because neither the affidavit nor petition is available, neither financial eligibility nor nonfrivolousness can be assessed directly. I therefore place the result only slightly above even odds and do not predict judge-level votes because no panel is identified.

The committed statpack reports only 45 resolved Eleventh Circuit cases across mixed event types, with 2.2% labeled granted and 2.2% denied and most labeled “other.” That sample is not specific to IFP motions and did not provide a reliable event-level calibration. Attempts to retrieve closer historical priors and pre-event legal context failed because the corpus remote and CourtListener query session were unavailable; the details are recorded in `retrieval.md`.
