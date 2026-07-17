# Bell v. Gilley, No. 25-1141 — petition disposition

**Prediction: P(any grant, GVR included) = 0.45; modal disposition `denied`.**
This is a close call, and the probability reflects that: if granted, the
disposition would be `gvr` (a Munsingwear vacatur), not a plenary grant.

## What is actually being asked

This is not an ordinary cert petition. The sole question presented asks the
Court to **vacate the Fourth Circuit's judgment under United States v.
Munsingwear, Inc., 340 U.S. 36 (1950), and remand with instructions to dismiss
as moot** — the petition's own conclusion requests grant-vacate-remand, not
plenary review. Bell, a federal prisoner who served more than twenty years
(overserving his post-Taylor-corrected sentence by roughly 2,422 days),
challenged his 2003 mandatory-Guidelines career-offender sentence via 28
U.S.C. § 2241. The Fourth Circuit (Bell v. Streeval, 147 F.4th 452) held that
Jones v. Hendrix forecloses saving-clause review even for constitutional
claims and that this raises no Suspension Clause problem, with Judge
Richardson concurring separately on the Suspension Clause rationale. Three
weeks after the mandate issued, Bell completed his (early-terminated) term of
supervised release, mooting the case before he could seek review.

So the realistic outcome space is binary: **GVR with instructions to dismiss
as moot** (counts as a grant) or **deny** (leaving the published precedent in
place). Plenary grant, dismissal, or withdrawal are negligible tail
possibilities.

## Signals pointing toward a grant (GVR)

1. **Call for response after waiver.** The government waived (Apr 9); the
   Court requested a response (Apr 22). The Court can deny without a
   response, so the CFR shows the Munsingwear request survived initial pool
   screening and is being taken seriously. The SG has since taken two
   extensions (BIO now due July 22, 2026), suggesting a substantive
   opposition is being written.
2. **The Court's revealed practice is generous with Munsingwear vacatur.**
   Summary vacaturs on mootness are routine (e.g., Chapman v. Doe (2023),
   granted over a dissent arguing the practice had become too automatic;
   Beers v. Barr; Slatery v. Adams & Boyle; Kendall v. Doster; Tennessee v.
   Kennedy (Jan. 2026)). The corpus shows a steady stream of `gvr`
   dispositions in the current Term, including several from the Fourth
   Circuit.
3. **The government's own litigating position helps Bell.** The government
   argued in the Fourth Circuit that the case became moot when Bell left
   prison in June 2024 — i.e., *before* the court of appeals decided it. On
   that view the judgment issued in a moot case, which makes vacatur the
   textbook remedy and makes it awkward for the SG to now defend the
   judgment's preservation.
4. **Sympathetic equities and elite counsel.** Arnold & Porter (counsel of
   record Dana Kagan McGinley, with Andrew Tutt, who appears on a successful
   GVR petition this Term in the corpus priors); a petitioner who overserved
   by nearly seven years on a sentence enhanced under a residual clause
   materially identical to the one Johnson invalidated; a paid petition on
   Term 2025's docket.

## Signals pointing toward denial

1. **The Bancorp "voluntary action" problem is real.** Under U.S. Bancorp v.
   Bonner Mall, vacatur is inequitable where the party seeking it "caused the
   mootness by voluntary action." Bell's supervised release was originally
   set to run to roughly June 2027 — well past any plausible cert timeline.
   The case mooted in December 2025 only because Bell himself moved (pro se)
   for early termination and the sentencing court granted it in part. That
   but-for causation gives the SG a strong, doctrinally clean opposition:
   this was not pure "happenstance." Bell's counters (the government
   consented to early termination; the government said the case was already
   moot in 2024 anyway) blunt but do not eliminate the argument.
2. **Vacatur here erases published circuit precedent the government won.**
   The Fourth Circuit's post-Jones saving-clause/Suspension Clause holding is
   valuable to the government; the SG will defend it, and several Justices in
   the Jones majority may prefer the precedent stand. Denial costs the Court
   nothing and requires no opinion.
3. **Base rates.** Modern discretionary-cert petitions deny ~95% overall;
   CA4-originating petitions grant ~4.6%. Those rates understate this
   petition's chances (it asks for the cheap disposition, drew a CFR, and is
   well-lawyered), but they anchor the prior low: the burden is on the
   petition to distinguish itself, and the observable signals only partially
   do so.

## Net assessment

Conditional on the Court reaching a clean "happenstance mootness" view, this
is a near-certain summary vacatur — the practice is routine, and the
government's own mootness argument below invites it. But the early-termination
sequence gives the SG a genuine Bancorp defense, and the Court's cheapest path
with a moot prisoner case and a government-favorable published precedent is a
silent denial. I weigh these as slightly favoring denial: **P(grant incl.
GVR) = 0.45**, modal disposition **denied**. If granted, the form is a GVR
(Munsingwear vacatur with instructions to dismiss as moot). Timing-wise the
BIO is due July 22, 2026, so the likely disposition point is the long
conference or shortly after (early October 2026); a relist before a summary
vacatur would be unsurprising.

Per-judge votes are omitted: a cert-stage disposition of this kind is decided
without published votes, and I have no signal granular enough to make
per-Justice calls meaningful.

## Inputs used

- Snapshot `data/cases/scotus/73281628/record/snapshots/2026-07-16.json`
  (docket entries through June 16, 2026; paid case, Term 2025, linked
  application 25A813).
- Provisioned `questions-presented.txt` and full `petition.txt` (20 pp.,
  fetched 2026-07-16, no truncation) — the QP and the Reasons for Granting
  section drive the analysis above.
- No brief in opposition exists yet (due July 22, 2026), so the SG's actual
  ground of opposition is a modeled assumption, the main uncertainty in this
  forecast.
- Corpus priors and the committed statpack base rates (see `retrieval.md`).

The case is genuinely pending (`forward` mode); no outcome information was
sought or encountered.
