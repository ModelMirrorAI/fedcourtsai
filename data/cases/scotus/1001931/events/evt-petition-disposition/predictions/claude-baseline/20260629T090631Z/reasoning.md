# Prediction reasoning — scotus/1001931, evt-petition-disposition

## The legal question

Will the petition in *Merchants' & Manufacturers' Bank v. Pennsylvania*
(Supreme Court docket No. 801) be granted? The event's `decision_target` is the
petition's **disposition**; consistent with the convention used for this event
kind, "granted" means the petition succeeds — the petitioner obtains the relief
sought from the Court.

## Governing standard

The governing standard depends on the era and the nature of the filing, and the
snapshot does not state either explicitly. Two regimes are relevant:

- **Discretionary certiorari (post-1925).** Review is "not a matter of right,
  but of judicial discretion" (Sup. Ct. R. 10); the Court grants only on
  "compelling reasons" (a circuit conflict, conflict with its precedent, or an
  important unsettled federal question). Across all petitions the modern grant
  rate is roughly 1%.
- **Mandatory appellate jurisdiction (pre-1925).** Before the Judges' Bill of
  1925, the Court heard most appeals and writs of error as of right and decided
  them on the merits; the meaningful "disposition" was then whether the judgment
  below was affirmed or reversed, and historically the Court affirmed more often
  than it reversed.

## Facts from the snapshot that drive the outcome

Reasoning is based solely on the provisioned snapshot
(`data/cases/scotus/1001931/record/snapshots/2026-06-29.json`). The snapshot is
unusually sparse, and the few signals it carries point strongly to a
**historical, pre-modern** matter rather than a modern discretionary cert
petition:

- **Old-style docket number.** The docket number is `801` — a bare sequential
  number with no Term-year prefix (contrast a modern docket like `01-7700`).
  This is the form used for the Court's historical appeal/writ-of-error docket.
- **No modern docket data.** `date_argued`, `date_filed`, `date_cert_granted`,
  `date_cert_denied`, `date_terminated`, and `date_last_filing` are all null,
  `docket_entries` is empty, and there is no assigned judge or panel. The only
  substantive dates (`date_created` / `date_modified`, 2014-10-30) reflect a bulk
  ingest of historical U.S. Reports material, not case activity.
- **An opinion cluster is attached.** The docket links to exactly one opinion
  cluster (id 1446332), indicating the matter produced a signed opinion — i.e.,
  it was decided on the merits rather than summarily disposed of. Per the
  contract I do **not** open that cluster to read the merits outcome: that would
  be fetching new case facts, which is prohibited; I use only the *fact that a
  cluster exists* as a structural signal.
- **Subject-matter context.** The caption (a national bank as petitioner against
  a State) fits the well-known 19th-century line of disputes over state taxation
  of national-bank shares — a class of cases the Court routinely heard on the
  merits under its then-mandatory jurisdiction. (This is general legal context,
  not a case-specific fact drawn from outside the snapshot.)

## Probability and disposition

Taken together, the signals indicate this is a historical merits case, so the
modern ~1% cert base rate does **not** apply. The honest difficulty is that the
snapshot does not let me determine the merits outcome (affirm vs. reverse), and I
am not permitted to read the opinion cluster to find it. I therefore fall back on
the structural base rate for the relevant regime: under the Court's mandatory
appellate jurisdiction, affirmance of the judgment below was more common than
reversal, so a petitioner obtaining the relief sought ("granted") is the less
likely outcome.

I assign **P(granted) = 0.35** and predict **disposition = denied**
(`granted = 0`) — i.e., the petitioner more likely than not did not obtain the
relief sought. The probability is deliberately near the middle of the range, and
**confidence is low (0.30)**, because the determinative facts (era, exact
posture, and merits outcome) are not recoverable from this snapshot. This is a
conservative call under genuine ambiguity rather than a confident one; it should
not be read as the near-certain denial that a modern, distinguishing-feature-free
cert petition would warrant.

## Votes

No panel or per-Justice vote information is present in the snapshot, and the
Court does not publish individual votes for a disposition of this kind, so no
per-judge votes are recorded.

## Note on ambiguity

Because the snapshot is too sparse to fix the era and posture with confidence, I
have flagged this on the triggering issue (#283) so a maintainer can confirm
whether `evt-petition-disposition` for a historical mandatory-jurisdiction matter
should be scored on the petition's *acceptance* or on the *merits* outcome. I did
not stall: I made the most conservative reasonable call above and finished.
