# Bernard v. Ignelzi, No. 25-1356 — cert disposition prediction

**Prediction: deny. P(grant, GVR included) ≈ 0.015.**

## The case

Walter Bernard, a Pennsylvania attorney, sued Judge Philip Ignelzi of the
Allegheny County Court of Common Pleas under 42 U.S.C. § 1983, alleging the
judge personally directed sheriff's deputies to arrest him without a warrant
inside his home (and later orchestrated a second arrest producing nineteen
days of incarceration), all while the underlying contempt matter was on
appeal. The district court dismissed on absolute judicial immunity at the
Rule 12(b)(6) stage; the Third Circuit affirmed in a **non-precedential**
opinion (Dec. 31, 2025), holding in footnote 8 that the "judge acted as a law
enforcement officer" theory was **forfeited** because it was not raised below,
and holding in the alternative that immunity attached because Judge Ignelzi
had "the power to manage" the underlying landlord-tenant and contempt matters.
Rehearing en banc was denied January 27, 2026.

The question presented: whether absolute judicial immunity bars a § 1983
action against a state trial judge who personally directs and supervises
police officers in conducting a warrantless arrest of a litigant in his home.
The petition (counsel of record: Bruce Fein) claims a 4–1 split — the Fourth
(*Gibson v. Goldston*, 2023), Eighth (*Rockett v. Eighmy*, 2023), Sixth
(*King v. Love*, 1985), and Fifth (*Harper v. Merckle*, 1981) Circuits deny
immunity for judge-conducted law-enforcement acts under *Lo-Ji Sales v. New
York* (1979), versus the Third Circuit below.

## Docket posture at the snapshot (2026-07-17)

- Paid petition, docketed June 8, 2026 (Term 2025 docket, No. 25-1356).
- Respondent (represented by the Administrative Office of Pennsylvania
  Courts) **waived the right to respond** on July 7, 2026.
- **Distributed July 15 for the Conference of September 28, 2026** — the long
  conference. No call for a response, no CVSG, no amicus support on the
  docket, zero relists as of the snapshot.

## Base rates

From the committed statpack (modern discretionary-cert petitions,
denial-reweighted): overall grant rate ~3% (Term 2025 estimate 2.5%; Term
2024, 3.0%). Third Circuit-originating petitions: granted 2.9%. Petitions
with zero relists: 0.8% granted (this petition has not yet reached its first
conference, so the unconditional ~2.5–3% is the honest anchor, with the
relist table describing the path any grant would have to travel). No CVSG:
3.0%.

## Adjustments from the anchor

**Downward, and decisive:**

1. **Vehicle problem — forfeiture.** The Third Circuit's primary holding was
   that the *Lo-Ji Sales* executive-function theory was forfeited; the merits
   holding was an alternative in the same footnote. The Court almost never
   takes a case where the question presented was held forfeited below — the
   procedural ruling is an independent ground that would let the Court's
   resolution of the split evade the case entirely. The petition's *Joseph*
   and *Singleton v. Wulff* arguments are pleas to look past the vehicle
   defect, which is itself a tell.
2. **Non-precedential decision below.** An unpublished, non-precedential
   Third Circuit opinion that never cites *Lo-Ji Sales*, *Gibson*, or
   *Rockett* does not actually commit the circuit to anything; the claimed
   split is therefore between four circuits and one unpublished footnote.
   The Court ordinarily waits for a published, reasoned conflict.
3. **The split is distinguishable.** In *Lo-Ji Sales*, *Gibson*, and
   *Rockett* the judge was personally present in the field — searching the
   store, at the litigant's home, walking children into jail cells. Here the
   allegation is that the judge *ordered* officers to bring a litigant in a
   pending contempt matter before him. That sits much closer to *Mireles v.
   Waco* (1991), where the Court summarily *upheld* immunity for a judge who
   ordered officers to seize an attorney and haul him into the courtroom,
   even on allegations of excessive force. A fair reading is tension, not a
   square conflict — and the respondent's waiver suggests Pennsylvania's
   court administrators see it the same way.
4. **Posture signals.** Waiver of response with no call for a response and a
   routine distribution to the long conference is the classic denial path.
   Any grant would first require a CFR (adding months and a fresh hurdle),
   then relists. Nothing on the docket shows the Court has noticed the case.
5. **Substantive headwinds.** The Court is historically protective of
   absolute judicial immunity (*Stump*, *Mireles*), and the
   disgruntled-litigant flavor of a lawyer suing the judge in his own
   landlord-tenant contempt dispute is the very scenario immunity doctrine
   exists to absorb.

**Upward, modestly:** it is a paid, competently drafted, counseled petition
presenting a clean Rule 12(b)(6) posture (allegations taken as true, no
factual disputes), the circuit activity is recent (*Gibson* and *Rockett*
both 2023), and the underlying issue — judges leading warrantless raids with
categorical immunity — is genuinely cert-worthy in a better vehicle. That
keeps this above the sub-1% floor of hopeless petitions, but not by much.

The petition's alternative request for summary reversal (a GVR-adjacent
outcome) does not change much: the Court does not summarily reverse without
first calling for a response, and there is no intervening decision of this
Court that would drive a GVR (*Zorn v. Linton* predates the Third Circuit's
rehearing denial).

## Bottom line

Anchor ~2.5–3%, cut materially for the forfeiture vehicle defect, the
non-precedential decision below, the *Mireles*-shaped distinction, and the
waiver/no-CFR posture; credit slightly for counsel, the paid docket, and the
real underlying tension. **P(grant incl. GVR) = 0.015; predicted disposition:
denied**, most likely without recorded dissent, at or shortly after the
September 28, 2026 conference.

No votes predicted (a denial produces none).

## Inputs used

- Snapshot `data/cases/scotus/73452191/record/snapshots/2026-07-17.json`
  (docket entries, parties, waiver, distribution).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt`
  (29 pp., full text) — the QP, the split argument, the vehicle argument, and
  the forfeiture posture are taken from these. No brief in opposition exists
  (response waived).
- Committed `metrics/statpack.md` base rates; one `fedcourts query` for
  recent granted-petition priors; one CourtListener MCP lookup (see
  `retrieval.md`). Mode is `forward`; no outcome-revealing material was
  encountered (the case is pending, conference not yet held).
