# The GEO Group, Inc. v. Nwauzor, No. 25-828 — cert disposition

**Prediction: granted, P(grant incl. GVR) = 0.55.**

## The legal question

Whether the Supremacy Clause (intergovernmental immunity and/or preemption)
bars Washington from classifying federal immigration detainees who participate
in ICE's congressionally mandated Voluntary Work Program — reimbursed from
appropriations at $1/day — as "employees" under the Washington Minimum Wage
Act when the detention facility is operated by a private federal contractor
(GEO, at the Northwest ICE Processing Center in Tacoma). The Ninth Circuit
(Murguia, W. Fletcher; Bennett dissenting) affirmed a ~$37M judgment against
GEO, holding no direct regulation, no discrimination against the federal
government (because Washington's high court construed the MWA to reach state
detainees held in *private* facilities), and no preemption.

## Grant-side signals (from the provisioned record)

1. **CVSG.** On May 18, 2026 — after a single distribution for the May 14
   conference — the Court invited the Solicitor General's views. In the corpus
   statpack, CVSG petitions grant at **27.1%** against a ~3% baseline for
   modern discretionary-cert petitions and ~5–7% for paid petitions; a CVSG
   after first distribution is itself a screened-salience signal.
2. **Executive-branch alignment.** The United States filed amicus briefs
   supporting GEO's Supremacy Clause position at both the panel and en banc
   stages, across three administrations of both parties (petition at 15–16).
   The current administration's interest in immigration-detention contracting
   is intense, and the judgment has already forced suspension of the work
   program at the facility. A grant-recommending SG brief is substantially
   more likely than not, and the Court usually follows a grant recommendation.
   My estimate composes roughly as P(SG says grant) ≈ 0.7–0.75 ×
   P(grant | SG grant rec) ≈ 0.75, plus a small residual if the SG says deny.
3. **En banc division below.** Rehearing en banc was denied over the recorded
   dissent of **seven judges**, with opinions by Judge Bumatay (joined by
   Callahan and VanDyke) and a statement by Judge Collins (joined by R. Nelson
   and Bress) adopting Judge Bennett's panel dissent — a classic pre-grant
   marker, and the panel majority filed a counter-statement, underscoring the
   intra-circuit heat.
4. **Asserted circuit split.** The petition claims the Second, Third, and
   Fourth Circuits hold that states cannot target federal contractors to evade
   the Supremacy Clause, versus the Ninth Circuit's contractor-diminished
   protection rule (via *GEO Group v. Newsom* (en banc)).
5. **Court's adjacent engagement.** The Court decided *GEO Group v. Menocal*
   (No. 24-758) on February 25, 2026 — detainee-work-program litigation
   against the same petitioner — and in *United States v. Washington*, 596
   U.S. 832 (2022), unanimously reversed the Ninth Circuit on a Washington
   statute that discriminated against the federal government; petitioner
   frames this case as Washington's sequel.
6. **Petition quality/stakes.** Paid petition, Paul Clement as counsel of
   record, ~$37M judgment, amicus support at the petition stage (Day 1
   Alliance / Professional Services Council), and two respondents (the
   Nwauzor class and the State of Washington) filing separate BIOs.

## Deny-side considerations (from the BIO)

- **Split is contestable.** The BIO argues the 2d/3d/4th Circuit cases apply
  the same direct-regulation/indirect-cost standard the Ninth Circuit used,
  and that the Third Circuit's *CoreCivic* decision expressly aligned itself
  with the Ninth Circuit — so the case reduces to factbound error correction.
- **State-specific and narrow.** One state's minimum-wage act, one facility,
  a state-supreme-court construction of state law (on certified questions)
  that the Court would owe deference; no similar law identified elsewhere.
- **Vehicle problems on preemption.** GEO abandoned its below-argued 1978
  appropriations-cap theory and now presses a practical-impossibility theory
  the Ninth Circuit said was raised only by an amicus — a forfeiture argument
  — and the contract itself requires state-law compliance and sets no wage cap.
- **Discrimination holding rests on state-law parity.** The Washington Supreme
  Court construed the MWA to reach private detention contractors equally,
  state or federal, which blunts the discrimination theory's clean edge.
- **Mootness drift.** The BIO notes ICE detention-policy changes could keep
  the issue from recurring; CVSG cases also occasionally wash out (settlement,
  contract renegotiation) before the Court acts.

## Synthesis

The base rate for a paid petition is ~5–7%; the CVSG bucket alone lifts this
case to ~27%. This petition sits well above the median CVSG case: the federal
government is not a bystander whose views are unknown — it has *twice* filed
amicus briefs below endorsing petitioner's exact position, making a
grant-recommending SG brief highly likely, and post-CVSG grants track the
SG's recommendation closely. Layer on the seven-judge en banc dissent, the
Clement petition, the concrete disruption of a federal program, and this
Court's demonstrated appetite for Ninth Circuit immigration-federalism
correction (*United States v. Washington*), and the case profiles as one of
the strongest grant candidates in the CVSG pool. The BIO's no-split and
vehicle points are real (they could channel a grant onto the
intergovernmental-immunity question alone, or support a deny if the SG
surprises), and CVSG timing means resolution likely slips deep into OT2026,
leaving room for washout. I land at **P(grant) = 0.55**, modal disposition
**granted** (a plenary grant; no intervening decision makes a GVR likely).

`big_case_score` = 0.7: a decision would define how far states can regulate
federal contractors performing federal functions — consequential for
immigration detention and federal contracting generally — though the
minimum-wage posture is narrower than a marquee constitutional case.

## Inputs used

- Snapshot `data/cases/scotus/73279966/record/snapshots/2026-07-16.json`
  (docket through the May 18, 2026 CVSG; paid case, Term 2025, linked
  application 25A464).
- Provisioned documents: `questions-presented.txt`, `petition.txt` (250 pp.,
  truncated — appendix cut off), `brief-in-opposition.txt` (Nwauzor
  respondents' BIO, 43 pp.). The State of Washington's separate BIO was not
  provisioned; its themes are visible in the Nwauzor BIO and the reply's
  docket entry.
- Committed statpack (`metrics/statpack.md` / `.json`) for base rates; the
  per-Term salience-band table referenced in the prompt is not present in the
  committed statpack build, so I anchored on the CVSG and fee-class cuts.
- CourtListener MCP (forward mode): confirmed *GEO Group v. Menocal*,
  No. 24-758, decided 2026-02-25. No material about this petition's own
  disposition was sought or surfaced — none can exist; the CVSG response is
  still pending as of the snapshot date.
