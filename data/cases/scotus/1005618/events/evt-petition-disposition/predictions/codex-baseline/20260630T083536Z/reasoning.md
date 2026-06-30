# Prediction: Ex Parte Transportes Maritimos

## Event

The event is the petition disposition for `scotus/1005618`, titled *Ex Parte Transportes Maritimos*. The target is whether the petition will be granted, denied, dismissed, or otherwise disposed.

## Snapshot Used

I used `data/cases/scotus/1005618/record/snapshots/2026-06-30.json`. I did not fetch new docket facts. The snapshot identifies a SCOTUS case with docket number `26, Original`, case name *Ex Parte Transportes Maritimos*, a linked CourtListener cluster, and no docket entries. It has no filing date, no cert-grant date, no cert-denial date, no argument date, no termination date, no lower-court source, and no panel or vote information.

## Governing Standard

For this event, `granted` means the Court allows the petition or application to proceed in a way that counts as a grant, rather than refusing relief, dismissing it, or resolving it in another non-grant posture. A SCOTUS original or extraordinary-writ petition faces a demanding discretionary threshold. The Court generally grants such relief only where the petitioner shows a clear right to the writ or an appropriate exercise of the Court's original jurisdiction, and ordinary errors or matters better handled through another route usually lead to denial, dismissal, or another non-grant disposition.

## Case-Specific Signals

The strongest signal against a grant is the absence of any affirmative grant marker in the snapshot. There are no docket entries, no grant or argument dates, and no description of an issue that would justify original or extraordinary relief. The case is also not presented as an ordinary merits docket with briefing or argument activity.

The main countervailing signal is the linked cluster. In a sparse historical SCOTUS record, a cluster can mean the case produced a published opinion or order rather than a bare docket denial. That makes a simple modern-certiorari denial baseline less apt. But the snapshot does not reveal the cluster contents, and the corpus priors for resolved SCOTUS petition-disposition events show `granted` as rare. In the local corpus, resolved SCOTUS petition-disposition priors excluding this case had 4 `granted` outcomes out of 244; among docket numbers marked `Original`, the split was 1 `granted`, 5 `dismissed`, 4 `other`, and 1 `denied`.

Because this case is docketed as `Original` and has a cluster but no visible grant signal, I treat `other` as more likely than a clean `denied` label, while still predicting no grant. The exact non-grant label is uncertain because the snapshot has no docket text explaining the petition or final order.

## Probability and Disposition

I predict `other`, with `P(granted) = 0.08`. This is above the broad SCOTUS petition grant prior because original-writ cases in the corpus include a small number of grants and the linked cluster suggests a non-routine disposition. It remains low because the snapshot lacks any concrete grant, argument, or merits-progress marker. I do not provide Justice-by-Justice votes because the snapshot contains no vote data.
