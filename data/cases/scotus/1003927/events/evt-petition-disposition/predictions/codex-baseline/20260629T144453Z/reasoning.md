# Prediction: evt-petition-disposition

## Legal Question

The event asks for the disposition of a petition in `State of Oklahoma v. State of Texas (United States, Intervener)`, Supreme Court docket `13`. I treat "granted" as the Court allowing the petition to proceed, rather than denying leave or otherwise disposing of it without reaching the merits.

## Governing Standard

For an original Supreme Court matter between states, the Court has original jurisdiction, and state-versus-state disputes are the strongest candidates for the Court to exercise that jurisdiction. Even so, the Court generally screens original petitions and can deny leave where the controversy is not sufficiently serious, where another forum is adequate, or where the pleading posture is not suitable for immediate Supreme Court adjudication.

## Snapshot Facts Used

The snapshot used was `data/cases/scotus/1003927/record/snapshots/2026-06-29.json`.

The available facts are sparse. The case is in the Supreme Court, captioned as a dispute between Oklahoma and Texas, and the United States is listed as an intervener. The docket number is `13`. The snapshot has no docket entries, no panel, no cert-grant or cert-denial date, no termination date, and no lower-court appeal source. It does include one CourtListener opinion cluster reference.

## Reasoning

The strongest grant signal is the posture: a state-versus-state original action is the category most likely to receive Supreme Court treatment, and the United States being listed as intervener suggests the dispute had moved beyond a bare, facially deficient petition. The opinion-cluster reference is also consistent with the matter having generated judicial action beyond an unexplained denial.

The counterweight is the thin snapshot. There are no docket entries describing the petition, no dates showing that leave was granted, and no details about the subject matter or procedural history. Because the event definition is generic and unresolved, I avoid treating the cluster reference as conclusive proof of a grant.

On balance, I predict that the petition was granted, with a probability of 0.66. Confidence is only 0.42 because the prediction rests on structural signals rather than a complete docket history.

## Votes

No per-justice votes are predicted. The snapshot does not identify a panel or provide enough vote-specific information.
