# Prediction: petition disposition

## Event

The event asks for the disposition of the petition in `scotus/1033955`, `Bartemeyer v. Iowa`.

The event definition is a petition event with decision target `disposition`. It is unresolved and is not tied to a specific docket entry.

## Snapshot Facts Used

I used the provisioned snapshot `data/cases/scotus/1033955/record/snapshots/2026-07-03.json`.

The snapshot identifies a Supreme Court docket for `Bartemeyer v. Iowa`, with short case name `Bartemeyer`, CourtListener docket id `1033955`, court id `scotus`, slug `bartemeyer-v-iowa`, and one CourtListener cluster reference.

The snapshot contains no docket number, docket entries, filing date, termination date, argument date, cert-grant date, cert-denial date, originating court, lower-court appeal information, party list beyond the case name, panel, assigned judge, issue statement, or merits summary.

## Legal Standard And Calibration

For a Supreme Court petition disposition, the grant question is discretionary. The usual indicators are a conflict among courts, an important federal question, a suitable vehicle, and a procedural posture that permits the Court to reach the issue. If the filing is better understood as an extraordinary writ or older non-certiorari proceeding, the disposition may not map cleanly to an ordinary cert grant or denial.

I used local corpus context for calibration. Resolved Supreme Court rows in the local corpus were strongly weighted away from `granted`: among 296 resolved SCOTUS rows, about 1.4% were `granted`, 4.4% were `denied`, 15.9% were `dismissed`, and 78.4% were `other`. The term-specific cut for the current SCOTUS term had no resolved rows, and the snapshot lacks an originating court, so those cuts did not add useful specificity. Grouping by missing term and missing originating court preserved essentially the same low grant rate and high `other` share.

I also used `fedcourts query --court scotus --limit 5` as a qualitative check. The returned examples were older or sparse SCOTUS records, mostly labeled `other`, which is consistent with using `other` for records that have a Supreme Court cluster but do not present a modern petition docket with cert dates.

## Reasoning

The snapshot does not contain the facts that usually support predicting a cert grant: there is no question presented, split signal, lower-court decision, filing chronology, amicus activity, relist history, or docket entry showing consideration by the Court. That pushes the grant probability close to the very low SCOTUS base rate.

The one cluster reference is a modest signal that the record may correspond to some Supreme Court disposition or opinion rather than a simple petition denial. But without cert dates or docket entries, that signal does not justify predicting `granted`. In this corpus, similarly sparse SCOTUS records with cluster references are more commonly coded as `other`, likely because the underlying proceeding does not fit an ordinary modern petition disposition label.

I therefore predict `other`, with `P(granted) = 0.08`. This is above the raw 1.4% resolved SCOTUS grant base rate because the cluster reference leaves some chance that the Court took action beyond denying a petition, but it remains low because the snapshot lacks any case-specific certworthiness or procedural facts.

No per-Justice votes are predicted. The snapshot does not identify votes, and petition-stage vote information is not available from the provided facts.
