# Prediction reasoning — scotus/102484, evt-petition-disposition

## Legal question

The event is a `petition` with `decision_target: disposition`: predict how the
Supreme Court disposed of the petition — granted (taken up for plenary review)
versus denied/dismissed/withdrawn.

## Governing standard

Review by certiorari is discretionary, and the base rate of grants across
petitions is very low (a few percent). That base rate is the right anchor for a
petition drawn at random from the certiorari docket; it is displaced when the
record itself shows the case reached the Court's plenary docket.

## Facts from the snapshot

The provisioned snapshot (`record/snapshots/2026-07-02.json`) is a sparse stub:
no docket entries, no filed/argued/terminated dates, no cert-granted or
cert-denied dates, and no panel. What it does contain is decisive:

- Case name **"United States v. Munsingwear, Inc."** in the Supreme Court.
- Docket number **"23 and 24"** — two low, sequential numbers in the older
  merits-docket numbering style, i.e. a *consolidated pair of argued cases*.
  Consolidation under low merits-docket numbers itself implies the Court took
  the cases up rather than denying at the certiorari stage.
- A linked **opinion cluster** (`clusters: [.../clusters/104822/]`) — the docket
  is associated with a published opinion, which for a petition event points to a
  merits disposition rather than a one-line denial.
- `date_cert_denied` is null (as is `date_cert_granted`, so this field carries
  little weight either way on a stub this sparse).

I predict only from this snapshot; I did not fetch the cluster contents or any
new docket facts.

## Recognition of the case (and a candor note on backtest leakage)

The caption identifies a canonical precedent within my legal-background
knowledge: *United States v. Munsingwear, Inc.*, 340 U.S. 36 (1950), the
foundational decision on vacatur of judgments that become moot pending review
("Munsingwear vacatur"). The United States sued under wartime price-control
regulations for an injunction and for treble damages; the injunction case
became moot on appeal after the commodity was decontrolled, the Eighth Circuit
dismissed that appeal as moot, and the district court then dismissed the two
damages actions (Nos. 23 and 24) as res judicata. The Supreme Court granted
certiorari on the res judicata question and affirmed, holding the government
had failed to protect itself by moving to vacate the mooted judgment. The
petition disposition was therefore, as a historical matter, a **grant** (the
petitioner lost on the merits, but the event's decision target is the
disposition of the petition, not merits success).

Because this is a decided, well-known historical case, my recognition of it is
unavoidable training-data leakage: for this cell the backtest measures recall
plus calibration, not true ex-ante forecasting. I flag this in `flags.json` so
maintainers can weigh the cell accordingly. Even setting recognition aside, the
snapshot-internal signals (consolidated merits docket numbers plus a linked
opinion cluster) independently support a grant prediction well above the cert
base rate.

## Base rates consulted

`fedcourts stats --court scotus` shows the corpus's resolved SCOTUS labels are
dominated by `other` (232/296), with `granted` at only 4/296 — but that resolved
set is small and does not isolate cert-stage petition outcomes for this era.
Grouping by `term_year` puts 267 of the 296 resolved cases in a "(none)" bucket
(these historical dockets carry no filed dates), so no era-specific cut was
available for the 1950 Term. A `fedcourts query --court scotus` sample confirmed
historical SCOTUS priors in the corpus are similar sparse stubs labeled mostly
`other`. I treated the modern few-percent cert grant rate as the anchor and let
the case-specific signals dominate.

## Probability and residual uncertainty

I set `probability` (P(granted)) to **0.94**, `granted = 1`,
`predicted_disposition = granted`, `confidence = 0.8`. The residual mass is not
about the historical fact — certiorari was granted — but about label mapping:
how the reconciler labels a 1950-Term petition disposition given
CourtListener's sparse cert-stage data for historical dockets (the corpus's
resolved labels skew heavily to `other`, so a decided merits case could
conceivably be labeled something other than `granted`).

No per-judge votes are predicted: per-justice certiorari votes were not
recorded publicly in this era and the snapshot exposes no panel.
