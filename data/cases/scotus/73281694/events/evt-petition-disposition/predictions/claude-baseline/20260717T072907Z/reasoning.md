# Norfolk Southern Railway Co. v. Mallory, No. 25-1208 — cert disposition

**Prediction: denied. P(grant, GVR included) = 0.20.**

## The legal question

This is the return trip of *Mallory v. Norfolk Southern Railway Co.*, 600 U.S.
122 (2023), which held (5–4) that Pennsylvania's consent-by-registration
general-jurisdiction scheme, 42 Pa. C.S. § 5301(a)(2)(i), does not violate the
Due Process Clause on these facts. The majority expressly left Norfolk
Southern's alternative dormant Commerce Clause argument "for consideration on
remand" (600 U.S. at 127 n.3), and Justice Alito's controlling-fifth-vote
concurrence said there is "a good prospect" the scheme violates the Commerce
Clause in a case with no forum link (id. at 160). Norfolk Southern now asks
the Court to answer exactly that reserved question: whether Pennsylvania may
exercise general jurisdiction over an out-of-state defendant, in a suit by an
out-of-state plaintiff on claims wholly unconnected to Pennsylvania, based
solely on corporate registration.

## Governing standard

Certiorari is discretionary (S. Ct. R. 10): a split among circuits or state
courts of last resort, an important undecided federal question, and vehicle
quality dominate. A jurisdictional prerequisite also looms here: under 28
U.S.C. § 1257(a) the Court reviews only final judgments of the highest state
court in which a decision could be had, and it will not review a federal claim
the state courts disposed of on an independent and adequate state
procedural ground.

## Facts from the snapshot and provisioned documents that drive the call

**Signals toward grant (why this is far above the paid-petition base rate):**

- **The Court itself teed the question up.** Footnote 3 of *Mallory* reserved
  it; Alito's concurrence is a roadmap for striking the scheme down, and the
  four *Mallory* dissenters (Barrett, Roberts, Kagan, Kavanaugh) are openly
  hostile to registration-jurisdiction. On the merits, five sympathetic votes
  plausibly exist.
- **Call for response.** Respondents waived (Apr 22, 2026); the Court
  requested a response on Apr 29, 2026 — at least one chambers took the
  petition seriously. In the statpack's signal cuts a CFR-like salience event
  is the strongest available pre-conference marker short of relists/CVSG
  (CVSG-flagged petitions run ~27% grant vs ~3% baseline; this is not a CVSG
  but the CFR is directionally similar, weaker).
- **Cert-stage amici** from the Atlantic Legal Foundation and Washington
  Legal Foundation; elite counsel (Carter Phillips / Sidley Austin); a paid
  petition by a Fortune-500 railroad — a "paradigmatic instrumentality of
  interstate commerce," a category the Court's dormant Commerce Clause cases
  treat solicitously (*Davis v. Farmers' Co-op*, 262 U.S. 312).
- **The issue is spreading**: Illinois has enacted registration-jurisdiction
  statutes; North Carolina (PDII, stayed by the state supreme court) and
  Minnesota (Lynn) courts have extended *Mallory*; petitioner credibly argues
  nationwide forum-shopping uncertainty.

**Signals toward denial (why they dominate):**

- **The BIO exposes a severe, likely dispositive vehicle defect.** The trial
  court never decided the dormant Commerce Clause question: by orders of
  April 5, 2024 and January 28, 2025 (reproduced in the BIO appendix), it held
  Norfolk Southern **waived** the argument under Pa. R. Civ. P. 1032 by
  omitting it from its original preliminary objections. The Superior Court and
  Pennsylvania Supreme Court denied discretionary interlocutory review without
  briefing, argument, or opinion. So no court below has passed on the federal
  question, and the ruling under review rests on an independent state
  procedural ground — precisely the posture in which the Court "with very rare
  exceptions" refuses review (*Adams v. Robertson*, 520 U.S. 83). The petition
  conspicuously describes the trial court as rejecting the arguments "without
  explanation," which the BIO persuasively rebuts with the orders themselves.
- **Finality under § 1257 is doubtful.** The case sits at the preliminary-
  objection stage in the trial court. Petitioner's *Cox Broadcasting* /
  *Goodyear* analogies are weakened by the BIO's point that in every cited
  case a lower court had actually adjudicated the jurisdictional question on
  the merits; here none did.
- **No split.** No federal circuit or state court of last resort has decided
  the dormant Commerce Clause question post-*Mallory*. The only appellate
  decision (Minnesota's nonprecedential *Lynn v. BNSF*) drew a cert petition
  (No. 25-1046) that the Court **denied on May 4, 2026** — while this very
  petition was pending with a CFR outstanding. *Am. Food & Vending* is on
  appeal to the Tenth Circuit; the North Carolina Supreme Court has PDII. The
  question is percolating, and the Court's normal course is to let it.
- **Distribution posture.** The petition was distributed July 15 for the
  September 28, 2026 long conference — the modal outcome of the long
  conference for any given petition is denial, and no relist signal exists yet.

## Weighing

Anchors: the statpack's modern discretionary-cert slice runs ~95% denied /
~3% granted overall; Term-2025 estimated grant rate 2.5%. A CFR'd, amicus-
supported, elite-counsel paid petition on a question the Court itself
reserved sits far above that anchor — comparable CFR'd petitions historically
grant in the 10–20% range, and the *Mallory* history alone could plausibly
push this one to 30%+ **if the vehicle were clean**.

It is not. The waiver holding means the Court would have to reach past an
independent and adequate state ground and decide a constitutional question no
lower court addressed — the classic flaw that kills otherwise-grantable
petitions. Petitioner's best counters (the Superior Court's citation of *Hunt
Refining* reads merits-flavored; footnote 3 of *Mallory* assumed the argument
remained live on remand; the waiver ruling may be wrong state law) are
arguable but require the Court to litigate Pennsylvania procedure at the cert
stage. With a clean vehicle likely to emerge from the Tenth Circuit or a state
supreme court within a Term or two, and with the Court having just denied
*Lynn*, the most probable outcome is denial — possibly with a statement from
Justice Alito respecting denial or noting the vehicle problem.

A GVR is essentially unavailable (no intervening decision). Dismissal is
implausible. I put P(grant) at **0.20** — well above base rate for the CFR,
the reserved question, and the five potentially sympathetic votes; well below
even odds for the waiver/finality defects, the absence of a split, and the
contemporaneous *Lynn* denial.

**Disposition: denied; granted = 0; probability = 0.20; confidence = 0.6.**

## Inputs used

- Snapshot `data/cases/scotus/73281694/record/snapshots/2026-07-17.json`
  (docket through July 15, 2026 distribution).
- Provisioned `questions-presented.txt`, `petition.txt` (29 pp.), and
  `brief-in-opposition.txt` (32 pp., incl. the trial court's waiver orders) —
  the QP anchored the analysis; the petition and BIO were weighed against each
  other as the contract directs.
- Committed `metrics/statpack.md` base rates (modern discretionary-cert
  slice, per-Term table, CVSG/relist cuts).
