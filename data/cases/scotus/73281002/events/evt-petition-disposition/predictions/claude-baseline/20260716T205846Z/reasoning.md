# RNC v. Eakin, No. 25-962 — cert disposition prediction

**Prediction: grant (P = 0.62), most likely a plenary grant; a meaningful minority
of the grant mass is a Munsingwear GVR if the case moots out on state-law grounds.**

## The legal question

The Third Circuit (149 F.4th 291, Aug. 26, 2025) held that Pennsylvania's
requirement that mail voters handwrite a date on the ballot-return envelope
violates the First and Fourteenth Amendments under the *Anderson-Burdick*
balancing framework, even while agreeing the burden of compliance is "minimal"
and that the requirement has detected actual fraud (*Commonwealth v. Mihaliak*).
Rehearing en banc was denied 7–6 (158 F.4th 185) over two dissentals (Phipps, J.,
on the intervening Pennsylvania Supreme Court decision in *Center for Coalfield
Justice*; Bove, J., on federalism, circuit splits, and misapplication of
*Crawford*/*Brnovich*/*McDonald*). The petition presents three QPs asking the
Court to cabin *Anderson-Burdick*: (1) whether a non-discriminatory rule imposing
the usual burdens of voting is constitutional; (2) whether mail-voting rules get
only rational-basis review when in-person voting is available (*McDonald*);
(3) whether a minimal burden triggers only rational-basis review and whether
burden is measured by cost of compliance or consequence of noncompliance.

## Governing standard for the prediction

Cert is discretionary; the base rate for a modern paid petition is a few percent.
The question is how far this cell's signals move it off that anchor.

## Signals from the snapshot and provisioned documents

Grant-positive, in rough order of strength:

1. **CVSG (June 29, 2026).** After full briefing and the June 25 conference, the
   Court invited the Solicitor General's views. The corpus statpack's CVSG cut
   puts resolved CVSG petitions at **27.1% granted / 71.2% denied** (n=59),
   versus 3.0% granted without a CVSG — a ~9x uplift before any case-specific
   adjustment.
2. **A federal court of appeals invalidated a state election statute.** This is
   a classic near-sufficient cert factor even without a split, and the panel
   itself acknowledged its decision implicates multiple circuit splits
   (Pet.App.31a n.23, 43a n.35) on the *McDonald* rational-basis question and
   on *Anderson-Burdick* methodology (burden measurement; state's evidentiary
   burden).
3. **The Commonwealth itself is a co-petitioner.** Pennsylvania's Attorney
   General intervened below to defend the statute and filed the companion
   petition (No. 25-967, VIDED, linked on this docket) — a state asking the
   Court to review the invalidation of its own election law.
4. **Escalating docket engagement.** Nearly all county-board respondents waived;
   the Court called for a response (Apr. 1), granted the Eakin respondents an
   extension, took full BIOs and a reply, considered the case at conference,
   and then CVSG'd rather than denying.
5. **Heavy cert-stage amicus support for petitioners**: Missouri + 20 other
   states, Pennsylvania Senate/House Republican leaders, Center for Election
   Confidence, America First Legal, and an election-law scholars' brief
   (Morley), whose motion for leave was granted June 29.
6. **A 7–6 en banc denial** with six judges joining substantive dissentals,
   including an explicit call for Supreme Court intervention.
7. **Prior interest by sitting Justices.** Three Justices dissented from the
   stay denial in *Ritter v. Migliori*, 142 S. Ct. 1824 (2022), on the closely
   related materiality-provision attack on this same date requirement, and the
   Court later Munsingwear-vacated *Migliori*. The Court's appetite for orderly,
   non-emergency mail-voting cases is current: it granted, argued, and decided
   *Watson v. RNC*, No. 24-1260 (June 29, 2026) this Term.
8. **Predictable SG alignment.** The current administration's SG is very likely
   to side with petitioners (the RNC and 21 amicus states) on the merits; CVSG
   cases where the SG recommends grant are granted at high rates historically.

Denial-side considerations:

1. **Shrinking practical stakes.** *Coalfield Justice*, 343 A.3d 1178 (Pa. 2025),
   now requires notice and a provisional-ballot cure for dating errors; only
   ~0.23% of 2024 mail ballots were rejected for dating errors even pre-cure.
   The provisioned Northampton County BIO argues the cure is incomplete
   (ballots arriving near the 8 p.m. deadline can't be cured), but the SG or
   the Court could see a diminishing controversy not worth plenary review.
2. **The *Baxter* overhang.** *Baxter v. Philadelphia Board of Elections*
   (Pa. Supreme Court, argued Sept. 10, 2025; still undecided on the public
   record as of the snapshot date) presents the same date requirement under the
   Pennsylvania Constitution, plus Act 77's non-severability clause. If the
   Pennsylvania Supreme Court strikes the requirement on state grounds, the
   federal case becomes moot. The petition itself concedes the correct response
   would then be a **Munsingwear GVR** (grant, vacate, remand to dismiss) —
   which still lands on the grant side of the binary axis, so this tail mostly
   converts plenary-grant probability into GVR probability rather than into
   denial. A long hold pending *Baxter* is also possible, delaying disposition.
3. The Court has historically been able to duck this specific dispute
   (*Ritter* mooted; *Ball v. Chapman* stayed in state court), and CVSGs in
   politically charged cases sometimes precede a quiet denial.

## Weighing

Anchoring on the CVSG bucket (~27% grant) and adjusting upward for the unusually
strong stack of traditional cert factors — statute invalidated, state as
petitioner, acknowledged splits, 7–6 en banc, 21-state amicus support, prior
Justice-level interest, and a highly predictable pro-petitioner SG — I put
P(any grant, GVR included) at **0.62**. Decomposed: roughly 0.50 plenary grant,
0.10–0.12 GVR (mostly the *Baxter*-mootness path), ~0.38 denial (an SG brief
recommending denial on diminished-stakes grounds followed by a denial, possibly
with dissents). Disposition will very likely not come until the SG files —
realistically winter 2026–spring 2027 (OT2026).

`predicted_disposition` is **granted** as the single most likely label;
`granted=1` and `probability=0.62` express P(grant incl. GVR).

## Big-case score

0.8. A merits decision would recalibrate *Anderson-Burdick* — the framework
governing essentially all constitutional challenges to state ballot-casting
rules — in a case captioned RNC v. (DSCC-backed) plaintiffs over Pennsylvania
mail voting, with a non-severability clause that could theoretically unwind
universal mail voting in a marquee swing state. High stakes independent of the
grant odds; a denial would leave the Third Circuit's invalidation in place,
itself consequential for 2026 Pennsylvania elections.

## Inputs used

- Snapshot `record/snapshots/2026-07-16.json` (docket through the June 29, 2026
  CVSG).
- `record/documents/questions-presented.txt` and `petition.txt` (full 55-page
  petition: QPs, splits, vehicle discussion including the *Baxter*/Munsingwear
  concession).
- `record/documents/brief-in-opposition.txt` — note this is **Northampton
  County's** 9-page BIO (the pipeline fetched the docket's "BIO" entry), not the
  principal Eakin/DSCC brief in opposition, which is on the docket but was not
  provisioned. The Northampton BIO's *Coalfield Justice*-gap and
  fraud-detection arguments are folded in above; the Eakin BIO's arguments are
  inferred only from the docket structure, not read. Flagged in `flags.json`.
- Corpus statpack (CVSG, relist, circuit, and Term base rates); `fedcourts query`
  returned no similar priors (see `retrieval.md`).
- Forward-mode web checks on *Baxter* status and recent SCOTUS election-law
  activity (all pre-date or are contemporaneous with the snapshot; nothing
  outcome-revealing exists — the petition is undecided pending the CVSG).
