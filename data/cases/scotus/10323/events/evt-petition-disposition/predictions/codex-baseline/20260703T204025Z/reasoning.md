# Prediction: Auflick v. Wainwright

## Event

The event asks for the disposition of the Supreme Court petition in `scotus/10323`, captioned `Auflick v. Wainwright`, docketed as `979, Misc`. I interpret `granted` as the Court accepting the petition for review. A denial, dismissal, withdrawal, or other procedural termination is a non-grant for the binary field.

## Snapshot Used

I used `data/cases/scotus/10323/record/snapshots/2026-07-03.json`. I did not fetch new docket facts.

The snapshot identifies a Supreme Court docket with the case name, docket number, CourtListener docket id `10323`, and one linked opinion-cluster resource. It has no docket entries, no filing date, no argument date, no termination date, no cert-grant or cert-denial date, no lower-court or originating-circuit metadata, no petition-stage order text, and no vote or panel information.

## Governing Standard And Baseline

Supreme Court petition review is discretionary. The ordinary prior for a petition is denial or another non-grant disposition because the Court grants only a small fraction of petitions. The local corpus base-rate check for resolved SCOTUS petition events was consistent with that caution: among 296 resolved SCOTUS petition events, 4 were labeled `granted`, 13 `denied`, 47 `dismissed`, and 232 `other`.

That aggregate prior is imperfect for this sparse historical docket. The corpus query results show old Supreme Court records with linked opinion clusters across grants, denials, dismissals, and other extraordinary-writ or historical procedural postures. The cluster reference therefore matters, but it is not enough by itself to infer a grant.

## Case-Specific Assessment

The case-specific snapshot does not show a cert grant date, an argument date, merits briefing, lower-court conflict, federal question, or any other direct grant signal. The `Misc` docket style is also consistent with miscellaneous or in forma pauperis petition practice, where denial is the ordinary outcome absent a strong visible reason for review.

The strongest counter-signal is the linked opinion-cluster resource. But because the snapshot does not expose the cluster contents, and because similar historical corpus rows include non-grant dispositions with clusters, I give that signal limited weight. On this record, the conservative prediction is a denied petition rather than a grant or merits disposition.

I predict `denied`, with `P(granted) = 0.02`. Confidence is only moderate because the snapshot is sparse and historical SCOTUS labeling sometimes routes non-modern petition outcomes to `other` rather than `denied`.

I do not predict Justice-by-Justice votes. The event is petition disposition, and the snapshot contains no vote data tied to the petition decision.
