# Prediction: scotus/1061793 — evt-petition-disposition

**Case:** Baby Boy Doe, a Fetus, by His Court-Appointed Guardian Ad Litem,
Murphy, Cook County Public Guardian v. Mother Doe (petition to the Supreme
Court of the United States from the Illinois courts).

**Prediction:** relief denied — `granted = 0`, P(granted) = 0.01,
predicted disposition `denied`.

## Prior-knowledge disclosure

This is a well-known case, and I recognize it from general legal knowledge:
it is the Supreme Court sequel to *In re Baby Boy Doe*, 632 N.E.2d 326 (Ill.
App. Ct. 1994), the December 1993 Illinois forced-cesarean litigation brought
by Cook County Public Guardian Patrick Murphy as guardian ad litem for a
fetus. I know from that background that the guardian's application to the
Supreme Court did not succeed (Justice Stevens, as Circuit Justice, denied
emergency relief in December 1993, and the Court never granted review). Per
the predict contract I state this explicitly here and in `flags.json`
(category `other`) so the evaluation can discount this cell. The analysis
below is nonetheless built from the pre-decision record and the legal
landscape as it stood at filing, and the probability I give is the one I
would give without the hindsight.

## What the snapshot shows

The provisioned snapshot (`record/snapshots/2026-07-09.json`) is a bare
opinion-import docket: no docket number, no filing or termination dates, no
docket entries, no party or attorney records — only the caption, the court
(`scotus`), and a link to a single opinion cluster (which I did not open,
since for this case it would be the outcome itself). The prediction therefore
rests on the caption, the procedural posture it implies, and general legal
context from the case's era. This thinness is flagged as `data-quality` in
`flags.json`.

## The legal question and posture

The caption tells us the petitioner is a *fetus*, appearing through a
court-appointed guardian ad litem (the Cook County Public Guardian), adverse
to its own mother ("Mother Doe"). That posture matches the Illinois
forced-cesarean litigation: physicians believed the fetus faced death or
severe injury from placental insufficiency unless the mother underwent a
cesarean section she refused on religious grounds; the State's Attorney and
then the Public Guardian sought a court order compelling the surgery; the
Illinois trial and appellate courts refused, holding that a competent
woman's common-law and constitutional right to refuse invasive medical
treatment is not diminished by pregnancy and that Illinois courts will not
balance fetal interests against it; the Illinois Supreme Court declined
expedited review. The guardian then sought emergency relief and certiorari
from the U.S. Supreme Court in December 1993 (October Term 1993).

The question presented, in substance: whether a state court may (or must) be
permitted to order a competent pregnant woman to undergo major surgery for
the benefit of a viable fetus — i.e., whether the fetus has federally
cognizable interests that can override the mother's bodily integrity.

## Why the Court would deny relief

1. **Merits headwinds.** Granting relief would require holding that a fetus
   has constitutional interests that can override a competent adult's right
   to refuse invasive medical treatment. *Roe v. Wade*, 410 U.S. 113 (1973),
   held a fetus is not a "person" under the Fourteenth Amendment, and
   *Planned Parenthood v. Casey*, 505 U.S. 833 (1992) — decided barely a year
   earlier — had just reaffirmed the core of Roe. *Cruzan v. Director*, 497
   U.S. 261 (1990), had meanwhile recognized a competent adult's
   constitutionally protected liberty interest in refusing unwanted medical
   treatment. The petition asks the Court to cut against all three lines at
   once. The 1993 Court had no appetite for that.

2. **Vehicle problems are fatal.**
   - **Mootness.** The pregnancy ends on a timescale of days to weeks; by
     the time of plenary consideration there is no order that could operate.
     "Capable of repetition, yet evading review" is a stretch where the
     dispute turns on one patient's refusal of one surgery.
   - **Adequate and independent state ground.** The Illinois Appellate Court
     rested substantially on Illinois common law of informed refusal (*In re
     E.G.*; *Stallman v. Youngquist*), insulating the judgment from federal
     review.
   - **Standing/party problems.** A guardian ad litem asserting federal
     rights of a fetus against the fetus's own mother presents threshold
     Article III and third-party-standing questions the Court would have to
     resolve before reaching anything.

3. **No conflict to resolve.** The contemporaneous authority ran one way:
   *In re A.C.*, 573 A.2d 1235 (D.C. 1990) (en banc), the leading
   forced-cesarean case, had vacated such an order and held the woman's
   wishes control in virtually all cases. Forced-intervention orders were
   rare, and the Illinois decision aligned with the trend. There was no
   split among federal circuits or state high courts calling for
   resolution.

4. **Base rates.** Certiorari is discretionary and the grant rate is a few
   percent at best (the committed statpack's corpus-wide SCOTUS cut shows
   resolved petitions at roughly 1.4% granted; the modern
   discretionary-cert section referenced by the predict prompt is not
   present in the committed statpack, which I flagged). Corpus retrieval
   over resolved 1990s SCOTUS priors surfaced no comparable
   fetal-rights/bodily-integrity petitions, so nothing in retrieval pulls
   the estimate above the base rate — and every case-specific factor above
   pushes it below.

## Probability and votes

Starting from a low single-digit cert base rate and adjusting sharply
downward for mootness, the state-ground problem, the standing problem, the
absence of a split, and merits that would collide with Casey the Term after
it was decided: **P(granted) = 0.01**. Disposition: **denied** — the Court
denies emergency relief and/or certiorari rather than dismissing a petition
properly before it; nothing in the record suggests withdrawal.

The per-judge votes list all nine members of the October Term 1993 Court
(Rehnquist, Blackmun, Stevens, O'Connor, Scalia, Kennedy, Souter, Thomas,
Ginsburg) as `denied`: a petition this flawed does not attract even the
four votes needed to grant, and denial orders are unsigned. Even the
Justices most sympathetic to state interests in potential life (Rehnquist,
Scalia, Thomas) would see the mootness and vehicle defects; the rest would
also view the merits as foreclosed.

**Confidence: 0.85** — high, reflecting the overwhelming convergence of base
rate, vehicle defects, and merits posture; discounted from certainty because
the snapshot is nearly bare and the corpus's era labels are noisy.
