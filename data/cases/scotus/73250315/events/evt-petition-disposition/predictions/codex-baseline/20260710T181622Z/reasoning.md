# Prediction: petition disposition

## Prediction

I predict that the petition will be denied, with `P(granted) = 0.16`.

## Event And Record Used

The event definition identifies an unresolved SCOTUS petition-disposition event for `scotus/73250315`, titled `Isaac Nformangum v. United States`, opened on April 27, 2026.

I used the provisioned snapshot `data/cases/scotus/73250315/record/snapshots/2026-07-10.json`, the provisioned `questions-presented.txt`, the provisioned `petition.txt`, and `record/documents/documents.json`. The cell is in forward mode. I did not read the outcome artifact.

The snapshot shows docket number `25-7259`, Term 2025, an IFP cert petition from the Fifth Circuit, and a petition filed April 1, 2026. The United States initially waived response on May 21, 2026. The petition was distributed for the June 11, 2026 conference, but on June 8, 2026 the Court requested a response. The response deadline was later extended to August 7, 2026. No brief in opposition was provisioned.

## Question Presented

The petition asks whether an indictment's failure to allege an essential element of a criminal offense is structural error requiring automatic reversal, or instead is subject to harmless-error review. The petition argues that the Fifth Circuit found the indictment failed to state the mens rea element for an 18 U.S.C. 875(c) threat count, but affirmed under harmless-error review.

The petition frames the issue as an entrenched split: the Fourth and Ninth Circuits treat omission of an essential indictment element as structural, while several other circuits, including the Fifth, apply harmless-error review. It also notes that the Court previously granted certiorari in `United States v. Resendiz-Ponce` on a related issue but did not ultimately decide the structural-error question.

## Legal Standard And Calibration

Certiorari is discretionary. The strongest grant signals are a real conflict among courts, federal importance, recurring legal consequences, a clean vehicle, and a developed adversarial presentation. The committed statpack's broad resolved SCOTUS rows show a low grant base rate, about 1.4% for resolved SCOTUS cases in the available labeled corpus. The rendered statpack in this checkout does not include the prompt's named modern discretionary-cert heading, so I treated the broad SCOTUS row as a low baseline rather than a precise modern cert estimate.

This case has two important positive signals. First, the Court requested a response after the Solicitor General waived, which is materially stronger than an ordinary waiver-and-denial path. Second, the petition presents a legal split on a criminal procedure issue with a plausible constitutional dimension, and it asserts that the lower court directly held the indictment failed to state the offense but affirmed anyway.

The negative signals are still substantial. The petition is IFP, the lower-court decision is unpublished, there is no BIO yet, no amici are provisioned, no relist is shown, and the government's eventual response could argue that the vehicle is poor because the evidence of subjective intent was strong and the sentence was one year of probation. The petition also depends on the Court wanting to revisit a technical indictment-error question where most circuits have apparently accepted harmless-error review.

## Reasoning

I move the grant probability far above the ordinary cert baseline because a response request after waiver often means at least one Justice or the Clerk's Office sees a nontrivial issue, and because the petition identifies a clean doctrinal disagreement between structural-error and harmless-error treatment.

I still predict denial. At the snapshot date, the Court had not received the government's merits-stage opposition. Without the BIO, there is no way to assess vehicle objections, forfeiture/preservation arguments, the factual basis for harmlessness, or whether the government will concede any conflict. The case's unpublished posture, IFP status, and modest sentence make it less likely to be the vehicle the Court chooses for a broad Fifth Amendment grand-jury rule.

The best forecast is therefore an elevated cert petition that remains more likely than not to be denied. I assign `P(granted) = 0.16`: meaningfully above the baseline because of the response request and asserted split, but not close to even odds absent stronger docket signals such as a filed BIO that confirms the split, amicus support, a relist pattern, or a clearer vehicle.

## Votes

I do not predict individual Justice votes. Cert-stage votes are not exposed in the provisioned record, and the petition has not yet reached a fully briefed conference posture in the snapshot.

## Limitations

Corpus prior queries were attempted but could not reach the remote corpus because network name resolution failed in this sandbox. I proceeded with the provisioned docket, petition documents, and committed statpack base rates. No outcome-revealing material was encountered.
