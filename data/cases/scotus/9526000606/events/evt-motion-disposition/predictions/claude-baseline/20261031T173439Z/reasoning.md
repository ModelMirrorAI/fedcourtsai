# Reasoning — P(unqualified grant) = 0.012

**Inputs.** Snapshot `record/snapshots/2026-10-17.json` (arrival-position cut, one
proceedings entry: application for a stay of removal submitted to Justice Alito, Oct 16,
2026). No `record/documents/` were provisioned, so I had no application text. I do not
know what grounds the application raises or which order below it targets beyond the
Third Circuit case number 25-2933. The counsel of record is the lead applicant herself
(Gina P. Silva), so the filing is self-represented. Context: forward mode, `band: null`,
no response requested, not referred, 0 amicus.

**Anchor.** Statpack, "The interim docket (applications)". I pooled the substantive
resolved slice over application-Terms 2016–2025 (strictly before 2026, within the
ten-Term window): 160 granted / 1466 resolved ≈ 10.9%. That clears the floor of 50.
The caption reads as the current estimator caption (a scored base rate).

**Adjustment.** That pool mixes government and high-profile applications, where grants
cluster, with routine individual ones. A self-represented immigration stay of removal
sent to a single Circuit Justice is about the least likely substantive application to
be granted. In my understanding of practice these are denied almost without exception,
and usually without a called-for response. The Nken standard (likelihood of success
plus irreparable harm), filtered through the cert-worthiness of an individual
removal-order review, is rarely met at this level. I therefore go far below the anchor,
to ~1%. I leave a small residual for an administrative stay or an unusual underlying
issue I cannot see without the application text.

**Uncertainty.** The main one is the missing application text. A represented filing,
or one tied to a pending circuit split on a removal question, would move me up a few
points. The snapshot also shows a `DocketedDate` of Oct 28, 2026, later than its own
Oct 17 date (provenance `truncated`). I read this as the docketing header being refreshed
while the entries were cut at arrival. It does not change the forecast.

**Corpus query.** One query of recent denied SCOTUS substantive applications returned
mostly individual/pro se applications of the same shape. It is consistent with the
adjustment, but it is shape only, not a conditioned rate.
