# scotus/73272995 — Bylsma v. United States District Court for the Middle District of Pennsylvania (No. 25-5082)

## Prediction

**Disposition: dismissed. P(granted) = 0.001. granted = 0.**

## Important caveat: the provisioned snapshot already shows the effective outcome

This is a forward-mode cell and `event.yaml` says `resolved: false`, but the
provisioned baseline snapshot (`record/snapshots/2026-07-12.json`) already
carries the case to its effective end: the IFP motion was denied on
October 6, 2025, the petitioner was given until October 27, 2025 to pay the
Rule 38(a) docketing fee and refile in Rule 33.1 booklet format, no compliant
refiling ever appeared on the docket, and the final entry (January 15, 2026)
reads "Case considered closed." The event stayed open in the pipeline only
because that closure language carries no machine-readable cert disposition. I
encountered this in the provisioned input itself, not via retrieval; it is
disclosed in `flags.json` so the evaluation can discount the cell. The
pre-decision analysis below reaches the same call independently.

## The legal question and governing standard

The event is the disposition of a petition for a writ of certiorari,
governed by Supreme Court Rule 10: review is discretionary and granted only
for compelling reasons — a genuine circuit split, a conflict with this
Court's precedent, or an important undecided federal question. A companion
gate for an IFP filer is Rule 39 (and Rule 39.8 for frivolous or abusive
filings): if leave to proceed in forma pauperis is denied, the petition is
never adjudicated unless the petitioner pays the fee and complies with
Rule 33.1.

## Pre-decision facts that drive the outcome

From the snapshot, the docketed petition (May 12/July 10, 2025), and the
provisioned petition text and questions-presented section:

- **Pro se, IFP, no counsel of record.** The petitioner represents himself;
  the docket is fee-class IFP (`sJsonCaseType: "IFP"`). In the current-Term
  corpus slice, resolved IFP petitions show **zero grants** (62 resolved:
  96.8% denied, 3.2% dismissed).
- **The question presented is not a certworthy legal question.** The QP asks
  whether "a Real Estate and Bankruptcy Fraud racket operated by the
  Pennsylvania Judicial Elite" — allegedly protected by the Middle District
  of Pennsylvania and the Third Circuit, and said to conceal attempted
  murders — is "compelling enough reason for THIS COURT to grant review."
  This is a conspiracy narrative, not a disputed question of federal law; it
  presents no circuit split and no legal issue on which review could be
  granted.
- **The respondent is the lower court itself.** The caption names the
  district court (the petition's internal caption names individual
  respondents), the posture of a mandamus-style grievance against the judges
  who ruled below (Third Circuit No. 25-1307, decided March 11, 2025). The
  cited authorities are recusal/mandamus cases (In re Murchison, In re
  Asbestos School Litigation), a class of petition the Court essentially
  never takes.
- **No merits-side signals.** One conference distribution (9/29/2025), no
  relists, no CVSG, no amici, no response on file.

## Base rates and priors

The committed statpack's modern discretionary-cert slice puts the overall
grant rate at ~4.9% (denial-reweighted, Term 2025), driven entirely by paid
petitions (~7.2% of paid vs 0.0% of IFP resolved grants). A `fedcourts query`
for 2020s SCOTUS petitions resolved as "dismissed" returns exactly this
profile: pro se petitions terminated procedurally without any order on the
merits. This petition sits at the bottom of the IFP pool even before the
procedural default.

## Why "dismissed" rather than "denied"

Predicting as of the pre-decision record: the realistic outcomes were (a)
cert denied at conference, or (b) IFP denied under Rule 39 with the case
closing on failure to pay — a procedural termination with no order ever
acting on the petition itself. A petition attacking the integrity of the
courts below, with a non-legal QP, is the classic Rule 39.8 profile, and the
docket in fact took path (b): IFP denied, fee never paid, case closed. Since
no denial of certiorari was (or now ever will be) entered, the closure maps
to **dismissed** in this project's disposition vocabulary — termination
without adjudication — rather than **denied**. "Denied" is the runner-up
label if the outcome former treats fee-default closures as constructive
denials; either way `granted = 0`.

## Probability

P(granted) = 0.001. The IFP-class base rate this Term is 0/62; the petition
presents no certworthy question; and the docket already shows the case
closed after a Rule 39 IFP denial with no compliant refiling. The residual
0.1% covers only record error or an extraordinary reopening. Confidence 0.97
on the categorical call, with the residual mass on "denied" as the
alternative label for the same non-grant outcome.

No per-judge votes are predicted: no recorded vote occurs on an IFP
denial/closure of this kind.
