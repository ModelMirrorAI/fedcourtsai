# Trice v. Texas, No. 25-1195 — cert petition disposition

**Prediction: denied. P(any grant, GVR included) = 0.10.**

## The legal question

The petition presents a single question: whether Texas Penal Code § 21.02(d) —
the continuous-sexual-abuse statute, which expressly provides that jurors "are
not required to agree unanimously on which specific acts of sexual abuse were
committed by the defendant" — violates the Sixth and Fourteenth Amendment right
to a unanimous jury verdict as recognized in *Ramos v. Louisiana*, 590 U.S. 83
(2020). Petitioner was convicted after a jury trial in Erath County, Texas of
continuous sexual abuse of a child (40 years) plus six other sexual-offense
counts (10–20 years, all concurrent). The Eleventh Court of Appeals (Eastland)
affirmed in a published opinion, *Trice v. State*, 721 S.W.3d 614 (Tex.
App.—Eastland 2025); the Texas Court of Criminal Appeals refused discretionary
review on January 15, 2026. The petition is paid, timely, and the federal claim
was pressed and passed on below — the vehicle is procedurally clean.

## Governing standard

Certiorari is discretionary under Sup. Ct. R. 10; the practical drivers are a
genuine split of authority, an important and recurring federal question, a
clean vehicle, and signals of internal Court interest (call for response,
relists, CVSG, amicus support).

## Signals from the docket (snapshot of 2026-07-17)

- **Paid petition**, counseled (solo Fort Worth practitioner, not Supreme
  Court specialist bar). Not capital.
- Texas **waived** its response (May 7, 2026); the case was distributed for
  the May 28, 2026 conference; on **May 26, 2026 the Court requested a
  response** (CFR) — the single strongest positive signal on this docket. A
  CFR means at least one chambers wants the State's view before conference; it
  materially lifts grant odds over the ~5% paid baseline, though the modal
  post-CFR outcome remains denial.
- Response deadline extended to **July 24, 2026** — the petition is genuinely
  pending (forward mode); disposition will likely come off the summer-list
  conferences in late September/October 2026 (OT2026).
- **No amicus support** at the cert stage, and no relists yet (the CFR
  pre-empted the first conference).

## Merits of the cert case

**For a grant.** The legal tension is real: *Richardson v. United States*, 526
U.S. 813 (1999), required juror unanimity on each predicate "violation" of the
federal CCE statute, choosing that construction partly to avoid the
constitutional unanimity problem; § 21.02(d) codifies exactly the construction
*Richardson* avoided. *Richardson*'s escape hatch — that the Sixth Amendment
unanimity right had not then been applied to the states — closed with *Ramos*.
The question recurs across a dozen-plus states with continuous-course-of-conduct
statutes (California, Arizona, New York, Wisconsin, Maryland, etc.), and the
Texas Court of Criminal Appeals has conspicuously ducked it (dismissing the
ground as improvidently granted in *Allen v. State* (2021), refusing PDR in
*Purcell* (2024) and here). The opinion below is published, and the petition
candidly frames the issue as one that "has not been, but should be settled" —
Rule 10(c)'s importance prong rather than a split.

**Against a grant.** There is **no split**: every Texas intermediate court,
the one federal district court to reach it (*Mumphord v. Lumpkin*, S.D. Tex.
2023), and — as far as the petition shows — every other state court to consider
such statutes post-*Ramos* has upheld them under the settled
elements-versus-manner-and-means framework (*Schad*, *Richardson*'s own
dictum). *Richardson* itself flagged child-sex-abuse course-of-conduct statutes
as statutes that "may well respond" to special proof difficulties and could
"represent an exception" — a ready distinction. The Court has seen this
question repeatedly since *Ramos* and has denied without recorded dissent; no
merits decision of the Court has ever engaged it (confirmed by CourtListener
search). Facts are unsympathetic (four teenage victims, extensive testimony),
which historically discourages the Court from using such cases as vehicles.
Practical stakes are blunted by six concurrent convictions (up to 20 years)
untouched by the question presented, so even a win does not promptly free
petitioner — a soft vehicle discount. No amici, no elite counsel, no CVSG.

## Base rates and calibration

From the committed statpack (live/historical slice): modern discretionary-cert
petitions grant at ~2.5–3.3% overall per recent Terms; **paid** petitions at
~5.4% (Term 2025 per-fee-class detail in `statpack.json`). Zero-relist
petitions grant at 0.8%; the statpack carries no call-for-response cut, and the
"Segment base rate by salience band" table referenced in the prompt is not
present in the current statpack version, so the CFR lift is estimated from
general knowledge of SCOTUS practice: a called-for response in a paid case
historically multiplies grant odds several-fold, putting a reasonable
conditional range at ~8–15%.

Weighing the CFR (strongly positive) against the issue-specific history
(uniform lower-court consensus, repeated recent denials of this exact
question, *Richardson*'s child-abuse dictum, unsympathetic facts, concurrent
sentences, no amici), I place P(grant) at **0.10** — well above the paid
baseline on the CFR signal, but the likeliest single outcome is a denial after
the BIO arrives and the case is distributed in the fall, possibly after a
relist. A GVR is implausible (no intervening decision to GVR against), and
dismissal/withdrawal has no basis in this record.

**Predicted disposition: denied** (granted = 0, probability = 0.10,
confidence = 0.70).

## Big-case score

0.50 — a merits ruling would decide the constitutionality of
continuous-course-of-conduct statutes in a dozen-plus states and reshape child
sexual-abuse prosecutions nationally (high stakes if decided), but the petition
itself is low-salience: no press profile, no amici, non-specialist counsel.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-17.json`), the petition text
including the full Eleventh Court of Appeals opinion in the appendix
(`record/documents/petition.txt`), the questions-presented extract, the event
definition, `metrics/statpack.md` + `statpack.json` base rates, `fedcourts
query` corpus priors (unproductive for this topic — see `retrieval.md`), and
three CourtListener MCP searches for prior petitions/merits treatment of the
question. No brief in opposition exists yet (due July 24, 2026), so the
State's cert-stage arguments could not be weighed.
