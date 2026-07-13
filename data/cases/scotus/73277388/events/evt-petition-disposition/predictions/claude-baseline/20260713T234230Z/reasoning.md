# Genesis Financial Solutions, Inc. v. Ford, No. 25-311 — cert disposition

**Prediction: denied (P(granted) = 0.28).** A well-above-baseline grant
probability driven by strong docket signals, but denial remains the single
most likely disposition.

## The legal question

Whether the FAA, 9 U.S.C. § 2, preempts Maryland's *Cheek* rule requiring an
arbitration clause inside an otherwise-valid contract to be supported by its
own separate consideration. The petition (Sidley Austin) frames a lopsided
split: the Fourth Circuit alone (Noohi v. Toll Bros., 708 F.3d 599; Johnson v.
Continental Finance Co., 131 F.4th 169) enforces the arbitration-specific
consideration requirement, against contrary holdings of the First (Soto),
Second (Distajo), Third (Harris), Sixth (Wilson), and Eighth (Barker)
Circuits. Substantively this sits squarely in the line of Concepcion /
DIRECTV / Kindred Nursing equal-treatment cases in which this Court has
repeatedly — sometimes summarily — struck down state rules singling out
arbitration clauses.

## Facts from the snapshot that drive the outcome

Signals pointing toward a grant:

- **Call for a response (Nov 6, 2025).** Respondent Ford twice tried to waive
  (waivers not accepted for filing); the case was distributed for the
  11/14/2025 conference and the Court then requested a response. A CFR is a
  Court-initiated interest signal that empirically lifts paid-petition grant
  odds by roughly an order of magnitude over the ~2–3% baseline.
- **Petition-stage amicus** from the American Bankers Association (Orrick),
  plus support from nominal respondent Spring Oaks (Rule 12.6 letter). The
  U.S. Chamber supported petitioner's position below.
- **Paid petition, experienced SCOTUS counsel**, clean interlocutory posture
  (direct appeal from denial of a motion to compel under § 16(a)(1)(B)), and a
  genuine, mature circuit conflict.
- **A live companion vehicle.** Johnson v. Continental Finance Co., No. 25-34
  (docketed July 10, 2025) presents the same question from the same circuit.
  Per CourtListener (record last updated May 7, 2026), Johnson was still
  pending — neither granted nor denied — some ten months after docketing. A
  paid petition surviving that long without denial almost always means
  serious consideration (relists, a hold, or a CVSG). Statpack cuts show what
  such signals do to grant rates: 2 relists → ~39% grant, CVSG → ~28%.

Signals pointing away from a *granted* disposition for **this docket**:

- **This petition is riding second.** Johnson is the earlier-filed, published,
  divided-panel decision (with a Niemeyer dissent); the Genesis Fourth Circuit
  opinion is short and unpublished, and rehearing en banc was denied as
  untimely. If the Court takes the question, Johnson is the more natural
  merits vehicle, with Genesis held. A hold ends in GVR (scored *granted*
  under the corpus convention) only if the petitioner side prevails in
  Johnson; if the Fourth Circuit were affirmed, Genesis ends *denied*.
- **The extraordinary BIO schedule.** Respondents' time to respond has been
  extended four times — Dec 8, 2025 → Jan 7 → Feb 6 → May 7 → **Oct 30, 2026**,
  the last "with petitioner's consent." A petitioner consenting to push its
  own petition past the next Term's opening is consistent with waiting out
  Johnson (e.g., an SG brief there) — but also consistent with settlement
  discussions, which would end this docket in dismissal/withdrawal.
- **Base rates.** Modern discretionary cert petitions grant at ~2.4–3%
  (Terms 2024–25); Fourth Circuit petitions at ~5.5%. Every grant-side signal
  above is an uplift on a very low prior. And this Court does deny
  consumer-finance petitions with apparent splits — it declined the related
  rent-a-bank/NBA-preemption question in Conti in May 2026.

## Probability construction

Rough scenario weights:

- Court takes the question (grants Johnson and/or Genesis, or summarily
  reverses): ~35%. Conditional on that, Genesis ends "granted" either by
  being granted/consolidated (~20%) or by GVR after a petitioner-side merits
  win (~80% hold-for-Johnson path × ~80% reversal likelihood given this
  Court's FAA-preemption record) — together ~0.84.
- Outright denial of both petitions: ~50%.
- Settlement → dismissed/withdrawn: ~12%.
- Other: ~3%.

P(granted) ≈ 0.35 × 0.84 ≈ **0.28**. The most likely single disposition is
still **denied** (~50–55% mass), so `granted = 0` and
`predicted_disposition = denied`, with the probability carrying the
substantial grant-side risk. No per-Justice votes are predicted for a cert
disposition.

Timing note: with the BIO due October 30, 2026 and a likely hold for Johnson,
this event probably does not resolve before late 2026, plausibly mid-2027.

## Inputs used

Snapshot `record/snapshots/2026-07-13.json` (docket entries through May 5,
2026); provisioned `record/documents/questions-presented.txt` and
`petition.txt` (30 pp., full text — anchored the QP and split analysis; no
brief in opposition exists yet given the extensions); committed
`metrics/statpack.md` base rates; retrieval detailed in `retrieval.md`.
