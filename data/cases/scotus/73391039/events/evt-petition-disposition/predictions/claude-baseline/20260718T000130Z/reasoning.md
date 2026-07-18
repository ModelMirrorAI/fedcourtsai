# Foley v. Orange County, Florida (No. 25-1308) — cert disposition

**Prediction: denied. P(grant, GVR included) ≈ 0.004.**

## The case

David W. Foley, Jr., et ux., petition pro se from the Eleventh Circuit's
unpublished affirmance in No. 24-14143 (decided October 29, 2025; rehearing
denied December 23, 2025). Docket metadata from CourtListener shows the appeal
arose from a Middle District of Florida civil-rights action, *Foley v. Orange
County*, 6:22-cv-00456 (42 U.S.C. § 1983, filed 2022), against Orange County
and six individual county employees — the same individuals (Boldig, Gordon,
Gould, Hossfield, Relvini, Smith) named as respondents here. The district
docket also shows a September 2025 judgment on attorney fees below, and the
petitioners have litigated against this county repeatedly since at least 2012
(e.g., 6:12-cv-00269). The petition PDF is a scanned filing whose text could
not be extracted (`empty_text: true` in `documents.json`), so the questions
presented are not directly readable; the analysis rests on the docket
snapshot, the lower-court record metadata, and base rates. Nothing in the
record suggests the QPs present anything beyond case-specific error
correction, and every observable structural signal is negative.

## Governing standard

Certiorari is discretionary and granted only for compelling reasons (Sup. Ct.
R. 10) — a genuine circuit split, an important and recurring federal question,
or a decision in conflict with this Court's precedent. Fact-bound error
correction from an unpublished court of appeals affirmance is the paradigm
denial.

## Signals from the snapshot

Working against any grant:

- **Pro se petitioner as own counsel of record.** Paid rather than IFP, but
  self-represented petitions essentially never secure plenary review absent an
  extraordinary legal question; the scanned, non-typeset filing confirms no
  professional Supreme Court counsel is involved.
- **All respondents waived response** (both the individual respondents on
  June 23, 2026 and Orange County itself), and as of the July 17, 2026
  snapshot the Court has **not called for a response**. The Court's settled
  practice is to request a response before granting; a petition distributed
  without one is on the denial track.
- **Distributed July 1, 2026 for the September 28, 2026 long conference** —
  the opening-of-Term conference at which the summer's accumulated petitions
  are cleared, overwhelmingly by denial. Zero relists or other engagement
  signals exist, and no CVSG.
- **Unpublished Eleventh Circuit decision** with no indication of a dissent,
  en banc activity (rehearing denied), or split; no amici at any stage.
- **Repeat local-government litigation** with a fee judgment against the
  plaintiff below — a posture the Court has no appetite to review.

Nothing works in favor: no split alleged that we can observe, no supporting
amici, no government involvement, no companion case pending.

## Base rates and the adjustment

From the committed statpack (live/historical modern discretionary-cert
slice): overall modern cert grant rate ~3%; Term 2025 paid petitions grant at
~5.4% and IFP at ~1.1%; petitions with **zero relists** grant at ~0.8%; the
Eleventh Circuit's modern grant rate is ~4.4%. (No salience-band table is
present in the committed statpack, so I anchored on the relist-0 and fee-class
cuts directly.)

This is a paid petition, but the paid-class ~5.4% is dominated by counseled
petitions; the correct cell here is paid-but-pro-se, no response requested,
no relist, long-conference distribution. Each of those conditions
independently pushes well below the relist-0 rate of 0.8%, since that bucket
still includes counseled petitions that drew responses. A GVR is also
implausible: no obviously intervening decision touches a fact-bound § 1983
affirmance. I set **P(grant incl. GVR) = 0.004** — a small residual for the
unread QPs and any unnoticed vehicle value — and predict **denied**, most
likely in the order list following the September 28, 2026 conference.
Dismissal/withdrawal paths (settlement, procedural default) carry the usual
small residual mass but are far less likely than a straight denial.

## Big-case score

0.03. A one-plaintiff § 1983 dispute with a single county, unpublished below,
no amici, no press posture — negligible stakes even in the unlikely event of
a grant.
