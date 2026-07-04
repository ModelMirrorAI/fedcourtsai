# Prediction: petition disposition

## Event

The event asks for the disposition of the petition in `scotus/1038383`, `United States v. Hodge`.

The event definition is a petition event with decision target `disposition`. It is unresolved and is not tied to a specific docket entry.

## Snapshot Facts Used

I used the provisioned snapshot `data/cases/scotus/1038383/record/snapshots/2026-07-04.json`.

The snapshot identifies a Supreme Court docket for `United States v. Hodge`, with short case name `Hodge`, CourtListener docket id `1038383`, court id `scotus`, slug `united-states-v-hodge`, and one CourtListener cluster reference.

The snapshot contains no docket number, docket entries, filing date, termination date, argument date, cert-grant date, cert-denial date, originating court, lower-court appeal information, party list beyond the case caption, panel, assigned judge, issue statement, petition document, merits summary, or petitioner/respondent role.

## Legal Standard And Calibration

For a Supreme Court petition disposition, a grant is discretionary. The usual grant signals are an important federal question, a conflict among lower courts, a clean vehicle, and a procedural posture that permits the Court to decide the question. A petition involving the United States can sometimes have a higher grant rate if the Solicitor General is the petitioner, but this snapshot does not identify who petitioned or what issue was presented.

I used local corpus context for calibration. Resolved Supreme Court rows in the local corpus were strongly weighted away from `granted`: among 296 resolved SCOTUS rows, about 1.4% were `granted`, 4.4% were `denied`, 15.9% were `dismissed`, and 78.4% were `other`. The term-year grouping mostly reflected missing term data and did not add useful specificity for this snapshot.

I also used `fedcourts query --court scotus --limit 10` as a qualitative check. The returned examples were mostly historical or sparse Supreme Court records, often labeled `other`, which supports treating `other` as the likely label when a SCOTUS record has a cluster reference but lacks modern petition-docket facts.

## Reasoning

The snapshot lacks the facts that usually support predicting certiorari or other petition relief: there is no question presented, lower-court decision, circuit split, filing chronology, response posture, amicus activity, relist history, or docket entry showing Court consideration. That pushes the grant probability toward the low SCOTUS petition baseline.

The caption includes the United States, which is a small upward signal because federal-government petitions can be more certworthy when the government seeks review. But the caption alone does not show that the United States is the petitioner, that the case is a modern cert petition, or that there is a vehicle-worthy federal issue. I therefore give that signal limited weight.

The one cluster reference suggests the record may correspond to a Supreme Court disposition or opinion rather than a simple denied cert petition. In this corpus, similarly sparse SCOTUS records with cluster references are often categorized as `other`, likely because the underlying proceeding or historical record does not map cleanly to a modern petition grant/denial label.

I predict `other`, with `P(granted) = 0.09`. This is above the raw 1.4% resolved SCOTUS grant base rate because the United States caption and cluster reference leave some chance of action beyond denial, but still low because the snapshot provides no case-specific certworthiness facts.

No per-Justice votes are predicted. The snapshot does not identify votes, and petition-stage vote information is not available from the provided facts.
