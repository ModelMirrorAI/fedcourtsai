# Burford German Funding LLC v. financialright claims GmbH, No. 25-1269 — petition disposition

**Prediction: GVR (grant, vacate, and remand in light of *Jules v. Andre Balazs Properties*), P(any grant, GVR included) = 0.60.**

## The legal question

Whether a federal court that has subject-matter jurisdiction over a pending
matter also has jurisdiction to resolve motions to stay (FAA § 3) and compel
arbitration (FAA § 4) of that matter, or must instead find an independent
jurisdictional basis for those motions.

Respondent financialright claims (FRC) filed a 28 U.S.C. § 1782 discovery
application in the District of Delaware against the Burford petitioners, its
former litigation-funding partners in the German trucks-cartel litigation.
Petitioners moved under FAA §§ 3 and 4 to stay the § 1782 proceeding and compel
arbitration under the parties' Capital Provision Agreement. The district court
held sua sponte that it lacked subject-matter jurisdiction over those motions
while granting the § 1782 application; a divided Third Circuit panel affirmed
(Oct. 22, 2025), holding that § 4 motions always require an independent
jurisdictional basis via § 4's look-through provision even when filed in a
pending action, and that the § 3 motion rose and fell with the § 4 motion.
Judge Matey dissented, citing *Badgerow v. Walters*, 596 U.S. 1, 15 (2022)
("[j]urisdiction to decide the case includes jurisdiction to decide the
motion"). Rehearing en banc was denied January 2, 2026.

## The decisive development: *Jules* was decided May 14, 2026

The petition is explicitly and almost exclusively a **hold-for-*Jules*-and-GVR**
petition: it asks the Court to hold for *Jules v. Andre Balazs Properties*,
No. 25-83 (cert. granted Dec. 5, 2025; argued Mar. 30, 2026), then grant,
vacate, and remand.

*Jules* has now come down — May 14, 2026, **unanimous**, per Justice Sotomayor,
**affirming the Second Circuit** (608 U.S. ___ (2026)). The Court held that a
federal court that stayed claims under FAA § 3 retains jurisdiction to confirm
or vacate the resulting award under §§ 9–10 without any independent
jurisdictional basis on the face of those motions: "nothing in the FAA
precludes the normal operation of federal jurisdiction regarding live claims
pending before a federal court," reaffirming *Badgerow*'s statement that
jurisdiction to decide a case includes jurisdiction to decide a motion within
it. That squarely rejects the analytical premise of the Third Circuit's
decision here — that FAA motions filed in a pending action nonetheless require
an independent jurisdictional showing. The rejection is cleanest as to the § 3
motion, which the Third Circuit dismissed without independent analysis.

The docket since then reads like the standard pre-GVR sequence:

1. **Jun 9, 2026** — respondent waives its right to respond.
2. **Jun 16, 2026** — petitioners file a supplemental brief (timed to flag the
   *Jules* decision), which is "(Distributed)".
3. **Jun 17, 2026** — distributed for the September 28, 2026 long conference.
4. **Jul 15, 2026** — **response requested**, due August 14, 2026.

The call for a response is the strongest single docket signal available at this
snapshot. Under the Court's settled practice it will not grant relief —
including a GVR — while a waiver is on file, so a chambers that intends to act
must first call for a response. A CFR issued mid-summer, three months before
the conference, in a petition whose only realistic path is a *Jules* GVR, is
most consistent with the Court teeing the case up for disposition in light of
*Jules* rather than a quiet denial (which required no response at all).

## What cuts the other way

The probability is 0.60 rather than 0.80+ because respondent has a genuine BIO
to write, on two lines:

- ***Jules* is a §§ 9–10 case; the decision below construed § 4.** *Jules*
  itself reaffirmed that § 4 is textually unique — its "save for" look-through
  language has no analogue elsewhere in the FAA. Respondent will argue the
  Third Circuit merely applied § 4's own text, which *Jules* did not disturb,
  so there is no "reasonable probability" of a different result on remand
  (*Lawrence v. Chater*, 516 U.S. 163, 167 (1996)). This argument is weakest
  for the § 3 motion, which has no look-through language and which the panel
  dismissed derivatively.
- **Alternative grounds.** The panel also held that § 4's "limiting"
  prerequisites were unmet because § 1782 applications are not "civil actions"
  and do not "qualify for arbitration" — a ground arguably independent of the
  jurisdictional premise *Jules* undermines. A BIO can argue the judgment
  stands regardless, making a GVR pointless.

Against that: the GVR standard is lenient (reasonable probability of
reconsideration, not certainty of reversal); the panel was divided, with the
dissent already reasoning exactly as *Jules* later did; the majority itself
described the governing precedents as "far from clear" and "admittedly murky";
and the equities are stark — respondent invoked the very federal jurisdiction
it then argued did not extend to petitioners' responsive motions. The
petitioners are represented by an experienced Supreme Court boutique (Kellogg
Hansen), and the ask is calibrated to what the Court routinely does after
deciding a lead case.

## Base rates and adjustment

From the committed statpack (modern discretionary-cert slice): the raw grant
rate for paid petitions is ~2.5–3% per Term, and Third Circuit petitions in the
selected slice run granted ~13% / denied ~69%. Those anchors are dominated by
plenary-grant dynamics and do not capture this posture. The correct reference
class is *hold-for-a-just-decided-companion-case petitions that draw a CFR
after a waiver*: recent corpus GVR priors (e.g., *Whitton v. Dixon*, GVR'd
June 1, 2026 after conference distribution; *FBI v. Fazaga*; *Bannon v.
United States*) show the Court GVR-ing readily this Term where an intervening
decision implicates the judgment below. Conditional on (a) a unanimous
intervening decision rejecting the analytical premise below, (b) a divided
panel, and (c) a CFR consistent with intended action, I estimate:

- **GVR: ~0.55**
- **Plenary grant: ~0.04** (the Court just decided *Jules*; it would let the
  Third Circuit apply it first; no developed split on the § 1782-specific
  question)
- **Deny: ~0.38** (BIO persuades that § 4's look-through text plus the
  alternative arbitrability ground insulate the judgment)
- **Dismissed/withdrawn (settlement): ~0.03**

That yields P(granted, GVR included) ≈ 0.60, with `gvr` as the modal
disposition. Timing: resolution most likely at or shortly after the
September 28, 2026 long conference, once the BIO (due Aug. 14) and any
supplemental briefs are in.

## Leakage note

This is a **forward** cell; the petition's own disposition does not yet exist
and nothing retrieved concerns it. The *Jules* opinion (a different case,
decided May 14, 2026 — before this snapshot) is legitimate forward signal
under the retrieval contract, and it is the single most probative input here.

## Inputs used

- Snapshot `data/cases/scotus/73317900/record/snapshots/2026-07-17.json`
  (docket through the Jul 15, 2026 CFR).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt`
  (full petition text; QP anchored the analysis; no BIO exists yet — the CFR
  response is due Aug. 14, 2026).
- CourtListener MCP: the *Jules* slip opinion (cluster 10858761 / opinion
  11326163).
- Corpus priors (`fedcourts query`, 2020s SCOTUS GVRs) and the committed
  `metrics/statpack.md` base rates.
