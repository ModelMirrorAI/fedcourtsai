# Blevins v. Alabama State Bar, No. 25-1344 — cert prediction

**Prediction: deny. P(any grant, GVR included) ≈ 0.003.**

## The case

Jerry M. Blevins, an Alabama attorney appearing as his own counsel of record,
petitions from the Supreme Court of Alabama's December 19, 2025 decision (No.
SC-2024-0693, rehearing denied February 27, 2026) affirming a six-month
suspension and public reprimand imposed by the Alabama State Bar's
Disciplinary Board over a 2017 client fee dispute. The single question
presented asks whether the Alabama Supreme Court's interpretation of
Ala. Code § 34-3-62 (1975) — a statute letting an attorney resolve a fee
dispute by motion in circuit court, upon which the attorney "shall not be
subject to prosecution, suspension, or removal under this chapter" — and its
application to his case violated procedural due process under the Fourteenth
Amendment.

## The legal theory and why it fails as a cert vehicle

The petition's theory is a fair-notice / retroactive-construction claim
resting on *Marks v. United States*, 430 U.S. 188 (1977): Blevins says he
brought his fee dispute to circuit court in express reliance on § 34-3-62's
safe-harbor text, so disciplining him after the Alabama Supreme Court
construed the statute narrowly (as protecting only *retention of the disputed
funds*, not immunizing the underlying conduct from charges of excessive fees
and failure to communicate) deprived him of due process, as the Alabama court
itself once recognized in *Brooks v. Alabama State Bar*, 574 So. 2d 33 (Ala.
1990).

Every certiorari-stage consideration cuts against review:

- **No split, no recurring question.** The petition alleges no conflict among
  state high courts or federal circuits — it does not even have a "reasons
  for granting" argument beyond the merits. It asks the Court to
  error-correct one state court's reading of one state statute as applied to
  one attorney. Under Rule 10 this is the paradigm of a fact-bound,
  splitless petition.
- **The federal question is thin and arguably unpreserved.** By the
  petition's own account (its "First Instance When Federal Question Raised"
  section), the due-process argument first appeared in Blevins's *reply
  brief* on appeal, in February 2025 — years into the disciplinary
  proceeding. That raises a serious preservation/presentation problem under
  28 U.S.C. § 1257, and the Alabama Supreme Court disposed of it on a
  reliance-specific ground (he had no caselaw basis for believing the
  statute conferred "blanket immunity"), which reads more like a fact-bound
  application of fair-notice doctrine than a rejection of a federal rule.
- **The merits presentation is weak.** The 12-page petition rests on a
  paraphrase of *Marks* and on *Brooks* — an Alabama case that shows the
  state court already applies the *Marks* fair-notice principle, i.e., there
  is no doctrinal defiance to correct, only a disputed application. The
  unexpected-narrowing theory (closest federal analogue: *Bouie v. City of
  Columbia*) is not developed.
- **The respondent waived its response** (July 1, 2026). The Court
  essentially never grants a paid petition without at least calling for a
  response; as of the snapshot no CFR has issued, and the case was
  distributed for the September 28, 2026 "long conference," where the deny
  rate is at its seasonal peak.
- **Litigant profile.** A self-represented attorney challenging his own
  discipline, with a parallel federal suit against the Alabama justices and
  bar officials pending in the Middle District of Alabama (No.
  2:26-cv-00133) — a profile the Court almost invariably denies. Attorney
  discipline is an area the Court leaves to the states.

## Base rates and adjustment

From the committed statpack (live/historical slice): modern
discretionary-cert petitions grant at ~3% overall; OT2025 overall grant rate
2.5%; **paid** petitions (this is a paid case, per the docket) grant at
~5.4% (OT2025) to ~6.9% (OT2024). Adjusting down from the paid anchor:
zero relists as of the snapshot (relist-0 bucket grants at 0.8%), no CVSG,
state-court origin (state-court petitions in the corpus grant far below the
circuit average; several state-court buckets show 0% granted), waived
response with no CFR, no amicus support indicated, no split, fact-bound QP.
Each of these is independently associated with denial; jointly they put the
case well below the relist-0 floor. The statpack's salience-band table is not
present in the committed statpack.md, so I anchored on the relist/CVSG/fee
cuts directly.

**P(grant) ≈ 0.003.** A GVR is also implausible — no intervening decision of
this Court bears on the QP — so the residual grant mass is essentially
plenary-grant tail risk only. Predicted disposition: **denied**, most likely
in the orders following the September 28, 2026 conference.

## Stakes

`big_case_score` = 0.03: a one-attorney disciplinary matter under a
state-specific fee statute, with no national or doctrinal stakes if decided.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-18.json` (docket 25-1344:
  filing, waiver, distribution).
- Provisioned `record/documents/petition.txt` (full 12-page petition text)
  and `questions-presented.txt`.
- `metrics/statpack.md` and per-fee-class detail in `metrics/statpack.json`.
- One `fedcourts query` corpus pull (see `retrieval.md`).
- Mode is `forward` (pending case, conference set for 2026-09-28); no
  outcome-revealing material was sought or encountered.
