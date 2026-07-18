# Crites-Bachert v. Providence Health & Services – Oregon (No. 25-1317)

**Prediction: denied. P(grant, GVR included) = 0.004.**

## The legal question

The petition asks whether a civilian has an implied private right of action to
enforce the "option to accept or refuse" condition of the emergency-use-
authorization statute, 21 U.S.C. § 360bbb-3(e)(1)(A)(ii)(III) — i.e., whether a
hospital that suspended a non-employee surgeon's privileges for refusing an
EUA COVID-19 vaccine can be sued for violating an informed-consent right the
petitioner locates in the BioShield Act. The Ninth Circuit (unpublished
memorandum, Nov. 10, 2025) affirmed Rule 12(b)(6) dismissal, holding that
21 U.S.C. § 337(a) and *Buckman Co. v. Plaintiffs' Legal Committee*, 531 U.S.
341 (2001), commit FDCA enforcement exclusively to the federal government;
rehearing and rehearing en banc were denied Dec. 19, 2025.

## Why this is a near-certain denial

**No genuine split.** The petition's own framing concedes that "every other
court that has considered the issue" has refused civilian claims under
§ 360bbb-3 — that is uniformity, not conflict. The asserted "split" is with
Court of Federal Claims military-pay decisions (*Harkins*, *Bassen*, *Botello*)
construing a *different statute*, 10 U.S.C. § 1107a, for service members in a
Tucker Act posture. A tension between circuit holdings on § 360bbb-3 and Fed.
Cl. standing rulings on § 1107a is not the kind of conflict Rule 10 targets,
and the Court of Federal Claims cases do not even hold that § 360bbb-3 creates
a private damages action against private employers.

**The merits theory runs against settled doctrine.** The Court's implied-
right-of-action jurisprudence (*Sandoval*, *Gonzaga*, and most recently
*Medina v. Planned Parenthood South Atlantic* (2025), which the petition
itself cites for how "rare" enforceable rights are) is strongly hostile to
implying new private rights, and *Buckman* plus § 337(a) squarely support the
Ninth Circuit's reading for the FDCA specifically. The July 2021 OLC opinion
reached the same consensus view that § 564 does not bar entities from
requiring EUA vaccines. There is no doctrinal instability for the Court to
resolve — the decision below is a routine application of existing precedent.

**The genre has been repeatedly denied.** The Court declined every COVID-
vaccine-mandate challenge of this type across 2021–2024 (e.g., *Johnson v.
Brown*, *We The Patriots*, *Dr. A. v. Hochul*, *Kheriaty*), including
petitions pressing the same EUA informed-consent theory. With the mandates
themselves long rescinded, the issue is of diminishing prospective
importance — a retrospective damages suit by a single plaintiff.

**Docket signals all point to denial.** From the 2026-07-18 snapshot:
respondent *waived* its right to respond (June 12, 2026), and the Court
distributed the petition for the September 28, 2026 long conference without
calling for a response — a grant essentially never happens without at least a
CFR. Zero relists, no CVSG, no amici noted on the docket, an unpublished
non-precedential decision below, and a solo-practitioner counsel of record.
The corpus's recent grants (June 30, 2026 conference) all show 3+
distributions and high salience — the opposite profile of this cell.

## Base-rate anchoring

From `metrics/statpack.md` (modern discretionary-cert dockets, denial-
reweighted): OT2025 grant rate ≈ 2.5%; paid-case and CA9 cuts sit near 3%;
the **0-relist bucket grants at 0.8%**; no-CVSG at 3.0%. This petition is a
paid filing (slightly grant-favorable vs. IFP) but carries a waived response,
no relists yet, a fringe legal theory foreclosed by circuit consensus, and a
repeatedly-denied subject matter. Starting from the 0-relist bucket's 0.8%
and adjusting down for the waived response, the absence of any split, and the
genre's uniform denial record, I set **P(grant) = 0.004**. A GVR is
implausible (no pending related merits case could intervene), and dismissal/
withdrawal signals are absent, so the predicted disposition is a plain
**denial**, most likely in the orders list following the September 28, 2026
conference.

## Inputs used

- Snapshot `data/cases/scotus/73500217/record/snapshots/2026-07-18.json` (docket
  entries, waiver, distribution, paid status, Term 2025).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt`
  (full petition text — QP, claimed split, *Harkins*/*Bassen*/*Botello* reliance,
  Ninth Circuit's § 337(a)/*Buckman* rationale).
- No brief in opposition exists (response waived), consistent with
  `documents.json`.
- Corpus priors and committed statpack base rates; CourtListener checks logged
  in `retrieval.md`.

Mode is `forward`; no search surfaced any disposition of this petition (it is
genuinely pending — conference is scheduled for 9/28/2026), so there is no
leakage to flag.
