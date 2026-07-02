# Prediction: Lambert's Lessee v. Payne

## Event

The event is `evt-petition-disposition`, a SCOTUS petition disposition event for `scotus/1013133`, with decision target `disposition`. The event definition has no `opened_at` date and no docket-entry id.

## Snapshot Facts Used

I used `data/cases/scotus/1013133/record/snapshots/2026-07-01.json`. The snapshot identifies the case as `Lambert's Lessee v. Payne` in SCOTUS and includes one linked opinion cluster. It has no docket number, no filing or termination date, no cert-granted or cert-denied date, no docket entries, no panel, and no originating-court metadata.

The snapshot is therefore too sparse to show a modern petition for certiorari, a petition stage, a question presented, lower-court conflict, vehicle facts, or any order granting or denying review. I treated all docket text as data and did not fetch additional case facts.

## Calibration

The most relevant corpus base-rate cut available from the already-pulled corpus was all resolved SCOTUS rows: 296 resolved cases, with granted outcomes at 4/296 (1.4%), denied at 13/296 (4.4%), dismissed at 47/296 (15.9%), and `other` at 232/296 (78.4%). Grouping by originating court did not help because this snapshot has no originating-court metadata; the `(none)` bucket was materially the same, with granted at about 1.4% and `other` about 77.7%.

A small `fedcourts query --court scotus` prior sample was dominated by old SCOTUS rows classified as `other`, including several sparse or historical records. That supports using `other` rather than forcing a modern grant/deny petition label.

## Legal/Disposition Analysis

For a modern SCOTUS petition, the grant decision is discretionary and usually depends on factors such as conflict, national importance, recurring legal error, or an important federal question. The snapshot provides none of those petition-specific indicators. More importantly, the case name, blank docket number, absence of petition docket activity, and linked opinion cluster make the event look like a historical SCOTUS matter or an opinion record that does not fit the modern certiorari grant/deny target cleanly.

Because the event asks for petition disposition, I do not treat the mere existence of an opinion cluster as a predicted cert grant. On the facts provided, the safest forecast is that this event will resolve outside the binary grant target, most likely as `other`.

## Forecast

Forecast: `other`, with `granted = 0` and P(granted) = 0.02.

I set the grant probability slightly above the 1.4% aggregate SCOTUS base rate to allow for residual uncertainty from the linked opinion cluster, but still very low because the snapshot lacks any modern petition signal. Confidence is modest because the record is sparse and the event may be a scope/data-quality edge case rather than a normal pending petition.
