# Rationale — P(grant) = 0.006

**Inputs:** I read the snapshot `record/snapshots/2026-10-24.json` and `record/context.json` (mode `forward`, band `baseline` under `sal-v4`, distribution_count 0, no CVSG). No documents were provisioned under `record/documents/`, so there is no petition, QP or BIO text. I worked from the docket metadata alone.

**What the record shows:**
- This is a paid petition, docketed October 23, 2026.
- The lower court is the Fourth Circuit (No. 25-2149), decided June 23, 2026, with rehearing denied July 21, 2026.
- The petitioner is self-represented: the attorney field names the petitioner, and the snapshot is marked not counsel of record.
- The respondent is a private medical practice. The single docket entry is the filing itself.

**Anchor:** The petitioner is private, so the caption-class floor is `baseline`, which is also the band context.json gives. I pooled `baseline`'s bracketed `reached` rate over the prior Terms the sal-v4 table shows (2017–2025). The per-Term figures run 3.9%–5.9%, and the weighted pool comes to roughly 5%. I did not use Term 2026's row (1.4%, n=146), because that row contains this case's own Term.

**Adjustment:** I moved well below the anchor. The `baseline` floor covers all private paid petitions, most of which have counsel and often experienced Supreme Court counsel. Self-represented paid petitions are granted far more rarely, a small fraction of a percent. That figure is general knowledge, not a committed statpack cut. The pack does not split by representation, so the size of this discount is my judgment. Nothing on the docket points the other way: no amici, no government party, no related cases. I settled on 0.6%, and the main way I would be wrong is an unforeseen GVR.

**Claims:**
- `relist-increment` 0.95: from zero distributions, almost every paid petition reaches conference at least once. The remaining 5% covers withdrawal, dismissal, or the snapshot never catching the distribution.
- `cvsg-increment` 0.002.
- `summary-disposition-route` 0.35, conditional on a grant.
- `dissent-from-denial` 0.01.

**Uncertainty:** I never saw the petition text. If it raises a real circuit split, my number is too low, though a self-represented paid filing rarely does. I made no CourtListener retrieval and used committed base rates only.
