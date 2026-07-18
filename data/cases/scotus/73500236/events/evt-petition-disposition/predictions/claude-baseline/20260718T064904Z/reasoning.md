# Colorado Bondshares, et al. v. Marin Metropolitan District, et al. (No. 25-1334)

**Prediction: denied. P(grant, GVR included) = 0.015.**

## The legal question

Petitioners (a Colorado municipal-bond mutual fund and UMB Bank as bond
trustee) seek review of an unpublished Colorado Court of Appeals decision
(No. 2024CA1092, June 12, 2025) holding that (1) the Due Process Clause bars
imposing the District's "Required-Mill-Levy" — recharacterized as a special
assessment in the earlier *Landmark Towers* litigation — on a landowner
(Century) whose parcel received no benefit, even though Century bought the
parcel with full knowledge of both the assessment and the lack of benefit;
and (2) petitioners' unjust-enrichment claim for repayment of the $30.5M
bond proceeds fails because the District already spent the money. The
Colorado Supreme Court denied review on January 26, 2026. The two questions
presented are framed as whether the Colorado Court of Appeals "correctly
construed case law stemming from this Court" (*Village of Norwood v. Baker*,
*Myles Salt*, *Penn Central*; *Marsh v. Fulton County*, *Louisiana v. Wood*).

## Governing standard

Certiorari is discretionary and governed by Rule 10: the Court grants
principally to resolve splits among circuits or state courts of last resort,
or to settle important undecided federal questions — "a petition for a writ
of certiorari is rarely granted when the asserted error consists of
erroneous factual findings or the misapplication of a properly stated rule
of law."

## Facts from the snapshot and petition that drive the outcome

Negative signals (each individually strong; together nearly dispositive):

1. **No split alleged.** The petition claims no conflict among circuits or
   state high courts. Both QPs literally ask whether the lower court
   "correctly construed" this Court's precedent — the error-correction
   framing Rule 10 disfavors — and the petition itself twice labels the
   issues "matters of first impression."
2. **Weak vehicle posture.** The decision below is an *unpublished* opinion
   of a state *intermediate* court (Colo. App. R. 35(e)); the Colorado
   Supreme Court declined review. Unpublished intermediate-court decisions
   set no binding precedent, undercutting the "dangerous precedent other
   states will adopt" theme.
3. **Both respondents waived the right to respond** (June 15–16, 2026) and
   the Court has not called for a response. A CFR is a near-prerequisite to
   a modern grant; as of the snapshot none has issued.
4. **No amicus support** appears on the docket — notable because the
   municipal-bond industry could have filed if it saw the systemic stakes
   the petition asserts.
5. **First distribution, to the 9/28/2026 long conference.** No relists, no
   CVSG. Relists are the classic pre-grant signal (statpack: 0-relist
   petitions grant ~0.8%; 2 relists ~34%); nothing of the kind has occurred
   yet.
6. **The prior round of this same dispute was denied.** *UMB Bank, N.A. v.
   Landmark Towers Ass'n*, No. 19-241, cert. denied Nov. 25, 2019 (140 S.
   Ct. 566) — the *Landmark* decision this petition tries to distinguish
   already came to the Court from the same district's bond litigation and
   was turned away (public information predating the snapshot; legitimate
   forward signal).
7. The takings/due-process question is entangled with a state-law
   characterization (tax vs. special assessment under Colorado law), and
   the unjust-enrichment question is substantially one of Colorado common
   law (*Normandy Estates*) with old general-law federal cites — an
   adequate-and-independent-state-ground shadow over both QPs.

Positive signals (modest):

- Paid petition by competent counsel (Kutak Rock), with a real
  federal-constitutional hook (*Norwood*, *Myles Salt*) and a
  policy argument about municipal borrowing costs.
- Justice Gorsuch granted a filing extension — routine, not a signal of
  interest.

## Base rates and adjustment

From the committed statpack (live/historical slice, denial-reweighted):
modern discretionary-cert petitions grant ~2.5–3.3% per recent Term
overall; **paid** petitions grant ~5.4% (Term 2025) to ~6.9% (Term 2024).
Starting from the paid-class anchor (~5–6%), the case-specific features
cut sharply against a grant: no split + error-correction framing +
unpublished state intermediate decision + double respondent waiver with no
CFR + no amici + prior denial in the same dispute. Petitions with this
profile grant well below the paid-class average; the 0-relist bucket
(~0.8%) is where this case currently sits, though the long-conference
distribution leaves some room for a CFR/relist path I can't yet observe.
I land at **P(grant) = 0.015**, disposition **denied**. GVR is essentially
unavailable — no intervening decision of this Court is in play.

`big_case_score` = 0.15: real sector stakes for special-district finance
($30.5M in bonds, an argument about municipal borrowing costs), but the
dispute is fact-bound, Colorado-specific, and anchored to an unpublished
opinion; if denied (or even decided) it would draw trade-press, not
national, attention.

## Degradations

The cell's corpus query service was unreachable (`fedcourts query` timed
out against the local sidecar on two attempts), so no similar-prior
retrieval from the corpus was possible; I relied on the committed
`metrics/statpack.md` / `statpack.json` for base rates instead. The
statpack in this checkout carries no "Segment base rate by salience band"
table, so the relist/CVSG signal was read from its separate cuts. One
CourtListener MCP lookup supplied the prior *Landmark Towers* cert denial.
Details in `retrieval.md`; noted in `flags.json`.
