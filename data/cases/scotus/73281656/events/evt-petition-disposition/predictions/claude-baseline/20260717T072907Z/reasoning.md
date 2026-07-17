# Lindsey v. South Carolina, No. 25-1176 — cert disposition prediction

**Prediction: denied. P(any grant, GVR included) = 0.07.**

## The case

Marion Alexander Lindsey, a South Carolina death-row inmate, petitions from
the Supreme Court of South Carolina's 3–2 affirmance (Nov. 5, 2025) of the
denial of state post-conviction relief on his penalty-phase
ineffective-assistance claim. Capital case, paid petition, docketed April 14,
2026; BIO filed June 29; reply filed July 14; **distributed July 15 for the
September 28, 2026 long conference**. Counsel of record is Paul W. Hughes
(McDermott Will & Schulte), with the Yale Law School Supreme Court Clinic —
elite, experienced Supreme Court counsel.

Questions presented (from the provisioned `questions-presented.txt`):

1. Whether Strickland prejudice must be assessed on the **cumulative effect**
   of counsel's deficiencies, or may be evaluated error-by-error in isolation.
2. Whether a trial court's **wholesale adoption of the State's proposed
   order** in a capital case, without judicial guidance or substantive change,
   violates due process or the Eighth Amendment.

## Governing standard

Cert is discretionary; the realistic anchors are (a) the base rate for paid,
modern cert petitions and (b) the classic grant signals: a genuine,
acknowledged split; vehicle cleanliness; stakes; and the Court's revealed
appetite for the issue.

## Grant-side considerations

- **The QP1 split is real and long-recognized.** The petition documents a
  1st/2d/7th/9th (plus Iowa) vs. 4th/6th/8th (now South Carolina) division on
  aggregating assumed deficiencies at Strickland's prejudice step, and notes
  the Court granted this very question in Banks v. Dretke (2004) without
  resolving it. Scholarship confirms the disarray.
- **State-court posture avoids AEDPA**, which petitioner plausibly argues
  makes this a cleaner vehicle than a habeas case.
- **A 3–2 split below** with a substantial dissent (Hill, J., joined by
  Beatty, J.) tabulating the omitted mitigation against a single statutory
  aggravator — a signal the underlying prejudice question is close on the
  facts.
- Capital stakes; a rubber-stamped 192-page State-drafted PCR order (initially
  signed with ~155 errors, then re-adopted after remand with only cosmetic
  changes) is a fact pattern that could draw some Justices' attention on QP2.

## Deny-side considerations (these dominate)

- **Base rates.** Statpack, modern discretionary-cert petitions: overall
  grant a few percent; Term-2025 **paid** petitions grant ≈ **5.4%**
  (IFP ≈ 1.1%). Petitions from **state courts** grant more rarely still (the
  state-court buckets in the originating-court table run 0–16% on tiny
  denominators, mostly 100% denied). Relist-0 petitions grant ≈ 0.8%; this
  one has not yet been distributed twice, though a serious capital petition
  would typically be relisted before any grant — the final-disposition
  probability must price in that path.
- **Preservation / vehicle defect.** The BIO's lead argument is that Lindsey
  never asked the state courts to adopt a cumulative-prejudice framework —
  the phrase appears in neither his PCR appellate brief nor the opinion below
  — so there is "no ruling to review." From the provisioned record this
  looks at least colorable: the state supreme court's opinion proceeds
  item-by-item but closes with a global no-prejudice conclusion quoting the
  Strickland/Thornell aggregate-reweighing standard, which lets the Court
  read the decision below as *applying* the right test rather than cleanly
  presenting the split. That reading substantially weakens QP1 as a vehicle.
- **Direction of error.** This Court's recent Strickland-prejudice work
  (Thornell v. Jones (2024), Dunn v. Reeves, Shinn) has almost uniformly
  granted to *reverse relief* awarded to capital petitioners, not to review
  state-court denials of relief. A grant here would run against that
  revealed preference.
- **QP2 is fact-bound.** Jefferson v. Upton was a narrow, pre-AEDPA
  per curiam remand; the Court has repeatedly declined to constitutionalize
  proposed-order practice, and the state court here credited the judge's
  express statements that the order matched how he "saw the case." The
  dissent below took no exception on this issue — no split below on QP2's
  facts.
- **An alternative forum is open.** Lindsey's federal habeas case
  (D.S.C. No. 2:26-cv-00560) is already filed, and the BIO notes he is not
  near exhaustion. The Court routinely denies state-PCR petitions when
  federal habeas review remains available, and no execution date currently
  forces its hand (the prior date was stayed in February 2026).

## Weighing

Start from the paid-petition anchor (~5%). Adjust up for elite counsel, a
genuine and well-documented split, capital stakes, and the dissent below —
factors that plausibly double the odds. Adjust back down for the
preservation problem, the fact-bound second question, the Court's current
hostility to defendant-side Strickland grants, and the pending federal
habeas alternative. Net: **~7%** for any grant. A GVR is unlikely — no
intervening decision of this Court bears on the QPs (Thornell predates the
decision below and was addressed by it). The likeliest single outcome is a
straight denial, quite possibly after one or more relists and with a
dissent from (or statement respecting) denial by Justice Sotomayor and/or
Justice Jackson.

**predicted_disposition: denied; granted = 0; probability = 0.07.**

## Big-case score

0.45. A capital case tied to a recently-stayed execution, litigated by
prominent counsel, on a question (cumulative Strickland prejudice) that an
estimated 80% of capital habeas cases implicate. If the Court took and
decided it, the doctrinal significance would be substantial; as a docket
matter it is otherwise low-profile, with no amicus activity visible on the
docket as of the snapshot.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-17.json` (docket through the
  July 15, 2026 distribution).
- Provisioned `questions-presented.txt`, `petition.txt` (47 pp., read in
  full), `brief-in-opposition.txt` (36 pp., read in full).
- Committed `metrics/statpack.md` base rates (modern discretionary-cert
  section, per-Term paid/IFP detail from `statpack.json`).
- Corpus `fedcourts query` calls (see `retrieval.md`) — citation-filtered
  queries returned no rows, so no case-level priors informed the number
  beyond the statpack aggregates.
